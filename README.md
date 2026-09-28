# Sistema de gestion inteligente de literatura medica de acceso abierto

Proyecto final de la materia CSDS-352 (Ciencia de Datos y Aprendizaje Automatico), Jala University.

## Descripcion

Sistema que ingiere articulos medicos de acceso abierto, los convierte en representaciones vectoriales (embeddings) usando un modelo local, los guarda en una base de datos vectorial, y permite explorarlos mediante agrupamiento (clustering), busqueda semantica y control de calidad automatico (deteccion de anomalias y clasificacion de calidad).

## Dominio del proyecto

Literatura medica de acceso abierto, obtenida del subconjunto de acceso abierto (Open Access Subset) de PubMed Central (PMC), filtrando explicitamente por `open access[filter]` en la busqueda para asegurar que cada articulo tenga una licencia abierta confirmada por PMC (tipicamente CC-BY, CC0 o similar). La licencia de cada articulo descargado queda registrada en `data/raw/metadata.csv`.

Tema de busqueda inicial: "artificial intelligence in healthcare" (ajustable con el parametro `--query` del comando `fetch`).

## Lo que cubre el proyecto

1. Pipeline de ingesta de documentos: CLI y API, soporte para texto plano y PDF, embedding local.
2. Almacenamiento en base de datos vectorial (Chroma) con metadatos.
3. Interfaz de exploracion (busqueda semantica ya disponible; visualizacion de clusters pendiente para la segunda mitad del proyecto).
4. Control de calidad (deteccion de anomalias y clasificacion de calidad, pendiente para la segunda mitad del proyecto).

## Arquitectura inicial

```
src/
  ingestion/       CLI, adquisicion desde PMC (pmc_fetcher.py), carga de archivos locales (document_loader.py), pipeline (pipeline.py)
  preprocessing/    Limpieza y chunking de texto (text_cleaning.py)
  embeddings/       Wrapper del modelo local de Sentence Transformers (embedder.py)
  storage/          Wrapper de Chroma como base de datos vectorial (vector_store.py)
  api/              API minima con FastAPI (app.py)
data/
  raw/              Documentos originales descargados + metadata.csv con su licencia
  processed/        Base de datos vectorial persistida (Chroma)
tests/              Pruebas basicas con pytest
```

Flujo: `fetch` (adquiere articulos de PMC con licencia confirmada) -> `ingest` (carga, limpia, fragmenta, genera embeddings y guarda en Chroma) -> consultas de busqueda semantica sobre la base vectorial.

## Instalacion

Requiere Python 3.10 o superior.

```
python -m venv .venv
.venv\Scripts\activate        (en Windows)
pip install -r requirements.txt
```

## Uso

Descargar articulos de acceso abierto sobre un tema:

```
python -m src.ingestion.cli fetch --query "artificial intelligence in healthcare" --output-dir data/raw --max-results 200
```

Procesar los documentos descargados y guardarlos en la base vectorial:

```
python -m src.ingestion.cli ingest --input-dir data/raw --persist-directory data/processed/chroma
```

Limpiar los datos descargados y la base vectorial de una corrida anterior (util antes de volver a correr fetch/ingest desde cero):

```
python -m src.ingestion.cli reset
```

Levantar la API:

```
uvicorn src.api.app:app --reload
```

## Pruebas

```
pytest tests/ -v
```

## Estado actual (evaluacion intermedia)

- Pipeline de ingesta (CLI y API) implementado y probado con pruebas basicas.
- Pipeline de preprocesamiento (limpieza y chunking) implementado y probado.
- Adquisicion de datos desde PMC Open Access implementada, con registro de licencia por articulo.
- Integracion con modelo de embedding local (all-MiniLM-L6-v1) y base de datos vectorial (Chroma) implementada.
- Pendiente para la segunda mitad del proyecto: clustering, visualizacion interactiva, deteccion de anomalias y clasificacion de calidad.
