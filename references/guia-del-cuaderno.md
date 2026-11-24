# Usar el cuaderno de decisión

Descargar [el Excel en blanco](../assets/cuaderno-de-decision.xlsx) o crear una copia nueva con `python3 scripts/cuaderno.py nuevo RUTA_NUEVA.xlsx`. Las herramientas usan Python 3.10 o posterior y su biblioteca estándar. El libro puede rellenarse directamente en Excel.

## Cómo avanza el trabajo

| Hoja | Qué registra el equipo | Qué comprueba el cuaderno |
|---|---|---|
| Decisión | Mandato en B6:B14 y recomendación en B17:B24 | Encuadre, trazabilidad de la nota y recuentos documentados |
| Árbol | ID, padre, pregunta, criterio de división, alcance, impacto, capacidad y justificación | Referencia al padre, unicidad y orientación inicial de prioridad |
| Pruebas | Hipótesis, predicción, explicación rival, refutación, método, responsable, plazo e interpretación | Cuenta el respaldo favorable, adverso y no concluyente vinculado a cada prueba |
| Evidencia | Fuente y localizador, fecha de corte, periodo, población, resultado, sentido y limitación | Cada observación completa pertenece a una prueba identificada |
| Opciones | Resultado respecto al criterio común, condición indispensable, costo, plazo, riesgo, evidencia y condición de cambio | Separa opciones comparables, restricciones por verificar y descartes respaldados |
| Acciones | Compromiso, responsable, fecha, verificación, estado y referencia de cierre | Una acción cerrada tiene una referencia localizable |

Las celdas amarillas reciben los datos del equipo. Las áreas verde claro contienen fórmulas. Cada registro tiene un ID estable dentro de su hoja. Elegir un texto de hasta 32 caracteres, sin espacios ni los caracteres `*`, `?` o `~`. Se recomienda usar letras, dígitos y guiones. La coincidencia de IDs admite mayúsculas y minúsculas. En Árbol, dejar el padre vacío para las ramas que dependen directamente de la pregunta de Decisión.

Cada registro ocupa una fila entre la 7 y la 56. Hay capacidad para 50 filas por hoja de registro. Si se necesita más capacidad, ampliar conjuntamente fórmulas, validaciones, rangos y auditor antes de utilizar filas adicionales. Al ordenar, seleccionar filas completas para conservar la asociación entre campos.

## Interpretar los controles

Un registro de evidencia necesita fuente, fecha, población, observación y limitación. Si no se identificó una limitación, consignar la revisión realizada. En Pruebas, una hipótesis sostenida requiere evidencia a favor y una refutada requiere evidencia en contra. El campo de interpretación es obligatorio al pronunciarse, incluso si el resultado es inconcluyente. Describir allí cómo se resolvieron en concreto los resultados contradictorios y si comparten origen. El número de observaciones orienta a sus registros y requiere interpretación.

El panel muestra «Documentación completa» cuando el mandato y la nota tienen sus campos y la evidencia principal lleva a una prueba interpretada con un resultado concluyente. Una prueba principal inconcluyente deja la recomendación como provisional. En la ruta Comparar se necesitan al menos dos opciones documentadas, que pueden incluir un descarte respaldado, y una opción recomendada que cumpla la condición indispensable. El panel comprueba el vínculo principal. El auditor recorre todas las filas y detecta también los ciclos de varios niveles. La cobertura MECE, la fuerza causal y la calidad de la recomendación se revisan con el equipo.

## Auditar un archivo recibido

Ejecutar `python3 scripts/cuaderno.py auditar ARCHIVO.xlsx`. Agregar `--json` para obtener estado, cantidad de registros y hallazgos con hoja y celda. Los códigos de salida son 0 cuando no se encuentran hallazgos estructurales, 1 cuando hay errores o pendientes y 2 si el archivo no se puede procesar o el destino ya existe. Un libro en blanco devuelve «sin iniciar». El auditor lee los campos de entrada guardados y comprueba sus relaciones sin depender del resultado almacenado en las fórmulas de control. Si se utilizan fórmulas en campos de entrada, recalcular y guardar antes de auditar.

Corregir primero los identificadores repetidos, padres circulares y vínculos rotos. Después, revisar hipótesis concluidas sin evidencia compatible, opciones sin respaldo y acciones cerradas sin comprobación. Cuando la recomendación sea provisional, comunicar el pendiente y su efecto sobre la decisión.

## Preparar la nota del comité

La orden `python3 scripts/cuaderno.py nota ARCHIVO.xlsx NOTA_NUEVA.md` crea un documento editable a partir del mandato, la recomendación registrada, la evidencia principal y las observaciones adversas ligadas a la misma prueba. Incluye alternativas, incertidumbre, condición de cambio, responsable y fecha. Los datos ausentes aparecen como pendientes. Si existen hallazgos de integridad, añade los cinco primeros y remite al auditor para consultar el resto. El equipo revisa la evidencia y el lenguaje antes de presentar la nota.
