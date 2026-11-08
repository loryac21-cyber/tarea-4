# Evaluación · enaho_residentes · modo con

## Pedido

```text
Responde la pregunta con datos oficiales. Si no puedes saber una cifra con certeza, pon null: no estimes. En «fuente» di de dónde sale cada cifra (código de serie, archivo, documento o cálculo).

¿Cuántas personas son residentes habituales en el módulo 02 (características de los miembros del hogar) de la ENAHO 2024 del INEI, con el criterio de residencia habitual del INEI?
```

## Configuración de la sesión

- Modelo: `claude-sonnet-5-5`
- Herramientas disponibles: `Glob`, `Grep`, `PowerShell`, `Read`, `Skill`, `StructuredOutput`, `mcp__bcrp__agregar_anual`, `mcp__bcrp__buscar_series`, `mcp__bcrp__comparar_paises`, `mcp__bcrp__graficar_series`, `mcp__bcrp__resumen`, `mcp__bcrp__serie`
- Servidores MCP: `bcrp` (connected)
- Skills: `developing-with-streamlit`, `graficando-enaho`, `limpiando-enaho`, `mapeando-enaho`, `design`, `design-sync`, `dataviz`, `update-config`, `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`, `claude-api`, `run`, `run-skill-generator`, `plugin-authoring`, `anthropic-skills:built-in-browser`, `anthropic-skills:chrome-browser`, `anthropic-skills:computer-use`, `anthropic-skills:deep-research`, `anthropic-skills:docs`, `anthropic-skills:docx`, `anthropic-skills:google-workspace`, `anthropic-skills:import-memory`, `anthropic-skills:morning`, `anthropic-skills:pdf`, `anthropic-skills:pptx`, `anthropic-skills:skill-creator`, `anthropic-skills:xlsx`

### Llamada a `PowerShell`

```json
{
 "command": "Get-ChildItem -Recurse -Depth 2 -Exclude evaluacion | Where-Object { $_.FullName -notmatch '\\\\evaluacion' } | Select-Object -ExpandProperty FullName"
}
```

<details><summary>Resultado</summary>

```text
Command contains a UNC path that could trigger network requests
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
pyproject.toml
.python-version
uv.lock
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
agente\registro.py
agente\ejecutar_agente.py
figuras\bcrp_agro_alimentos.png
salidas\validacion.txt
salidas\hogares_2024.parquet
salidas\personas_2024.parquet
salidas\indicadores.csv
figuras\enaho_pobreza_area_2024.csv
figuras\enaho_pobreza_area_2024.png
figuras\enaho_distribucion_pobres_area_2024.csv
figuras\enaho_distribucion_pobres_area_2024.png
figuras\enaho_pobreza_departamento_2024.png
figuras\enaho_pobreza_departamento_2024.csv
salidas\comparacion_mapa_referencia.csv
mapas\pobreza_departamento_2024.png
mapas\pobreza_departamento_2024.csv
```

</details>

### Llamada a `Read`

```json
{
 "file_path": "C:\\Users\\Lory\\AppData\\Local\\Temp\\tarea4_evaluacion\\con_herramientas\\salidas\\validacion.txt"
}
```

### Llamada a `Read`

```json
{
 "file_path": "C:\\Users\\Lory\\AppData\\Local\\Temp\\tarea4_evaluacion\\con_herramientas\\.claude\\skills\\limpiando-enaho\\reference.md"
}
```

<details><summary>Resultado</summary>

