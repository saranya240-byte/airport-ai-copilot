from src.vector_store import PolicyVectorStore


class PolicyRAG:

    def __init__(self):
        self.vector_store = PolicyVectorStore()

    def build(self, chunks):
        self.vector_store.build(chunks)

    def retrieve(self, query, top_k=3):

        results = self.vector_store.search(
            query,
            top_k=top_k
        )

        return results

    def format_context(self, results):

        context_parts = []

        for i, result in enumerate(results, start=1):

            source = result["metadata"]["source"]
            airport = result["metadata"]["airport"]
            category = result["metadata"]["category"]

            text = result["text"]

            context = (
                f"Source {i}:\n"
                f"Document: {source}\n"
                f"Airport: {airport}\n"
                f"Category: {category}\n"
                f"Policy:\n{text}"
            )

            context_parts.append(context)

        return "\n\n".join(context_parts)
