"""Limpieza y particionado (chunking) de texto.

Se aplican sobre el texto crudo de cada documento antes de generar los
embeddings: normalizan espacios y cortan los textos largos en fragmentos
manejables.
"""

import re


def clean_text(text: str) -> str:
    """Junta todos los espacios en uno solo y saca los del inicio y el final."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Corta un texto largo en fragmentos de tamano fijo, con solapamiento.

    Se mide en caracteres, no en tokens, para no depender de un tokenizador.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size debe ser mayor que overlap")

    text = clean_text(text)
    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        end = start + chunk_size
        fragment = text[start:end].strip()
        if fragment:
            chunks.append(fragment)
        if end >= len(text):
            break
        start += step
    return chunks
