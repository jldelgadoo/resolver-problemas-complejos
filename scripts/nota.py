"""Redactar una nota trazable con los datos aportados en el cuaderno."""
from html import escape

PENDIENTE = "Pendiente"


def campo(valor):
    if valor is None or str(valor).strip() == "":
        return PENDIENTE
    texto = escape(" ".join(str(valor).split()), quote=False)
    for marca in ("\\", "|", "[", "]", "*", "_", chr(96), "#", "!"):
        texto = texto.replace(marca, "\\" + marca)
    return texto


def tabla(encabezados, filas):
    def linea(fila):
        return "| " + " | ".join(campo(v) for v in fila) + " |"
    return [linea(encabezados), "|" + "---|" * len(encabezados), *[linea(fila) for fila in filas]]


def redactar(revision, informe):
    if informe["estado"] == "sin iniciar":
        raise ValueError("El cuaderno está en blanco. Utiliza la nota editable o completa primero el mandato.")
    d = revision.hojas["Decisión"]
    filas = revision.filas
    def principal(hoja, id_valor):
        if not revision.unico(hoja, id_valor):
            return {}
        n = revision.indice[hoja][id_valor.casefold()][0]
        return filas[hoja][n]
    ev = principal("Evidencia", d.get("B18"))
    prueba = principal("Pruebas", ev.get("B"))
    nota = ["# Nota de decisión", "", campo(d.get("B17")), "",
            *tabla(("Mandato", "Información"), [
                ("Pregunta de decisión", d.get("B6")), ("Quién decide", d.get("B7")),
                ("Fecha límite", revision.fecha_visible(d.get("B12"))), ("Alcance y horizonte", d.get("B8")),
                ("Línea base", d.get("B9")), ("Criterio de éxito", d.get("B10")),
                ("Condición indispensable", d.get("B11")), ("Estado de la documentación", informe["estado"])]),
            "", "## Fundamento y evidencia adversa", "",
            *tabla(("Trazabilidad", "Contenido"), [
                ("Evidencia principal", d.get("B18")), ("Hipótesis vinculada", prueba.get("C")),
                ("Estado de la prueba", prueba.get("J")), ("Interpretación del equipo", prueba.get("K"))])]
    observaciones = []
    if ev:
        observaciones.append(ev)
    if prueba:
        for f in filas["Evidencia"].values():
            if f is not ev and isinstance(f["B"], str) and f["B"].casefold() == prueba["A"].casefold() and f["G"] == "En contra":
                observaciones.append(f)
    if observaciones:
        nota += ["", *tabla(("ID", "Sentido", "Observación y alcance", "Fuente", "Fecha de corte", "Limitación"),
                [(f["A"], f["G"], " · ".join(str(f[c]) for c in ("F","E") if f[c] is not None),
                  f["C"], revision.fecha_visible(f["D"]), f["H"]) for f in observaciones])]
    if filas["Opciones"]:
        nota += ["", "## Alternativas consideradas", "", "Opción propuesta · " + campo(d.get("B21")), "",
                 *tabla(("ID", "Alternativa", "Resultado comparable", "Condición indispensable", "Costo y plazo", "Desventaja", "ID evidencia", "Qué cambiaría la elección"),
                 [tuple(f[c] for c in "ABCDEFGH") for f in filas["Opciones"].values()])]
    nota += ["", "## Compromiso y revisión", "",
             *tabla(("Elemento", "Acuerdo"), [("Incertidumbre dominante", d.get("B19")),
               ("Condición que cambia la decisión", d.get("B22")), ("Próximo compromiso", d.get("B20")),
               ("Responsable", d.get("B23")), ("Próxima revisión", revision.fecha_visible(d.get("B24")))])]
    if informe["hallazgos"]:
        ordenados = sorted(informe["hallazgos"], key=lambda h: h["tipo"] != "error")
        nota += ["", "## Pendientes de revisión", "", *tabla(("Ubicación", "Hallazgo"),
                 [(h["hoja"]+"!"+h["celda"], h["mensaje"]) for h in ordenados[:5]])]
        if len(ordenados) > 5:
            nota += ["", f"El auditor contiene {len(ordenados) - 5} hallazgos adicionales."]
    return "\n".join(nota) + "\n"
