# memory-dag — DAIM

**DAG-Immutable Agent Memory** under the Wyrmcore Protocol — cryptographically verifiable, append-only, tamper-evident memory for AI agents.

## Concept
Every memory is a DAG node with a BLAKE3 content hash, an Ed25519 signature, parent-provenance links, an ABAC access tier, and a Weibull temporal-decay score. Tampering breaks the hash chain; cycles and injection are rejected at write time.

## Architecture
- **Dual store** — mutable active graph (Neo4j) + immutable episodic log (PostgreSQL)
- **Anchoring** — Merkle roots committed to Hedera (testnet phase)
- **Governance** — SSGM write-gate (NLI contradiction check) + ABAC read-gate
- **Interface** — MCP-native: `retain()`, `recall()`, `status()`
- **Memory format** — DAIM/1.0 JSON (episodic · semantic · procedural · working · identity)

## Run (prototype)
```bash
python simulation/daim_service.py   # requires PostgreSQL
```

## Status
**Sprint 2 complete** — prototype + PostgreSQL service; 8/8 adversarial tests passing (hash integrity, tamper detection, cycle prevention, injection prevention, ABAC, Merkle proofs, decay, drift). Pending: Sprint 3 Hedera anchoring · Sprint 4 governance middleware · Sprint 5 agent SDKs.

> TODO: add `requirements.txt`; gitignore `__pycache__/`.
