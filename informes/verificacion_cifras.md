# Verificación de cifras del informe final

Siete afirmaciones numéricas de [`informe_final.md`](informe_final.md) comprobadas por un camino distinto al del agente:
las de la ENAHO se recalcularon leyendo `sumaria-2024.dta` directo del zip del INEI (sin las skills ni sus bases) y se
compararon con la cifra publicada; las del BCRP se pidieron a la API pública sin pasar por el MCP y se miraron en la
tabla web del BCRP. El recálculo está en [`verificar_cifras.py`](verificar_cifras.py) y su salida en
[`verificacion_cifras.csv`](verificacion_cifras.csv).

```bash
uv run informes/verificar_cifras.py
```

| # | Afirmación del informe | Valor del informe | Valor comprobado | Fuente o procedimiento | ¿Coincide? | Diferencia |
|---|---|---:|---:|---|:---:|---|
| 1 | Pobreza monetaria rural 2024 | 39.30 % | 39.3028 % (recálculo) · 39.3 % (INEI) | `sumaria-2024.dta`, `estrato >= 6`, ponderado con `factor07 × mieperho`; INEI, informe técnico de pobreza 2024 y validación de la sesión 16 | Sí | Redondeo (0.003 pp) |
| 2 | Pobreza monetaria urbana 2024 | 24.81 % | 24.8070 % · 24.8 % (INEI) | Igual, `estrato <= 5` | Sí | Redondeo |
| 3 | Cajamarca, el departamento con más pobreza | 45.01 % | 45.0069 % · 45.0 % (sesión 16) | Igual, `ubigeo[:2] == "06"`; `referencias/pobreza_departamento_2024.csv` de la sesión 16 | Sí | Redondeo |
| 4 | El 72.74 % de las personas pobres vive en zonas urbanas | 72.74 % | 72.7439 % | Pobres urbanos expandidos / total de pobres expandidos, recalculado de la sumaria | Sí | Redondeo |
| 5 | Inflación de alimentos y bebidas de Lima, promedio 2022 | 10.78 % | 10.7757 % (API) · 10.775 % (web) | PN09822PM: los 12 valores de 2022 de la [tabla web](https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN09822PM/html/2022-1/2024-12/) suman 129.30; ÷ 12 = 10.775 | Sí | Redondeo |
| 6 | Inflación de alimentos y bebidas de Lima a diciembre de 2024 | 1.25 % | 1.2481 % (API) · 1.25 % (web) | PN09822PM, Dic24 en la [tabla web](https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN09822PM/html/2022-1/2024-12/) | Sí | Ninguna |
| 7 | PBI agropecuario: +5.57 % en 2024 y −2.04 % en 2023 | 5.57 % / −2.04 % | 5.5725 % (API) · 5.6 % / −2.0 % (web) | El informe lo calculó como variación del índice promedio anual PN01755AM con `agregar_anual`; se contrastó con la serie anual oficial PM04968AA ([tabla web](https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales/resultados/PM04968AA/html/2019/2024/)) | Sí | La web muestra un decimal |

En la misma tabla web de PN09822PM se ven también el máximo del informe (13.16 % en Feb23) y el mínimo (0.69 % en
Sep24). Las tablas web se consultaron el 8 de noviembre de 2026.

## Diferencias y cómo se explican

- **Redondeo.** Todas las diferencias son menores a 0.005: el informe usa dos decimales, el INEI y la web del BCRP,
  uno.
- **Dos caminos para el PBI agropecuario.** El agente obtuvo +5.57 % de la serie mensual del índice (PN01755AM)
  llevada a promedio anual; el BCRP publica la variación anual oficial (PM04968AA) en 5.5725 %. Que coincidan es una
  prueba más de que `agregar_anual` agrega bien.
- **Pobreza nacional 27.58 % y 27.53 %.** No es un error: la primera pondera hogares con `factor07 × mieperho` (método
  del INEI) y la segunda personas con `facpob07`. Ambas están a menos de 0.1 pp del 27.6 % oficial
  (`salidas/validacion.txt`).
- **Restas hechas por el agente.** La brecha rural−urbana (14.49 pp) y Cajamarca−Ica (39.00 pp) son restas de
  cifras ya estimadas; el agente lo dijo en el informe. Con los valores recalculados: 39.3028 − 24.8070 = 14.4958 pp.

## Manejo de errores

En la ejecución integrada ninguna herramienta falló. Lo que hace el sistema cuando algo falla está probado aparte:

- El MCP devuelve un error claro, sin inventar un número, ante un código inexistente, una serie anual pasada a
  `agregar_anual`, una operación inválida o series de frecuencias distintas (`mcp/test_server.py`).
- `agregar_anual` marca los años incompletos (por ejemplo 2026, con datos hasta octubre) en `advertencias`.
- `limpiar.py` se detiene sin guardar la base si falla una validación esencial (`ESTADO: DETENIDO`), y `graficar.py`
  y `mapear.py` se niegan a correr sin la base limpia o sin los 25 departamentos.
