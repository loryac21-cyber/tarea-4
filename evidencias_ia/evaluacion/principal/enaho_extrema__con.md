# Evaluación · enaho_extrema · modo con

## Pedido

```text
Responde la pregunta con datos oficiales. Si no puedes saber una cifra con certeza, pon null: no estimes. En «fuente» di de dónde sale cada cifra (código de serie, archivo, documento o cálculo).

Según la ENAHO 2024 del INEI, ¿cuál fue la tasa de pobreza extrema nacional, en % de personas?
```

## Configuración de la sesión

- Modelo: `claude-sonnet-5-5`
- Herramientas disponibles: `Glob`, `Grep`, `PowerShell`, `Read`, `Skill`, `StructuredOutput`, `mcp__bcrp__agregar_anual`, `mcp__bcrp__buscar_series`, `mcp__bcrp__comparar_paises`, `mcp__bcrp__graficar_series`, `mcp__bcrp__resumen`, `mcp__bcrp__serie`
- Servidores MCP: `bcrp` (connected)
- Skills: `developing-with-streamlit`, `graficando-enaho`, `limpiando-enaho`, `mapeando-enaho`, `design`, `design-sync`, `dataviz`, `update-config`, `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`, `claude-api`, `run`, `run-skill-generator`, `plugin-authoring`, `anthropic-skills:built-in-browser`, `anthropic-skills:chrome-browser`, `anthropic-skills:computer-use`, `anthropic-skills:deep-research`, `anthropic-skills:docs`, `anthropic-skills:docx`, `anthropic-skills:google-workspace`, `anthropic-skills:import-memory`, `anthropic-skills:morning`, `anthropic-skills:pdf`, `anthropic-skills:pptx`, `anthropic-skills:skill-creator`, `anthropic-skills:xlsx`

### Llamada a `Glob`

```json
{
 "pattern": "salidas/**"
}
```

### Llamada a `Glob`

```json
{
 "pattern": "**/*.{dta,sav,csv,parquet}"
}
```

<details><summary>Resultado</summary>

```text
No files found
```

</details>

<details><summary>Resultado</summary>

```text
.claude\skills\mapeando-enaho\referencias\pobreza_departamento_2024.csv
datos\bcrp\catalogo_bcrp.csv
```

</details>

### Llamada a `PowerShell`

```json
{
 "command": "Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch 'evaluacion' } | Select-Object -ExpandProperty FullName"
}
```

<details><summary>Resultado</summary>

```text
Command contains script block that may execute arbitrary code
```

</details>

### Llamada a `Glob`

```json
{
 "pattern": "**/*"
}
```

<details><summary>Resultado</summary>

```text
.gitattributes
.claude\skills\mapeando-enaho\referencias\mapa_pobreza_2024_sesion16.png
.claude\skills\mapeando-enaho\referencias\pobreza_departamento_2024.csv
datos\geo\peru_departamental_simple.geojson
datos\enaho\966-Modulo02.zip
datos\enaho\966-Modulo34.zip
.python-version
datos\bcrp\catalogo_bcrp.csv
mcp\server.py
mcp\test_server.py
.gitignore
.claude\skills\limpiando-enaho\scripts\limpiar.py
.claude\skills\graficando-enaho\scripts\graficar.py
.claude\skills\mapeando-enaho\scripts\mapear.py
.claude\skills\limpiando-enaho\SKILL.md
.claude\skills\limpiando-enaho\reference.md
.claude\skills\graficando-enaho\SKILL.md
.claude\skills\mapeando-enaho\SKILL.md
CLAUDE.md
.mcp.json
datos\LEEME.md
agente\ejecutar_agente.py
agente\demo_skills.py
agente\registro.py
pyproject.toml
uv.lock
```

</details>

### Agente

Los microdatos están, así que uso la skill de limpieza.

### Llamada a `Skill`

```json
{
 "skill": "limpiando-enaho"
}
```

<details><summary>Resultado</summary>

```text
Launching skill: limpiando-enaho
```

</details>

### Llamada a `PowerShell`

```json
{
 "command": "uv run C:/Users/Lory/AppData/Local/Temp/tarea4_evaluacion/con_enaho_extrema/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024",
 "timeout": 600000
}
```

<details><summary>Resultado</summary>

