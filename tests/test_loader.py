from src.document_loader import (
    load_policy_documents,
    chunk_documents
)


documents = load_policy_documents()

chunks = chunk_documents(documents)

print("Documents:", len(documents))
print("Chunks:", len(chunks))

for i, chunk in enumerate(chunks[:10]):

    print("\n==============================")
    print("Chunk:", i + 1)

    print("Source:",
          chunk["metadata"]["source"])

    print("Airport:",
          chunk["metadata"]["airport"])

    print("Category:",
          chunk["metadata"]["category"])

    print("\nText:")
    print(chunk["text"])