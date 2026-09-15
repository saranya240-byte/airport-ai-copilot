from src.document_loader import (
    load_policy_documents,
    chunk_documents
)

from src.rag import PolicyRAG
from src.llm import generate_answer


class RAGService:

    def __init__(self):

        print("Initializing RAG service...")

        # Load policy documents
        documents = load_policy_documents()

        # Create chunks
        chunks = chunk_documents(documents)

        # Create RAG system
        self.rag = PolicyRAG()

        # Build vector store
        self.rag.build(chunks)

        print("RAG service initialized successfully.")


    def ask(self, question):

        # Retrieve relevant policy chunks
        results = self.rag.retrieve(
            question,
            top_k=3
        )

        # Convert retrieved chunks into context
        context = self.rag.format_context(
            results
        )

        # Generate answer using Ollama
        answer = generate_answer(
            question,
            context
        )

        return {
            "question": question,
            "answer": answer,
            "retrieved_documents": results
        }
