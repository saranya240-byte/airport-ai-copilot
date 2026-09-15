from src.document_loader import (
    load_policy_documents,
    chunk_documents
)


def test_document_loading():

    documents = load_policy_documents()

    assert len(documents) == 7


def test_document_metadata():

    documents = load_policy_documents()

    first_document = documents[0]

    assert "source" in first_document["metadata"]
    assert "airport" in first_document["metadata"]
    assert "category" in first_document["metadata"]


def test_chunking():

    documents = load_policy_documents()

    chunks = chunk_documents(documents)

    assert len(chunks) > len(documents)


def test_chunk_metadata():

    documents = load_policy_documents()

    chunks = chunk_documents(documents)

    for chunk in chunks:

        assert "source" in chunk["metadata"]
        assert "airport" in chunk["metadata"]
        assert "category" in chunk["metadata"]