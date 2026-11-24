"""Pruebas de integridad con identificadores y valores de control, sin casos de negocio."""
import sys
import unittest
from decimal import Decimal
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from cuaderno import EDITABLE, Revision, auditar, crear
from leer_xlsx import cargar
from nota import redactar


def libro_base():
    hojas = cargar(RAIZ / "assets/cuaderno-de-decision.xlsx", {"Decisión", *EDITABLE})
    d = hojas["Decisión"]
    for n in (*range(6, 15), *range(17, 25)):
        d["B" + str(n)] = "Texto"
    d.update(B12=date.today(), B13="Comparar", B18="E", B21="O", B24=date.today())
    def fila(hoja, n, valores):
        hojas[hoja].update({chr(65+i)+str(n): v for i, v in enumerate(valores) if v is not None})
    fila("Árbol", 7, ("R", None, "T", "T", "T", "Alto", "Alta", "T"))
    fila("Pruebas", 7, ("P", "R", "T", "T", "T", "T", "T", "T", date.today(), "Sostenida", "T"))
    fila("Evidencia", 7, ("E", "P", "T", date.today(), "T", "T", "A favor", "T"))
    fila("Opciones", 7, ("O", "T", "T", "Cumple", "T", "T", "E", "T"))
    fila("Opciones", 8, ("Q", "T", "T", "Incumple", None, None, "E"))
    return hojas


class Integridad(unittest.TestCase):
    def test_copia_en_blanco(self):
        with TemporaryDirectory() as d:
            destino = Path(d) / "cuaderno.xlsx"
            crear(destino)
            self.assertEqual(destino.read_bytes(), (RAIZ / "assets/cuaderno-de-decision.xlsx").read_bytes())
            self.assertEqual(auditar(destino)["estado"], "sin iniciar")
            with self.assertRaises(FileExistsError):
                crear(destino)

    def test_cadena_documentada(self):
        informe = Revision(libro_base()).informe()
        self.assertEqual(informe["hallazgos"], [])
        self.assertEqual(informe["estado"], "documentado")

    def test_ciclo_indirecto(self):
        hojas = libro_base()
        hojas["Árbol"].update(B7="S", A8="S", B8="R")
        alertas = Revision(hojas).informe()["hallazgos"]
        self.assertEqual({h["celda"] for h in alertas if "ciclo" in h["mensaje"]}, {"B7", "B8"})

    def test_evidencia_y_estado(self):
        for modificador, celda, destino in [
            (("Evidencia", "G7", "En contra"), "J7", "Pruebas"),
            (("Pruebas", "J7", "Refutada"), "J7", "Pruebas"),
            (("Pruebas", "J7", "Inconcluyente"), "B18", "Decisión"),
            (("Pruebas", "K7", ""), "K7", "Pruebas"),
            (("Evidencia", "C7", ""), "C7", "Evidencia"),
            (("Opciones", "A8", "o"), "A7", "Opciones"),
            (("Decisión", "B21", "Q"), "B21", "Decisión"),
            (("Evidencia", "B7", "Z"), "B7", "Evidencia"),
            (("Acciones", "B57", "T"), "B57", "Acciones"),
        ]:
            with self.subTest(modificador=modificador):
                hojas = libro_base()
                hoja, pos, valor = modificador
                hojas[hoja][pos] = valor
                registros = {(h["hoja"],h["celda"]) for h in Revision(hojas).informe()["hallazgos"]}
                self.assertIn((destino, celda), registros)

    def test_contradiccion_requiere_juicio(self):
        hojas = libro_base()
        for col in "ABCDEFGH":
            hojas["Evidencia"][col+"8"] = hojas["Evidencia"][col+"7"]
        hojas["Evidencia"].update(A8="F", G8="En contra")
        self.assertFalse(Revision(hojas).informe()["hallazgos"])
        hojas["Pruebas"]["K7"] = ""
        self.assertTrue(any(h["celda"] == "K7" for h in Revision(hojas).informe()["hallazgos"]))

    def test_nota_conserva_opciones_y_evidencia_adversa(self):
        hojas = libro_base()
        hojas["Opciones"].update(B7="Primera opción", B8="Segunda opción")
        for col in "ABCDEFGH":
            hojas["Evidencia"][col+"8"] = hojas["Evidencia"][col+"7"]
        hojas["Evidencia"].update(A8="F", G8="En contra", F8="Observación adversa")
        revision = Revision(hojas)
        nota = redactar(revision, revision.informe())
        for valor in ("Primera opción", "Segunda opción", "Observación adversa", "En contra"):
            self.assertEqual(nota.count(valor), 1)
        self.assertNotIn("Pendientes de revisión", nota)
        self.assertEqual(revision.fecha_visible(Decimal("45600")), "04/11/2024")
        hojas.calendario_1904 = True
        self.assertEqual(revision.fecha_visible(Decimal("1")), "02/01/1904")

    def test_cierre_requiere_referencia(self):
        hojas = libro_base()
        hojas["Acciones"].update(A7="A", B7="T", C7="T", D7=date.today(), E7="T", F7="Cerrada")
        self.assertTrue(any(h["celda"] == "G7" for h in Revision(hojas).informe()["hallazgos"]))
        hojas["Acciones"]["G7"] = "T"
        self.assertFalse(Revision(hojas).informe()["hallazgos"])


if __name__ == "__main__":
    unittest.main()
