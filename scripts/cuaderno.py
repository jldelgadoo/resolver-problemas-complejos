#!/usr/bin/env python3
"""Crear y auditar un cuaderno de resolución estructurada de problemas."""
import argparse
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from leer_xlsx import cargar
from nota import redactar

RAIZ = Path(__file__).resolve().parents[1]
FIN = 56
EDITABLE = {"Árbol": "H", "Pruebas": "K", "Evidencia": "H", "Opciones": "H", "Acciones": "G"}
CABECERAS = {"Árbol": ("ID rama", "Control de la rama"), "Pruebas": ("ID prueba", "Control de la prueba"),
             "Evidencia": ("ID evidencia", "Control de evidencia"), "Opciones": ("ID opción", "Control de la opción"),
             "Acciones": ("ID acción", "Control de la acción")}
CONTROL = {"Árbol": "J", "Pruebas": "O", "Evidencia": "I", "Opciones": "I", "Acciones": "H"}
UBICACION = re.compile(r"([A-Z]+)([1-9][0-9]*)")
RUTAS = ("Diagnosticar", "Comparar", "Comunicar")
SENTIDOS = ("A favor", "En contra", "No concluyente")
ESTADOS = ("Pendiente", "En curso", "Sostenida", "Refutada", "Inconcluyente")


def clave(v):
    return v.casefold() if isinstance(v, str) else None


def hay(v):
    return bool(v.strip()) if isinstance(v, str) else v is not None


def fecha(v):
    return isinstance(v, date) or (isinstance(v, Decimal) and 0 < v <= 2958465 and v == v.to_integral_value())


def id_valido(v):
    return isinstance(v, str) and 0 < len(v) <= 32 and not any(c.isspace() or c in "*?~" for c in v)


def crear(destino):
    if destino.suffix.lower() != ".xlsx":
        raise ValueError("El destino debe tener extensión .xlsx.")
    with (RAIZ / "assets/cuaderno-de-decision.xlsx").open("rb") as origen, destino.open("xb") as salida:
        try:
            shutil.copyfileobj(origen, salida)
        except OSError:
            salida.close()
            destino.unlink(missing_ok=True)
            raise


