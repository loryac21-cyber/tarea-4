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

### Llamada a `Read`

```json
{
 "file_path": "C:\\Users\\Lory\\AppData\\Local\\Temp\\tarea4_evaluacion\\con_enaho_residentes\\.claude\\skills\\limpiando-enaho\\SKILL.md"
}
```

<details><summary>Resultado</summary>

```text
1	---
2	name: limpiando-enaho
3	description: Limpia, une y valida los módulos 34 (sumaria) y 02 (miembros del hogar) de la ENAHO 2024 del INEI y arma las bases de hogares y personas con pobreza monetaria, pobreza extrema, departamento, área urbana/rural, sexo, edad y factores de expansión. Úsala cuando pidan limpiar, unir, validar o analizar la ENAHO o los microdatos del INEI, o calcular la pobreza (nacional, urbana, rural, por departamento, región, sexo o edad), y antes de graficar o mapear la ENAHO si no existe salidas/personas_2024.parquet.
4	argument-hint: "[año, por defecto 2024]"
5	allowed-tools: Bash(uv run:*), Read, Glob
6	---
7	# Limpiar la ENAHO
8	
9	Lo que no se discute (llaves, filtro de residentes, unión, ponderación, validación) está en `scripts/limpiar.py`.
10	Córrelo tal cual: no reescribas el pipeline ni corrijas cifras a mano.
11	
12	1. Revisa que existan `datos/enaho/966-Modulo34.zip` y `datos/enaho/966-Modulo02.zip` (966 = ENAHO 2024).
13	   Si faltan, agrega `--descargar` al comando del paso 2. Si el INEI no responde, pide al usuario bajarlos desde el
14	   navegador con los enlaces de `reference.md` y detente.
15	2. Corre exactamente, desde la raíz del proyecto:
16	   `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio 2024`
17	3. Lee `salidas/validacion.txt`. Si dice `ESTADO: DETENIDO` o el comando terminó con error, **detente** y muestra
18	   las verificaciones fallidas. No ajustes nada para que coincida con la referencia.
19	4. Responde con las cifras de `salidas/indicadores.csv` (una fila por indicador y grupo, columna `valor_pct`) o
20	   calcula sobre `salidas/hogares_2024.parquet` / `salidas/personas_2024.parquet` siempre con su factor:
21	   - pobreza nacional, por área, región o departamento: hogares con `factor_personas` (= factor07 × mieperho),
22	     el método del INEI;
23	   - pobreza por sexo, edad u otra característica individual: personas con `facpob07`.
24	   Nunca uses un promedio simple. En `reference.md` hay un ejemplo de cálculo ponderado.
25	5. En cada cifra di la fuente y el método: «INEI, ENAHO 2024, ponderado con factor07 × mieperho». Si el grupo tiene
26	   menos de 300 casos en `n_muestral`, adviértelo: la estimación es poco precisa.
27	6. Antes de usar una variable que no esté en las bases, lee `reference.md`.
28	
29	Salidas: `salidas/validacion.txt`, `salidas/indicadores.csv`, `salidas/hogares_2024.parquet` y
30	`salidas/personas_2024.parquet` (los parquet no se suben a git: se regeneran con este paso).
31	
```

</details>

### Llamada a `Grep`

```json
{
 "pattern": "residente|P204|P205|P206|RESIDENTE",
 "path": "C:\\Users\\Lory\\AppData\\Local\\Temp\\tarea4_evaluacion\\con_enaho_residentes\\.claude\\skills\\limpiando-enaho",
 "output_mode": "content",
 "-i": true
}
```

<details><summary>Resultado</summary>

```text
.claude\skills\limpiando-enaho\SKILL.md:9:Lo que no se discute (llaves, filtro de residentes, unión, ponderación, validación) está en `scripts/limpiar.py`.
.claude\skills\limpiando-enaho\reference.md:27:| `p204` | 02 | ¿Es miembro del hogar? | 1 sí, 2 no |
.claude\skills\limpiando-enaho\reference.md:28:| `p205` | 02 | ¿Estuvo ausente más de 30 días? | 1 sí, 2 no |
.claude\skills\limpiando-enaho\reference.md:29:| `p206` | 02 | ¿Estuvo presente más de 30 días? (no miembros) | 1 sí, 2 no |
.claude\skills\limpiando-enaho\reference.md:40:| residente habitual | `((p204 == 1) & (p205 == 2)) \| ((p204 == 2) & (p206 == 1))` → 108,664 personas |
.claude\skills\limpiando-enaho\reference.md:52:2. **Personas** (`facpob07`, solo residentes habituales): da 27.53 %. Sirve para características individuales como
.claude\skills\limpiando-enaho\reference.md:54:   `mieperho` no cuenta exactamente a los mismos residentes.
.claude\skills\limpiando-enaho\reference.md:76:| Residentes habituales | 108,664 de 117,721 | sesión 16 |
.claude\skills\limpiando-enaho\scripts\limpiar.py:9:  3. Filtrar residentes habituales: (p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1).
.claude\skills\limpiando-enaho\scripts\limpiar.py:40:    "residentes": 108_664,
.claude\skills\limpiando-enaho\scripts\limpiar.py:61:COLUMNAS_PERSONAS = LLAVES + ["codperso", "p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]
.claude\skills\limpiando-enaho\scripts\limpiar.py:120:def residentes_habituales(p):
.claude\skills\limpiando-enaho\scripts\limpiar.py:121:    return ((p.p204 == 1) & (p.p205 == 2)) | ((p.p204 == 2) & (p.p206 == 1))
.claude\skills\limpiando-enaho\scripts\limpiar.py:138:    p = p[residentes_habituales(p)].copy()
.claude\skills\limpiando-enaho\scripts\limpiar.py:139:    n_residentes = len(p)
.claude\skills\limpiando-enaho\scripts\limpiar.py:146:    return personas, n_residentes
.claude\skills\limpiando-enaho\scripts\limpiar.py:194:def validar(sumaria, modulo02, hogares, personas, n_residentes, ind):
.claude\skills\limpiando-enaho\scripts\limpiar.py:218:    chequear(True, "Residentes habituales", n_residentes == REFERENCIA["residentes"],
.claude\skills\limpiando-enaho\scripts\limpiar.py:219:             f"{n_residentes:,} (referencia {REFERENCIA['residentes']:,}) con "
.claude\skills\limpiando-enaho\scripts\limpiar.py:220:             "(p204==1 & p205==2) | (p204==2 & p206==1)")
.claude\skills\limpiando-enaho\scripts\limpiar.py:223:             len(personas) == n_residentes and sin_hogar == 0,
.claude\skills\limpiando-enaho\scripts\limpiar.py:301:    personas, n_residentes = construir_personas(modulo02, hogares)
.claude\skills\limpiando-enaho\scripts\limpiar.py:303:    chequeos = validar(sumaria, modulo02, hogares, personas, n_residentes, ind)
```

