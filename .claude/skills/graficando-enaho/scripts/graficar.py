"""Gráficos de pobreza monetaria con la ENAHO 2024, siempre con estimaciones ponderadas.

    uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo area
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo todos
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --tipo departamento --indicador extrema

Tipos: area (urbana/rural), region (costa, sierra, selva, Lima Metropolitana), sexo, edad, departamento,
distribucion (dónde viven las personas pobres) o todos. Lee salidas/hogares_2024.parquet y personas_2024.parquet;
si no existen, hay que correr antes la skill limpiando-enaho. Cada PNG va a figuras/ con un CSV al lado que trae las
cifras exactas del gráfico.
"""
import argparse
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[4]
COLOR, COLOR_RESALTE, GRIS = "#1f4e79", "#c0504d", "#555555"
INDICADORES = {"pobreza": ("pobre", "Pobreza monetaria"), "extrema": ("pobre_extremo", "Pobreza extrema")}
METODO_HOGARES = "factor07 × mieperho"
METODO_PERSONAS = "facpob07 (personas residentes)"


def tasa(df, ind, peso):
    return float((df[ind] * df[peso]).sum() / df[peso].sum() * 100)


def por_grupo(df, grupo, ind, peso):
    t = (df.assign(_num=df[ind] * df[peso]).groupby(grupo)
         .agg(num=("_num", "sum"), pob=(peso, "sum"), n_muestral=(ind, "size")))
    t["valor_pct"] = t.num / t.pob * 100
    t["poblacion_expandida"] = t.pob.round()
    return t[["valor_pct", "poblacion_expandida", "n_muestral"]].reset_index()


def pie(ax_fig, metodo, anio, extra=""):
    ax_fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {anio} (módulos 34 y 02). Estimación ponderada con {metodo}. "
                            f"{extra}Elaboración propia.", fontsize=7, color=GRIS)


def titular(fig, ax, titulo, subtitulo):
    """Título analítico arriba (qué y cuándo) y, debajo, el subtítulo con la unidad."""
    fig.suptitle(textwrap.fill(titulo, 80), x=0.01, ha="left", fontsize=12, fontweight="bold")
    ax.set_title(subtitulo, loc="left", fontsize=9, color=GRIS, pad=8)


