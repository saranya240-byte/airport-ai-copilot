from src.document_loader import (
    load_policy_documents,
    chunk_documents
)

from src.rag import PolicyRAG
from src.llm import generate_answer


# --------------------------------------------------
# 1. Load Policy Documents
# --------------------------------------------------

documents = load_policy_documents()

print(f"Documents loaded: {len(documents)}")


# --------------------------------------------------
# 2. Create Chunks
# --------------------------------------------------

chunks = chunk_documents(documents)

print(f"Chunks created: {len(chunks)}")


# --------------------------------------------------
# 3. Build RAG System
# --------------------------------------------------

rag = PolicyRAG()

rag.build(chunks)


# --------------------------------------------------
# 4. User Question
# --------------------------------------------------

question = "What is the maximum surge multiplier allowed at SFO?"

print("\nUSER QUESTION")
print("=" * 60)
print(question)


# --------------------------------------------------
# 5. Retrieve Relevant Policies
# --------------------------------------------------

results = rag.retrieve(
    question,
    top_k=3
)


# --------------------------------------------------
# 6. Create RAG Context
# --------------------------------------------------

context = rag.format_context(results)


print("\nRETRIEVED CONTEXT")
print("=" * 60)
print(context)


# --------------------------------------------------
# 7. Generate LLM Answer
# --------------------------------------------------

print("\nGENERATING ANSWER...")
print("=" * 60)

answer = generate_answer(
    question,
    context
)


# --------------------------------------------------
# 8. Display Final Answer
# --------------------------------------------------

print("\nFINAL RAG ANSWER")
print("=" * 60)

print("Answer:", answer.get("answer"))

print(
    "Policy Reasoning:",
    answer.get("policy_reasoning")
)

print(
    "Source:",
    answer.get("source")
)

print(
    "Grounded:",
    answer.get("grounded")
)
