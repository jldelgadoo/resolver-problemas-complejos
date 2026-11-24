"""Lector de valores de entrada de libros XLSX. No ejecuta macros ni fórmulas."""
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import posixpath
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

XML = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"


def parte(libro, ruta):
    info = libro.getinfo(ruta)
    if info.file_size > 32 * 1024 * 1024:
        raise ValueError("Una hoja supera el tamaño admitido por el auditor.")
    return ET.fromstring(libro.read(info))


def texto(elemento):
    if elemento is None:
        return ""
    fragmentos = elemento.findall(XML + "t") + elemento.findall(XML + "r/" + XML + "t")
    return "".join(n.text or "" for n in fragmentos)


def valor(celda, cadenas):
    tipo = celda.get("t", "n")
    if tipo == "inlineStr":
        return texto(celda.find(XML + "is"))
    dato = celda.findtext(XML + "v")
    if dato in (None, ""):
        return None
    if tipo == "s":
        indice = int(dato)
        if not 0 <= indice < len(cadenas):
            raise ValueError("Índice de cadena no válido en el libro.")
        return cadenas[indice]
    if tipo == "n":
        numero = Decimal(dato)
        if not numero.is_finite():
            raise ValueError("El libro contiene un número no finito.")
        return numero
    if tipo == "d":
        return date.fromisoformat(dato[:10])
    if tipo in {"b", "e"}:
        return None
    return dato


class Hojas(dict):
    """Hojas del libro junto a su calendario de fechas."""

    def __init__(self, calendario_1904=False):
        super().__init__()
        self.calendario_1904 = calendario_1904


def cargar(ruta: Path, requeridas: set[str]) -> dict:
    try:
        with ZipFile(ruta) as libro:
            manifest = parte(libro, "xl/workbook.xml")
            relaciones = parte(libro, "xl/_rels/workbook.xml.rels")
            destinos, cadenas = {}, []
            for rel in relaciones.findall(REL):
                if rel.get("TargetMode") == "External":
                    continue
                destino = rel.attrib["Target"]
                ruta_xml = destino.lstrip("/") if destino.startswith("/") else posixpath.normpath(posixpath.join("xl", destino))
                tipo = rel.attrib["Type"].rsplit("/", 1)[-1]
                if tipo == "worksheet":
                    destinos[rel.attrib["Id"]] = ruta_xml
                if tipo == "sharedStrings":
                    cadenas = [texto(si) for si in parte(libro, ruta_xml).findall(XML + "si")]
            propiedades = manifest.find(XML + "workbookPr")
            usa_1904 = propiedades is not None and propiedades.get("date1904", "0").lower() in {"1", "true"}
            hojas = Hojas(usa_1904)
            for hoja in manifest.iter(XML + "sheet"):
                nombre = hoja.attrib["name"]
                if nombre in requeridas:
                    raiz = parte(libro, destinos[hoja.attrib[RID]])
                    celdas = {}
                    for celda in raiz.iter(XML + "c"):
                        v = valor(celda, cadenas)
                        if v is not None and v != "":
                            celdas[celda.attrib["r"]] = v
                        elif celda.find(XML + "f") is not None:
                            celdas[celda.attrib["r"]] = None
                    hojas[nombre] = celdas
            ausentes = requeridas - hojas.keys()
            if ausentes:
                raise ValueError("Faltan hojas del cuaderno: " + ", ".join(sorted(ausentes)))
            return hojas
    except (BadZipFile, KeyError, ET.ParseError, InvalidOperation, IndexError) as error:
        raise ValueError("El archivo no es un XLSX legible con la estructura del cuaderno.") from error
