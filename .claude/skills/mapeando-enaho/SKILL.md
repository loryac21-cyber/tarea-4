---
name: mapeando-enaho
description: Hace el mapa coroplético de la pobreza monetaria o la pobreza extrema por departamento del Perú con la ENAHO 2024 del INEI, uniendo por código ubigeo con el GeoJSON departamental del curso (25 unidades, Lima y Callao separados), y lo compara con la referencia oficial. Úsala cuando pidan un mapa de la pobreza, la pobreza por departamento o región en un mapa, o las diferencias territoriales de la ENAHO.
argument-hint: "[pobreza | extrema]"
allowed-tools: Bash(uv run:*), Read, Glob
---
# Mapear la ENAHO

1. Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho` y sigue solo si su
   validación terminó en `ESTADO: OK`.
2. Corre desde la raíz del proyecto: `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --indicador pobreza`
   (o `--indicador extrema`). Si falta el GeoJSON en `datos/geo/`, el script lo baja del repositorio del curso.
3. Si el script termina con error (menos de 25 departamentos con dato, Lima o Callao unidos), detente y explica el
   error. No unas por nombre para «arreglarlo».
4. Lee la línea «Comparación con la referencia de la sesión 16» y `salidas/comparacion_mapa_referencia.csv`:
   informa cuántos departamentos coinciden y la diferencia máxima.
5. Abre `mapas/<indicador>_departamento_2024.png` con Read para revisarlo y responde con la ruta, el departamento
   con más y con menos pobreza y la tabla `mapas/<indicador>_departamento_2024.csv`.

## Reglas

| Regla | Por qué |
|---|---|
| Unir `ubigeo[:2]` con `FIRST_IDDP`, ambos texto de dos dígitos, `validate="1:1"` | «APURIMAC» no es «Apurímac»; un código sin cero deja un departamento en blanco |
| Exigir 25 departamentos con dato | Un hueco en el mapa se lee como «sin pobreza» |
| Lima (15) y Callao (07) separados | Son departamentos distintos en el ubigeo y en el GeoJSON |
| Un color de claro a oscuro, desde 0, nunca arcoíris | La intensidad debe leerse como «más pobreza» |
| Leyenda con la unidad: «% de personas» | Para no confundir con % de hogares |
| Nota al pie con fuente, ponderación y llave de unión | Para que otra persona pueda reproducirlo |

Fuente de las geometrías: `peru_departamental_simple.geojson` de la sesión 06 del curso (campo `FIRST_IDDP`).
La referencia `referencias/pobreza_departamento_2024.csv` y el mapa `referencias/mapa_pobreza_2024_sesion16.png`
vienen de la sesión 16.