```text
1	Validación de la ENAHO 2024 · limpiando-enaho · 2026-11-08 00:03
2	Archivos: 966-Modulo34/sumaria-2024.dta, 966-Modulo02/enaho01-2024-200.dta
3	
4	[APROBADA] (esencial) Hogares en la sumaria: 33,691 (referencia 33,691)
5	[APROBADA] (esencial) Llaves de hogar únicas en la sumaria: 0 duplicados de conglome+vivienda+hogar
6	[APROBADA] (esencial) Filas del módulo 02: 117,721 (referencia 117,721)
7	[APROBADA] (esencial) Llaves de persona únicas en el módulo 02: 0 duplicados de conglome+vivienda+hogar+codperso
8	[APROBADA] (esencial) Llaves con ceros iniciales (texto): conglome '015009', ubigeo '010101'
9	[APROBADA] (esencial) Residentes habituales: 108,664 (referencia 108,664) con (p204==1 & p205==2) | (p204==2 & p206==1)
10	[APROBADA] (esencial) Unión m:1 sin perder ni duplicar personas: 108,664 filas después de unir, 0 personas sin hogar en la sumaria
11	[APROBADA] (esencial) 25 códigos territoriales (ubigeo[:2]): 25 códigos: 01–25
12	[APROBADA] (esencial) Factores de expansión presentes y positivos: factor07 nulos: 0, facpob07 nulos: 0
13	[APROBADA] Población expandida: factor07 × mieperho ≈ suma de facpob07: 34,482,700 frente a 34,147,768 (+0.98 %)
14	[APROBADA] (esencial) Pobreza monetaria nacional (hogares, factor07 × mieperho): 27.58 % (referencia 27.6 %, tolerancia ±0.1 pp)
15	[APROBADA] (esencial) Pobreza monetaria nacional (personas, facpob07): 27.53 % (referencia 27.6 %, tolerancia ±0.1 pp)
16	[APROBADA] El promedio simple NO coincide con la estimación ponderada (prueba de que se pondera): promedio simple sin factor: 25.61 % frente a 27.53 % ponderado
17	[APROBADA] (esencial) Pobreza extrema nacional: 5.50 % (referencia 5.5 %)
18	[APROBADA] (esencial) Pobreza urbana (estrato <= 5): 24.81 % (referencia 24.8 %)
19	[APROBADA] (esencial) Pobreza rural (estrato >= 6): 39.30 % (referencia 39.3 %)
20	[APROBADA] Pobreza de Lima Metropolitana (dominio 8): 28.21 % (referencia 28.2 %)
21	
22	Resultado: 17 de 17 verificaciones aprobadas; 0 esenciales fallidas.
23	ESTADO: OK, la base procesada se puede usar.
24	
```

</details>

<details><summary>Resultado</summary>

