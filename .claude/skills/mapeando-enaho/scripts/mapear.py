"""Mapa coroplético de la pobreza monetaria por departamento con la ENAHO 2024.

    uv run .claude/skills/mapeando-enaho/scripts/mapear.py
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador extrema

Une por código, nunca por nombre: ubigeo[:2] de la ENAHO con FIRST_IDDP del GeoJSON del curso, ambos como texto de
dos dígitos. Exige 25 unidades con dato (Lima 15 y Callao 07 van separados) y compara cada departamento con
referencias/pobreza_departamento_2024.csv de la sesión 16. Salidas: mapas/<nombre>.png,
mapas/<nombre>.csv (cifras del mapa) y salidas/comparacion_mapa_referencia.csv.
"""
import argparse
import sys
from pathlib import Path

import geopandas as gpd
import httpx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
URL_GEOJSON = ("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/"
               "peru_departamental_simple.geojson")
REFERENCIA = AQUI.parent / "referencias" / "pobreza_departamento_2024.csv"
INDICADORES = {"pobreza": ("pobre", "Pobreza monetaria"), "extrema": ("pobre_extremo", "Pobreza extrema")}
TOLERANCIA_PP = 0.1


def geometrias(raiz):
    ruta = raiz / "datos" / "geo" / "peru_departamental_simple.geojson"
    if not ruta.exists():
        print(f"Bajando el GeoJSON del curso a {ruta.relative_to(raiz)} ...")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        r = httpx.get(URL_GEOJSON, timeout=120, follow_redirects=True)
        r.raise_for_status()
        ruta.write_bytes(r.content)
    g = gpd.read_file(ruta)
    g["FIRST_IDDP"] = g.FIRST_IDDP.astype(str).str.zfill(2)
    return g


