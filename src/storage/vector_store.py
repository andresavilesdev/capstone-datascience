"""Chroma como base vectorial local para guardar embeddings y metadatos."""

import chromadb


class VectorStore:
    """Envuelve una coleccion de Chroma para guardar y consultar embeddings."""

    def __init__(self, persist_directory: str, collection_name: str = "documentos"):
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(collection_name)

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Agrega documentos con sus embeddings y metadatos a la coleccion."""
        self._collection.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def query(self, query_embedding: list[float], n_results: int = 5) -> dict:
        """Busca los documentos mas parecidos a un embedding de consulta (busqueda semantica)."""
        return self._collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

    def count(self) -> int:
        return self._collection.count()