def barras(t, etiqueta, titulo, subtitulo, archivo, metodo, anio, nacional=None, horizontal=False, resaltar=None):
    """Barras desde cero, un solo color, el valor escrito en cada barra y la línea del promedio nacional."""
    titulo = textwrap.fill(titulo, 80)
    alto = max(4.2, 0.28 * len(t) + 1.6) if horizontal else 4.6
    fig, ax = plt.subplots(figsize=(8.5, alto), dpi=200)
    colores = [COLOR_RESALTE if resaltar and resaltar(r) else COLOR for _, r in t.iterrows()]
    if horizontal:
        ax.barh(t[etiqueta], t.valor_pct, color=colores)
        ax.invert_yaxis()
        for i, v in enumerate(t.valor_pct):
            ax.text(v + 0.4, i, f"{v:.1f}", va="center", fontsize=8)
        ax.set_xlim(0, max(t.valor_pct) * 1.15)
        ax.set_xlabel("% de personas")
        if nacional is not None:
            ax.axvline(nacional, color=GRIS, ls="--", lw=1)
            ax.text(nacional, -0.9, f"Perú {nacional:.1f} %", ha="center", fontsize=8, color=GRIS)
    else:
        ax.bar(t[etiqueta], t.valor_pct, color=colores, width=0.6)
        for i, v in enumerate(t.valor_pct):
            ax.text(i, v + 0.6, f"{v:.1f} %", ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(0, max(t.valor_pct) * 1.2)
        ax.set_ylabel("% de personas")
        if nacional is not None:
            ax.axhline(nacional, color=GRIS, ls="--", lw=1)
            ax.text(len(t) - 0.5, nacional + 0.6, f"Perú {nacional:.1f} %", ha="right", fontsize=8, color=GRIS)
    titular(fig, ax, titulo, subtitulo)
    ax.spines[["top", "right"]].set_visible(False)
    pie(fig, metodo, anio)
    fig.tight_layout(rect=(0, 0.04, 1, 0.93 if "\n" in titulo else 0.95))
    ruta = RAIZ / "figuras" / f"{archivo}.png"
    fig.savefig(ruta)
    plt.close(fig)
    t.to_csv(ruta.with_suffix(".csv"), index=False, encoding="utf-8")
    return ruta


def graficar(tipo, hogares, personas, indicador, anio):
    ind, nombre = INDICADORES[indicador]
    sufijo = "" if indicador == "pobreza" else "_extrema"
    nac_h, nac_p = tasa(hogares, ind, "factor_personas"), tasa(personas, ind, "facpob07")
    if tipo == "area":
        t = por_grupo(hogares, "area", ind, "factor_personas").sort_values("valor_pct", ascending=False)
        brecha = t.valor_pct.max() - t.valor_pct.min()
        return barras(t, "area", f"{nombre}: el área rural supera a la urbana en {brecha:.1f} puntos ({anio})",
                      "% de personas en situación de pobreza, por área de residencia (urbana: estrato 1 a 5)",
                      f"enaho_{indicador}_area_{anio}", METODO_HOGARES, anio, nac_h)
    if tipo == "region":
        t = por_grupo(hogares, "region_natural", ind, "factor_personas").sort_values("valor_pct", ascending=False)
        return barras(t, "region_natural", f"{nombre} por región natural, {anio}",
                      "% de personas; Lima Metropolitana es el dominio 8 de la ENAHO",
                      f"enaho_{indicador}_region_{anio}", METODO_HOGARES, anio, nac_h)
    if tipo == "sexo":
        t = por_grupo(personas, "sexo", ind, "facpob07").sort_values("valor_pct", ascending=False)
        dif = t.valor_pct.max() - t.valor_pct.min()
        return barras(t, "sexo", f"{nombre} por sexo, {anio}: diferencia de {dif:.1f} puntos",
                      "% de personas residentes habituales, según sexo",
                      f"enaho_{indicador}_sexo_{anio}", METODO_PERSONAS, anio, nac_p)
    if tipo == "edad":
        t = por_grupo(personas, "grupo_edad", ind, "facpob07")
        orden = ["0-14", "15-29", "30-44", "45-64", "65 y más"]
        t = t.set_index("grupo_edad").loc[orden].reset_index()
        return barras(t, "grupo_edad", f"{nombre} por grupo de edad, {anio}: los niños, los más afectados",
                      "% de personas residentes habituales, por edad en años cumplidos",
                      f"enaho_{indicador}_edad_{anio}", METODO_PERSONAS, anio, nac_p,
                      resaltar=lambda r: r.valor_pct == t.valor_pct.max())
    if tipo == "departamento":
        t = por_grupo(hogares, "nombre_departamento", ind, "factor_personas").sort_values("valor_pct", ascending=False)
        mayor, menor = t.iloc[0], t.iloc[-1]
        return barras(t, "nombre_departamento",
                      f"{nombre} por departamento, {anio}: de {menor.valor_pct:.1f} % en {menor.nombre_departamento} "
                      f"a {mayor.valor_pct:.1f} % en {mayor.nombre_departamento}",
                      "% de personas; Lima no incluye al Callao. En rojo, los departamentos sobre el promedio nacional",
                      f"enaho_{indicador}_departamento_{anio}", METODO_HOGARES, anio, nac_h, horizontal=True,
                      resaltar=lambda r: r.valor_pct > nac_h)
    if tipo == "distribucion":
        d = hogares.assign(pp=hogares[ind] * hogares.factor_personas, pob=hogares.factor_personas).groupby("area")[
            ["pp", "pob"]].sum()
        t = pd.DataFrame({"area": d.index, "pobres_pct": d.pp / d.pp.sum() * 100,
                          "poblacion_pct": d.pob / d.pob.sum() * 100, "pobres_millones": d.pp / 1e6}).reset_index(drop=True)
        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=200)
        x = range(len(t))
        ax.bar([i - 0.2 for i in x], t.poblacion_pct, width=0.4, color="#9dc3e6", label="% de la población")
        ax.bar([i + 0.2 for i in x], t.pobres_pct, width=0.4, color=COLOR, label="% de las personas pobres")
        for i, r in t.iterrows():
            ax.text(i - 0.2, r.poblacion_pct + 1, f"{r.poblacion_pct:.1f}", ha="center", fontsize=9)
            ax.text(i + 0.2, r.pobres_pct + 1, f"{r.pobres_pct:.1f}\n({r.pobres_millones:.2f} M)", ha="center",
                    fontsize=9)
        ax.set_xticks(list(x), t.area)
        ax.set_ylim(0, 100)
        ax.set_ylabel("%")
        ax.legend(frameon=False)
        urbana = t.set_index("area").loc["Urbana", "pobres_pct"]
        titular(fig, ax, f"La tasa es más alta en el campo, pero {round(urbana / 10)} de cada 10 personas en "
                         f"{nombre.lower()} viven en zonas urbanas ({anio})" if urbana > 50 else
                f"¿Dónde viven las personas en {nombre.lower()}? {anio}",
                "% de la población total y % de las personas pobres que vive en cada área (millones de pobres)")
        ax.spines[["top", "right"]].set_visible(False)
        pie(fig, METODO_HOGARES, anio)
        fig.tight_layout(rect=(0, 0.04, 1, 0.92))
        ruta = RAIZ / "figuras" / f"enaho_distribucion_pobres_area_{anio}{sufijo}.png"
        fig.savefig(ruta)
        plt.close(fig)
        t.to_csv(ruta.with_suffix(".csv"), index=False, encoding="utf-8")
        return ruta
    raise SystemExit(f"Tipo no reconocido: {tipo}")


def main():
    global RAIZ
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tipo", default="todos",
                    choices=["area", "region", "sexo", "edad", "departamento", "distribucion", "todos"])
    ap.add_argument("--indicador", default="pobreza", choices=list(INDICADORES))
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args()
    RAIZ = a.raiz
    salidas = RAIZ / "salidas"
    faltan = [f for f in (f"hogares_{a.anio}.parquet", f"personas_{a.anio}.parquet") if not (salidas / f).exists()]
    if faltan:
        print(f"Falta salidas/{faltan[0]}: corran primero la skill limpiando-enaho "
              f"(uv run .claude/skills/limpiando-enaho/scripts/limpiar.py).", file=sys.stderr)
        sys.exit(2)
    hogares = pd.read_parquet(salidas / f"hogares_{a.anio}.parquet")
    personas = pd.read_parquet(salidas / f"personas_{a.anio}.parquet")
    (RAIZ / "figuras").mkdir(exist_ok=True)
    tipos = ["area", "region", "sexo", "edad", "departamento", "distribucion"] if a.tipo == "todos" else [a.tipo]
    for tipo in tipos:
        ruta = graficar(tipo, hogares, personas, a.indicador, a.anio)
        tabla = pd.read_csv(ruta.with_suffix(".csv"))
        print(f"Guardé {ruta.relative_to(RAIZ).as_posix()} y su tabla:")
        print(tabla.round(2).to_string(index=False))
        print()


if __name__ == "__main__":
    main()
