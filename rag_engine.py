"""
rag_engine.py
Enterprise AI Knowledge Assistant
"""

import os
import time
import ollama

from config import UPLOAD_DIR, OLLAMA_MODEL
from document_loader import DocumentLoader
from chunker import TextChunker
from vector_store import VectorStore
from prompts import SYSTEM_PROMPT, PROMPT_TEMPLATE


class RAGEngine:

    def __init__(self):

        print("🚀 Initializing RAG Engine...")

        self.loader = DocumentLoader()
        self.chunker = TextChunker()
        self.store = VectorStore()

        print("✅ RAG Engine Ready")

    # ---------------------------------------------------------
    # Build Knowledge Base
    # ---------------------------------------------------------

    def ingest(self):

        self.store.reset()

        documents = self.loader.load_directory(UPLOAD_DIR)

        total_documents = 0
        total_chunks = 0

        for doc in documents:

            chunks = self.chunker.chunk(doc["text"])

            self.store.add_document(
                doc["filename"],
                chunks
            )

            total_documents += 1
            total_chunks += len(chunks)

        return {
            "documents": total_documents,
            "chunks": total_chunks
        }

    # ---------------------------------------------------------
    # Retrieve
    # ---------------------------------------------------------

    def retrieve(self, question):

        return self.store.search(question)

    # ---------------------------------------------------------
    # Build Context
    # ---------------------------------------------------------

    def build_context(self, hits):

        context = ""

        for hit in hits:

            context += f"""
SOURCE:
{hit['source']}

CONTENT:
{hit['text']}

---------------------------------------

"""

        return context

    # ---------------------------------------------------------
    # Ask Question
    # ---------------------------------------------------------

    def ask(self, question):

        start = time.time()

        hits = self.retrieve(question)

        if not hits:

            return {
                "answer": "I couldn't find relevant information in the uploaded documents.",
                "sources": [],
                "confidence": 0,
                "time": round(time.time() - start, 2)
            }

        context = self.build_context(hits)

        prompt = PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )

        try:

            response = ollama.chat(

                model=OLLAMA_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response["message"]["content"]

        except Exception as e:

            answer = f"⚠ Ollama Error:\n\n{e}"

        sources = sorted(
            list(
                {
                    hit["source"]
                    for hit in hits
                }
            )
        )

        confidence = round(
            sum(hit["score"] for hit in hits) / len(hits),
            2
        )

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "time": round(time.time() - start, 2)
        }

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def stats(self):
        """
        Returns:
            documents -> uploaded files
            chunks -> indexed chunks
        """

        uploaded_docs = len(
            [
                f for f in os.listdir(UPLOAD_DIR)
                if os.path.isfile(os.path.join(UPLOAD_DIR, f))
            ]
        )

        return {
            "documents": uploaded_docs,
            "chunks": self.store.count()
        }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    bot = RAGEngine()

    print(bot.ingest())

    response = bot.ask(
        "Summarize the uploaded document."
    )

    print("\nAnswer:\n")
    print(response["answer"])

    print("\nSources:")
    print(response["sources"])

    print("\nConfidence:")
    print(response["confidence"])