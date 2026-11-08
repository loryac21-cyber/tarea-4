---
name: limpiando-enaho
description: Limpia, une y valida los módulos 34 (sumaria) y 02 (miembros del hogar) de la ENAHO 2024 del INEI y arma las bases de hogares y personas con pobreza monetaria, pobreza extrema, departamento, área urbana/rural, sexo, edad y factores de expansión. Úsala cuando pidan limpiar, unir, validar o analizar la ENAHO o los microdatos del INEI, o calcular la pobreza (nacional, urbana, rural, por departamento, región, sexo o edad), y antes de graficar o mapear la ENAHO si no existe salidas/personas_2024.parquet.
argument-hint: "[año, por defecto 2024]"
allowed-tools: Bash(uv run:*), Read, Glob
---
# Limpiar la ENAHO

Lo que no se discute (llaves, filtro de residentes, unión, ponderación, validación) está en `scripts/limpiar.py`.
Córrelo tal cual: no reescribas el pipeline ni corrijas cifras a mano.

1. Revisa que existan `datos/enaho/966-Modulo34.zip` y `datos/enaho/966-Modulo02.zip` (966 = ENAHO 2024).
   Si faltan, agrega `--descargar` al comando del paso 2. Si el INEI no responde, pide al usuario bajarlos desde el
   navegador con los enlaces de `reference.md` y detente.
2. Corre exactamente, desde la raíz del proyecto:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio 2024`
3. Lee `salidas/validacion.txt`. Si dice `ESTADO: DETENIDO` o el comando terminó con error, **detente** y muestra
   las verificaciones fallidas. No ajustes nada para que coincida con la referencia.
4. Responde con las cifras de `salidas/indicadores.csv` (una fila por indicador y grupo, columna `valor_pct`) o
   calcula sobre `salidas/hogares_2024.parquet` / `salidas/personas_2024.parquet` siempre con su factor:
   - pobreza nacional, por área, región o departamento: hogares con `factor_personas` (= factor07 × mieperho),
     el método del INEI;
   - pobreza por sexo, edad u otra característica individual: personas con `facpob07`.
   Nunca uses un promedio simple. En `reference.md` hay un ejemplo de cálculo ponderado.
5. En cada cifra di la fuente y el método: «INEI, ENAHO 2024, ponderado con factor07 × mieperho». Si el grupo tiene
   menos de 300 casos en `n_muestral`, adviértelo: la estimación es poco precisa.
6. Antes de usar una variable que no esté en las bases, lee `reference.md`.

Salidas: `salidas/validacion.txt`, `salidas/indicadores.csv`, `salidas/hogares_2024.parquet` y
`salidas/personas_2024.parquet` (los parquet no se suben a git: se regeneran con este paso).
