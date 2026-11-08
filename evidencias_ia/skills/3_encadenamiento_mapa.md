# Skills · 3_encadenamiento_mapa

## Pedido

```text
Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.
```

## Configuración de la sesión

- Modelo: `claude-sonnet-5-5`
- Herramientas disponibles: `Glob`, `Grep`, `PowerShell`, `Read`, `Skill`
- Servidores MCP: 
- Skills: `developing-with-streamlit`, `graficando-enaho`, `limpiando-enaho`, `mapeando-enaho`, `design`, `design-sync`, `dataviz`, `update-config`, `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`, `claude-api`, `run`, `run-skill-generator`, `plugin-authoring`, `anthropic-skills:built-in-browser`, `anthropic-skills:chrome-browser`, `anthropic-skills:computer-use`, `anthropic-skills:deep-research`, `anthropic-skills:docs`, `anthropic-skills:docx`, `anthropic-skills:google-workspace`, `anthropic-skills:import-memory`, `anthropic-skills:morning`, `anthropic-skills:pdf`, `anthropic-skills:pptx`, `anthropic-skills:skill-creator`, `anthropic-skills:xlsx`

### Llamada a `Skill`

```json
{
 "skill": "mapeando-enaho"
}
```

<details><summary>Resultado</summary>

```text
Launching skill: mapeando-enaho
```

</details>

### Llamada a `Glob`

```json
{
 "pattern": "salidas/*"
}
```

<details><summary>Resultado</summary>

```text
salidas\comparacion_mapa_referencia.csv
salidas\validacion.txt
salidas\indicadores.csv
```

</details>

### Agente

No existe `salidas/hogares_2024.parquet`, así que primero uso la skill de limpieza.

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

### Llamada a `Glob`

```json
{
 "pattern": "datos/enaho/*"
}
```

<details><summary>Resultado</summary>

```text
datos\enaho\966-Modulo02.zip
datos\enaho\966-Modulo34.zip
```

</details>

### Agente

Los zips ya están, así que corro la limpieza.

### Llamada a `PowerShell`

```json
{
 "command": "uv run C:/Users/Lory/Documents/GitHub/tareas-python/tarea-4/.claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024",
 "description": "Run ENAHO cleaning pipeline",
 "timeout": 600000
}
```

### Llamada a `Read`

```json
{
 "file_path": "C:\\Users\\Lory\\Documents\\GitHub\\tareas-python\\tarea-4\\salidas\\validacion.txt"
}
```

<details><summary>Resultado</summary>

```text
Validación de la ENAHO 2024 · limpiando-enaho · 2026-11-08 00:07
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

<details><summary>Resultado</summary>

```text
1	Validación de la ENAHO 2024 · limpiando-enaho · 2026-11-08 00:07
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

### Agente

Validación en `ESTADO: OK`. Ahora el mapa.

### Llamada a `PowerShell`

```json
{
 "command": "uv run C:/Users/Lory/Documents/GitHub/tareas-python/tarea-4/.claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobreza",
 "description": "Generate poverty choropleth map",
 "timeout": 600000
}
```

<details><summary>Resultado</summary>

```text
Comparación con la referencia de la sesión 16: 25 de 25 departamentos coinciden (±0.1 pp); diferencia máxima 0.049 pp.
Guardé mapas/pobreza_departamento_2024.png con 25 departamentos con dato (unión por código, validate='1:1').
departamento nombre_departamento  valor_pct
          06           Cajamarca  45.009998
          16              Loreto  42.970001
          21                Puno  39.939999
          19               Pasco  38.970001
          10             Huánuco  38.959999
          07              Callao  33.860001
          09        Huancavelica  33.400002
          05            Ayacucho  32.759998
          20               Piura  31.860001
          13         La Libertad  30.190001
          25             Ucayali  27.070000
          15                Lima  27.070000
          24              Tumbes  26.900000
          01            Amazonas  25.750000
          23               Tacna  23.990000
          03            Apurímac  23.959999
          02              Áncash  22.770000
          22          San Martín  22.020000
          08               Cusco  18.540001
          12               Junín  18.500000
          04            Arequipa  15.780000
          14          Lambayeque  14.040000
          17       Madre de Dios  11.150000
          18            Moquegua  10.970000
          11                 Ica   6.010000
```

