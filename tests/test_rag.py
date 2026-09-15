from src.document_loader import (
    load_policy_documents,
    chunk_documents
)

from src.rag import PolicyRAG


def create_rag():

    documents = load_policy_documents()

    chunks = chunk_documents(documents)

    rag = PolicyRAG()

    rag.build(chunks)

    return rag


def test_sfo_surge_policy():

    rag = create_rag()

    results = rag.retrieve(
        "What is the maximum surge multiplier allowed at SFO?",
        top_k=3
    )

    assert len(results) > 0

    assert results[0]["metadata"]["source"] == "sfo_pricing.md"


def test_sfo_driver_queue_policy():

    rag = create_rag()

    results = rag.retrieve(
        "What happens when a driver leaves the SFO queue?",
        top_k=3
    )

    assert len(results) > 0

    sources = [
        result["metadata"]["source"]
        for result in results
    ]

    assert "sfo_driver_policy.md" in sources


def test_jfk_surge_policy():

    rag = create_rag()

    results = rag.retrieve(
        "What is the maximum surge multiplier allowed at JFK?",
        top_k=3
    )

    assert len(results) > 0

    sources = [
        result["metadata"]["source"]
        for result in results
    ]

    assert "jfk_pricing.md" in sources


def test_lax_completion_policy():

    rag = create_rag()

    results = rag.retrieve(
        "What completion rate requires investigation at LAX?",
        top_k=3
    )

    assert len(results) > 0

    sources = [
        result["metadata"]["source"]
        for result in results
    ]

    assert "lax_operations.md" in sources