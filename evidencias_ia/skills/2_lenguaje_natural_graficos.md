# Skills · 2_lenguaje_natural_graficos

## Pedido

```text
Grafica la pobreza monetaria de la ENAHO 2024 por sexo y por grupo de edad, y dime las cifras de cada grupo.
```

## Configuración de la sesión

- Modelo: `claude-sonnet-5-5`
- Herramientas disponibles: `Glob`, `Grep`, `PowerShell`, `Read`, `Skill`
- Servidores MCP: 
- Skills: `developing-with-streamlit`, `graficando-enaho`, `limpiando-enaho`, `mapeando-enaho`, `design`, `design-sync`, `dataviz`, `update-config`, `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`, `claude-api`, `run`, `run-skill-generator`, `plugin-authoring`, `anthropic-skills:built-in-browser`, `anthropic-skills:chrome-browser`, `anthropic-skills:computer-use`, `anthropic-skills:deep-research`, `anthropic-skills:docs`, `anthropic-skills:docx`, `anthropic-skills:google-workspace`, `anthropic-skills:import-memory`, `anthropic-skills:morning`, `anthropic-skills:pdf`, `anthropic-skills:pptx`, `anthropic-skills:skill-creator`, `anthropic-skills:xlsx`

### Llamada a `Skill`

```json
{
 "skill": "graficando-enaho"
}
```

<details><summary>Resultado</summary>

```text
Launching skill: graficando-enaho
```

</details>

### Llamada a `Glob`

```json
{
 "pattern": "salidas/*.parquet"
}
```

<details><summary>Resultado</summary>

```text
salidas\hogares_2024.parquet
salidas\personas_2024.parquet
```

</details>

### Agente

Las bases existen. Genero los gráficos de sexo y edad.

### Llamada a `PowerShell`

```json
{
 "command": "uv run C:/Users/Lory/Documents/GitHub/tareas-python/tarea-4/.claude/skills/graficando-enaho/scripts/graficar.py --tipo sexo; uv run C:/Users/Lory/Documents/GitHub/tareas-python/tarea-4/.claude/skills/graficando-enaho/scripts/graficar.py --tipo edad"
}
```

<details><summary>Resultado</summary>

```text
Guardé figuras/enaho_pobreza_sexo_2024.png y su tabla:
  sexo  valor_pct  poblacion_expandida  n_muestral
 Mujer      27.68           17694762.0       56077
Hombre      27.37           16453003.0       52587

Guardé figuras/enaho_pobreza_edad_2024.png y su tabla:
grupo_edad  valor_pct  poblacion_expandida  n_muestral
      0-14      37.52            7941994.0       26489
     15-29      25.97            7512400.0       23122
     30-44      27.87            6689119.0       20648
     45-64      21.15            7803731.0       24735
  65 y más      22.74            4200522.0       13670
```

</details>

### Llamada a `Read`

```json
{
 "file_path": "C:/Users/Lory/Documents/GitHub/tareas-python/tarea-4/figuras/enaho_pobreza_sexo_2024.png"
}
```

### Llamada a `Read`

```json
{
 "file_path": "C:/Users/Lory/Documents/GitHub/tareas-python/tarea-4/figuras/enaho_pobreza_edad_2024.png"
}
```

<details><summary>Resultado</summary>