</details>

### Llamada a `Read`

```json
{
 "file_path": "C:\\Users\\Lory\\Documents\\GitHub\\tareas-python\\tarea-4\\mapas\\pobreza_departamento_2024.png"
}
```

<details><summary>Resultado</summary>

```text
{"type": "image", "source": {"type": "base64", "data": "iVBORw0KGgoAAAANSUhEUgAABaAAAAcwCAYAAAAiWeOiAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjExLjIsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvgI3uAAAAAAlwSFlzAAAewgAAHsIBbtB1PgABAABJREFUeJzs3QecE9X2wPGTsksHQbqAoCggKkWsiIoNe+/12Z/Yn/XZe+9ir8+KFZUmiEgREKQjvffeYWuS+X/O4Ow/LEk2yWYyk+T3/Xz2w7JpNzd3JjNnzj3XYxiGIQAAAAAAAAAApJg31U8IAAAAAAAAAAABaAAAAAAAAACAbciABgAAAAAAAADYggA0AAAAAAAAAMAWBKABAAAAAAAAALYgAA0AAAAAAAAAsAUBaAAAAAAAAACALQhAAwAAAAAAAABsQQAaAAAAAAAAAGALAtAAAAAAAAAAAFsQgAYAAAAAAAAA2IIANAAAAAAAAADAFgSgAQAAAAAAAAC2IAANAAAAAAAAALAFAWgAAAAAAAAAgC0IQAMAAAAAAAAAbEEAGgAAAAAAAABgCwLQAAAAAAAAAABbEIAGAAAAAAAAANiCADQAAAAAAAAAwBYEoAEAAAAAAAAAtiAADQAAAAAAAACwBQFoAAAAAAAAAIAtCEADAAAAAAAAAGxBABoAAAAAAAAAYAsC0AAAAAAAAAAAWxCABgAAAAAAAADYggA0AAAAAAAAAMAWBKABAAAAAAAAALYgAA0AAAAAAAAAsAUBaAAAAAAAAACALQhAAwAAAAAAAABsQQAaAAAAAAAAAGALAtAAAAAAAAAAAFsQgAYAAAAAAAAA2IIANAAAAAAAAADAFn57nhaJ6Nmzp0ydOnWXv1955ZVy3XXX0ZkAHMd+CpUxcOBAeeqpp3b5e/Xq1WXw4MF0LgAAAABksYwNQH/66afy3nvvxXVfj8cjNWvWlDp16kjz5s3loIMOkmOOOUYaN24sbqDB51GjRu3yd20jALgB+ylUxurVqyN+z9WoUYOOBZARQqGQTJw40fz5+++/ZcWKFbJ582YxDMM8x2jSpIl07NjRPH5v3bp1pV5r27Zt8uuvv8qIESNk1apVsnbtWvOCXaNGjaRt27Zy6qmnmv+6/X2EKykpkYsvvtj8PoikWbNm0rt375S9HgAAcJeMDUAvWbIk4slsvPx+v5xyyiny5JNPygEHHJDStgHIDfPmzZN//etfEW/7+eefpV69emlvEwAkg/0ZGAO7CgaD5iyNzz77zPx3/fr1cQ2UI4880jzHOProoxMaWBoIfuKJJ6RXr15SXFwc9X533XWXmVDz6quvmq/ltvcRySOPPCI//PBD1Nv33nvvSr8GAABwr4wNQFdWIBAwA0Q6LfjZZ5+V//znP043CUCG0QylaBfCNNMHADIF+zMwBnZ1yCGHmJnCifrjjz/MDGINFL/wwgtxPWbatGnSo0cPWblyZVz3nzBhgnTr1k3uu+8+eeaZZ1zzPiIZM2ZMpR4PAAAyX84vQlhaWip33nmnmWkAAAAAACreTOFoXnzxRXnooYfiKnOlgd54g8/hNJHmjjvucMX7iKSgoMBc10azsAEAQO7K2Qzo8u655x4544wzpEWLFk43BQBc5+233zanBpfHPhMAgNgB4osuukjat28fNRnm8ssvlw0bNiTdjVqK4/jjjzdrQzv1PqK5++67Ze7cuba1CwAAZIasDEDrVfpDDz207P+bNm0y69q9//77MmPGjIiPKSwslNdee01eeumlNLYUADIDtfIBALlOFzM/66yz5OCDD5amTZvK1q1bZeTIkfLhhx9GvEhrlf376KOPop5jvPzyy2YGdLSF+bRMoH4H6/mMLtL3/fffR7zvDTfcIPPnz5cqVao48j4i0YUU9QJ2OF0YXsu9AACA3JKVAWi9Mh9pQY5bb71VrrnmGvnkk08iPq5fv34VHlTpCtFac01rommtNp3SpgdqejClC461adPGfO3DDjtM8vPzU/ae1q1bJz/99JOMHj3anJ6nK1jrQelxxx0np59+uvn6FenZs2fEA1ydFnfdddeZv+vzDhgwQAYNGiSLFy+WjRs3mhmOX3zxRcznnjJlinngOnny5J36pEGDBtK5c2eznfGs1q1TCP/66y+pjNtuu03OP//8iJ/dwoULzT7QVb+XLVtmrsS9fft2c6GXatWqSa1atWSPPfYwD/T1c9TP0y5XXXVVxIyQ8M9DP4OvvvrK7F9dAb1x48ay//77mwvf6e+RTg769u1rLjCjj9X3bI2Ts88+O66TknSM+XjGop4M9e/fX4YOHSrLly83M4R0ZXatd3jeeefJbrvtJsmo7FgdNmyYPPjgg+bvOnaiOfPMMyUvL2+Xv+sJn9ZSTNfYTNV2H8/zuH2bi+c9pGJf65ZtKNn9eSJ0u9QAg76OvoZ+rrpv0sWxzjnnHDPIkUqp+q5J93hw6zaut2fS/ixTvjedGKvJfmfa8Z3mhuPmVNNA7QMPPGDOlvR4PLv0gR576meqCS+R/P777xH/rtvmm2++GfE2/fzGjx8vjRo1KvubfpY6azNSPWX93Pv06WNmKaf7fUSiAfOrr77aHAOWAw880FzQ8I033oj7eQAAQJYwMtQTTzyhRzMRfwYOHBj1cevWrTN8Pl/Ex3m9XiMYDEZ8nP79vffeM9q0aRP1dcN/mjRpYjz11FNGQUFBhe+la9euEZ/jgQceMEpKSownn3zSqFatWtTXatiwofHll19W6nXU6NGjjdatW+9yu77nSEKhkPHpp58aBxxwQFx9cuyxx5qvEctxxx0X13PF+nnllVd2ed7XXnvNqFWrVsLP1aVLF2PQoEGGHTp06BD189Bx85///Mcck5Huk5eXZzz22GPmZ2D57bffjObNm0d9L61atTJGjRoVd/ucGvP6um+99ZZRt27dqK+1++67G99++23c7yWVY1VftzLj84Ybbkjr2EzVdl/R82TCNpeufa3T21Ay+/NkjBgxwmjbtm3U96PftbfeequxZcsW4+OPP454nxo1alT4OnZ816RzPLh5G8+0/ZnbvzedGKuV/c5M9RhIx/4vnXRsfvLJJ3Hdd9iwYVHfX6NGjSI+Rs9Zoj3m9ddfj/gY7aM6depEfMzxxx/vyPuI5NJLL93psVWqVDGmTZtm3HnnnRGfe++99477uQEAQObJuQC0atasWdTHrl27dpf7r1y50ujevXtSB+bt27c3pk+fntSJxV133WWceuqpcb/W008/nfQJjB5sRjvR3nfffXd5Lu2nU045JeH+0IDEc889l/YA9L333lup57z//vuNVIt2Iq0n0Mccc0xc7brpppvM53r77bejnnSXD/ZMmjSpwrY5Nebvvvtu48ILL4zrdfT99unTp8L3kuqxmuqTdbvHZqq2+0QD0G7c5tK1r3VyG0pmf56M77//3gzoxfN+OnfubLz00ktJBaDt+q5J53hw8zaeafszN39vOjFWU/GdaUcA2u79Xzpt27YtofvvtttuEd9XgwYNIt7/nnvuidoXS5Ysifo6559/fsTHVK1a1SgtLU37+yjvu+++2+WxL7/8snkbAWgAAHJTzgWgNSOjdu3aUR+7ffv2ne6/ceNGo127dpU6OK9fv74xf/78hE8sNFMg0df65ptvEn6d6667zjygjPac5QMWms3WsWPHSvWJZpZlUgBafzSrKZWinUjn5+cn1K777rsvalZ/tGBQLJk05jUTJ9ZJlR1j1W0Bm4rGZqq2+3QHoCt6X8lI177WyW0o0c81GZMnT447+FxRH8cKQNv5XZPO8eDmbTzT9mdu/d7MlLEa6Tsz1WMgHfs/N9M+jvSeDjvssIj31yz4aFnrseiFr2j9F88Fk1S/j3CrVq0yP8Pwx+n7tGYfEIAGACA3ZWUN6Fi0Pt6WLVsi3lanTh2pXr36LvX1Zs6cWanX1BqS
… [314146 caracteres más en el .jsonl]
```

