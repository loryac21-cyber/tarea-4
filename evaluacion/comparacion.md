# ¿Mejoran el MCP y las Skills las respuestas de Claude Code?

Las mismas 10 preguntas ([`preguntas.csv`](preguntas.csv)) en dos configuraciones de Claude Code, cada pregunta en una
sesión nueva de `claude -p`. Resultados completos en [`resultados.csv`](resultados.csv); transcripción de cada
sesión en [`../evidencias_ia/evaluacion/principal/`](../evidencias_ia/evaluacion/principal/).

| | Modo A · sin MCP ni Skills | Modo B · con MCP y Skills |
|---|---|---|
| **Respuestas correctas** | **0 / 10** | **10 / 10** |
| Incorrectas | 0 | 0 |
| No contestadas («no sé», valor `null`) | 10 | 0 |
| Tiempo promedio por pregunta | 6.9 s | 24.7 s |
| Turnos promedio | 2.0 | 7.0 |
| Costo total informado por Claude Code | US$ 0.06 | US$ 0.72 |

## Diseño

**Preguntas.** 4 del BCRP (PBI agropecuario 2024, inflación de alimentos a diciembre de 2024, su promedio de 2022 y
exportaciones no tradicionales agropecuarias 2024), 4 de la ENAHO 2024 (pobreza rural, Cusco, pobreza extrema y
número de residentes habituales) y 2 que combinan ambas fuentes. Las respuestas esperadas se fijaron **antes** de
correr el experimento y no salen del agente: las del BCRP se comprobaron pidiendo cada serie directo a la API y
mirando la tabla web ([`verificar_verdades.py`](verificar_verdades.py), 6 de 6 coinciden); las de la ENAHO son las
cifras del INEI y de la tabla de validación de la sesión 16.

**Tolerancias**, definidas de antemano: 0.05 pp para tasas del BCRP, 20 millones de US$ para exportaciones, 0.1 pp
para tasas de la ENAHO, 0 para el número de residentes y 0.15 pp para la brecha rural−urbana.

**Preguntas combinadas.** Piden dos cifras (una del BCRP y una de la ENAHO) y una afirmación verdadera o falsa que
mide la coherencia de la interpretación: «¿permiten estos datos concluir que la inflación de alimentos causó la
pobreza rural?» (lo correcto es *no*) y «¿la brecha rural−urbana fue mayor a 10 puntos?» (lo correcto es *sí*). Se
califican como correctas solo si las dos cifras están dentro de su tolerancia **y** la afirmación es la correcta;
«parcial» si solo una parte está bien.

**Condiciones.** Mismo modelo (Sonnet, `claude-sonnet-5-5`), misma instrucción («si no puedes saber una cifra con
certeza, pon null: no estimes; di la fuente»), misma salida JSON validada con `--json-schema`, y sesiones
independientes (`--no-session-persistence`).

| | Modo A | Modo B |
|---|---|---|
| Herramientas habilitadas | Ninguna (`--tools ""`) | `PowerShell`, `Read`, `Glob`, `Grep`, `Skill` |
| Servidores MCP | Ninguno (`--strict-mcp-config`) | Solo `bcrp` (6 herramientas) |
| Permisos | — | `mcp__bcrp`, `Skill`, `PowerShell(uv run:*)`, `Read`, `Glob`, `Grep` |
| Carpeta de trabajo | Carpeta temporal vacía fuera del proyecto: no ve `CLAUDE.md`, skills, datos ni resultados | Una copia del proyecto **por pregunta**, sin `evaluacion/` (respuestas esperadas), `informes/`, `evidencias_ia/`, `salidas/`, `figuras/` ni `mapas/`: solo código y datos originales del INEI |

Que la copia del modo B no tenga `salidas/` obliga a calcular la ENAHO en la misma sesión con las skills, en vez de
leer un resultado previo (ver «Variante» abajo).

## Pregunta por pregunta

| Pregunta | Esperada | Modo A | Modo B | Herramientas del modo B |
|---|---|---|---|---|
| PBI agropecuario 2024 | 5.5725 % | no sabe | **5.57** | `buscar_series`, `resumen` |
| Inflación de alimentos, dic-2024 | 1.2481 % | no sabe | **1.25** | `buscar_series`, `serie` |
| Inflación de alimentos, promedio 2022 | 10.7757 % | no sabe | **10.78** | `buscar_series`, `agregar_anual` |
| Exportaciones no tradicionales agropecuarias 2024 | 11,096.16 | no sabe | **11,096.16** | `buscar_series`, `serie`, `agregar_anual` |
| Pobreza rural 2024 | 39.3 % | no sabe | **39.3** | `limpiando-enaho` → `limpiar.py` |
| Pobreza en Cusco | 18.5 % | no sabe | **18.54** | `limpiar.py` (leyó el `SKILL.md`) |
| Pobreza extrema nacional | 5.5 % | no sabe | **5.5** | `limpiando-enaho` → `limpiar.py` |
| Residentes habituales | 108,664 | no sabe | **108,664** | `limpiar.py` (leyó el `SKILL.md`) |
| Inflación de alimentos + pobreza rural + ¿causalidad? | 1.2481 · 39.3 · no | no sabe (afirmación correcta) | **1.25 · 39.3 · no** | `buscar_series`, `serie`, `limpiando-enaho` |
| PBI agropecuario + brecha rural−urbana + ¿> 10 pp? | 5.5725 · 14.5 · sí | no sabe | **5.57 · 14.5 · sí** | `buscar_series`, `serie`, `limpiando-enaho` |

