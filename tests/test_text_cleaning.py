import pytest

from src.preprocessing.text_cleaning import chunk_text, clean_text


def test_clean_text_normaliza_espacios():
    assert clean_text("  hola   mundo\n\n  ") == "hola mundo"


def test_clean_text_con_texto_vacio():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_chunk_text_texto_corto_da_un_solo_chunk():
    texto = "a" * 50
    chunks = chunk_text(texto, chunk_size=800, overlap=100)
    assert chunks == [texto]


def test_chunk_text_texto_largo_produce_varios_chunks_con_solapamiento():
    texto = "a" * 2000
    chunks = chunk_text(texto, chunk_size=800, overlap=100)
    assert len(chunks) > 1


def test_chunk_text_documento_vacio_da_lista_vacia():
    assert chunk_text("") == []


def test_chunk_text_chunk_size_menor_que_overlap_lanza_error():
    with pytest.raises(ValueError):
        chunk_text("algo", chunk_size=50, overlap=100)
