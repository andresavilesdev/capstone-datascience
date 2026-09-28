"""Carga documentos locales (.txt y .pdf) para el pipeline de ingesta."""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class LoadedDocument:
    source_path: str
    text: str


class UnsupportedDocumentType(Exception):
    """Error para tipos de archivo que el loader no soporta."""


def load_document(path: str) -> LoadedDocument:
    """Carga un documento .txt o .pdf y devuelve su texto crudo."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {path}")

    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = _extract_pdf_text(file_path)
    else:
        raise UnsupportedDocumentType(
            f"Tipo de archivo no soportado: {suffix}. Se espera .txt o .pdf"
        )

    return LoadedDocument(source_path=str(file_path), text=text)


def _extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def load_documents_from_dir(directory: str) -> list[LoadedDocument]:
    """Carga todos los .txt y .pdf de un directorio, sin entrar en subcarpetas."""
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"No se encontro el directorio: {directory}")

    documents = []
    for file_path in sorted(dir_path.iterdir()):
        if file_path.suffix.lower() in (".txt", ".pdf"):
            documents.append(load_document(str(file_path)))
    return documents