```text
{"type": "image", "source": {"type": "base64", "data": "iVBORw0KGgoAAAANSUhEUgAABqQAAAOYCAYAAACzUJJJAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjExLjIsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvgI3uAAAAAAlwSFlzAAAewgAAHsIBbtB1PgABAABJREFUeJzs3QncTOX///HLvosihFAka0gbpagoRNpUUolKSPumTasWKSqKdqTSQgtJSFmyJJEoFaLImn13/x/v6/c/853lzNyznZm57/v1fDzmcc89c86Z6yxz5pzrc12fK19WVlaWAQAAAAAAAAAAADyS36sFAwAAAAAAAAAAAEJACgAAAAAAAAAAAJ4iIAUAAAAAAAAAAABPEZACAAAAAAAAAACApwhIAQAAAAAAAAAAwFMEpAAAAAAAAAAAAOApAlIAAAAAAAAAAADwFAEpAAAAAAAAAAAAeIqAFAAAAAAAAAAAADxFQAoAAAAAAAAAAACeIiAFAAAAAAAAAAAATxGQAgAAAAAAAAAAgKcISAEAAAAAAAAAAMBTBKQAAAAAAAAAAADgKQJSAAAAAAAAAAAA8BQBKQAAAAAAAAAAAHiKgBQAAAAAAAAAAAA8VdDbxQMAAAAAkDN98cUXZsqUKeboo482V1xxhalQoYLvva+++spMmDDB1KxZ0/Tp0yet5QS8NmDAALNq1Srf/40aNTI9e/ZkwwMAgJjky8rKyoptltzpjz/+MM8++2zI6+eee665+OKL01ImAJmPcweQt9x6661mz549Aa9VrFjR9O/fP21lyily6rbLqeVG5uMaIvO38fPPP29uv/123/8lSpQwDz74oLnzzjtNgQIFTNeuXc2oUaNM+/btzWeffZb08udWHPs5z7Bhw0yvXr18/zds2NAGasuVK2fyqr1795pp06aZhQsXmg0bNphdu3YZ/+q1U045xXTr1i2tZcyruHYDgDwWkLr55pvN/v37s52uYMGC5rDDDjPly5c3J5xwgjnppJNMyZIlTbrMmDHDnHHGGSGv33HHHWbgwIFpKROAzMe5A8hbdK2yc+fOgNdq165tli1blrYy5RQ5ddtlarnXrVtnFi9ebFurr1271mzdutUGzgoXLmyvsY899ljTpEkTU7du3YQ+R5+h3zp93pYtW0zZsmVNpUqVzJlnnmnq1KmTseV2aPn9+vUzBw8edH1/6NChJn/+9GQx5xois7exvvcKPu/YsSPkPZ0DGjRoYD766CNbAc09Y+r2C1JvwYIFplmzZjYAI/Xr1zdTp061dTl51auvvmp/WzZv3hx2mi5dutiANVIvU6/dAAAepewbMWKE70IlFsWKFTOXXXaZbXGmG1EAuY8qfRYtWhTy+nPPPWdbnAIAgPDmz59v7rnnHhvQUWvsaKgCpm/fvubGG2+0PTqioQp2VaI9/PDDZsWKFWGnO+6448xjjz1mr+EzodxulEYtUoXgSy+9lLaAFDI/aOIEo5SWrFChQua1114zu3fvNr/++qt9OC666KI0lhTwjoL6Osc7dTz16tXL88GoIUOGmFtuuSVXHnbcrwMA8tQYUrqwf/vtt83YsWPNK6+8YtMfAMhdlGNfefiDPf744wSkAADIxsqVK21FYCxUad67d28blPn888/N4YcfHnF6pRxS5fqkSZOyXfZvv/1mOnfubN577z0zZswYU6RIkbSV282HH35I63TE7c8//7R/NXaU0pU5aaB0XH755Ze+6RQ0Ve8RIDe67rrrbIpFUc/VvN4zatu2beaBBx4wuRX36wCAPBWQ8r8Jvvbaa23Kjg4dOqS7OAAAAECON3v2bHPBBReY7777LmyPoAMHDpi2bdua6dOnx7TsTz75xHTq1MkGjpLd2yiacrtROkD1agHipbSUb775ZkDl+zHHHGMmTpxox4xRr/8aNWq4pp4DcgONofbxxx/b50rRqmDUkUceafIyjRm1ffv2kNfVaOL666+3AWznt0q9iAEAQBoDUhr41UnFpzQgStehgV+VwiPYoUOH7ICZ55xzjilevHiqiggAMatZs6av1ay/Ro0asTUBAJ5SxZd6ZqiiUI251qxZYyvLfvjhB9fpZ82aZXsMXX311a7vP/PMM67BqNKlS9t5dC2/fPly884774SMq6NK+pdfftmOJ5vqcodr1b9p06aop0fulMh1mnqDhBvLTPNzrYfcTHUyOj87358LL7zQVKhQweR1Tm+xYE8++aTtLQkAADIoINWxY0dz+umnB7z20EMP2bzuunkN9vfff9vWlhoIEgAylQa7pgU2ACBVNOZit27dbHrrk08+OeR9Nfx64403zA033GArFIO9//77roGd9evXm0cffdR1YHD1UvKvmO/Ro4c57bTTQsaN1QDv11xzjQ1gparc4caF8k+pVrRoUTte7ZYtW6KaH7kH12lAfNTLR4F9BHLrHSWMgw4AQA5K2ff000+bjz76yKxbty7kvcmTJ2cbkNKNpW6Sf/75Z7N582ab8k8tedSVvGnTpubEE080hQsXTkpZddOt1p/6LPXwOuKII2zLuNatW9sb3exa0jz77LMhr5977rnm4osvts/V0lTj6ygf/7///mvTpjzyyCNhWyIpf/H3339v00WoBejOnTtNmTJlTOXKlU2LFi1sq9NI/vvvP3PvvfeaeKkiQpUOblSpsWDBAjsQ9j///GPLtm/fPtvjTZUUumA74YQTwrY6jNeyZcvMCy+8EHE765hRsFMtfFX5oVQbSg9ZqVKlkPkOHjxoKzR++uknu0+0fZs0aWKXF2vvvWQdq9EcSyr3119/bVsaq9ylSpWyA9C2adMmrjEYEjnWNC7clClT7HMNZh6uB6Xbd0iDqrql50nm8ZXodzOa+TPpOxJNeRM516X72I/1PBot7SOlotJ4Evv377fHfsuWLU3jxo1902hciT179oRUhPXv3z/p6/LNN9/YMVuC6Zysc3Mw7VO3wZd1XnDrzZCTj5NEqJeGcuf772f11m7YsGHSPiPR3+5MLYOX287L82Uq9nky6fv9119/Rfwtz5cvn+nevbv9Pr3++uuu10pu3nrrrZAAk+gcEbxtde5TaiIFfvzpvPXuu++GNNTwstxuY0/dc889Aa8NGDDAjlEbT0BK14BuPWzat29vH+nkxXlT37eZM2fa3x6dH7RMBSX13dAy9ShUqFDS1sHr69pYrtPScY2dG/ZhOuSG7ZaJ961e/d6m85hMxjrpWNN45+KW4UcGDx5sxy0MbqShHsGpvB7U7/iPP/5oz1Fad9X5aF11/3DUUUfZRuL6m5Pu19Nx7ZYbzjEAkNGykqxIkSJZWmzw47vvvgs7T4cOHVznOfPMM8POM2vWrKyOHTtm5c+f33Ve51G6dOms22+/PWvt2rURy63yuc1/xx132PdfffXVrDJlyrhOc8QRR2S9/vrrcS//4MGDWU899VRWsWLFQt5funRpyLIWLFiQ1blz56yCBQtGXPe6detmvfvuu2HLtHr16ojzZ/e45pprXPdllSpVol5GzZo1s1544YWsAwcOZCXD5MmTI27nJ554Iqto0aIh7xcqVCjr5ptvztq3b59vWR9//HHWUUcd5bq8I488MuuDDz6IqkypPlY//PDDsOUuWbJk1vPPPx/19kzGsXbLLbfEfYzt37/f8+Mr0e9mdvsj074jXp/r0nXsx3oejdaWLVuyrr/++rDrcNJJJ2X9/PPPdtoSJUqEvF+7dm1P1uXFF190nf/NN990/bzt27e7Tt+mTZuYy5fpx0k8Nm3alNWtW7esfPnyuX52s2bNfNs+lv3sxW93Irwog5fbzsvzZSr2ebq99957Ya9h3DRu3Nh1+jlz5rhO//XXX7tOf8YZZ6S03P503aDzsv98Z511VtahQ4fsPovmWiPYJ5984jrfww8/nJWoWK8hvDxv/vjjj1mtW7cO+51wHmXLls267rrr
… [89870 caracteres más en el .jsonl]
```