def pobreza_departamental(hogares, ind):
    t = (hogares.assign(_num=hogares[ind] * hogares.factor_personas)
         .groupby(["departamento", "nombre_departamento"])
         .agg(num=("_num", "sum"), poblacion_expandida=("factor_personas", "sum"), n_muestral=(ind, "size"))
         .reset_index())
    t["valor_pct"] = t.num / t.poblacion_expandida * 100
    t["pobres_expandidos"] = t.num.round()
    return t.drop(columns="num")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--indicador", default="pobreza", choices=list(INDICADORES))
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--raiz", type=Path, default=RAIZ)
    a = ap.parse_args()
    raiz = a.raiz
    hogares_pq = raiz / "salidas" / f"hogares_{a.anio}.parquet"
    if not hogares_pq.exists():
        print(f"Falta salidas/{hogares_pq.name}: corran primero la skill limpiando-enaho "
              "(uv run .claude/skills/limpiando-enaho/scripts/limpiar.py).", file=sys.stderr)
        sys.exit(2)

    ind, nombre = INDICADORES[a.indicador]
    tabla = pobreza_departamental(pd.read_parquet(hogares_pq), ind)
    geo = geometrias(raiz)
    # La unión: por código, uno a uno. Si un código perdió su cero o falta, aquí falla.
    mapa = geo.merge(tabla, left_on="FIRST_IDDP", right_on="departamento", how="left", validate="1:1")
    sin_dato = mapa[mapa.valor_pct.isna()].NOMBDEP.tolist()
    if len(mapa) != 25 or sin_dato or set(mapa.FIRST_IDDP) != set(tabla.departamento):
        print(f"ERROR: el mapa debe tener 25 departamentos con dato; tiene {len(mapa)} y sin dato: {sin_dato}.",
              file=sys.stderr)
        sys.exit(1)
    if not {"07", "15"} <= set(mapa.FIRST_IDDP):
        print("ERROR: Lima (15) y Callao (07) deben ir separados.", file=sys.stderr)
        sys.exit(1)

    # Comparación con la referencia de la sesión 16 (solo pobreza monetaria 2024)
    if a.indicador == "pobreza" and a.anio == 2024:
        ref = pd.read_csv(REFERENCIA, dtype={"ccdd": str}).rename(columns={"departamento": "nombre_referencia"})
        comp = tabla.merge(ref, left_on="departamento", right_on="ccdd", how="outer", validate="1:1")
        comp["diferencia_pp"] = (comp.valor_pct - comp.pobreza_pct).round(3)
        comp["coincide"] = comp.diferencia_pp.abs() <= TOLERANCIA_PP
        comp = comp[["departamento", "nombre_departamento", "valor_pct", "pobreza_pct", "diferencia_pp", "coincide"]]
        comp = comp.rename(columns={"valor_pct": "calculado_pct", "pobreza_pct": "referencia_sesion16_pct"})
        comp.to_csv(raiz / "salidas" / "comparacion_mapa_referencia.csv", index=False, encoding="utf-8")
        print(f"Comparación con la referencia de la sesión 16: {int(comp.coincide.sum())} de {len(comp)} "
              f"departamentos coinciden (±{TOLERANCIA_PP} pp); diferencia máxima "
              f"{comp.diferencia_pp.abs().max():.3f} pp.")
        if not comp.coincide.all():
            print("AVISO: no coinciden:", comp[~comp.coincide].to_string(index=False))

    # El mapa: un color de claro a oscuro desde 0, leyenda con la unidad, valores escritos
    fig, ax = plt.subplots(figsize=(7.2, 9.2), dpi=200)
    mapa.plot(column="valor_pct", cmap="Oranges", vmin=0, vmax=mapa.valor_pct.max(), linewidth=0.5,
              edgecolor="white", ax=ax, legend=True,
              legend_kwds={"label": f"{nombre} (% de personas)", "shrink": 0.55, "pad": 0.02})
    proyectada = mapa.to_crs(32718)
    puntos = proyectada.representative_point().to_crs(mapa.crs)
    for (_, fila), p in zip(mapa.iterrows(), puntos):
        texto = f"{fila.valor_pct:.1f}"
        color = "white" if fila.valor_pct > mapa.valor_pct.max() * 0.6 else "#222222"
        if fila.FIRST_IDDP == "07":       # el Callao es muy pequeño: etiqueta afuera, con flecha
            ax.annotate(f"Callao {texto}", xy=(p.x, p.y), xytext=(p.x - 3.2, p.y - 0.4), fontsize=7,
                        arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.6}, color="#222222")
        elif fila.FIRST_IDDP == "15":
            ax.annotate(f"Lima {texto}", xy=(p.x, p.y), xytext=(p.x - 3.0, p.y + 0.3), fontsize=7,
                        arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.6}, color="#222222")
        else:
            ax.text(p.x, p.y, texto, ha="center", va="center", fontsize=6.5, color=color)
    mayor = tabla.loc[tabla.valor_pct.idxmax()]
    menor = tabla.loc[tabla.valor_pct.idxmin()]
    fig.suptitle(f"{nombre} por departamento, {a.anio}", x=0.03, ha="left", fontsize=13, fontweight="bold")
    ax.set_title(f"De {menor.valor_pct:.1f} % en {menor.nombre_departamento} a {mayor.valor_pct:.1f} % en "
                 f"{mayor.nombre_departamento}; Lima y Callao por separado", loc="left", fontsize=9, color="#555555")
    ax.set_axis_off()
    fig.text(0.02, 0.015, f"Fuente: INEI, ENAHO {a.anio} (módulos 34 y 02); límites departamentales del repositorio del "
                          "curso. Estimación ponderada\ncon factor07 × mieperho; unión por código ubigeo[:2] = "
                          "FIRST_IDDP. Elaboración propia.", fontsize=6.5, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    (raiz / "mapas").mkdir(exist_ok=True)
    salida = raiz / "mapas" / f"{a.indicador}_departamento_{a.anio}.png"
    fig.savefig(salida)
    plt.close(fig)
    tabla.sort_values("valor_pct", ascending=False).to_csv(salida.with_suffix(".csv"), index=False, encoding="utf-8")
    print(f"Guardé {salida.relative_to(raiz).as_posix()} con {len(mapa)} departamentos con dato "
          f"(unión por código, validate='1:1').")
    print(tabla.sort_values("valor_pct", ascending=False)[["departamento", "nombre_departamento", "valor_pct"]]
          .round(2).to_string(index=False))


if __name__ == "__main__":
    main()