</details>

### Agente

El mapa de pobreza monetaria por departamento con la ENAHO 2024 está listo: `mapas/pobreza_departamento_2024.png`.

La tabla de datos quedó en `mapas/pobreza_departamento_2024.csv`. Primero corrí `limpiando-enaho` porque faltaba `salidas/hogares_2024.parquet`. Su validación dio `ESTADO: OK` (17 de 17 verificaciones).

- **Unión:** los 25 departamentos tienen dato. La unión fue por código (`ubigeo[:2]` con `FIRST_IDDP`, `validate='1:1'`), con Lima y Callao separados.
- **Comparación con la referencia de la sesión 16:** coinciden los 25 de 25 departamentos (±0.1 pp). La diferencia máxima es 0.049 pp.
- **Más pobreza:** Cajamarca, con 45.0 % de personas.
- **Menos pobreza:** Ica, con 6.0 %.
- **Siguientes en pobreza:** Loreto (43.0 %), Puno (39.9 %), Pasco (39.0 %) y Huánuco (39.0 %).
- **Lima y Callao:** Lima tiene 27.1 % y Callao 33.9 %.
- **Mapa:** usa una sola escala de color, de claro a oscuro desde 0, con la leyenda «% de personas». Revisé la imagen y la leyenda y la nota al pie se leen bien.

