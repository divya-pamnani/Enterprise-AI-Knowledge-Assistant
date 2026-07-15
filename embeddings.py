"""
embeddings.py
Enterprise AI Knowledge Assistant

Generates sentence embeddings using Sentence Transformers.
"""

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL


class EmbeddingModel:
    """
    Loads the embedding model only once and generates embeddings.
    """

    _model = None

    def __init__(self):

        if EmbeddingModel._model is None:

            print("🔄 Loading embedding model...")

            EmbeddingModel._model = SentenceTransformer(
                EMBEDDING_MODEL
            )

            print("✅ Embedding model loaded.")

        self.model = EmbeddingModel._model

    # ---------------------------------------------------------
    # Encode Text
    # ---------------------------------------------------------

    def encode(self, texts):

        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embeddings.tolist()

    # ---------------------------------------------------------
    # Embedding Dimension
    # ---------------------------------------------------------

    def dimension(self):

        return self.model.get_sentence_embedding_dimension()


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    model = EmbeddingModel()

    sentences = [
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning"
    ]

    embeddings = model.encode(sentences)

    print("Number of embeddings:", len(embeddings))
    print("Embedding dimension:", model.dimension())
    