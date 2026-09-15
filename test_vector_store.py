from src.document_loader import (
    load_policy_documents,
    chunk_documents
)

from src.vector_store import PolicyVectorStore


# 1. Load documents
documents = load_policy_documents()

print(
    "Documents loaded:",
    len(documents)
)


# 2. Create chunks
chunks = chunk_documents(documents)

print(
    "Chunks created:",
    len(chunks)
)


# 3. Create vector store
vector_store = PolicyVectorStore()


# 4. Generate embeddings and build FAISS
vector_store.build(chunks)


print(
    "Vectors stored:",
    vector_store.index.ntotal
)
