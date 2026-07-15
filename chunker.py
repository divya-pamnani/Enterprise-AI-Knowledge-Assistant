"""
chunker.py
Enterprise AI Knowledge Assistant

Splits large documents into overlapping chunks for RAG retrieval.
"""

from config import CHUNK_SIZE, CHUNK_OVERLAP


class TextChunker:
    """
    Splits text into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP
    ):

        self.chunk_size = chunk_size
        self.overlap = overlap

    # ---------------------------------------------------------
    # Chunk Text
    # ---------------------------------------------------------

    def chunk(self, text):

        if not text:
            return []

        text = text.strip()

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def stats(self, text):

        chunks = self.chunk(text)

        return {
            "characters": len(text),
            "chunks": len(chunks),
            "chunk_size": self.chunk_size,
            "overlap": self.overlap
        }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    sample = (
        "Artificial Intelligence is transforming industries. "
        * 100
    )

    chunker = TextChunker()

    chunks = chunker.chunk(sample)

    print("Chunks:", len(chunks))
    print("-" * 50)
    print(chunks[0][:200])