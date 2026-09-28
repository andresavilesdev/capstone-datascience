from pathlib import Path

import pytest

from src.ingestion.document_loader import (
    UnsupportedDocumentType,
    load_document,
    load_documents_from_dir,
)


def test_load_document_txt(tmp_path: Path):
    archivo = tmp_path / "ejemplo.txt"
    archivo.write_text("contenido de prueba", encoding="utf-8")

    documento = load_document(str(archivo))

    assert documento.text == "contenido de prueba"
    assert documento.source_path == str(archivo)


def test_load_document_archivo_inexistente():
    with pytest.raises(FileNotFoundError):
        load_document("no_existe.txt")


def test_load_document_tipo_no_soportado(tmp_path: Path):
    archivo = tmp_path / "ejemplo.docx"
    archivo.write_text("contenido", encoding="utf-8")

    with pytest.raises(UnsupportedDocumentType):
        load_document(str(archivo))


def test_load_documents_from_dir_ignora_archivos_no_soportados(tmp_path: Path):
    (tmp_path / "uno.txt").write_text("uno", encoding="utf-8")
    (tmp_path / "dos.txt").write_text("dos", encoding="utf-8")
    (tmp_path / "notas.md").write_text("no deberia cargarse", encoding="utf-8")

    documentos = load_documents_from_dir(str(tmp_path))

    assert len(documentos) == 2
