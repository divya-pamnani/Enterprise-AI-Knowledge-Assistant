"""
vector_store.py
Enterprise AI Knowledge Assistant

Vector Database using ChromaDB
"""

import chromadb

from embeddings import EmbeddingModel
from config import VECTOR_DB_DIR, TOP_K


class VectorStore:

    def __init__(self):

        print("📦 Initializing Vector Database...")

        self.embedding_model = EmbeddingModel()

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name="enterprise_documents",
            metadata={"hnsw:space": "cosine"}
        )

        print("✅ Vector Database Ready")

    # ---------------------------------------------------------
    # Reset Database
    # ---------------------------------------------------------

    def reset(self):

        try:
            self.client.delete_collection(
                "enterprise_documents"
            )
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name="enterprise_documents",
            metadata={"hnsw:space": "cosine"}
        )

    # ---------------------------------------------------------
    # Add Document
    # ---------------------------------------------------------

    def add_document(self, filename, chunks):

        if not chunks:
            return

        embeddings = self.embedding_model.encode(chunks)

        ids = []
        metadatas = []

        for i, chunk in enumerate(chunks):

            ids.append(f"{filename}_{i}")

            metadatas.append(
                {
                    "source": filename,
                    "chunk": i
                }
            )

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(self, query, top_k=TOP_K):

        query_embedding = self.embedding_model.encode(query)

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        hits = []

        if len(results["documents"]) == 0:
            return hits

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, dist in zip(
            documents,
            metadatas,
            distances
        ):

            similarity = round(
                (1 - dist) * 100,
                2
            )

            hits.append(
                {
                    "text": doc,
                    "source": meta["source"],
                    "chunk": meta["chunk"],
                    "score": similarity
                }
            )

        return hits

    # ---------------------------------------------------------
    # Count Chunks
    # ---------------------------------------------------------

    def count(self):

        return self.collection.count()

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def stats(self):
        """
        Returns:
            documents -> unique uploaded files
            chunks -> indexed chunks
        """

        chunk_count = self.collection.count()

        sources = set()

        if chunk_count > 0:

            data = self.collection.get(
                include=["metadatas"]
            )

            for meta in data["metadatas"]:

                if meta is not None:
                    sources.add(meta["source"])

        return {
            "documents": len(sources),
            "chunks": chunk_count
        }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    store = VectorStore()

    store.reset()

    store.add_document(
        "demo.txt",
        [
            "Artificial Intelligence is transforming industries.",
            "Machine Learning is a subset of AI.",
            "Deep Learning uses neural networks."
        ]
    )

    print("Statistics")
    print(store.stats())

    print("\nSearch Results\n")

    results = store.search(
        "What is machine learning?"
    )

    print(results)