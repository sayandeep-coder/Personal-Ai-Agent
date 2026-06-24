# ADR-001: Why PostgreSQL + pgvector instead of Pinecone, Weaviate, or Qdrant

## Status

Accepted for Phase 1.

## Context

Personal-AI-Agent needs durable relational state and semantic retrieval. The system must store users, conversations, messages, memories, tasks, daily briefings, tool executions, and agent runs. It also needs vector search over user-scoped memory.

The main alternatives considered were:

| Option | Summary |
| --- | --- |
| PostgreSQL + pgvector | Single relational database with vector extension. |
| Pinecone | Managed vector database optimized for vector search at scale. |
| Weaviate | Vector database with schema, hybrid search, and managed/self-hosted options. |
| Qdrant | High-performance vector database with filtering and self-hosted/managed options. |

## Decision

Use PostgreSQL with pgvector for Phase 1 memory storage and semantic search.

PostgreSQL remains the system of record for all application state. pgvector stores memory embeddings in the same database so vector retrieval can be filtered transactionally by `user_id`, memory type, expiration, task state, and source metadata.

## Rationale

Phase 1 needs strong product velocity, operational simplicity, and correct user-scoped retrieval more than independent vector database scaling. Most memory retrieval queries require both semantic similarity and relational filters. Keeping these in one database avoids dual-write complexity, consistency gaps, and additional operational burden.

## Pros

| Pro | Impact |
| --- | --- |
| One source of truth | Memories, metadata, and embeddings are updated transactionally. |
| Simpler operations | No separate vector service, network path, backup process, or auth model. |
| Strong filtering | `user_id`, task, type, expiry, and metadata filters stay close to vector search. |
| Lower Phase 1 cost | Avoids managed vector database spend before scale requires it. |
| Easier local development | Dockerized Postgres can support the full memory system. |
| SQL observability | Standard SQL, migrations, backups, and indexes apply. |
| Reduced dual-write risk | No need to synchronize Postgres rows with a separate vector store. |

## Cons

| Con | Mitigation |
| --- | --- |
| Vector search may become slower at large scale | Use HNSW/IVFFlat indexes, metadata filters, read replicas, and partitioning. |
| Postgres carries mixed workload | Separate transactional and retrieval read paths with replicas later. |
| Fewer vector-native features | Implement only needed ranking features in application code. |
| Embedding dimension migrations require care | Store `embedding_model` and run async backfills. |
| Scaling isolation is limited | Migrate vector search behind a repository interface if needed. |

## Consequences

### Immediate Consequences

- Memory retrieval repository must support vector search and metadata filters.
- Migrations must enable the `vector` extension.
- The `memories` table must include `embedding`, `embedding_model`, `importance`, `confidence`, and metadata fields.
- Application ranking remains outside the database except for initial candidate retrieval.

### Long-Term Consequences

- The database team must monitor vector index size, query latency, and vacuum behavior.
- A future migration to Pinecone, Weaviate, or Qdrant remains possible because the agent depends on a memory repository interface, not pgvector directly.
- If memory volume grows substantially, the project should evaluate dedicated vector infrastructure using production latency and cost data.

## Alternatives Considered

### Pinecone

Pinecone provides managed vector search with strong scalability and low operational overhead for vector workloads. It was not selected for Phase 1 because the project still needs PostgreSQL for relational state, which would introduce dual writes and cross-system consistency challenges before there is evidence that pgvector is insufficient.

### Weaviate

Weaviate offers a rich vector-native object model and hybrid search. It was not selected for Phase 1 because the Personal-AI-Agent data model is primarily relational and audit-oriented. Weaviate may be reconsidered if hybrid retrieval becomes the dominant workload.

### Qdrant

Qdrant is operationally attractive and efficient for vector search. It was not selected for Phase 1 because pgvector is adequate for the expected early workload and keeps deployment simpler. Qdrant is a strong future candidate if vector search becomes independently scalable infrastructure.

## Review Trigger

Revisit this decision when one or more conditions are true:

- p95 memory retrieval latency exceeds product targets after index tuning.
- Memory corpus grows beyond comfortable Postgres index size.
- Multi-tenant isolation requires dedicated vector shards.
- Hybrid search quality becomes a top-level product differentiator.
- Vector workload interferes with core transactional database performance.