</details>

### Llamada a `PowerShell`

```json
{
 "command": "uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024; Get-Content salidas/validacion.txt",
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
ValidaciÃ³n de la ENAHO 2024 Â· limpiando-enaho Â· 2026-11-08 00:10
Archivos: 966-Modulo34/sumaria-2024.dta, 966-Modulo02/enaho01-2024-200.dta

[APROBADA] (esencial) Hogares en la sumaria: 33,691 (referencia 33,691)
[APROBADA] (esencial) Llaves de hogar Ãºnicas en la sumaria: 0 duplicados de conglome+vivienda+hogar
[APROBADA] (esencial) Filas del mÃ³dulo 02: 117,721 (referencia 117,721)
[APROBADA] (esencial) Llaves de persona Ãºnicas en el mÃ³dulo 02: 0 duplicados de conglome+vivienda+hogar+codperso
[APROBADA] (esencial) Llaves con ceros iniciales (texto): conglome '015009', ubigeo '010101'
[APROBADA] (esencial) Residentes habituales: 108,664 (referencia 108,664) con (p204==1 & p205==2) | (p204==2 & p206==1)
[APROBADA] (esencial) UniÃ³n m:1 sin perder ni duplicar personas: 108,664 filas despuÃ©s de unir, 0 personas sin hogar en la sumaria
[APROBADA] (esencial) 25 cÃ³digos territoriales (ubigeo[:2]): 25 cÃ³digos: 01â€“25
[APROBADA] (esencial) Factores de expansiÃ³n presentes y positivos: factor07 nulos: 0, facpob07 nulos: 0
[APROBADA] PoblaciÃ³n expandida: factor07 Ã— mieperho â‰ˆ suma de facpob07: 34,482,700 frente a 34,147,768 (+0.98 %)
[APROBADA] (esencial) Pobreza monetaria nacional (hogares, factor07 Ã— mieperho): 27.58 % (referencia 27.6 %, tolerancia Â±0.1 pp)
[APROBADA] (esencial) Pobreza monetaria nacional (personas, facpob07): 27.53 % (referencia 27.6 %, tolerancia Â±0.1 pp)
[APROBADA] El promedio simple NO coincide con la estimaciÃ³n ponderada (prueba de que se pondera): promedio simple sin factor: 25.61 % frente a 27.53 % ponderado
[APROBADA] (esencial) Pobreza extrema nacional: 5.50 % (referencia 5.5 %)
[APROBADA] (esencial) Pobreza urbana (estrato <= 5): 24.81 % (referencia 24.8 %)
[APROBADA] (esencial) Pobreza rural (estrato >= 6): 39.30 % (referencia 39.3 %)
[APROBADA] Pobreza de Lima Met
… [169 caracteres más en el .jsonl]
```

</details>

### Llamada a `StructuredOutput`

```json
{
 "valor": 108664,
 "unidad": "personas (casos muestrales sin ponderar)",
 "fuente": "INEI, ENAHO 2024, módulo 02 (enaho01-2024-200.dta, dentro de 966-Modulo02.zip). Conteo sin ponderar de las filas que cumplen el criterio de residente habitual, (p204==1 & p205==2) | (p204==2 & p206==1). Es el filtro que aplica .claude/skills/limpiando-enaho/scripts/limpiar.py, ejecutado en esta sesión. Está en salidas/validacion.txt: 108,664 de 117,721 filas del módulo 02, y 108,664 filas en salidas/personas_2024.parquet."
}
```

<details><summary>Resultado</summary>

```text
Structured output provided successfully
```

</details>

## Resultado final

- Turnos: 6
- Duración: 16.0 s
- Costo informado por Claude Code: US$ 0.07961979999999999

{"valor":108664,"unidad":"personas (casos muestrales sin ponderar)","fuente":"INEI, ENAHO 2024, módulo 02 (enaho01-2024-200.dta, dentro de 966-Modulo02.zip). Conteo sin ponderar de las filas que cumplen el criterio de residente habitual, (p204==1 & p205==2) | (p204==2 & p206==1). Es el filtro que aplica .claude/skills/limpiando-enaho/scripts/limpiar.py, ejecutado en esta sesión. Está en salidas/validacion.txt: 108,664 de 117,721 filas del módulo 02, y 108,664 filas en salidas/personas_2024.parquet."}
