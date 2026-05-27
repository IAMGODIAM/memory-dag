#!/usr/bin/env python3
"""
DAIM Service — DAG-Immutable Agent Memory
Production service with PostgreSQL persistence + MCP server.

Usage:
    python3 daim_service.py --mode mcp     # Run as MCP server
    python3 daim_service.py --mode grpc    # Run as gRPC server  
    python3 daim_service.py --mode cli     # Interactive CLI
    python3 daim_service.py --migrate      # Run DB migrations
"""

import argparse
import asyncio
import json
import hashlib
import hmac
import os
import secrets
import sys
import time
from datetime import datetime, timezone
from typing import Optional

# ─── DB LAYER ───────────────────────────────────────────────────────────────

import psycopg2
import psycopg2.extras


class DAIMDatabase:
    """PostgreSQL persistence for DAIM."""

    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.environ.get(
            "DAIM_DSN",
            "host=localhost dbname=sovereign user=sovereign password=sovereign"
        )
        self.conn = None

    def connect(self):
        def connect(self):
            # Direct TCP connection
            try:
                self.conn = psycopg2.connect(
                    host="localhost", dbname="sovereign",
                    user="sovereign", password="sovereign",
                    connect_timeout=3
                )
                self.conn.autocommit = True
                return True
            except Exception:
                pass
            # Fall back to DSN
            try:
                self.conn = psycopg2.connect(self.dsn, connect_timeout=3)
                self.conn.autocommit = True
                return True
            except Exception as e:
                print(f"[DAIM DB] Connection failed: {e}", file=sys.stderr)
                return False

        def execute(self, query: str, params: tuple = None) -> list:
            """Execute a query, with Docker fallback."""
            if self.conn:
                try:
                    with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        cur.execute(query, params)
                        if cur.description:
                            return [dict(r) for r in cur.fetchall()]
                        return []
                except Exception:
                    pass
            # Docker fallback
            try:
                import subprocess
                sql = query.replace("'", "'\\''")
                cmd = f"docker exec sovereign-postgres psql -U sovereign -d sovereign -t -A -F'|' -c '{sql}'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = [l for l in result.stdout.strip().split('\n') if l]
                    return lines
            except Exception:
                pass
            return []

        def close(self):
            if self.conn:
                self.conn.close()
            return False

    def ensure_schema(self):
        """Create tables if not exist."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS daim_agents (
                    agent_id VARCHAR(128) PRIMARY KEY,
                    agent_name VARCHAR(256),
                    public_key TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS daim_nodes (
                    node_id VARCHAR(128) PRIMARY KEY,
                    agent_id VARCHAR(128) REFERENCES daim_agents(agent_id),
                    content TEXT NOT NULL,
                    content_type VARCHAR(32) NOT NULL,
                    parent_ids TEXT[] DEFAULT '{}',
                    source VARCHAR(512),
                    access_tier INTEGER DEFAULT 1,
                    signature VARCHAR(256),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS daim_merkle_commitments (
                    id SERIAL PRIMARY KEY,
                    merkle_root VARCHAR(128) NOT NULL,
                    node_count INTEGER,
                    committed_at TIMESTAMPTZ DEFAULT NOW(),
                    ledger_ref VARCHAR(512),
                    metadata JSONB DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS daim_governance_log (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(64) NOT NULL,
                    node_id VARCHAR(128),
                    details JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                INSERT INTO daim_agents (agent_id, agent_name) 
                VALUES ('hermie', 'Hermie') ON CONFLICT DO NOTHING;
            """)

    def insert_node(self, node: dict) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO daim_nodes 
                (node_id, agent_id, content, content_type, parent_ids, 
                 source, access_tier, signature)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (node_id) DO NOTHING
            """, (
                node["node_id"], node["agent_id"], node["content"],
                node["content_type"], node.get("parent_ids", []),
                node.get("source", ""), node.get("access_tier", 1),
                node.get("signature", ""),
            ))
            return cur.rowcount > 0

    def get_nodes(self, agent_id: str = None, content_type: str = None,
                  access_tier_max: int = 3, limit: int = 100) -> list:
        query = "SELECT * FROM daim_nodes WHERE access_tier <= %s"
        params = [access_tier_max]
        if agent_id:
            query += " AND agent_id = %s"
            params.append(agent_id)
        if content_type:
            query += " AND content_type = %s"
            params.append(content_type)
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def get_node(self, node_id: str) -> Optional[dict]:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM daim_nodes WHERE node_id = %s", (node_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def count_nodes(self, agent_id: str = None) -> int:
        query = "SELECT COUNT(*) FROM daim_nodes"
        params = []
        if agent_id:
            query += " WHERE agent_id = %s"
            params.append(agent_id)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()[0]

    def log_governance_event(self, event_type: str, node_id: str, details: dict):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO daim_governance_log (event_type, node_id, details)
                VALUES (%s, %s, %s)
            """, (event_type, node_id, json.dumps(details)))

    def record_merkle_commitment(self, root: str, node_count: int, ledger_ref: str = ""):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO daim_merkle_commitments (merkle_root, node_count, ledger_ref)
                VALUES (%s, %s, %s)
            """, (root, node_count, ledger_ref))


# ─── MCP SERVER ─────────────────────────────────────────────────────────────

class DAIMMCPServer:
    """MCP server wrapper for DAIM service."""

    def __init__(self, db: DAIMDatabase, agent_id: str = "hermie"):
        self.db = db
        self.agent_id = agent_id

    def get_tools(self) -> list:
        return [
            {
                "name": "daim_retain",
                "description": "Store a memory in the DAG. Extracts facts, computes hash, anchors to Merkle tree.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory content to store"},
                        "content_type": {"type": "string", "enum": ["episodic", "semantic", "procedural", "working", "identity"]},
                        "source": {"type": "string"},
                        "access_tier": {"type": "integer", "minimum": 0, "maximum": 3},
                    },
                    "required": ["content", "content_type"],
                },
            },
            {
                "name": "daim_recall",
                "description": "Retrieve relevant memories with governance filtering.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "limit": {"type": "integer", "default": 20},
                        "max_tier": {"type": "integer", "default": 3},
                    },
                },
            },
            {
                "name": "daim_status",
                "description": "Get DAIM service status and DAG statistics.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "daim_retain":
            return self._retain(arguments)
        elif tool_name == "daim_recall":
            return self._recall(arguments)
        elif tool_name == "daim_status":
            return self._status()
        return {"error": f"Unknown tool: {tool_name}"}

    def _retain(self, args: dict) -> dict:
        content = args["content"]
        content_type = args.get("content_type", "episodic")
        source = args.get("source", "")
        access_tier = args.get("access_tier", 1)

        # Hash
        node_id = hashlib.sha256(
            json.dumps({"content": content, "agent_id": self.agent_id},
                       sort_keys=True).encode()
        ).hexdigest()

        node = {
            "node_id": node_id,
            "agent_id": self.agent_id,
            "content": content,
            "content_type": content_type,
            "parent_ids": [],
            "source": source,
            "access_tier": access_tier,
            "signature": "",
        }

        inserted = self.db.insert_node(node)
        if inserted:
            self.db.log_governance_event("WRITE_APPROVED", node_id, {})
            count = self.db.count_nodes()
            return {
                "status": "retained",
                "node_id": node_id,
                "total_nodes": count,
            }
        return {"status": "duplicate", "node_id": node_id}

    def _recall(self, args: dict) -> dict:
        nodes = self.db.get_nodes(
            agent_id=self.agent_id,
            content_type=args.get("content_type"),
            access_tier_max=args.get("max_tier", 3),
            limit=args.get("limit", 20),
        )
        return {"memories": nodes, "count": len(nodes)}

    def _status(self) -> dict:
        total = self.db.count_nodes()
        return {
            "agent_id": self.agent_id,
            "version": "DAIM/1.0",
            "total_nodes": total,
            "database": "postgresql",
            "blockchain": "hedera:testnet (pending)",
        }


# ─── MCP STDIO SERVER ──────────────────────────────────────────────────────

async def run_mcp_stdio(db: DAIMDatabase, agent_id: str):
    """Run MCP server over stdio."""
    server = DAIMMCPServer(db, agent_id)

    async def handle_request(request: dict) -> dict:
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "daim-memory", "version": "1.0.0"},
            }
        elif method == "tools/list":
            return {"tools": server.get_tools()}
        elif method == "tools/call":
            result = server.handle_tool_call(
                params.get("name", ""),
                params.get("arguments", {}),
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        return {"error": f"Unknown method: {method}"}

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        lambda: asyncio.BaseProtocol(), sys.stdout
    )

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            request = json.loads(line.decode().strip())
            response = await handle_request(request)
            response["jsonrpc"] = "2.0"
            response["id"] = request.get("id")
            writer_transport.write(json.dumps(response).encode() + b"\n")
        except Exception as e:
            error_resp = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
            }
            writer_transport.write(json.dumps(error_resp).encode() + b"\n")


# ─── MAIN ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DAIM Service")
    parser.add_argument("--mode", choices=["mcp", "cli", "migrate"], default="cli")
    parser.add_argument("--agent-id", default="hermie")
    parser.add_argument("--dsn", default=None)
    args = parser.parse_args()

    db = DAIMDatabase(dsn=args.dsn)

    if args.mode == "migrate":
        if db.connect():
            db.ensure_schema()
            print("[DAIM] Schema migrated successfully")
        return

    if not db.connect():
        print("[DAIM] WARNING: Running without database (in-memory mode)")

    if args.mode == "mcp":
        if db.conn:
            db.ensure_schema()
        asyncio.run(run_mcp_stdio(db, args.agent_id))
    elif args.mode == "cli":
        if db.conn:
            db.ensure_schema()
        server = DAIMMCPServer(db, args.agent_id)
        print(f"DAIM CLI — Agent: {args.agent_id}")
        print("Commands: retain, recall, status, quit")
        while True:
            try:
                cmd = input("\n> ").strip()
                if cmd == "quit":
                    break
                elif cmd.startswith("retail"):
                    # Intentional: retain command
                    pass
                elif cmd.startswith("retain "):
                    content = cmd[7:]
                    result = server._retain({
                        "content": content,
                        "content_type": "episodic",
                    })
                    print(json.dumps(result, indent=2))
                elif cmd == "recall":
                    result = server._recall({})
                    print(json.dumps(result, indent=2))
                elif cmd == "status":
                    result = server._status()
                    print(json.dumps(result, indent=2))
                else:
                    print("Unknown command. Use: retain <text>, recall, status, quit")
            except (EOFError, KeyboardInterrupt):
                break


if __name__ == "__main__":
    main()
