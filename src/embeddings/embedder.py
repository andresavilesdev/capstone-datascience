"""Genera embeddings con un modelo local de Sentence Transformers.

Esta envuelto aca para poder cambiarlo facil si hace falta.
"""

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v1"


class LocalEmbedder:
    """Envuelve el modelo local de Sentence Transformers."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Genera un embedding por cada texto de la lista."""
        if not texts:
            return []
        embeddings = self._model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