```text
1	# Referencia de la ENAHO 2024 para `limpiando-enaho`
2	
3	## Archivos
4	
5	| Módulo | Archivo en el zip | Una fila por | Filas | Llaves | Factor |
6	|---|---|---|---|---|---|
7	| [34 · Sumaria](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip) | `sumaria-2024.dta` (no `sumaria-2024-12g.dta`) | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` |
8	| [02 · Miembros del hogar](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip) | `enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` |
9	
10	`966` es el código de la ENAHO 2024 (anual) en el portal de microdatos del INEI. Los zip van en `datos/enaho/`, que
11	git ignora.
12	
13	## Variables que usa el pipeline
14	
15	| Variable | Módulo | Qué es | Códigos |
16	|---|---|---|---|
17	| `conglome`, `vivienda`, `hogar`, `codperso` | 34 y 02 | Llaves. Texto con ceros: `015009`, `013`, `11`, `01` | — |
18	| `ubigeo` | 34 y 02 | Departamento, provincia y distrito. `ubigeo[:2]` = departamento | `01` Amazonas … `07` Callao … `15` Lima … `25` Ucayali |
19	| `dominio` | 34 | Dominio geográfico | 1-3 costa norte/centro/sur, 4-6 sierra norte/centro/sur, 7 selva, 8 Lima Metropolitana |
20	| `estrato` | 34 | Estrato de la muestra | 1-5 urbano, 6-8 rural |
21	| `mieperho` | 34 | Miembros del hogar (sin trabajadores del hogar ni pensionistas) | — |
22	| `pobreza` | 34 | Condición de pobreza del hogar | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
23	| `linea`, `linpe` | 34 | Línea de pobreza total y extrema, S/ por persona al mes | — |
24	| `gashog2d`, `inghog1d` | 34 | Gasto e ingreso del hogar, S/ al año | — |
25	| `factor07` | 34 | Factor de expansión del hogar | — |
26	| `p203` | 02 | Relación con el jefe del hogar | 1 jefe, 2 cónyuge, 3 hijo… |
27	| `p204` | 02 | ¿Es miembro del hogar? | 1 sí, 2 no |
28	| `p205` | 02 | ¿Estuvo ausente más de 30 días? | 1 sí, 2 no |
29	| `p206` | 02 | ¿Estuvo presente más de 30 días? (no miembros) | 1 sí, 2 no |
30	| `p207` | 02 | Sexo | 1 hombre, 2 mujer |
31	| `p208a` | 02 | Edad en años cumplidos | — |
32	| `facpob07` | 02 | Factor de expansión de la persona | — |
33	
34	La columna del año llega como `aÑo` (a veces se lee `a�o`); el script la renombra `anio`.
35	
36	## Variables construidas
37	
38	| En la base | Regla |
39	|---|---|
40	| residente habitual | `((p204 == 1) & (p205 == 2)) \| ((p204 == 2) & (p206 == 1))` → 108,664 personas |
41	| `departamento` | `ubigeo[:2]` (texto de dos dígitos) |
42	| `area` | `Urbana` si `estrato <= 5`, si no `Rural` |
43	| `region_natural` | Costa (dominio 1-3), Sierra (4-6), Selva (7), Lima Metropolitana (8) |
44	| `pobre`, `pobre_extremo` | `pobreza <= 2`, `pobreza == 1` |
45	| `factor_personas` | `factor07 × mieperho`: expande cada hogar a sus miembros |
46	| `grupo_edad` | 0-14, 15-29, 30-44, 45-64, 65 y más |
47	
48	## Dos maneras correctas de ponderar, y por qué dan 27.58 % y 27.53 %
49	
50	1. **Hogares** (`sumaria`, `factor07 × mieperho`): es el método del INEI para la pobreza oficial. Da 27.58 %
51	   nacional, 24.81 % urbano y 39.30 % rural, y reproduce la pobreza por departamento de la referencia.
52	2. **Personas** (`facpob07`, solo residentes habituales): da 27.53 %. Sirve para características individuales como
53	   sexo o edad. La diferencia (0.05 pp) viene de que `facpob07` está calibrado a proyecciones de población y
54	   `mieperho` no cuenta exactamente a los mismos residentes.
55	
56	Ambas quedan dentro de ±0.1 pp del 27.6 % oficial. El promedio simple sin factor da 25.6 %: por eso nunca se usa.
57	
58	```python
59	import pandas as pd
60	h = pd.read_parquet("salidas/hogares_2024.parquet")
61	p = pd.read_parquet("salidas/personas_2024.parquet")
62	tasa = lambda d, ind, peso: (d[ind] * d[peso]).sum() / d[peso].sum() * 100
63	tasa(h, "pobre", "factor_personas")                      # 27.58, nacional
64	h.groupby("area").apply(lambda d: tasa(d, "pobre", "factor_personas"))
65	p[p.edad < 18].pipe(tasa, "pobre", 
… [1175 caracteres más en el .jsonl]
```

</details>

### Llamada a `StructuredOutput`

```json
{
 "valor": 108664,
 "unidad": "personas (registros sin ponderar del módulo 02)",
 "fuente": "INEI, ENAHO 2024, módulo 02 (enaho01-2024-200.dta, 117,721 filas). Conteo de registros sin ponderar con el criterio de residente habitual del INEI: (p204==1 & p205==2) | (p204==2 & p206==1). Resultado en salidas/validacion.txt, generado por .claude/skills/limpiando-enaho/scripts/limpiar.py: 108,664, que coincide con la referencia. Es un conteo de muestra, no una población expandida."
}
```

<details><summary>Resultado</summary>

```text
Structured output provided successfully
```

</details>

## Resultado final

- Turnos: 6
- Duración: 9.3 s
- Costo informado por Claude Code: US$ 0.0683551

{"valor":108664,"unidad":"personas (registros sin ponderar del módulo 02)","fuente":"INEI, ENAHO 2024, módulo 02 (enaho01-2024-200.dta, 117,721 filas). Conteo de registros sin ponderar con el criterio de residente habitual del INEI: (p204==1 & p205==2) | (p204==2 & p206==1). Resultado en salidas/validacion.txt, generado por .claude/skills/limpiando-enaho/scripts/limpiar.py: 108,664, que coincide con la referencia. Es un conteo de muestra, no una población expandida."}
