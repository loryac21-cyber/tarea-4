---
name: graficando-enaho
description: Hace gráficos de la pobreza monetaria o de la pobreza extrema de la ENAHO 2024 del INEI por área urbana y rural, región natural, sexo, grupo de edad o departamento, y de dónde viven las personas pobres, con estimaciones ponderadas, título analítico, unidad y fuente. Úsala cuando pidan graficar, visualizar o comparar en un gráfico la pobreza de la ENAHO (urbana frente a rural, hombres frente a mujeres, niños, departamentos).
argument-hint: "[area | region | sexo | edad | departamento | distribucion | todos]"
allowed-tools: Bash(uv run:*), Read, Glob
---
# Graficar la ENAHO

1. Si no existen `salidas/hogares_2024.parquet` y `salidas/personas_2024.parquet`, usa primero la skill
   `limpiando-enaho` y sigue solo si su validación terminó en `ESTADO: OK`.
2. Traduce el pedido a un `--tipo`:

   | Pedido | `--tipo` |
   |---|---|
   | urbano y rural, campo y ciudad | `area` |
   | costa, sierra, selva, Lima Metropolitana | `region` |
   | hombres y mujeres, género | `sexo` |
   | niños, jóvenes, adultos mayores, edad | `edad` |
   | departamentos, regiones del país, ranking | `departamento` |
   | dónde viven los pobres, cuántos pobres hay | `distribucion` |
   | varios o «todos los gráficos» | `todos` |

   Para pobreza extrema agrega `--indicador extrema`.
3. Corre desde la raíz del proyecto: `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --tipo <tipo>`
4. Abre el PNG con Read para revisar que se lea bien. Responde con la ruta (`figuras/...png`) y las cifras de la
   tabla que imprime el script (también queda en `figuras/...csv`). No redondees distinto ni inventes cifras.

## Reglas que cumple el script (y que debe cumplir cualquier gráfico nuevo)

| Regla | Cómo |
|---|---|
| Ponderado | Área, región y departamento con `factor07 × mieperho`; sexo y edad con `facpob07` |
| Barras desde cero, ordenadas | Un solo color; en rojo, lo que se quiere resaltar |
| El valor escrito en cada barra | Y la línea punteada del promedio nacional |
| Título analítico | Dice qué muestra y cuándo, con la cifra clave |
| Unidad | «% de personas» en el eje o el subtítulo |
| Fuente | Nota al pie: «Fuente: INEI, ENAHO 2024 (módulos 34 y 02). Estimación ponderada con …» |
| Archivo | PNG a 200 dpi en `figuras/` y un CSV con las cifras al lado |

Si piden un corte que el script no tiene, escribe un script nuevo en `scripts/` con estas mismas reglas.
No afirmes causas: un gráfico muestra diferencias, no por qué ocurren.
