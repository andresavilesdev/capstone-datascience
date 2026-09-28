"""Descarga articulos de acceso abierto desde PubMed Central.

Solamente bajamos los que PMC marca como open access.
"""

import csv
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import requests

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


@dataclass
class FetchedArticle:
    pmcid: str
    title: str
    license_type: str
    text: str


def search_open_access_ids(query: str, max_results: int = 200) -> list[str]:
    """Busca IDs de articulos PMC de acceso abierto para un tema."""
    params = {
        "db": "pmc",
        "term": f"{query} AND open access[filter]",
        "retmax": str(max_results),
        "retmode": "json",
    }
    response = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_article(pmcid: str) -> FetchedArticle:
    """Descarga el texto completo y la licencia de un articulo de PMC por su ID."""
    params = {"db": "pmc", "id": pmcid, "rettype": "full", "retmode": "xml"}
    response = requests.get(f"{EUTILS_BASE}/efetch.fcgi", params=params, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    return FetchedArticle(
        pmcid=pmcid,
        title=_find_title(root),
        license_type=_find_license(root),
        text=_extract_body_text(root),
    )


def _normalize_whitespace(text: str) -> str:
    """Junta espacios y saltos de linea en uno solo.

    PMC a veces trae titulos con saltos de linea que parten la fila del CSV.
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _find_title(root: ET.Element) -> str:
    node = root.find(".//article-title")
    if node is None:
        return "sin titulo"
    return _normalize_whitespace("".join(node.itertext()))


def _find_license(root: ET.Element) -> str:
    """Devuelve el tipo de licencia declarado por PMC para el articulo."""
    license_node = root.find(".//license")
    if license_node is None:
        return "desconocida"
    license_type = license_node.get("license-type", "")
    href = license_node.get(XLINK_HREF, "")
    return license_type or href or "acceso abierto (tipo no especificado)"


def _extract_body_text(root: ET.Element) -> str:
    body = root.find(".//body")
    if body is None:
        return ""
    paragraphs = ["".join(p.itertext()).strip() for p in body.iter("p")]
    return "\n\n".join(p for p in paragraphs if p)


def fetch_and_save(
    query: str,
    output_dir: str,
    max_results: int = 200,
    delay_seconds: float = 0.4,
) -> list[FetchedArticle]:
    """Busca articulos de acceso abierto sobre un tema, los descarga y los guarda.

    Cada articulo queda como .txt y su licencia va a metadata.csv.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    ids = search_open_access_ids(query, max_results)
    articles: list[FetchedArticle] = []

    metadata_path = out_path / "metadata.csv"
    with metadata_path.open("w", encoding="utf-8", newline="") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["pmcid", "titulo", "licencia", "archivo"])

        for pmcid in ids:
            try:
                article = fetch_article(pmcid)
            except (requests.RequestException, ET.ParseError):
                continue

            if not article.text:
                continue

            filename = f"PMC{pmcid}.txt"
            (out_path / filename).write_text(article.text, encoding="utf-8")

            writer.writerow([article.pmcid, article.title, article.license_type, filename])
            articles.append(article)
            time.sleep(delay_seconds)

    return articles