</details>

<details><summary>Resultado</summary>

```text
{"type": "image", "source": {"type": "base64", "data": "iVBORw0KGgoAAAANSUhEUgAABqQAAAOYCAYAAACzUJJJAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjExLjIsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvgI3uAAAAAAlwSFlzAAAewgAAHsIBbtB1PgAA6OZJREFUeJzs3QWYXNX5OP4TQRIIFoomaJDiENwCRYJLoUBxdy1QKkgpxYq7FtcWLVDcA7RIcIoWCRAIECQEQiDZ//Pe73/2Nzs7szu7O3d3Nvl8nmeenZ25d+ZcnXvPe857ejQ0NDQkAAAAAAAAyEnPvD4YAAAAAAAAgoAUAAAAAAAAuRKQAgAAAAAAIFcCUgAAAAAAAORKQAoAAAAAAIBcCUgBAAAAAACQKwEpAAAAAAAAciUgBQAAAAAAQK4EpAAAAAAAAMiVgBQAAAAAAAC5EpACAAAAAAAgVwJSAAAAAAAA5EpACgAAAAAAgFwJSAEAAAAAAJArASkAAAAAAAByJSAFAAAAAABArgSkAAAAAAAAyFXvfD+++/jqq6/Sv//972avzzvvvGmhhRbqkjIB9c+5A6B+PPDAA+mnn35q8tq0006bVl111ZqfvydMmJDeeuut9Nlnn6XvvvsuNTQ0NL43xxxzpCWWWKLdy0HnmBx+w9tyTAAAAOStR0Px3XMN3H///dkNemt69+6dpp9++vSzn/0szT333KlHjx6pKw0bNiytttpqzV4/9NBD06mnntolZQLqn3MH1K+4xPniiy/SyJEj09dff53GjRuXppxyyuz6Y7755kv9+vWryffE53/yySfpyy+/TDPOOGOaffbZ02yzzVb35a7m2m3o0KFdfo3WFlHRPnbs2CavRWDh9ddfr9n5+5133knHHHNMuvXWW7NAVDnbbbdduuaaa9q1DHSeyeE3vC3HRL2r9bm2Wv/5z3+y7yynV69eqW/fvtl5OQKZtT4/AwDApKbmPaQ23njj9MMPP7RpnhlmmCFrpbfbbrulTTbZJPXsKZMgTIqGDx+eRo0a1ez1tdZaK00xxRRdUiZg0hGVlTfddFN6+eWX00svvZReeeWVZhWxBRFkGTRoUPrlL3+Z9tprr6wisa3fdcopp6Tbb789/e9//2v2/oILLpg222yzdNhhh2WNb+ql3KXOPffcdMABB1R8/8cff8waEfH/KqbjN6vS9gFqq5bn2vaKAOUTTzxR1bQDBw5M6623Xtpll13SSiutlEt5KM99BgBA99CzXtJl3HnnnWnzzTfPWim+/fbbXV0kIAdHH310Wn/99Zs9ogcAQEdFheGBBx6YLrnkkixw0FLQIHohRbq1k08+Of385z9PJ554YtXfc/7552eVoGeccUbZCtLw5ptvpr/+9a9pgQUWSFdccUVdlLvUG2+8kY444oh2zz+5iV5kO+20k2AUdJJan2s7w4gRI7Jz+corr5y23npr54tO5D4DAKB7qLsmr08++WQaMmRIlkKjo61+AQBaEz27//CHP2TB8ZNOOqnFaY8//vh05JFHVr1S4zOjpXz8Peigg7qs3KViTJkddtihYso5mouxhiKIV06kQJtrrrkae/kvueSSViF0QD2da9vr73//e1aeu+++u1ulPgUAgEkiILXCCitkqfkKrXtjAOhIS1NuzIKPP/44u6F45JFHOqt4AO0SYxjEGCulFl54YWsU6mT8lGg5H+Mvffjhh+ndd9+tOF5StLKP1E8rrrhi2ffvu+++ihWkEYyIhjQxvlB8T6nf/OY3adlll02rrLJKp5e7nD//+c/pmWeeSZOztp6/n3/++bKvR6qwSClG9+M3vD515rm2raaZZpo0yyyzZOkBY+youG+N3lsR5C/n3nvvTXfddVfaaKONcikPAAB0N50WkIqBgWOcqGLvvfde2mqrrcpWiDz66KPp4YcfTmuuuWZnFRGgzRZddNF0zz33WHNQR+aee+607bbbpi233DLrqRKDzhdEYOeQQw7JxiMpFQ1mItVSucDO+PHj05577llxHKZ99903awE/ceLEdPrpp6fDDz+8yTTx+u67755effXVimNl5lHuciIt4AknnNDktRgnqlKF6qSqrefvL7/8suzrv/jFL2pYKjqT3/D60xnn2rbaYIMN0vbbb59l8YhUqaUiKPWXv/wlXXDBBWXnj/O2gBQAANRByr555pknXXfddWmxxRbL0s6UuuOOO6oKSMWA21FRM3r06Cz1TLQmjpZrMahsrcXnRyu46OHVv3//rPVynz59qhonK1K9lIoWfpHmpWDMmDFZoO7TTz/NKoZiTK1oiVdJtJaOZf/iiy+yHOXRC23OOedMs846a6tlinUeQb/2iu9ZfPHFK74fN4SxHHGTFmWLG8xoSTjddNNly93ScrVXrIdyAc7S9fz5559nLSujEi/2w9lmm63iZ44bNy7b5rEssX7jRnTqqaduV/lqsa9Wuy/F9o1ljHL369cvy8Ef67692ruvvf7669k+HeK4Keehhx4qW7ZouV4pxUmt9q+OHpvVzp/nMrRFteVt77muHvb9tp5Hqy1/rI/Y/6P80Xsl9v+O/s6097iK8sRxE+ewYnG8rL322k0CGcXi/BjfVWqJJZZIc8wxR9381rZXtJy/4YYbsoBOpXUQ+8stt9zSmB64VLl9LNx6663p/fffb/Z6fNd+++3X+H9UgEaPmQcffLBZsCPOh9FaPsbO66xyl4ptF6n6intb/frXv84Gg6+Ujq4lo0aNyuYtNWjQoOxRa3Fcx34Y+2McK/PNN1+7P6uac8pHH32UXn755ex5pfXz4osvNvutivFjWvrN7cj1W7Vl7+zryq68Rilsq9gfowzxWxpljkdLv13d7Tc872Mir/2iLfI817ZXpEZtSfx+xnhXcZ0Q31uq3PLU2/XbBx98kF577bVmr8e9XmzrcvvE/fff3+z16Dk2ePDgTjs35HWfkee1T17XlAAA3UZDjU011VRRO9bs8fjjj1ec5xe/+EXZedZdd92K84wbN67h8ssvb1hjjTUa+vbtW3b+WWaZpWHrrbdueOyxx1otd5Sv3Gcceuih2fv/+9//Gn796183+65pppmmYbvttmt4//33O/T5L774YsNGG23UMOWUUzZ5/7///W+zz/rxxx8brr/++oZ11lmnYdpppy37uQsuuGDD73//+4ZRo0ZVLNOIESPKzlvtY6eddmr2mZdddlnD/vvv37DSSis19OnTp+K8PXr0aFhggQUaDjvssIY333yzoVbuv//+Ftfz8OHDG4YOHdrQs2fPJu+vssoq2bzFPvnkk4a99tqroV+/fk2mnXrqqRu23377hg8++KCqMnX2vvrpp5827Lnnng3TTz99k/d79+7dsMEGGzS8/PLLVa/PWuxrBx10ULv3sfj+vPevjh6brc1fb8dI3ue6rtz323IercYPP/zQcP7552fnhzh+KpU/1ss///nPZvtrJbU6h8f5qdy8xx9/fNnpn3nmmbLLsfDCCzd8++23nbIN68kll1xScXnKWW+99cpOf+edd5adPrZxuel/9atfdWq5W9tv5phjjoYvvviiYaGFFqrqPFzq1ltvLTvfMccc01BLt99+e8Nyyy3X7Hvmm2++hr/+9a+N5YxzVek0sWzlVHP+jv2/rb9d8YjjLa9jv16vKzv7GmXixIkN9957b3ZMzTrrrGW/N673ll9++YYjjzyy7O9Xd/sNz/uYyGu/aIt6Ode2x0knnVS2LLFM9X79ds4555T9/DgHljNmzJiy08d9VmeeG2p5n5HntU9e15QAAN1RXQSkdt9997LzLLPMMmWnHzZsWMM888zTpgvOuCn/7LPPKpahpYvkW265pezNXOnF/n333deuz7/qqquaVRgUHq+99lqTz3n22Wezm79qlztuIK+77rpOC0i153Ni2ePGOe+AVEvruVBpce655zbuY3FT0FK5
… [75782 caracteres más en el .jsonl]
```