```text
Validación de la ENAHO 2024 · limpiando-enaho · 2026-11-08 00:10
Archivos: 966-Modulo34/sumaria-2024.dta, 966-Modulo02/enaho01-2024-200.dta

[APROBADA] (esencial) Hogares en la sumaria: 33,691 (referencia 33,691)
[APROBADA] (esencial) Llaves de hogar únicas en la sumaria: 0 duplicados de conglome+vivienda+hogar
[APROBADA] (esencial) Filas del módulo 02: 117,721 (referencia 117,721)
[APROBADA] (esencial) Llaves de persona únicas en el módulo 02: 0 duplicados de conglome+vivienda+hogar+codperso
[APROBADA] (esencial) Llaves con ceros iniciales (texto): conglome '015009', ubigeo '010101'
[APROBADA] (esencial) Residentes habituales: 108,664 (referencia 108,664) con (p204==1 & p205==2) | (p204==2 & p206==1)
[APROBADA] (esencial) Unión m:1 sin perder ni duplicar personas: 108,664 filas después de unir, 0 personas sin hogar en la sumaria
[APROBADA] (esencial) 25 códigos territoriales (ubigeo[:2]): 25 códigos: 01–25
[APROBADA] (esencial) Factores de expansión presentes y positivos: factor07 nulos: 0, facpob07 nulos: 0
[APROBADA] Población expandida: factor07 × mieperho ≈ suma de facpob07: 34,482,700 frente a 34,147,768 (+0.98 %)
[APROBADA] (esencial) Pobreza monetaria nacional (hogares, factor07 × mieperho): 27.58 % (referencia 27.6 %, tolerancia ±0.1 pp)
[APROBADA] (esencial) Pobreza monetaria nacional (personas, facpob07): 27.53 % (referencia 27.6 %, tolerancia ±0.1 pp)
[APROBADA] El promedio simple NO coincide con la estimación ponderada (prueba de que se pondera): promedio simple sin factor: 25.61 % frente a 27.53 % ponderado
[APROBADA] (esencial) Pobreza extrema nacional: 5.50 % (referencia 5.5 %)
[APROBADA] (esencial) Pobreza urbana (estrato <= 5): 24.81 % (referencia 24.8 %)
[APROBADA] (esencial) Pobreza rural (estrato >= 6): 39.30 % (referencia 39.3 %)
[APROBADA] Pobreza de Lima Metropolitana (dominio 8): 28.21 % (referencia 28.2 %)

Resultado: 17 de 17 verificaciones aprobadas; 0 esenciales fallidas.
ESTADO: OK, la base procesada se puede usar.

Guardé salidas/hogares_2024.parquet (33,691 hogares), salidas/personas_2024.parquet (108,664 personas) y salidas/indicadores.csv (138 filas).
```

</details>

### Llamada a `Grep`

```json
{
 "pattern": "extrema",
 "path": "salidas/indicadores.csv",
 "output_mode": "content",
 "head_limit": 5
}
```

<details><summary>Resultado</summary>

```text
70:pobreza_extrema,nacional,Perú,5.5045,34482700,1898112,33691,hogares: factor07 × mieperho,Perú
71:pobreza_extrema,area,Rural,15.5185,6595188,1023472,11660,hogares: factor07 × mieperho,Rural
72:pobreza_extrema,area,Urbana,3.1363,27887512,874639,22031,hogares: factor07 × mieperho,Urbana
73:pobreza_extrema,region_natural,Costa,1.6149,8116794,131081,10321,hogares: factor07 × mieperho,Costa
74:pobreza_extrema,region_natural,Lima Metropolitana,3.2847,11431706,375502,4090,hogares: factor07 × mieperho,Lima Metropolitana

[Showing results with pagination = limit: 5]
```

</details>

### Llamada a `StructuredOutput`

```json
{
 "valor": 5.5,
 "unidad": "% de personas",
 "fuente": "INEI, ENAHO 2024 (módulos 34 sumaria y 02), ponderado con factor07 × mieperho. Es el resultado de correr la skill limpiando-enaho: salidas/indicadores.csv, fila pobreza_extrema/nacional/Perú = 5.5045 %, es decir 1,898,112 personas de 34,482,700 y 33,691 hogares en la muestra. La validación en salidas/validacion.txt dio 17 de 17 verificaciones aprobadas y 5.50 % frente a la referencia de 5.5 %."
}
```

<details><summary>Resultado</summary>

```text
Structured output provided successfully
```

</details>

## Resultado final

- Turnos: 10
- Duración: 19.5 s
- Costo informado por Claude Code: US$ 0.0783908

{"valor":5.5,"unidad":"% de personas","fuente":"INEI, ENAHO 2024 (módulos 34 sumaria y 02), ponderado con factor07 × mieperho. Es el resultado de correr la skill limpiando-enaho: salidas/indicadores.csv, fila pobreza_extrema/nacional/Perú = 5.5045 %, es decir 1,898,112 personas de 34,482,700 y 33,691 hogares en la muestra. La validación en salidas/validacion.txt dio 17 de 17 verificaciones aprobadas y 5.50 % frente a la referencia de 5.5 %."}
