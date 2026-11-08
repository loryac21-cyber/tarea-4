# Referencia de la ENAHO 2024 para `limpiando-enaho`

## Archivos

| Módulo | Archivo en el zip | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|---|
| [34 · Sumaria](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip) | `sumaria-2024.dta` (no `sumaria-2024-12g.dta`) | hogar | 33,691 | `conglome`, `vivienda`, `hogar` | `factor07` |
| [02 · Miembros del hogar](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip) | `enaho01-2024-200.dta` | persona | 117,721 | las tres + `codperso` | `facpob07` |

`966` es el código de la ENAHO 2024 (anual) en el portal de microdatos del INEI. Los zip van en `datos/enaho/`, que
git ignora.

## Variables que usa el pipeline

| Variable | Módulo | Qué es | Códigos |
|---|---|---|---|
| `conglome`, `vivienda`, `hogar`, `codperso` | 34 y 02 | Llaves. Texto con ceros: `015009`, `013`, `11`, `01` | — |
| `ubigeo` | 34 y 02 | Departamento, provincia y distrito. `ubigeo[:2]` = departamento | `01` Amazonas … `07` Callao … `15` Lima … `25` Ucayali |
| `dominio` | 34 | Dominio geográfico | 1-3 costa norte/centro/sur, 4-6 sierra norte/centro/sur, 7 selva, 8 Lima Metropolitana |
| `estrato` | 34 | Estrato de la muestra | 1-5 urbano, 6-8 rural |
| `mieperho` | 34 | Miembros del hogar (sin trabajadores del hogar ni pensionistas) | — |
| `pobreza` | 34 | Condición de pobreza del hogar | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
| `linea`, `linpe` | 34 | Línea de pobreza total y extrema, S/ por persona al mes | — |
| `gashog2d`, `inghog1d` | 34 | Gasto e ingreso del hogar, S/ al año | — |
| `factor07` | 34 | Factor de expansión del hogar | — |
| `p203` | 02 | Relación con el jefe del hogar | 1 jefe, 2 cónyuge, 3 hijo… |
| `p204` | 02 | ¿Es miembro del hogar? | 1 sí, 2 no |
| `p205` | 02 | ¿Estuvo ausente más de 30 días? | 1 sí, 2 no |
| `p206` | 02 | ¿Estuvo presente más de 30 días? (no miembros) | 1 sí, 2 no |
| `p207` | 02 | Sexo | 1 hombre, 2 mujer |
| `p208a` | 02 | Edad en años cumplidos | — |
| `facpob07` | 02 | Factor de expansión de la persona | — |

La columna del año llega como `aÑo` (a veces se lee `a�o`); el script la renombra `anio`.

## Variables construidas

| En la base | Regla |
|---|---|
| residente habitual | `((p204 == 1) & (p205 == 2)) \| ((p204 == 2) & (p206 == 1))` → 108,664 personas |
| `departamento` | `ubigeo[:2]` (texto de dos dígitos) |
| `area` | `Urbana` si `estrato <= 5`, si no `Rural` |
| `region_natural` | Costa (dominio 1-3), Sierra (4-6), Selva (7), Lima Metropolitana (8) |
| `pobre`, `pobre_extremo` | `pobreza <= 2`, `pobreza == 1` |
| `factor_personas` | `factor07 × mieperho`: expande cada hogar a sus miembros |
| `grupo_edad` | 0-14, 15-29, 30-44, 45-64, 65 y más |

## Dos maneras correctas de ponderar, y por qué dan 27.58 % y 27.53 %

1. **Hogares** (`sumaria`, `factor07 × mieperho`): es el método del INEI para la pobreza oficial. Da 27.58 %
   nacional, 24.81 % urbano y 39.30 % rural, y reproduce la pobreza por departamento de la referencia.
2. **Personas** (`facpob07`, solo residentes habituales): da 27.53 %. Sirve para características individuales como
   sexo o edad. La diferencia (0.05 pp) viene de que `facpob07` está calibrado a proyecciones de población y
   `mieperho` no cuenta exactamente a los mismos residentes.

Ambas quedan dentro de ±0.1 pp del 27.6 % oficial. El promedio simple sin factor da 25.6 %: por eso nunca se usa.

```python
import pandas as pd
h = pd.read_parquet("salidas/hogares_2024.parquet")
p = pd.read_parquet("salidas/personas_2024.parquet")
tasa = lambda d, ind, peso: (d[ind] * d[peso]).sum() / d[peso].sum() * 100
tasa(h, "pobre", "factor_personas")                      # 27.58, nacional
h.groupby("area").apply(lambda d: tasa(d, "pobre", "factor_personas"))
p[p.edad < 18].pipe(tasa, "pobre", "facpob07")           # niñas, niños y adolescentes
```

## Cifras de referencia (para comparar, nunca para copiar)

| Cifra | Valor | Fuente |
|---|---|---|
| Pobreza monetaria nacional | 27.6 % | INEI, informe técnico de pobreza 2024; sesión 16 |
| Pobreza extrema | 5.5 % | INEI; sesión 16 |
| Urbana / rural | 24.8 % / 39.3 % | sesión 16 |
| Lima Metropolitana (dominio 8) | 28.2 % | sesión 16 |
| Residentes habituales | 108,664 de 117,721 | sesión 16 |
| Hogares | 33,691 | sesión 16 |
| Por departamento | `.claude/skills/mapeando-enaho/referencias/pobreza_departamento_2024.csv` | sesión 16 |

## Trampas

- **Lima no es Lima Metropolitana.** El departamento 15 (Lima, 27.1 %) excluye al Callao (07) e incluye Lima
  provincias; Lima Metropolitana es el dominio 8 (28.2 %) y sí incluye al Callao.
- **Ceros iniciales.** Si una llave se lee como número, `015009` se vuelve `15009` y la unión falla.
- **Unidad de análisis.** La pobreza es del hogar; se expande a personas. No compares un % de hogares con un % de
  personas.
- **Asociación no es causa.** Que un grupo sea más pobre no dice por qué.
