from pathlib import Path

from src.ingestion.reset import _clear_directory_contents, _remove_directory, reset_data


def test_clear_directory_contents_borra_archivos_pero_conserva_la_carpeta(tmp_path: Path):
    carpeta = tmp_path / "data_raw"
    carpeta.mkdir()
    (carpeta / "PMC1.txt").write_text("contenido 1", encoding="utf-8")
    (carpeta / "PMC2.txt").write_text("contenido 2", encoding="utf-8")
    (carpeta / "metadata.csv").write_text("pmcid,titulo", encoding="utf-8")

    _clear_directory_contents(carpeta)

    assert carpeta.exists()
    assert list(carpeta.iterdir()) == []


def test_clear_directory_contents_conserva_gitkeep(tmp_path: Path):
    carpeta = tmp_path / "data_raw"
    carpeta.mkdir()
    (carpeta / ".gitkeep").write_text("", encoding="utf-8")
    (carpeta / "PMC1.txt").write_text("contenido", encoding="utf-8")

    _clear_directory_contents(carpeta)

    archivos_restantes = [item.name for item in carpeta.iterdir()]
    assert archivos_restantes == [".gitkeep"]


def test_clear_directory_contents_con_carpeta_inexistente_no_falla(tmp_path: Path):
    carpeta_inexistente = tmp_path / "no_existe"
    _clear_directory_contents(carpeta_inexistente)  # si no existe, no debe fallar


def test_remove_directory_borra_la_base_vectorial_completa(tmp_path: Path):
    carpeta_chroma = tmp_path / "chroma"
    carpeta_chroma.mkdir()
    (carpeta_chroma / "algo.bin").write_text("datos", encoding="utf-8")

    _remove_directory(carpeta_chroma)

    assert not carpeta_chroma.exists()


def test_remove_directory_con_carpeta_inexistente_no_falla(tmp_path: Path):
    _remove_directory(tmp_path / "no_existe")  # si no existe, no debe fallar


def test_reset_data_limpia_ambas_carpetas(tmp_path: Path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / ".gitkeep").write_text("", encoding="utf-8")
    (raw_dir / "PMC1.txt").write_text("contenido", encoding="utf-8")

    persist_directory = tmp_path / "data" / "processed" / "chroma"
    persist_directory.mkdir(parents=True)
    (persist_directory / "algo.bin").write_text("datos", encoding="utf-8")

    reset_data(raw_dir=str(raw_dir), persist_directory=str(persist_directory))

    assert [item.name for item in raw_dir.iterdir()] == [".gitkeep"]
    assert not persist_directory.exists()