class Revision:
    def __init__(self, hojas):
        self.hojas = hojas
        self.hallazgos = []
        self.filas = {}
        self.indice = {}
        for nombre, fin in EDITABLE.items():
            hoja = hojas[nombre]
            ids = defaultdict(list)
            filas = {}
            for n in range(7, FIN + 1):
                campos = {chr(i): hoja.get(chr(i) + str(n)) for i in range(ord("A"), ord(fin) + 1)}
                if any(hay(v) for v in campos.values()):
                    filas[n] = campos
                    if id_valido(campos["A"]):
                        ids[clave(campos["A"])].append(n)
            self.filas[nombre], self.indice[nombre] = filas, ids
        self.evidencias = set()
        self.sentidos = defaultdict(Counter)
        self.interpretadas = set()
        self.opciones = {}

    def fecha_visible(self, valor):
        if not fecha(valor):
            return None
        if isinstance(valor, date):
            return valor.strftime("%d/%m/%Y")
        dias = int(valor)
        if getattr(self.hojas, "calendario_1904", False):
            inicio = date(1904, 1, 1)
        elif dias == 60:
            return "29/02/1900 (calendario de Excel)"
        else:
            inicio = date(1899, 12, 31) if dias < 60 else date(1899, 12, 30)
        try:
            return (inicio + timedelta(days=dias)).strftime("%d/%m/%Y")
        except OverflowError:
            return None

    def marcar(self, hoja, celda, mensaje, nivel="pendiente"):
        self.hallazgos.append({"tipo": nivel, "hoja": hoja, "celda": celda, "mensaje": mensaje})

    def unico(self, nombre, v):
        return id_valido(v) and len(self.indice[nombre].get(clave(v), [])) == 1

    def validar_fila(self, nombre, n, obligatorios, fechas="", listas=None, referencia=None):
        fila = self.filas[nombre][n]
        inicio = len(self.hallazgos)
        def anotar(c, msj, nivel="pendiente"):
            self.marcar(nombre, c + str(n), msj, nivel)
        if not hay(fila["A"]):
            anotar("A", "Asignar un identificador.")
        elif not self.unico(nombre, fila["A"]):
            anotar("A", "Corregir el identificador inválido o repetido.", "error")
        for c in obligatorios:
            if not hay(fila[c]):
                anotar(c, "Completar el campo «" + self.hojas[nombre][c + "6"] + "».")
        for c in fechas:
            if not fecha(fila[c]):
                anotar(c, "Introducir una fecha de calendario válida.", "error" if hay(fila[c]) else "pendiente")
        for c, valores in (listas or {}).items():
            if fila[c] not in valores:
                anotar(c, "Elegir un valor de la lista.", "error" if hay(fila[c]) else "pendiente")
        if referencia:
            c, destino = referencia
            if not self.unico(destino, fila[c]):
                anotar(c, "Vincular un ID único de " + destino + ".", "error" if hay(fila[c]) else "pendiente")
        return len(self.hallazgos) == inicio

    def estructura(self):
        for nombre, fin in EDITABLE.items():
            hoja = self.hojas[nombre]
            if (hoja.get("A6"), hoja.get(CONTROL[nombre] + "6")) != CABECERAS[nombre]:
                raise ValueError("El diseño de columnas difiere de la plantilla en " + nombre + ".")
            for celda, v in hoja.items():
                col, n = UBICACION.fullmatch(celda).groups()
                if len(col) == 1 and col <= fin and int(n) >= 7:
                    if int(n) > FIN and hay(v):
                        self.marcar(nombre, celda, "El dato queda fuera del área con controles. Ampliar el modelo o trasladar la fila.", "error")
                    elif v is None:
                        self.marcar(nombre, celda, "La entrada contiene una fórmula sin valor guardado. Revisar y recalcular.", "pendiente")

    def arbol(self):
        padres = {}
        for n, f in self.filas["Árbol"].items():
            self.validar_fila("Árbol", n, "CDEH", listas={"F": ("Alto", "Medio", "Bajo"), "G": ("Alta", "Media", "Baja")})
            if hay(f["B"]):
                if not self.unico("Árbol", f["B"]):
                    self.marcar("Árbol", "B" + str(n), "El padre no identifica una rama única.", "error")
                elif self.unico("Árbol", f["A"]):
                    padres[clave(f["A"])] = clave(f["B"])
        visitados = set()
        for origen in padres:
            camino, indices = [], {}
            actual = origen
            while actual in padres and actual not in visitados and actual not in indices:
                indices[actual] = len(camino)
                camino.append(actual)
                actual = padres[actual]
            if actual in indices:
                for rama in camino[indices[actual]:]:
                    n = self.indice["Árbol"][rama][0]
                    self.marcar("Árbol", "B" + str(n), "La rama forma parte de un ciclo de padres.", "error")
            visitados.update(camino)

    def contrastar(self):
        for n, f in self.filas["Evidencia"].items():
            if self.validar_fila("Evidencia", n, "CEFH", "D", {"G": SENTIDOS}, ("B", "Pruebas")):
                self.evidencias.add(clave(f["A"]))
                self.sentidos[clave(f["B"])][f["G"]] += 1
        for n, f in self.filas["Pruebas"].items():
            inicio = len(self.hallazgos)
            self.validar_fila("Pruebas", n, "CDEFGH", "I", {"J": ESTADOS}, ("B", "Árbol"))
            if f["J"] not in ESTADOS[2:]:
                continue
            cuentas = self.sentidos[clave(f["A"])]
            requerido = {"Sostenida": "A favor", "Refutada": "En contra"}.get(f["J"])
            if not cuentas or (requerido and not cuentas[requerido]):
                self.marcar("Pruebas", "J" + str(n), "El estado declarado carece de evidencia documentada compatible.", "error")
            if not hay(f["K"]):
                self.marcar("Pruebas", "K" + str(n), "Explicar la interpretación y el tratamiento de la evidencia adversa.")
            if len(self.hallazgos) == inicio:
                self.interpretadas.add(clave(f["A"]))

    def opciones_y_acciones(self):
        for n, f in self.filas["Opciones"].items():
            valida = self.validar_fila("Opciones", n, "BC", listas={"D": ("Cumple", "Incumple", "Por verificar")})
            if f["D"] not in ("Cumple", "Incumple"):
                self.marcar("Opciones", "D" + str(n), "Verificar la condición indispensable antes de ordenar la opción.")
                continue
            if clave(f["G"]) not in self.evidencias:
                self.marcar("Opciones", "G" + str(n), "Vincular evidencia completa que respalde el cumplimiento o descarte.")
                valida = False
            if f["D"] == "Cumple" and not all(hay(f[k]) for k in "EFH"):
                self.marcar("Opciones", "E" + str(n), "Documentar costo/plazo, desventaja y condición que cambiaría la elección.")
                valida = False
            if valida:
                self.opciones[clave(f["A"])] = f["D"]
        for n, f in self.filas["Acciones"].items():
            self.validar_fila("Acciones", n, "BCE", "D", {"F": ("Pendiente", "En curso", "Cerrada")})
            if f["F"] == "Cerrada" and not hay(f["G"]):
                self.marcar("Acciones", "G" + str(n), "Adjuntar la referencia que comprueba el cierre.")

    def mandato(self):
        d = self.hojas["Decisión"]
        if d.get("A6") != "Pregunta de decisión" or d.get("A17") != "Acción recomendada y fundamento":
            raise ValueError("El diseño de la hoja Decisión difiere de la plantilla.")
        campos = [i for i in range(6, 25) if i not in (15, 16)]
        if not any(hay(d.get("B" + str(i))) for i in campos) and not any(self.filas.values()):
            self.marcar("Decisión", "B6", "Cuaderno en blanco. Formular la pregunta de decisión.")
            return "sin iniciar"
        for i in range(6, 15):
            celda = "B" + str(i)
            v = d.get(celda)
            if not hay(v):
                self.marcar("Decisión", celda, "Completar el mandato: " + d["A" + str(i)] + ".")
            elif (i == 12 and not fecha(v)) or (i == 13 and v not in RUTAS):
                self.marcar("Decisión", celda, "Revisar la fecha o el valor elegido.", "error")
        if not any(hay(d.get("B" + str(i))) for i in range(17, 25)):
            self.marcar("Decisión", "B17", "La recomendación sigue abierta.")
            return "en análisis"
        for i in (17, 19, 20, 22, 23):
            if not hay(d.get("B" + str(i))):
                self.marcar("Decisión", "B" + str(i), "Completar: " + d["A" + str(i)] + ".")
        if not fecha(d.get("B24")):
            self.marcar("Decisión", "B24", "Fijar una fecha válida de revisión.")
        ev = clave(d.get("B18"))
        if ev not in self.evidencias:
            self.marcar("Decisión", "B18", "La recomendación requiere evidencia principal válida o debe comunicarse como provisional.")
        else:
            n = self.indice["Evidencia"][ev][0]
            prueba = clave(self.filas["Evidencia"][n]["B"])
            if prueba not in self.interpretadas:
                self.marcar("Decisión", "B18", "Interpretar la prueba vinculada a la evidencia principal.")
            elif self.filas["Pruebas"][self.indice["Pruebas"][prueba][0]]["J"] == "Inconcluyente":
                self.marcar("Decisión", "B18", "La prueba principal sigue inconcluyente. Comunicar la recomendación como provisional.")
        if d.get("B13") == "Comparar" and (len(self.opciones) < 2 or self.opciones.get(clave(d.get("B21"))) != "Cumple"):
            self.marcar("Decisión", "B21", "Documentar dos opciones y elegir una que cumpla la condición indispensable.")
        return "en revisión" if self.hallazgos else "documentado"

    def informe(self):
        self.estructura()
        self.arbol()
        self.contrastar()
        self.opciones_y_acciones()
        estado = self.mandato()
        return {"estado": estado, "registros": {k: len(v) for k, v in self.filas.items()},
                "hallazgos": self.hallazgos, "alcance": "Integridad de entradas y vínculos. La suficiencia de la evidencia requiere juicio."}


