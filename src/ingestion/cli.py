"""Comandos de terminal para correr el pipeline de ingesta."""

import typer

from src.ingestion.pipeline import run_ingestion_pipeline
from src.ingestion.pmc_fetcher import fetch_and_save
from src.ingestion.reset import reset_data

app = typer.Typer(help="CLI del pipeline de ingesta de documentos.")


@app.command()
def fetch(
    query: str = typer.Option(..., help="Tema de busqueda en PubMed Central."),
    output_dir: str = typer.Option("data/raw", help="Carpeta donde guardar los articulos."),
    max_results: int = typer.Option(200, help="Cantidad maxima de articulos a descargar."),
) -> None:
    """Descarga articulos de acceso abierto de PubMed Central sobre un tema."""
    articles = fetch_and_save(query=query, output_dir=output_dir, max_results=max_results)
    typer.echo(f"Se descargaron {len(articles)} articulos en {output_dir}")


@app.command()
def ingest(
    input_dir: str = typer.Option("data/raw", help="Carpeta con los documentos a ingerir."),
    persist_directory: str = typer.Option(
        "data/processed/chroma", help="Carpeta donde persistir la base vectorial."
    ),
) -> None:
    """Procesa los documentos de una carpeta y los guarda en la base vectorial."""
    total_chunks = run_ingestion_pipeline(input_dir=input_dir, persist_directory=persist_directory)
    typer.echo(f"Se guardaron {total_chunks} fragmentos en la base vectorial")


@app.command()
def reset(
    raw_dir: str = typer.Option("data/raw", help="Carpeta con los documentos descargados a limpiar."),
    persist_directory: str = typer.Option(
        "data/processed/chroma", help="Carpeta de la base vectorial a limpiar."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="No pedir confirmacion antes de borrar."),
) -> None:
    """Borra lo descargado y la base vectorial, para arrancar de cero.

    Util cuando corrijo algo en el pipeline y quiero regenerar todo limpio.
    """
    if not yes:
        confirmado = typer.confirm(
            f"Esto borra todo el contenido de '{raw_dir}' y de '{persist_directory}'. Continuar?"
        )
        if not confirmado:
            typer.echo("Cancelado, no se borro nada.")
            raise typer.Exit()

    reset_data(raw_dir=raw_dir, persist_directory=persist_directory)
    typer.echo(f"Se limpiaron '{raw_dir}' y '{persist_directory}'.")


if __name__ == "__main__":
    app()
