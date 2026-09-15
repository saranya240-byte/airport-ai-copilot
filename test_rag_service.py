from src.rag_service import RAGService


# --------------------------------------------------
# 1. Initialize RAG Service
# --------------------------------------------------

service = RAGService()


# --------------------------------------------------
# 2. Ask a Policy Question
# --------------------------------------------------

question = "What is the maximum surge multiplier allowed at SFO?"


print("\nUSER QUESTION")
print("=" * 60)
print(question)


# --------------------------------------------------
# 3. Get RAG Answer
# --------------------------------------------------

result = service.ask(question)


# --------------------------------------------------
# 4. Display Final Answer
# --------------------------------------------------

answer = result["answer"]

print("\nFINAL ANSWER")
print("=" * 60)

print(
    "Answer:",
    answer.get("answer")
)

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


# --------------------------------------------------
# 5. Display Retrieved Documents
# --------------------------------------------------

print("\nRETRIEVED DOCUMENTS")
print("=" * 60)

for i, document in enumerate(
    result["retrieved_documents"],
    start=1
):

    print(
        f"{i}. "
        f"{document['metadata']['source']}"
    )
