import csv
import io
import xml.etree.ElementTree as ET

from src.ingestion.pmc_fetcher import (
    _extract_body_text,
    _find_license,
    _find_title,
    _normalize_whitespace,
)

ARTICULO_XML = """
<article>
  <front>
    <article-meta>
      <title-group><article-title>Titulo de prueba</article-title></title-group>
      <permissions>
        <license license-type="open-access" xmlns:xlink="http://www.w3.org/1999/xlink"
                  xlink:href="https://creativecommons.org/licenses/by/4.0/">
          <license-p>Distribuido bajo licencia CC-BY 4.0</license-p>
        </license>
      </permissions>
    </article-meta>
  </front>
  <body>
    <p>Primer parrafo del articulo.</p>
    <p>Segundo parrafo del articulo.</p>
  </body>
</article>
"""

ARTICULO_XML_TITULO_CON_SALTO_DE_LINEA = """
<article>
  <front>
    <article-meta>
      <title-group>
        <article-title>El Titulo Ocupa Varias Lineas:
A Systematic Review</article-title>
      </title-group>
    </article-meta>
  </front>
  <body><p>texto</p></body>
</article>
"""


def test_find_title_extrae_titulo():
    root = ET.fromstring(ARTICULO_XML)
    assert _find_title(root) == "Titulo de prueba"


def test_find_license_extrae_tipo_de_licencia():
    root = ET.fromstring(ARTICULO_XML)
    assert _find_license(root) == "open-access"


def test_extract_body_text_une_parrafos():
    root = ET.fromstring(ARTICULO_XML)
    texto = _extract_body_text(root)
    assert "Primer parrafo del articulo." in texto
    assert "Segundo parrafo del articulo." in texto


def test_find_license_sin_licencia_devuelve_desconocida():
    xml_sin_licencia = "<article><body><p>texto</p></body></article>"
    root = ET.fromstring(xml_sin_licencia)
    assert _find_license(root) == "desconocida"


def test_normalize_whitespace_quita_saltos_de_linea():
    assert _normalize_whitespace("linea uno\nlinea dos") == "linea uno linea dos"


def test_normalize_whitespace_colapsa_espacios_repetidos():
    assert _normalize_whitespace("a   b\t\tc") == "a b c"


def test_find_title_con_salto_de_linea_no_rompe_una_sola_linea():
    """Reproduce el bug real: el salto de linea de un titulo partia metadata.csv en dos."""
    root = ET.fromstring(ARTICULO_XML_TITULO_CON_SALTO_DE_LINEA)
    titulo = _find_title(root)

    assert "\n" not in titulo
    assert titulo == "El Titulo Ocupa Varias Lineas: A Systematic Review"

    # ademas confirma que un titulo ya normalizado, escrito en el CSV, vuelve
    # a leerse como una sola fila (antes del fix quedaba partido en dos)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["1", titulo, "licencia", "archivo.txt"])
    buffer.seek(0)
    filas = list(csv.reader(buffer))
    assert len(filas) == 1
