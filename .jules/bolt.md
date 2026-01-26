## 2024-05-22 - Batching Vector DB Upserts
**Learning:** Batching upserts to ChromaDB reduced insertion time by ~5.8x (39.9s -> 6.8s for 100 items). The overhead of Python function calls and potential DB transactions is significant for single items.
**Action:** Always prefer batch operations for vector database interactions, especially when processing bulk data like directory ingestion.
