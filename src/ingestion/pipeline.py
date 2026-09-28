"""Manda los documentos de una carpeta a la base vectorial."""

from uuid import uuid4

from src.embeddings.embedder import LocalEmbedder
from src.ingestion.document_loader import load_documents_from_dir
from src.preprocessing.text_cleaning import chunk_text
from src.storage.vector_store import VectorStore


def run_ingestion_pipeline(
    input_dir: str,
    persist_directory: str = "data/processed/chroma",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> int:
    """Corre el pipeline sobre todos los documentos de un directorio.

    Devuelve cuantos fragmentos quedo guardados.
    """
    documents = load_documents_from_dir(input_dir)
    embedder = LocalEmbedder()
    store = VectorStore(persist_directory=persist_directory)

    total_chunks = 0
    for document in documents:
        chunks = chunk_text(document.text, chunk_size=chunk_size, overlap=chunk_overlap)
        if not chunks:
            continue

        embeddings = embedder.embed(chunks)
        ids = [str(uuid4()) for _ in chunks]
        metadatas = [
            {"source": document.source_path, "chunk_index": i} for i in range(len(chunks))
        ]

        store.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        total_chunks += len(chunks)

    return total_chunks
