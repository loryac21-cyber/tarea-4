# Evidencias del uso de inteligencia artificial

Todo el proyecto se desarrolló con **Claude Code** (Anthropic) en VS Code. Las evidencias son las ejecuciones del
agente (exportación de las sesiones): cada vez que el agente trabajó con `claude -p`, los scripts del proyecto
guardaron la sesión completa en JSON (`.jsonl`, una línea por evento: cada mensaje, cada llamada a una herramienta MCP
o skill y su resultado) y una versión legible en Markdown (`.md`).

| Carpeta | Qué hay | Lo generó |
|---|---|---|
| [`mcp/`](mcp/) | Salida de las 11 pruebas del servidor (`pytest_11_passed.txt`) | `uv run pytest -v` |
| [`skills/`](skills/) | Tres pedidos que activan las skills: invocación directa (`/limpiando-enaho 2024`), lenguaje natural (gráficos por sexo y edad) y encadenamiento (mapa sin base procesada → `limpiando-enaho` y luego `mapeando-enaho`); `resumen_activacion.json` | `uv run agente/demo_skills.py` |
| [`integracion/`](integracion/) | La ejecución integrada que respondió la pregunta de investigación con 4 herramientas MCP y las 3 skills, y escribió `informes/informe_final.md` | `uv run agente/ejecutar_agente.py` |
| [`evaluacion/principal/`](evaluacion/principal/) | Las 20 sesiones del experimento (10 preguntas × 2 modos) | `uv run evaluacion/evaluar.py` |
| [`evaluacion/con_salidas_previas/`](evaluacion/con_salidas_previas/) | Primera corrida, en la que el modo con herramientas tenía las salidas ya calculadas | `--con-salidas --etiqueta con_salidas_previas` |
| [`evaluacion/sin_null/`](evaluacion/sin_null/) | Experimento extra: el modo sin herramientas sin permiso para decir «no sé» | `--modos sin --sin-null --etiqueta sin_null` |

Cómo leer una ejecución: abran el `.md`. La sección «Configuración de la sesión» lista el modelo, las herramientas,
los servidores MCP conectados y las skills disponibles; luego aparece cada «Llamada a `mcp__bcrp__...`» o
«Llamada a `Skill`» con su entrada, y su resultado desplegable.

**Datos sensibles.** Antes de publicar se buscaron correos, claves, tokens y contraseñas en todos los archivos de
esta carpeta: no hay ninguno (`apiKeySource: none`; las únicas apariciones de «token» son contadores de uso del
modelo). Las rutas muestran el usuario de Windows (`C:\Users\Lory\...`), que no es un dato sensible.
