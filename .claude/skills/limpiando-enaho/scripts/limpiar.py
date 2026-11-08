"""Limpia la ENAHO 2024 (módulos 34 y 02 del INEI) y arma las bases de hogares y personas con pobreza y factores.

    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py            # desde la raíz del proyecto
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024 --descargar

Pipeline (siempre en este orden, sesión 16 del curso):
  1. Leer los .dta dentro de los zip con convert_categoricals=False; las llaves quedan como texto.
  2. Normalizar los nombres de columna a minúscula (la del año llega como «aÑo»).
  3. Filtrar residentes habituales: (p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1).
  4. Unir personas con hogares por conglome, vivienda y hogar con merge(validate="m:1").
  5. Construir departamento = ubigeo[:2], área (urbano = estrato <= 5), pobre = pobreza <= 2, sexo, edad.
  6. Validar contra las cifras oficiales; si falla una validación esencial, se detiene sin guardar la base.
  7. Guardar salidas/hogares_2024.parquet, salidas/personas_2024.parquet, salidas/indicadores.csv y
     salidas/validacion.txt.

Toda cifra es ponderada: la pobreza de los hogares se expande a personas con factor07 × mieperho (método del INEI);
las características individuales (sexo, edad) usan facpob07 en la base de personas.
"""
import argparse
import io
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import httpx
import pandas as pd

RAIZ = Path(__file__).resolve().parents[4]          # scripts -> limpiando-enaho -> skills -> .claude -> raíz
CODIGOS_INEI = {2024: 966}                           # código de la ENAHO anual en el portal de microdatos
URL_INEI = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo}-Modulo{modulo}.zip"
LLAVES = ["conglome", "vivienda", "hogar"]
ANCHO_LLAVES = {"conglome": 6, "vivienda": 3, "hogar": 2, "codperso": 2, "ubigeo": 6}

# Cifras publicadas para la ENAHO 2024 (INEI y validación de la sesión 16 del curso). Solo se usan para COMPARAR:
# ningún resultado se copia de aquí.
REFERENCIA = {
    "hogares": 33_691,
    "filas_modulo_02": 117_721,
    "residentes": 108_664,
    "pobreza_nacional": 27.6,
    "pobreza_extrema": 5.5,
    "pobreza_urbana": 24.8,
    "pobreza_rural": 39.3,
    "pobreza_lima_metropolitana": 28.2,
}
TOLERANCIA_PP = 0.1          # puntos porcentuales: la que exige la tarea para la pobreza nacional

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua",
    "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
REGION_NATURAL = {1: "Costa", 2: "Costa", 3: "Costa", 4: "Sierra", 5: "Sierra", 6: "Sierra", 7: "Selva",
                  8: "Lima Metropolitana"}
GRUPOS_EDAD = [(0, 14, "0-14"), (15, 29, "15-29"), (30, 44, "30-44"), (45, 64, "45-64"), (65, 200, "65 y más")]

COLUMNAS_SUMARIA = LLAVES + ["anio", "mes", "ubigeo", "dominio", "estrato", "mieperho", "totmieho", "pobreza",
                             "linea", "linpe", "gashog2d", "inghog1d", "factor07"]
COLUMNAS_PERSONAS = LLAVES + ["codperso", "p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]


class ValidacionFallida(Exception):
    pass


# 1-2. Leer y normalizar --------------------------------------------------------------------------------------------

def normalizar_columnas(df):
    """Minúsculas y la columna del año como «anio» (en el .dta llega «aÑo», que a veces se lee como «a�o»)."""
    nombres = {}
    for c in df.columns:
        n = c.lower()
        if len(n) == 3 and n[0] == "a" and n[2] == "o" and not n.isascii():
            n = "anio"
        nombres[c] = n
    return df.rename(columns=nombres)


def llaves_como_texto(df):
    """Las llaves deben ser texto con sus ceros: «015009», no 15009. Si llegaran numéricas, se rellenan."""
    for c, ancho in ANCHO_LLAVES.items():
        if c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].astype("Int64").astype(str).str.zfill(ancho)
            df[c] = df[c].astype(str).str.strip().str.zfill(ancho)
    return df