</details>

### Agente

Generé los dos gráficos y los dos se leen bien. Las cifras son estimaciones ponderadas con `facpob07` (personas residentes).

**Por sexo** → `figuras/enaho_pobreza_sexo_2024.png` (tabla en el `.csv` del mismo nombre)

| Sexo | Pobreza monetaria | Población expandida | n muestral |
|---|---|---|---|
| Mujer | 27.68 % | 17,694,762 | 56,077 |
| Hombre | 27.37 % | 16,453,003 | 52,587 |

**Por grupo de edad** → `figuras/enaho_pobreza_edad_2024.png` (tabla en el `.csv` del mismo nombre)

| Edad | Pobreza monetaria | Población expandida | n muestral |
|---|---|---|---|
| 0-14 | 37.52 % | 7,941,994 | 26,489 |
| 15-29 | 25.97 % | 7,512,400 | 23,122 |
| 30-44 | 27.87 % | 6,689,119 | 20,648 |
| 45-64 | 21.15 % | 7,803,731 | 24,735 |
| 65 y más | 22.74 % | 4,200,522 | 13,670 |

El promedio nacional que marca el gráfico es 27.5 %.

- **Sexo:** la diferencia entre mujeres y hombres es de 0.3 puntos. Con estas cifras no puedo decir si es estadísticamente distinta de cero, porque el script no calcula errores estándar ni intervalos de confianza.
- **Edad:** los niños de 0 a 14 años tienen la tasa más alta, 37.5 %, unos 10 puntos sobre el promedio nacional. El grupo de 45 a 64 años tiene la más baja, 21.2 %.
- Estos gráficos describen diferencias de un solo año, 2024. No explican por qué ocurren.

