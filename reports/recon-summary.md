# DAG-BASED IMMUTABLE MEMORY FOR AGENTS
## Full Recon & Execution Plan — Wyrmcore Protocol v1.0
### Visionary: Hermie | Date: 2026-05-27 | Status: ACTIVE

---

## 1. CHAIRMAN'S THESIS

Agent memory is broken. Current systems are stateless, vendor-locked, mutable, and prone to catastrophic forgetting. The solution exists at the intersection of:

- **DAG-based blockchains** (IOTA Tangle, Hedera Hashgraph) — immutable, feeless, high-throughput ledgers
- **Cryptographic provenance** (Merkle trees, ECDH-keyed encryption, ZK proofs) — tamper-evident, verifiable, private
- **Knowledge graphs** (Neo4j, pgvector, graph-RAG) — structured, relationship-aware, queryable
- **Agent-native protocols** (MCP, A2A, PAM) — interoperable, model-agnostic, portable

The vision: **Every agent action, memory, and reasoning step is committed to an immutable DAG. Memory is not a cache — it is a ledger.** Agents become epistemic entities whose outputs are provably derived, temporally anchored, and impervious to post-hoc revision.

---

## 2. RECON — KEY SOURCES & FINDINGS

### 2.1 Foundational Papers

| ID | Source | Key Contribution |
|---|---|---|
| **[Wright2025]** | arXiv:2506.13246 — "On Immutable Memory Systems for Artificial Agents: A Blockchain-Indexed Automata-Theoretic Framework Using ECDH-Keyed Merkle Chains" | **THE foundational paper.** Introduces the Merkle Automaton: deterministic finite automata extended with blockchain-based commitments. Every transition, memory fragment, and reasoning step is committed within a Merkle structure rooted on-chain. Uses ECDH-derived symmetric encryption for access control over append-only DAG knowledge graphs. Zero-knowledge proofs for verifiable, privacy-preserving inclusion attestations. Defines "memory as law" — knowledge that cannot be erased, only appended. Formalizes Append-Only Reasoning Graphs (AORG), consensus-time anchoring via blockchain, and modular DAG instancing for partial context awareness. |
| **[Ravindran2025]** | arXiv:2605.11032 — "Portable Agent Memory: A Protocol for Provenance-Verified Memory Transfer Across Heterogeneous LLM Agents" (Microsoft) | **The portability protocol.** Five-component memory model M=(E,S,P,W,I): episodic, semantic, procedural, working, identity. Merkle-DAG with BLAKE3 content-addressing and Ed25519 signing. Capability-scoped access tokens. Injection-resistant re-hydration pipeline. Transfer Continuity Scores of 0.83-0.92 across Claude/GPT-4/Gemini vs 0.28-0.45 no-memory baseline. Python SDK, 54 tests, <0.5s execution. |
| **[SSGM2026]** | arXiv:2603.11768 — "Governing Evolving Memory in LLM Agents: Risks, Mechanisms, and the Stability and Safety Governed Memory (SSGM) Framework" | **THE governance framework.** Defines 4 failure categories: Stability (semantic drift, procedural drift, goal drift), Validity (hallucination, temporal obsolescence), Efficiency (latency, index bloat), Safety (memory poisoning, privacy leakage). Proposes governance middleware that decouples memory evolution from execution. Formal bounded semantic drift theorem. Weibull decay functions for temporal relevance. Write-validation gates with NLI contradiction checking. Immutable episodic log + mutable active graph dual-track architecture. |

### 2.2 Open-Source Implementations