def descargar(zip_path, modulo, anio):
    url = URL_INEI.format(codigo=CODIGOS_INEI[anio], modulo=modulo)
    print(f"Bajando {url} ...")
    r = httpx.get(url, timeout=600, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    if not r.content.startswith(b"PK"):
        raise SystemExit(f"El INEI no devolvió un zip para {url}. Bájenlo desde el navegador a {zip_path.parent}.")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path.write_bytes(r.content)


def leer_dta(zip_path, empieza, columnas):
    """Lee el .dta cuyo nombre empieza con `empieza` dentro del zip, sin convertir etiquetas en categorías."""
    with zipfile.ZipFile(zip_path) as zf:
        nombres = [n for n in zf.namelist() if Path(n).name.lower().startswith(empieza) and n.lower().endswith(".dta")]
        # sumaria-2024.dta, no sumaria-2024-12g.dta (la de 12 grupos de gasto)
        nombres.sort(key=len)
        if not nombres:
            raise SystemExit(f"No encontré {empieza}*.dta dentro de {zip_path.name}.")
        contenido = io.BytesIO(zf.read(nombres[0]))
    df = normalizar_columnas(pd.read_stata(contenido, convert_categoricals=False))
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        raise SystemExit(f"Faltan columnas en {nombres[0]}: {faltan}")
    return llaves_como_texto(df[columnas].copy()), nombres[0]


# 3-5. Filtrar, unir y construir -------------------------------------------------------------------------------------

def residentes_habituales(p):
    return ((p.p204 == 1) & (p.p205 == 2)) | ((p.p204 == 2) & (p.p206 == 1))


def construir_hogares(s):
    s = s.copy()
    s["departamento"] = s.ubigeo.str[:2]
    s["nombre_departamento"] = s.departamento.map(DEPARTAMENTOS)
    s["area"] = s.estrato.le(5).map({True: "Urbana", False: "Rural"})
    s["region_natural"] = s.dominio.map(REGION_NATURAL)
    s["lima_metropolitana"] = s.dominio.eq(8)
    s["pobre"] = s.pobreza.le(2)
    s["pobre_extremo"] = s.pobreza.eq(1)
    s["factor_personas"] = s.factor07 * s.mieperho      # expande el hogar a sus miembros (método INEI)
    return s


def construir_personas(p, hogares):
    p = p[residentes_habituales(p)].copy()
    n_residentes = len(p)
    personas = p.merge(hogares, on=LLAVES, how="left", validate="m:1", indicator=True)
    personas["sexo"] = personas.p207.map({1: "Hombre", 2: "Mujer"})
    personas["edad"] = personas.p208a
    personas["grupo_edad"] = pd.cut(personas.edad, bins=[g[0] - 1 for g in GRUPOS_EDAD] + [GRUPOS_EDAD[-1][1]],
                                    labels=[g[2] for g in GRUPOS_EDAD]).astype(str)
    personas["jefe_hogar"] = personas.p203.eq(1)
    return personas, n_residentes


# Estimaciones ponderadas --------------------------------------------------------------------------------------------

def tasa(df, indicador, peso):
    """Porcentaje ponderado: suma de pesos con el indicador / suma de pesos. Nunca un promedio simple."""
    return float((df[indicador] * df[peso]).sum() / df[peso].sum() * 100)


def tabla(df, indicador, peso, grupo, metodo, nombre):
    filas = []
    grupos = [("Perú", df)] if grupo is None else df.groupby(grupo, sort=True)
    for valor, g in grupos:
        filas.append({"indicador": nombre, "desagregacion": grupo or "nacional", "grupo": valor,
                      "valor_pct": round(tasa(g, indicador, peso), 4),
                      "poblacion_expandida": round(float(g[peso].sum())),
                      "personas_pobres_expandidas": round(float((g[indicador] * g[peso]).sum())),
                      "n_muestral": len(g), "metodo": metodo})
    return filas


def indicadores(hogares, personas):
    H = "hogares: factor07 × mieperho"
    P = "personas: facpob07"
    filas = []
    for ind, nombre in [("pobre", "pobreza_monetaria"), ("pobre_extremo", "pobreza_extrema")]:
        for grupo in [None, "area", "region_natural", "departamento"]:
            filas += tabla(hogares, ind, "factor_personas", grupo, H, nombre)
        filas += tabla(hogares[hogares.lima_metropolitana], ind, "factor_personas", None, H, nombre + "_lima_metropolitana")
        for grupo in [None, "area", "departamento", "sexo", "grupo_edad"]:
            filas += tabla(personas, ind, "facpob07", grupo, P, nombre)
    df = pd.DataFrame(filas)
    df.loc[df.desagregacion == "departamento", "nombre"] = df.grupo.map(DEPARTAMENTOS)
    df.loc[df.desagregacion != "departamento", "nombre"] = df.grupo
    # cuántos de los pobres viven en cada área (distribución, no tasa)
    pobres_area = hogares.assign(pp=hogares.pobre * hogares.factor_personas).groupby("area").pp.sum()
    for area, v in pobres_area.items():
        filas_dist = {"indicador": "distribucion_de_pobres", "desagregacion": "area", "grupo": area, "nombre": area,
                      "valor_pct": round(float(v / pobres_area.sum() * 100), 4), "poblacion_expandida": None,
                      "personas_pobres_expandidas": round(float(v)), "n_muestral": int((hogares.area == area).sum()),
                      "metodo": H}
        df = pd.concat([df, pd.DataFrame([filas_dist])], ignore_index=True)
    return df


# 6. Validar ---------------------------------------------------------------------------------------------------------

def validar(sumaria, modulo02, hogares, personas, n_residentes, ind):
    """Devuelve [(esencial, nombre, aprobada, detalle)]. Las esenciales detienen el proceso si fallan."""
    chequeos = []

    def chequear(esencial, nombre, aprobada, detalle):
        chequeos.append((esencial, nombre, bool(aprobada), detalle))

    def cifra(indicador, desagregacion, grupo, metodo_contiene):
        f = ind[(ind.indicador == indicador) & (ind.desagregacion == desagregacion) & (ind.grupo == grupo)
                & ind.metodo.str.contains(metodo_contiene)]
        return float(f.valor_pct.iloc[0])

    chequear(True, "Hogares en la sumaria", len(sumaria) == REFERENCIA["hogares"],
             f"{len(sumaria):,} (referencia {REFERENCIA['hogares']:,})")
    chequear(True, "Llaves de hogar únicas en la sumaria", not sumaria.duplicated(LLAVES).any(),
             f"{sumaria.duplicated(LLAVES).sum()} duplicados de conglome+vivienda+hogar")
    chequear(True, "Filas del módulo 02", len(modulo02) == REFERENCIA["filas_modulo_02"],
             f"{len(modulo02):,} (referencia {REFERENCIA['filas_modulo_02']:,})")
    chequear(True, "Llaves de persona únicas en el módulo 02", not modulo02.duplicated(LLAVES + ["codperso"]).any(),
             f"{modulo02.duplicated(LLAVES + ['codperso']).sum()} duplicados de conglome+vivienda+hogar+codperso")
    chequear(True, "Llaves con ceros iniciales (texto)",
             sumaria.conglome.str.len().eq(6).all() and modulo02.codperso.str.len().eq(2).all()
             and sumaria.ubigeo.str.len().eq(6).all(),
             f"conglome {sumaria.conglome.iloc[0]!r}, ubigeo {sumaria.ubigeo.iloc[0]!r}")
    chequear(True, "Residentes habituales", n_residentes == REFERENCIA["residentes"],
             f"{n_residentes:,} (referencia {REFERENCIA['residentes']:,}) con "
             "(p204==1 & p205==2) | (p204==2 & p206==1)")
    sin_hogar = int((personas._merge != "both").sum())
    chequear(True, "Unión m:1 sin perder ni duplicar personas",
             len(personas) == n_residentes and sin_hogar == 0,
             f"{len(personas):,} filas después de unir, {sin_hogar} personas sin hogar en la sumaria")
    deps = sorted(hogares.departamento.unique())
    chequear(True, "25 códigos territoriales (ubigeo[:2])", deps == sorted(DEPARTAMENTOS),
             f"{len(deps)} códigos: {deps[0]}–{deps[-1]}")
    chequear(True, "Factores de expansión presentes y positivos",
             hogares.factor07.gt(0).all() and personas.facpob07.gt(0).all(),
             f"factor07 nulos: {hogares.factor07.isna().sum()}, facpob07 nulos: {personas.facpob07.isna().sum()}")
    pob_h, pob_p = hogares.factor_personas.sum(), personas.facpob07.sum()
    chequear(False, "Población expandida: factor07 × mieperho ≈ suma de facpob07",
             abs(pob_h / pob_p - 1) < 0.01, f"{pob_h:,.0f} frente a {pob_p:,.0f} ({(pob_h / pob_p - 1) * 100:+.2f} %)")

    nac_h = cifra("pobreza_monetaria", "nacional", "Perú", "hogares")
    nac_p = cifra("pobreza_monetaria", "nacional", "Perú", "personas")
    simple = float(personas.pobre.mean() * 100)
    chequear(True, "Pobreza monetaria nacional (hogares, factor07 × mieperho)",
             abs(nac_h - REFERENCIA["pobreza_nacional"]) <= TOLERANCIA_PP,
             f"{nac_h:.2f} % (referencia {REFERENCIA['pobreza_nacional']} %, tolerancia ±{TOLERANCIA_PP} pp)")
    chequear(True, "Pobreza monetaria nacional (personas, facpob07)",
             abs(nac_p - REFERENCIA["pobreza_nacional"]) <= TOLERANCIA_PP,
             f"{nac_p:.2f} % (referencia {REFERENCIA['pobreza_nacional']} %, tolerancia ±{TOLERANCIA_PP} pp)")
    chequear(False, "El promedio simple NO coincide con la estimación ponderada (prueba de que se pondera)",
             abs(simple - nac_p) > 0.5, f"promedio simple sin factor: {simple:.2f} % frente a {nac_p:.2f} % ponderado")
    for nombre, ind_, des, grupo, ref in [
            ("Pobreza extrema nacional", "pobreza_extrema", "nacional", "Perú", "pobreza_extrema"),
            ("Pobreza urbana (estrato <= 5)", "pobreza_monetaria", "area", "Urbana", "pobreza_urbana"),
            ("Pobreza rural (estrato >= 6)", "pobreza_monetaria", "area", "Rural", "pobreza_rural")]:
        v = cifra(ind_, des, grupo, "hogares")
        chequear(True, nombre, abs(v - REFERENCIA[ref]) <= TOLERANCIA_PP,
                 f"{v:.2f} % (referencia {REFERENCIA[ref]} %)")
    lima = cifra("pobreza_monetaria_lima_metropolitana", "nacional", "Perú", "hogares")
    chequear(False, "Pobreza de Lima Metropolitana (dominio 8)",
             abs(lima - REFERENCIA["pobreza_lima_metropolitana"]) <= TOLERANCIA_PP,
             f"{lima:.2f} % (referencia {REFERENCIA['pobreza_lima_metropolitana']} %)")
    return chequeos


def escribir_validacion(ruta, chequeos, archivos, anio):
    lineas = [f"Validación de la ENAHO {anio} · limpiando-enaho · {datetime.now():%Y-%m-%d %H:%M}",
              f"Archivos: {', '.join(archivos)}", ""]
    for esencial, nombre, ok, detalle in chequeos:
        marca = "APROBADA" if ok else ("FALLIDA " if esencial else "AVISO   ")
        lineas.append(f"[{marca}] {'(esencial) ' if esencial else ''}{nombre}: {detalle}")
    fallidas = [c for c in chequeos if c[0] and not c[2]]
    aprobadas = sum(c[2] for c in chequeos)
    lineas += ["", f"Resultado: {aprobadas} de {len(chequeos)} verificaciones aprobadas; "
                   f"{len(fallidas)} esenciales fallidas."]
    lineas.append("ESTADO: OK, la base procesada se puede usar." if not fallidas else
                  "ESTADO: DETENIDO. No se guardó la base: revisen las verificaciones fallidas.")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return fallidas


# 7. Programa --------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--raiz", type=Path, default=RAIZ, help="carpeta del proyecto (con datos/ y salidas/)")
    ap.add_argument("--descargar", action="store_true", help="bajar los zip del INEI si faltan")
    a = ap.parse_args()
    if a.anio not in CODIGOS_INEI:
        raise SystemExit(f"Solo está configurada la ENAHO {list(CODIGOS_INEI)}; el año {a.anio} no.")

    codigo = CODIGOS_INEI[a.anio]
    datos, salidas = a.raiz / "datos" / "enaho", a.raiz / "salidas"
    salidas.mkdir(exist_ok=True)
    zips = {m: datos / f"{codigo}-Modulo{m}.zip" for m in ("34", "02")}
    for m, z in zips.items():
        if not z.exists():
            if not a.descargar:
                raise SystemExit(f"Falta {z.relative_to(a.raiz)}. Bájenlo de {URL_INEI.format(codigo=codigo, modulo=m)} "
                                 "o corran el script con --descargar.")
            descargar(z, m, a.anio)

    sumaria, archivo_s = leer_dta(zips["34"], "sumaria", COLUMNAS_SUMARIA)
    modulo02, archivo_p = leer_dta(zips["02"], f"enaho01-{a.anio}-200", COLUMNAS_PERSONAS)
    hogares = construir_hogares(sumaria)
    personas, n_residentes = construir_personas(modulo02, hogares)
    ind = indicadores(hogares, personas)
    chequeos = validar(sumaria, modulo02, hogares, personas, n_residentes, ind)
    fallidas = escribir_validacion(salidas / "validacion.txt", chequeos, [archivo_s, archivo_p], a.anio)
    print((salidas / "validacion.txt").read_text(encoding="utf-8"))
    if fallidas:
        print("ERROR: fallaron validaciones esenciales; no se guardan las bases.", file=sys.stderr)
        sys.exit(1)

    personas = personas.drop(columns="_merge")
    hogares.to_parquet(salidas / f"hogares_{a.anio}.parquet", index=False)
    personas.to_parquet(salidas / f"personas_{a.anio}.parquet", index=False)
    ind.to_csv(salidas / "indicadores.csv", index=False, encoding="utf-8")
    print(f"Guardé salidas/hogares_{a.anio}.parquet ({len(hogares):,} hogares), salidas/personas_{a.anio}.parquet "
          f"({len(personas):,} personas) y salidas/indicadores.csv ({len(ind)} filas).")


if __name__ == "__main__":
    main()