**Mejoraron las 10 preguntas** (de «no sé» a la cifra correcta con su fuente); **ninguna empeoró**. Las dos
preguntas combinadas usaron 2 herramientas MCP y una skill en la misma sesión.

**Tiempo por tipo (modo B):** 17.5 s en las del BCRP, 28.3 s en las de la ENAHO (incluye correr la limpieza
completa desde los zip del INEI) y 32.2 s en las combinadas. El modo A tarda unos 7 s porque solo responde.

## Principales errores y observaciones

1. **Sin herramientas, el modelo no tiene las cifras.** En el modo A dijo «no sé» en las 10 y explicó dónde habría
   que buscarlas (BCRPData, el informe técnico del INEI). Es la conducta correcta, pero no responde nada. En las
   combinadas acertó la interpretación causal («no se puede concluir causalidad») aunque no tenía los números: el
   razonamiento no era lo que faltaba, los datos sí.
2. **Si se le quita la salida «no sé», inventa** (experimento extra, abajo).
3. **Atajo con resultados previos.** En la primera corrida, el modo B tenía `salidas/` ya calculadas y respondió la
   ENAHO leyendo `salidas/indicadores.csv` sin activar ninguna skill (también 10/10). Es un uso válido del sistema,
   pero no mide las skills, así que se repitió desde datos crudos. Se conserva como variante.
4. **Skill sin la herramienta Skill.** En 2 de las 6 preguntas con ENAHO el agente leyó el `SKILL.md` con `Read` y
   corrió `limpiar.py` directamente, en vez de activar la skill con la herramienta `Skill`. El pipeline y el
   resultado son los mismos (`scripts_de_skills` en `resultados.csv`), pero la activación automática no es
   perfecta: depende de cómo el modelo explore la carpeta.
5. **Redondeo.** El modo B a veces redondea (1.25 frente a 1.2481; 18.54 frente a 18.5): todo dentro de la
   tolerancia fijada antes.

## Variante y experimento extra

| Corrida | Modo | Correctas | Incorrectas | Parciales | No sabe | Segundos |
|---|---|---:|---:|---:|---:|---:|
| Principal ([`resultados.csv`](resultados.csv)) | A · sin | 0 | 0 | 0 | 10 | 6.9 |
| | B · con, desde datos crudos | **10** | 0 | 0 | 0 | 24.7 |
| Variante con salidas previas ([`resultados_con_salidas_previas.csv`](resultados_con_salidas_previas.csv)) | A · sin | 0 | 0 | 0 | 10 | 7.4 |
| | B · con `salidas/` ya calculadas | **10** | 0 | 0 | 0 | 19.7 |
| **Sin salida «no sé»** ([`resultados_sin_null.csv`](resultados_sin_null.csv)) | A · sin, instrucción sin «pon null» | 0 | **3** | 2 | 5 | 9.0 |

**Sin salida fácil.** Se repitió el modo A quitando de la instrucción «si no puedes saber una cifra con certeza, pon
null: no estimes». El modelo **inventó 5 cifras**: PBI agropecuario 2024 = 3.6 % (es 5.57 %), pobreza rural = 39.8 %
(es 39.3 %), pobreza extrema = 5.7 % (es 5.5 %), y en las combinadas 39.8 % y 4.2 %. Todas venían con una cita
creíble («INEI, informe técnico Evolución de la pobreza monetaria 2014-2024», «Memoria 2024 del BCRP»), aunque el
propio modelo aclaraba que eran «de memoria, sin verificar». Son errores de pocas décimas, justo los que pasan
inadvertidos en un informe. Con el MCP y las skills, las mismas preguntas devolvieron la cifra exacta con su código
de serie o su archivo.

## Conclusión

El MCP y las skills convierten a Claude Code de un modelo que **no sabe** (o que, si se lo presiona, **inventa con
apariencia oficial**) en un sistema que responde 10 de 10 con la cifra exacta, el código de la serie o el archivo
de donde salió, y que hace las cuentas en Python (promedios anuales con `agregar_anual`, pobreza ponderada con
`factor07 × mieperho`). El costo es tiempo y dinero: unas 3.6 veces más segundos (24.7 frente a 6.9) y unas 13 veces
más costo por pregunta, sobre todo en la ENAHO, que se recalcula desde los microdatos. Para cifras que tienen que
ser verificables (un informe, una política pública), vale la pena; para una idea general, el modelo solo puede
orientar sobre dónde buscar, pero no sustituye la consulta.
