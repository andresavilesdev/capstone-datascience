"""Borra lo descargado del pipeline (data/raw y la base vectorial), para poder
correr fetch e ingest de nuevo sin datos viejos.
"""

import shutil
from pathlib import Path


def reset_data(raw_dir: str = "data/raw", persist_directory: str = "data/processed/chroma") -> None:
    """Borra lo descargado en raw_dir y la base vectorial."""
    _clear_directory_contents(Path(raw_dir))
    _remove_directory(Path(persist_directory))


def _clear_directory_contents(directory: Path) -> None:
    """Borra el contenido de un directorio, pero conserva la carpeta y el .gitkeep."""
    if not directory.exists():
        return
    for item in directory.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _remove_directory(directory: Path) -> None:
    """Borra un directorio entero si existe (para la base vectorial)."""
    if directory.exists():
        shutil.rmtree(directory)