Fuente: INEI, ENAHO 2024 (módulos 34 y 02).

## Resultado final

- Turnos: 7
- Duración: 25.4 s
- Costo informado por Claude Code: US$ 0.0766916

Generé los dos gráficos y los dos se leen bien. Las cifras son estimaciones ponderadas con `facpob07` (personas residentes).

**Por sexo** → `figuras/enaho_pobreza_sexo_2024.png` (tabla en el `.csv` del mismo nombre)

| Sexo | Pobreza monetaria | Población expandida | n muestral |
|---|---|---|---|
| Mujer | 27.68 % | 17,694,762 | 56,077 |
| Hombre | 27.37 % | 16,453,003 | 52,587 |

**Por grupo de edad** → `figuras/enaho_pobreza_edad_2024.png` (tabla en el `.csv` del mismo nombre)

| Edad | Pobreza monetaria | Población expandida | n muestral |
|---|---|---|---|
| 0-14 | 37.52 % | 7,941,994 | 26,489 |
| 15-29 | 25.97 % | 7,512,400 | 23,122 |
| 30-44 | 27.87 % | 6,689,119 | 20,648 |
| 45-64 | 21.15 % | 7,803,731 | 24,735 |
| 65 y más | 22.74 % | 4,200,522 | 13,670 |

El promedio nacional que marca el gráfico es 27.5 %.

- **Sexo:** la diferencia entre mujeres y hombres es de 0.3 puntos. Con estas cifras no puedo decir si es estadísticamente distinta de cero, porque el script no calcula errores estándar ni intervalos de confianza.
- **Edad:** los niños de 0 a 14 años tienen la tasa más alta, 37.5 %, unos 10 puntos sobre el promedio nacional. El grupo de 45 a 64 años tiene la más baja, 21.2 %.
- Estos gráficos describen diferencias de un solo año, 2024. No explican por qué ocurren.

Fuente: INEI, ENAHO 2024 (módulos 34 y 02).