| Project | Source | Status | Notes |
|---|---|---|---|
| **Hindsight MCP** | github.com/vectorize-io/hindsight | ✅ Active (v0.7, Mar 2026) | MCP-native memory server. retain/recall/reflect operations. Entity resolution, multi-strategy retrieval (semantic + BM25 + graph + temporal). Cross-encoder reranking. Docker-deployable. Mental models (auto-updating summaries). Persists to PostgreSQL+pgvector. This is the **closest existing implementation** to what we need. |
| **MingSeal** | github.com/jerrleey-cmd/mingseal-immutable-memory (based on Wright2025) | ⚠️ Early | MCP server for immutable, chain-verifiable memory. Based directly on Wright's paper. Works with any MCP-compatible agent. |
| **Portable Agent Memory SDK** | arXiv:2605.11032 (Microsoft) | ✅ Released | Python SDK, 54 tests. .pam/.pam.cbor formats. Ed25519 signing. Capability tokens. |
| **mem0** | github.com/mem0ai/mem0 | ✅ Active | Universal memory layer. SaaS + open-source. NO cryptographic verification, NO portability. Vendor lock-in. **Anti-pattern.** |
| **Letta/MemGPT** | github.com/letta-ai/letta | ✅ Active | OS-inspired memory management. Paging between context and external storage. No portability, no immutability. |
| **Zep** | github.com/getzep/zep | ✅ Active | Temporal knowledge graphs. Proprietary export format. No cryptographic integrity. |
| **AgentCivics** | Glama (@agentcivics/mcp-server) | 🔄 Early | "Civil registry for AI agents — identity is memory." Permissionless, immutable, decentralized. |

### 2.3 DAG Blockchain Infrastructure

| Platform | Architecture | Consensus | TPS | Fees | Agent Suitability |
|---|---|---|---|---|---|
| **IOTA Tangle** | DAG (Tangle) | Coordinatorless, PoW-light | 1000+ | Zero | ✅ Ideal for micro-transactions between agents |
| **Hedera Hashgraph** | DAG (gossip-about-gossip) | Virtual voting, aBFT | 10,000+ | $0.0001 | ✅ Enterprise-grade, governed, EVM-compatible |
| **Arweweave** | Blockchain (Succinct Proof of Access) | Proof of Access | ~100 | One-time | ✅ Permanent storage for large payloads |
| **Ethereum L2 (Base, Polygon)** | Rollup | Various | 2000+ | $0.001+ | ✅ Smart contract capability, EVM ecosystem |

**Recommendation:** Use **Neo4j** (already running on our mesh) for the graph layer, **IOTA Feeless DAG** for immutable commitment layer, and **IPFS/Arweave** for large blob storage. Wright's Merkle Automaton architecture applies regardless of the specific DAG ledger used.

---

## 3. THE MEMORY PROBLEM — ROOT CAUSE ANALYSIS

### 3.1 Six Critical Failures (from Ravindran2025, SSGM2026)

1. **Vendor Lock-in** — Memory accumulated in Claude/Gemini/GPT cannot be exported
2. **Session Amnesia** — Each new conversation starts from zero
3. **No Integrity Verification** — No mechanism to detect tampering
4. **Epistemic Drift** — Iterative summarization causes gradual nuance loss (formalized in SSGM Eq.4)
5. **Catastrophic Forgetting** — New learning overwrites old knowledge
6. **Memory Poisoning** — Adversarial content injected into storage hijacks agent behavior

### 3.2 The Stability-Plasticity Dilemma (SSGM)

- **Plasticity**: Agent must learn and adapt
- **Stability**: Agent must not forget or drift
- **Current systems**: Unconstrained autonomy → drift, hallucination, poisoning
- **SSGM solution**: Governance middleware that intercepts all memory writes with NLI contradiction checks + Weibull temporal decay

### 3.3 Wright's Insight: Memory as Law

> "Memory is not a cache but as a ledger — one whose contents are enforced by protocol, bound by cryptography, and constrained by formal logic."
> 
> "The agent becomes not a stochastic regurgitator of patterns but a witness whose statements are theorems in a committed, verifiable epistemic calculus."

---

## 4. PROPOSED ARCHITECTURE — DAG-IMMUTABLE AGENT MEMORY (DAIM)

### 4.1 Core Principles

1. **Append-only**: No memory is ever deleted, only appended with refinement edges
2. **Cryptographically anchored**: Every node has a hash; the DAG root is committed to a blockchain
3. **Provenance-verified**: Every memory unit carries source, timestamp, originator signature
4. **Access-controlled**: ECDH-derived keys enforce privilege tiers per fragment
5. **Portable**: Standard format (.pam/.pam.cbor) for cross-agent transfer
6. **Governed**: Write-validation gates prevent hallucination cascades
7. **Temporal**: Weibull decay functions auto-deprecate stale memories
8. **Identifiable**: Each agent has a persistent Ed25519 identity key

