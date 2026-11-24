# Resolver problemas complejos

Una skill en español para equipos que necesitan explicar una causa, elegir un curso de acción o presentar una decisión defendible. Conecta la pregunta del decisor con las hipótesis, la evidencia y los compromisos de ejecución.

**[Descargar el cuaderno Excel](https://raw.githubusercontent.com/jldelgadoo/resolver-problemas-complejos/main/assets/cuaderno-de-decision.xlsx)** · **[Leer la skill](SKILL.md)** · **[Abrir la nota de decisión](assets/nota-de-decision.md)** · **[Abrir el guion de presentación](assets/guion-de-presentacion.md)**

## Elegir cómo empezar

| Si necesitas… | Empieza por… | Obtienes… |
|---|---|---|
| Entender una brecha | Delimitar la pregunta y dividirla en ramas con un criterio explícito | Árbol MECE y prioridades de investigación |
| Contrastar una explicación | Definir predicción, explicación rival, refutación y prueba mínima | Registro de evidencia a favor y en contra con una interpretación trazable |
| Elegir una alternativa | Fijar condiciones obligatorias y criterios comparables | Recomendación, desventaja asumida y condición que cambiaría la elección |
| Preparar un comité | Ordenar los hallazgos según la decisión solicitada | Nota ejecutiva o guion de títulos con argumento, evidencia y acción |
| Revisar trabajo de terceros | Auditar el cuaderno y comprobar el razonamiento | Hallazgos localizados por hoja y celda y preguntas de revisión |

## Usar la skill y la plantilla

**Con un agente.** En Codex, copia el repositorio en `.agents/skills/resolver-problemas-complejos/` dentro de tu proyecto e invoca `$resolver-problemas-complejos`. Indica la decisión, el destinatario y la evidencia disponible. Puedes pedir el diagnóstico completo o trabajar sobre un único entregable.

**En Excel.** Descarga una copia en blanco por decisión. El cuaderno tiene seis hojas y campos para 50 registros por hoja de trabajo. Permite seguir cada observación hasta la hipótesis y la rama que la originan. Las reglas de lectura y los criterios de cierre están en la [guía del cuaderno](references/guia-del-cuaderno.md).

**Desde la terminal.** Los comandos funcionan con Python 3.10 o posterior y su biblioteca estándar. El primero crea una copia del Excel. El segundo revisa un cuaderno completado y señala cada hallazgo por hoja y celda. El tercero arma la nota de comité con las entradas registradas, incluida la evidencia adversa.

```sh
python3 scripts/cuaderno.py nuevo RUTA_NUEVA.xlsx
python3 scripts/cuaderno.py auditar ARCHIVO.xlsx --json
python3 scripts/cuaderno.py nota ARCHIVO.xlsx NOTA_NUEVA.md
```

## Recursos del método

- [Formular la pregunta y construir el árbol](references/formular-y-descomponer.md)
- [Priorizar ramas y contrastar hipótesis](references/priorizar-y-contrastar.md)
- [Decidir y comunicar con la pirámide y SCQA](references/decidir-y-comunicar.md)
- [Comprobaciones reproducibles del cuaderno](evals/verificar.py)

Cuando la decisión requiere cuantificar una inversión en tecnología, se puede continuar con la [evaluación financiera de proyectos tecnológicos](https://github.com/jldelgadoo/evaluar-proyectos-tecnologicos).

## Procedencia y licencia

Adaptación independiente en español del trabajo publicado por **succtorlin**. Conserva el aviso de licencia MIT del repositorio original. El cuaderno, el auditor y los formatos ejecutivos se desarrollaron para esta edición. [Repositorio de origen](https://github.com/succtorlin/mckinsey-problem-solving-skill) · [Versión consultada](https://github.com/succtorlin/mckinsey-problem-solving-skill/tree/c87cac1000720bb135d87888e9d4db50bd6f0fa3/skills/mckinsey-problem-solving) · [Licencia MIT](LICENSE)

Para profundizar en los métodos descritos, se pueden consultar la conversación de McKinsey sobre resolución de problemas en siete pasos y la presentación del principio de la pirámide por su autora, Barbara Minto. [Método de siete pasos](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/how-to-master-the-seven-step-problem-solving-process) · [Principio de la pirámide](https://barbaraminto.com/)

### Lecturas complementarias

| Lectura | Cómo se relaciona con el trabajo |
|---|---|
| [The McKinsey Way, de Ethan M. Rasiel](https://www.mheducation.com/highered/mhp/product/mckinsey-way.html) | Formular el problema y acordar con el decisor qué trabajo aportará valor |
| [The McKinsey Mind, de Ethan M. Rasiel y Paul N. Friga](https://www.mheducation.com/highered/mhp/product/mckinsey-mind.html) | Organizar el análisis, el trabajo del equipo y la presentación de hallazgos |
| [The Pyramid Principle, de Barbara Minto](https://barbaraminto.com/textbook) | Agrupar argumentos bajo una respuesta central y escribir para quien decide |
