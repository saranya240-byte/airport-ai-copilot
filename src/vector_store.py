import os

# --------------------------------------------------
# SSL / Certificate Configuration
# --------------------------------------------------

# Use the Linux system certificate bundle.
# This is required in the current corporate network
# environment to access Hugging Face securely.

SYSTEM_CA = "/etc/ssl/certs/ca-certificates.crt"

os.environ["REQUESTS_CA_BUNDLE"] = SYSTEM_CA
os.environ["SSL_CERT_FILE"] = SYSTEM_CA
os.environ["CURL_CA_BUNDLE"] = SYSTEM_CA

print("Using certificate bundle:", SYSTEM_CA)


# --------------------------------------------------
# Imports
# --------------------------------------------------

import faiss
import pickle

from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Model Configuration
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# Policy Vector Store
# --------------------------------------------------

class PolicyVectorStore:

    def __init__(self):

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        self.index = None

        self.chunks = []


    # --------------------------------------------------
    # Build FAISS Index
    # --------------------------------------------------

    def build(self, chunks):

        self.chunks = chunks

        # Extract text from each chunk
        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        print(
            f"Creating embeddings for "
            f"{len(texts)} chunks..."
        )

        # Convert policy text into embeddings
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )

        # Get embedding size
        dimension = embeddings.shape[1]

        print(
            f"Embedding dimension: {dimension}"
        )

        # Create FAISS index using L2 distance
        self.index = faiss.IndexFlatL2(
            dimension
        )

        # Add embeddings to FAISS
        self.index.add(embeddings)

        print(
            f"FAISS index created with "
            f"{self.index.ntotal} vectors."
        )


    # --------------------------------------------------
    # Semantic Search
    # --------------------------------------------------

    def search(
        self,
        query,
        top_k=3
    ):

        if self.index is None:

            raise ValueError(
                "Vector store has not been built."
            )

        # Convert query into an embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        # Search FAISS
        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index == -1:
                continue

            result = {
                "text": self.chunks[index]["text"],
                "metadata": self.chunks[index]["metadata"],
                "distance": float(distance)
            }

            results.append(result)

        return results


    # --------------------------------------------------
    # Save Vector Store
    # --------------------------------------------------

    def save(
        self,
        index_path,
        chunks_path
    ):

        if self.index is None:

            raise ValueError(
                "Vector store has not been built."
            )

        # Save FAISS index
        faiss.write_index(
            self.index,
            index_path
        )

        # Save chunks and metadata
        with open(
            chunks_path,
            "wb"
        ) as file:

            pickle.dump(
                self.chunks,
                file
            )

        print(
            "Vector store saved successfully."
        )


    # --------------------------------------------------
    # Load Vector Store
    # --------------------------------------------------

    def load(
        self,
        index_path,
        chunks_path
    ):

        # Load FAISS index
        self.index = faiss.read_index(
            index_path
        )

        # Load chunks and metadata
        with open(
            chunks_path,
            "rb"
        ) as file:

            self.chunks = pickle.load(
                file
            )

        print(
            "Vector store loaded successfully."
        )