### 4.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT LAYER (Hermes, Sue, etc.)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Hermie   │  │ Sue      │  │ Scout    │  ... agents          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │              │              │                            │
│       └──────────────┼──────────────┘                           │
│                      │ MCP / gRPC                                │
├──────────────────────┼──────────────────────────────────────────┤
│                 DAIM SERVICE LAYER                              │
│  ┌───────────────────┴──────────────────────────┐               │
│  │           Memory API (gRPC / MCP)             │               │
│  │  retain() │ recall() │ reflect() │ prove()    │               │
│  └───────────────────┬──────────────────────────┘               │
│                      │                                          │
│  ┌───────────────────┴──────────────────────────┐               │
│  │         Governance Middleware (SSGM)          │               │
│  │  Write Gate (NLI check) │ Read Gate (ABAC)   │               │
│  │  Weibull Decay │ Provenance Validator          │               │
│  └───────────────────┬──────────────────────────┘               │
│                      │                                          │
│  ┌───────────────────┴──────────────────────────┐               │
│  │           Dual-Track Storage                   │               │
│  │  ┌─────────────────┐  ┌─────────────────────┐ │               │
│  │  │ Mutable Active   │  │ Immutable Episodic  │ │               │
│  │  │ Graph (Neo4j)    │  │ Log (IOTA/Arweave)  │ │               │
│  │  │ + pgvector       │  │ + Merkle Roots      │ │               │
│  │  └─────────────────┘  └─────────────────────┘ │               │
│  └───────────────────────────────────────────────┘               │
│                                                                  │
│  ┌───────────────────────────────────────────────┐               │
│  │        Crypto Layer (Wright Architecture)      │               │
│  │  Ed25519 Identity │ ECDH Key Derivation       │               │
│  │  BLAKE3 Content Hash │ Merkle-DAG Provenance  │               │
│  │  ZK Inclusion Proofs │ Consensus-Time Anchors  │               │
│  └───────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Memory Artifact Format (Based on PAM)

```json
{
  "version": "DAIM/1.0",
  "agent_id": "did:dag:hermie:e5ab...",
  "artifact_id": "blake3:7a3f...",
  "created_at": "2026-05-27T20:42:00Z",
  "signature": "ed25519:...",
  "components": {
    "episodic": [...],
    "semantic": [...],
    "procedural": [...],
    "working": [...],
    "identity": [...]
  },
  "root_hash": "blake3:...",
  "parent_ids": [],
  "blockchain_anchor": {
    "ledger": "hedera:testnet",
    "transaction_id": "0.0.12345@1716844920.000000001",
    "merkle_root": "blake3:...",
    "consensus_timestamp": "2026-05-27T20:42:03.214567890Z"
  }
}
```

### 4.4 Node Structure (Each Memory Fragment)

```
Node = {
  content: <any>,           // The actual memory payload
  content_type: <string>,   // "episodic" | "semantic" | "procedural" | "working" | "identity"
  id: BLAKE3(canonical(content)),  // Content-addressable
  parent_ids: [Node.id],    // DAG edges (provenance chain)
  created_at: <ISO8601>,    // Consensus-anchored timestamp
  source_provenance: {
    originator: <agent_id>,
    source_uri: <string>,
    retrieval_context: <jsonb>
  },
  access_tier: <int>,       // Privilege level (0=public, 1=standard, 2=confidential, 3=root)
  encryption: {
    algorithm: "AES-256-GCM",
    key_derivation: "ECDH-HKDF",
    encrypted: <base64>
  },
  decay: {
    model: "weibull",
    scale: 30,              // days
    shape: 1.5,             // curvature
    last_accessed: <ISO8601>,
    relevance_score: 0.87   // Computed at query time
  }
}
```

### 4.5 The Append-Only Reasoning Graph (AORG)

Directed Acyclic Graph of inference nodes:

```
AORG = (V, E) where
  V = {v | v = (provenance, signature, hash, consensus_time)}
  E = {(u, v) | v is a logical refinement of u}
  
Constraints:
  - Acyclicity: no path v → ... → v
  - Justifiability: each edge must correspond to a formal inference rule
  - Finality: once committed and anchored, no vertex may be deleted
  - Traceability: any v must be reducible to axiomatic root nodes
```

### 4.6 Governance Middleware (SSGM Implementation)

