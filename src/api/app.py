"""API minima para exponer el pipeline de ingesta por HTTP."""

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile

from src.embeddings.embedder import LocalEmbedder
from src.ingestion.document_loader import load_document
from src.preprocessing.text_cleaning import chunk_text
from src.storage.vector_store import VectorStore

app = FastAPI(title="API de ingesta de documentos")

_embedder = LocalEmbedder()
_store = VectorStore(persist_directory="data/processed/chroma")


@app.post("/ingest")
async def ingest_document(file: UploadFile) -> dict:
    """Recibe el archivo y lo deja cargado en la base vectorial."""
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    document = load_document(tmp_path)
    chunks = chunk_text(document.text)
    if not chunks:
        return {"archivo": file.filename, "fragmentos_guardados": 0}

    embeddings = _embedder.embed(chunks)
    ids = [f"{file.filename}-{i}" for i in range(len(chunks))]
    metadatas = [{"source": file.filename, "chunk_index": i} for i in range(len(chunks))]
    _store.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

    return {"archivo": file.filename, "fragmentos_guardados": len(chunks)}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