def auditar(archivo):
    return Revision(cargar(archivo, {"Decisión", *EDITABLE})).informe()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operacion", required=True)
    nueva = sub.add_parser("nuevo", help="Crear una copia nueva del Excel en blanco.")
    nueva.add_argument("archivo", type=Path)
    aud = sub.add_parser("auditar", help="Comprobar entradas, vínculos, ciclos y coherencia del cierre.")
    aud.add_argument("archivo", type=Path)
    aud.add_argument("--json", action="store_true", help="Emitir resultados estructurados.")
    nota = sub.add_parser("nota", help="Preparar una nota ejecutiva en Markdown a partir de las entradas guardadas.")
    nota.add_argument("archivo", type=Path)
    nota.add_argument("destino", type=Path)
    args = parser.parse_args()
    try:
        if args.operacion == "nuevo":
            crear(args.archivo)
            print("Cuaderno creado en", args.archivo)
            return 0
        revision = Revision(cargar(args.archivo, {"Decisión", *EDITABLE}))
        informe = revision.informe()
        if args.operacion == "nota":
            if args.destino.suffix.lower() != ".md":
                raise ValueError("La nota de salida debe tener extensión .md.")
            contenido = redactar(revision, informe)
            with args.destino.open("x", encoding="utf-8") as f:
                try:
                    f.write(contenido)
                except OSError:
                    f.close()
                    args.destino.unlink(missing_ok=True)
                    raise
            print("Nota preparada en", args.destino)
            return 0
        if args.json:
            print(json.dumps(informe, ensure_ascii=False, indent=2))
        else:
            print("Estado:", informe["estado"])
            for h in informe["hallazgos"]:
                print(f"{h['tipo']} | {h['hoja']}!{h['celda']} | {h['mensaje']}")
            print(informe["alcance"])
        return 1 if informe["hallazgos"] else 0
    except FileExistsError:
        parser.exit(2, "El destino ya existe. Elige otro nombre.\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"No se pudo completar la operación: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