**Write Path:**
```
Agent generates delta → 
  Write Validation Gate (NLI contradiction check against core facts) →
    if CONTRADICTS: reject, create refinement fork
    if CONSISTENT: pass →
      Encrypt with ECDH-derived key →
        Compute BLAKE3 hash →
          Add to Mutable Active Graph (Neo4j) →
            Add to Immutable Episodic Log (IOTA Tangle) →
              Compute Merkle root →
                Commit root to blockchain (Hedera) →
                  Return proof-of-inclusion
```

**Read Path:**
```
Agent query → 
  Read Gate (ABAC access control check) →
    Retrieve from Active Graph (Neo4j + pgvector) →
      Parallel retrieval: semantic + BM25 + graph + temporal →
        Cross-encoder rerank →
          Apply Weibull decay filter (drop below freshness threshold) →
            Capability filter (remove unauthorized entries) →
              Summarize if exceeds token budget →
                Injection-resistant framing →
                  Return structured context
```

**Reconciliation (Periodic):**
```
Every N operations or T hours:
  Extract drifted concepts from Active Graph →
    Compare against Immutable Episodic Log →
      Compute semantic drift (cosine distance in embedding space) →
        if drift > threshold: reconcile by replaying raw traces →
          Emit reconciliation event to governance log
```

---

## 5. IMPLEMENTATION SPRINT PLAN

### Sprint 0: Foundation (Current)

| Task | Owner | Deliverable | Status |
|---|---|---|---|
| Recon complete | Hermie | this document | ✅ |
| Architecture finalized | Hermie | committed spec | 🔄 |
| Neo4j schema | Forge | deployed graph DB | ⏳ |
| PostgreSQL + pgvector | Draco | running + indexed | ⏳ |

### Sprint 1: Core DAG Memory Service

| Task | Owner | Deliverable | Status |
|---|---|---|---|
| `daim-service` Python package | Forge | gRPC + MCP server | ⏳ |
| Memory Node data model | Forge | Pydantic models | ⏳ |
| retain() endpoint | Forge | fact extraction + graph write | ⏳ |
| recall() endpoint | Forge | multi-strategy retrieval | ⏳ |
| reflect() endpoint | Forge | LLM-powered synthesis | ⏳ |
| Ed25519 identity keys | Draco | key generation + registry | ⏳ |
| BLAKE3 content addressing | Forge | hash computation | ⏳ |
| Merkle-DAG construction | Draco | tree build + verification | ⏳ |
| Capability token system | Forge | scoped access tokens | ⏳ |

### Sprint 2: Blockchain Anchoring & Provenance

| Task | Owner | Deliverable | Status |
|---|---|---|---|
| IOTA Tangle integration | Forge | feeless commitment TXs | ⏳ |
| Hedera testnet anchor | Draco | smart contract deployment | ⏳ |
| Consensus-time anchoring | Forge | block-height timestamps | ⏳ |
| ZK inclusion proofs | Scout | proof generation + verify | ⏳ |
| ECDH-HKDF key derivation | Forge | per-fragment encryption | ⏳ |
| Audit trail system | Draco | causal chain logging | ⏳ |

### Sprint 3: Governance Middleware

| Task | Owner | Deliverable | Status |
|---|---|---|---|
| Write Validation Gate (NLI) | Forge | contradiction detection | ⏳ |
| Weibull decay function | Forge | temporal relevance scoring | ⏳ |
| Read Filtering Gate (ABAC) | Forge | access-scoped retrieval | ⏳ |
| Injection-resistant framing | Forge | content escaping + typed blocks | ⏳ |
| Reconciliation engine | Forge | drift detection + correction | ⏳ |

### Sprint 4: Agent Integration & Testing

| Task | Owner | Deliverable | Status |
|---|---|---|---|
| Hermes MCP registration | Hermie | add daim to MCP config | ⏳ |
| Hermie memory service | Hermie | persistent agent memory | ⏳ |
| Sue (Base44) integration | Sue | memory API connection | ⏳ |
| Forge/Scout/Draco memory | Forge | all agents connected | ⏳ |
| Adversarial testing suite | Scout | tamper/drift/poison tests | ⏳ |
| Transfer Continuity Score eval | Scout | benchmark vs baseline | ⏳ |
| Load testing (10k+ operations) | Draco | throughput + latency report | ⏳ |