**Fuente:** INEI, ENAHO 2024 (módulos 34 y 02), ponderada con factor07 × mieperho. Los límites son `peru_departamental_simple.geojson` del curso. Las cifras salen de `mapas/pobreza_departamento_2024.csv`.

## Resultado final

- Turnos: 11
- Duración: 31.2 s
- Costo informado por Claude Code: US$ 0.09832490000000002

El mapa de pobreza monetaria por departamento con la ENAHO 2024 está listo: `mapas/pobreza_departamento_2024.png`.

La tabla de datos quedó en `mapas/pobreza_departamento_2024.csv`. Primero corrí `limpiando-enaho` porque faltaba `salidas/hogares_2024.parquet`. Su validación dio `ESTADO: OK` (17 de 17 verificaciones).

- **Unión:** los 25 departamentos tienen dato. La unión fue por código (`ubigeo[:2]` con `FIRST_IDDP`, `validate='1:1'`), con Lima y Callao separados.
- **Comparación con la referencia de la sesión 16:** coinciden los 25 de 25 departamentos (±0.1 pp). La diferencia máxima es 0.049 pp.
- **Más pobreza:** Cajamarca, con 45.0 % de personas.
- **Menos pobreza:** Ica, con 6.0 %.
- **Siguientes en pobreza:** Loreto (43.0 %), Puno (39.9 %), Pasco (39.0 %) y Huánuco (39.0 %).
- **Lima y Callao:** Lima tiene 27.1 % y Callao 33.9 %.
- **Mapa:** usa una sola escala de color, de claro a oscuro desde 0, con la leyenda «% de personas». Revisé la imagen y la leyenda y la nota al pie se leen bien.

**Fuente:** INEI, ENAHO 2024 (módulos 34 y 02), ponderada con factor07 × mieperho. Los límites son `peru_departamental_simple.geojson` del curso. Las cifras salen de `mapas/pobreza_departamento_2024.csv`.