### Sprint 5: Production Hardening & Documentation

| Task | Owner | Deliverable | Status |
|---|---|---|---|
| .pam/.pam.cbor serialization | Forge | portable artifact format | ⏳ |
| Python SDK | Forge | pip installable package | ⏳ |
| TypeScript SDK | Forge | npm installable package | ⏳ |
| API documentation | Miranda | full OpenAPI spec | ⏳ |
| Security audit | Scout | penetration test report | ⏳ |
| Performance benchmarks | Draco | ops/sec, storage growth, latency | ⏳ |

---

## 6. RISK REGISTER

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Key compromise | Full DAG rewrite | Low | YubiKey hardware signing, multi-sig policies |
| State bloat | Storage overflow | Medium | Checkpointing → Arweave snapshots, periodic pruning |
| Epistemic ossification | Can't adapt to new info | Medium | Conflict resolution protocols, distinguish drift from legitimate update |
| Blockchain dependency | Network outage | Low | Local-first with async anchoring, queue + retry |
| ZK proof overhead | Latency increase | Medium | Batch proofs, async generation, hardware acceleration |
| Governance gate latency | Slow writes | Medium | Async validation pipeline, optimistic writes with background sanitization |
| Cross-agent memory leakage | Privacy violation | Low | Strict ABAC, per-agent isolated banks, no shared context without explicit capability grant |
| Regulatory (GDPR right to erasure) | Legal | Low | Store only hashes on-chain; raw payloads encrypted & deletable |

---

## 7. SUCCESS CRITERIA

| Metric | Target | Measurement |
|---|---|---|
| Transfer Continuity Score | ≥ 0.80 | Cross-agent task completion (Ravindran2025 method) |
| Tamper detection rate | 100% | Mutation testing (1000+ trials) |
| Injection resistance | 100% | Attack pattern battery testing |
| Write latency (p99) | < 500ms | With governance gates active |
| Read latency (p99) | < 200ms | Multi-strategy retrieval + reranking |
| Storage efficiency | ≤ 50% of raw logs | Artifact size vs conversation history |
| Semantic drift bound | ≤ ε per reconciliation window | SSGM Theorem 1 |
| Agent onboarding time | < 5 min | New agent fully memory-connected |
| DAG depth at 1M nodes | O(log n) query | Graph traversal benchmarks |

---

## 8. WHAT MAKES THIS SOVEREIGN

1. **No vendor dependency** — Runs on our Neo4j + Hedera + Arweave stack
2. **Oracle-free** — Internal deterministic provêance, no Chainlink or external oracles
3. **Legal memory** — Wright's architecture satisfies legal evidentiary non-repudiation
4. **Interagent transfer** — PAM-compatible for cross-framework agent comms
5. **MCP-native** — Integrates with every tool-using agent (Hermes, Claude, Codex, etc.)
6. **Encrypted at rest** — ECDH-keyed fragments w/ per-access-tier decryption
7. **Forever** — Content-addressed + blockchain-anchored = permanent

---

## 9. RELATIONSHIP TO EXISTING PROJECTS

| Project | Relationship |
|---|---|
| **Hermes Agent (this system)** | Primary consumer of DAIM. Every session loads from the DAG. |
| **Hallways Boardroom** | Governance layer: Boardroom policy engine controls DAG checkpoints/freeze/prune |
| **e5-enclave-mission-context** | Mission memories are the highest-privilege tier in the DAG |
| **Sovereign Blog** | Published reflections can be anchored as public DAG nodes |
| **McCartney Deck** | NFT ownership records can be DAG-anchored for provenance |
| **EDEN Protocol** | EDEN agent memory can be DAIM-powered |

---

## 10. DELIVERABLES COMMITMENTS

| File | Contents |
|---|---|
| `reports/recon-summary.md` | This document — the full recon + architecture + plan |
| `simulation/dag-prototype.py` | DAG prototype with adversarial tests |
| `reports/simulation-report.pdf` | Simulation results |
| `reports/execution-roadmap.md` | Kanban board import format |

---

*Document committed to: github.com/IAMGODIAM/memory-dag*
*Wyrmcore Protocol v1.0 | Full Chairman Protocol authorized*
*Visionary: Hermie | Executor: Sue (Base44)*
