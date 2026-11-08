"""Servidor MCP del BCRP para el agente de investigación socioeconómica.

Herramientas: buscar_series, serie, resumen, agregar_anual (propia), graficar_series (propia) y comparar_paises.
Recursos: bcrp://serie/{codigo} y bcrp://series-clave. Prompts: informe(tema) e investigacion(pregunta).

    uv run pytest                     # las 8 pruebas del curso + las 3 de las herramientas propias
    uv run mcp/server.py              # el servidor, por stdio (así lo arranca Claude Code desde .mcp.json)

Las cuentas las hace Python, no el modelo: cada cifra sale de una llamada que se puede repetir y trae la URL de la API
del BCRP de donde salió. Basado en el proyecto de la sesión 04 del curso (FastMCP 4).
"""
import calendar
import json
import re
import time
import unicodedata
from functools import cache
from pathlib import Path

import httpx
import matplotlib

matplotlib.use("Agg")   # sin ventana: el servidor corre en segundo plano
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

AQUI = Path(__file__).parent
RAIZ = AQUI.parent
CATALOGO = RAIZ / "datos" / "bcrp" / "catalogo_bcrp.csv"
FIGURAS = RAIZ / "figuras"
URL_CATALOGO = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
BANCO_MUNDIAL = "https://api.worldbank.org/v2"
SOLO_LECTURA = {"readOnlyHint": True, "openWorldHint": True}
MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
         "jul": 7, "ago": 8, "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12}
PERIODOS_POR_ANIO = {"Mensual": 12, "Trimestral": 4}

mcp = FastMCP("bcrp", instructions=(
    "Series oficiales del Banco Central de Reserva del Perú (BCRP). Primero busca el código con buscar_series; "
    "luego usa resumen para variaciones, promedios y extremos, serie para los datos, agregar_anual para llevar una "
    "serie mensual a años (para compararla con la ENAHO, que es anual) y graficar_series para guardar un gráfico. "
    "No calcules a mano: cita siempre el código de la serie, el periodo y la URL de la fuente."))


def _sin_tildes(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


@cache
def catalogo():
    """El catálogo oficial: 17 mil series en unos 7 MB. Se baja una vez y queda en datos/bcrp/."""
    if not CATALOGO.exists():
        CATALOGO.parent.mkdir(parents=True, exist_ok=True)
        r = httpx.get(URL_CATALOGO, timeout=120)
        r.raise_for_status()
        CATALOGO.write_text(r.content.decode("latin-1"), encoding="utf-8")
    df = pd.read_csv(CATALOGO, sep=";", dtype=str).fillna("")
    df = df.rename(columns={"Código de serie": "codigo", "Categoría de serie": "categoria", "Grupo de serie": "grupo",
                            "Nombre de serie": "nombre", "Frecuencia": "frecuencia",
                            "Fecha de actualización": "actualizada", "Fecha de inicio": "inicio"})
    df["texto"] = (df.categoria + " " + df.grupo + " " + df.nombre).map(_sin_tildes)
    return df


def _ficha(codigo):
    fila = catalogo().query("codigo == @codigo")
    if fila.empty:
        raise ToolError(f"No existe el código de serie {codigo!r}. Búsquenlo con buscar_series.")
    f = fila.iloc[0]
    return {"codigo": f.codigo, "nombre": f"{f.grupo} - {f.nombre}", "categoria": f.categoria,
            "frecuencia": f.frecuencia, "inicio": f.inicio, "actualizada": f.actualizada}


@mcp.tool(annotations=SOLO_LECTURA)
def buscar_series(texto: str, frecuencia: str | None = None, limite: int = 10) -> list[dict]:
    """Busca series del BCRP por palabras: todas deben aparecer en la categoría, el grupo o el nombre.

    Ejemplos: "ipc 12 meses", "ipc alimentos y bebidas 12 meses", "pbi agropecuario", "tipo de cambio interbancario
    venta", "reservas internacionales netas", "tasa de referencia". frecuencia: "Diaria", "Mensual", "Trimestral" o
    "Anual". Devuelve el código, el nombre completo, la frecuencia y desde cuándo hay datos. Si no hay resultados,
    prueben con menos palabras.
    """
    df = catalogo()
    m = pd.Series(True, index=df.index)
    for palabra in _sin_tildes(texto).split():
        m &= df.texto.str.contains(re.escape(palabra))
    if frecuencia:
        m &= df.frecuencia.str.lower() == frecuencia.lower()
    # primero las series vigentes y, entre ellas, las de nombre más corto (las más generales)
    sel = df[m]
    orden = sel.assign(vieja=sel.actualizada < "2025", largo=(sel.grupo + sel.nombre).str.len())
    return [_ficha(c) for c in orden.sort_values(["vieja", "largo"]).head(limite).codigo]


# serie ----------------------------------------------------------------------------------------------------------

def _fecha_api(fecha, frecuencia, fin):
    """Lleva "2025-01", "2025-01-15", "2025-T1" o "2025" al formato que pide la API según la frecuencia.

    Si falta el mes o el día, `fin` dice si completar con el final del año o del mes (True) o con el inicio (False).
    """
    m = re.fullmatch(r"(\d{4})(?:-([TQ])?(\d{1,2}))?(?:-(\d{1,2}))?", str(fecha).strip().upper())
    if not m:
        raise ToolError(f"Fecha no válida: {fecha!r}. Usen 2025-01 (mensual), 2025-01-15 (diaria), "
                        "2025-T1 (trimestral) o 2025 (anual).")
    anio, trimestre, n, dia = int(m[1]), m[2], m[3], m[4]
    if frecuencia == "Anual":
        return str(anio)
    if frecuencia == "Trimestral":
        if n is None:
            return f"{anio}-{4 if fin else 1}"
        return f"{anio}-{int(n) if trimestre else (int(n) - 1) // 3 + 1}"
    mes = int(n) if n else (12 if fin else 1)
    if not 1 <= mes <= 12:
        raise ToolError(f"Mes no válido en {fecha!r}.")
    if frecuencia == "Diaria":
        dia = int(dia) if dia else (calendar.monthrange(anio, mes)[1] if fin else 1)
        return f"{anio}-{mes:02d}-{dia:02d}"
    return f"{anio}-{mes}"


def _anio(yy):
    return f"{'19' if int(yy) > 50 else '20'}{yy}"


def _periodo(nombre):
    """ "Ene.2025" -> "2025-01", "01.Oct.26" -> "2026-10-01", "T1.25" -> "2025-T1", "2025" -> "2025"."""
    if m := re.fullmatch(r"(\w{3})\.(\d{4})", nombre):
        return f"{m[2]}-{MESES[m[1].lower()]:02d}"
    if m := re.fullmatch(r"(\d{2})\.(\w{3})\.(\d{2})", nombre):
        return f"{_anio(m[3])}-{MESES[m[2].lower()]:02d}-{m[1]}"
    if m := re.fullmatch(r"T(\d)\.(\d{2})", nombre):
        return f"{_anio(m[2])}-T{m[1]}"
    return nombre


def _numero(texto):
    try:
        return float(texto)
    except (TypeError, ValueError):
        return None   # "n.d." y otros vacíos


@cache
def _bajar(url):
    """Pide JSON a la API. Si limita los pedidos responde HTML: se espera y se reintenta. Lo bajado queda en caché."""
    for intento in range(4):
        try:
            return httpx.get(url, timeout=60).json()
        except (httpx.HTTPError, ValueError):
            time.sleep(2 * (intento + 1))
    raise ToolError("El BCRP no respondió con datos. Esperen unos segundos y reintenten.")


def _serie(codigo, desde, hasta):
    ficha = _ficha(codigo)
    frecuencia = ficha["frecuencia"]
    url = f"{API}/{codigo}/json/{_fecha_api(desde, frecuencia, False)}/{_fecha_api(hasta, frecuencia, True)}"
    datos = [{"periodo": _periodo(p["name"]), "valor": v}
             for p in _bajar(url).get("periods", []) if (v := _numero(p["values"][0])) is not None]
    return {"codigo": codigo, "nombre": ficha["nombre"], "frecuencia": frecuencia, "datos": datos, "fuente": url}


@mcp.tool(annotations=SOLO_LECTURA)
def serie(codigo: str, desde: str, hasta: str) -> dict:
    """Datos de una serie del BCRP entre dos fechas, ambas incluidas.

    Fechas según la frecuencia de la serie: "2025-01" (mensual), "2025-01-15" (diaria), "2025-T1" (trimestral)
    o "2025" (anual). Si no saben el código, búsquenlo antes con buscar_series. Para variaciones, promedios o
    extremos usen resumen. Devuelve [{"periodo", "valor"}] y en "fuente" la URL de la API para verificar la cifra.
    """
    return _serie(codigo, desde, hasta)


# resumen --------------------------------------------------------------------------------------------------------

@mcp.tool(annotations=SOLO_LECTURA)
def resumen(codigo: str, desde: str, hasta: str) -> dict:
    """Resumen de una serie del BCRP entre dos fechas: primer y último dato, cambio, variación %, promedio,
    máximo y mínimo (con su periodo).

    Úsenla para cualquier valor puntual, variación, promedio o extremo: así las cuentas las hace Python y no el
    modelo. Mismas fechas que serie, por ejemplo desde="2025-12", hasta="2026-09". Para el dato de un solo
    periodo, pongan la misma fecha en desde y hasta.
    """
    s = _serie(codigo, desde, hasta)
    d = pd.DataFrame(s["datos"])
    if d.empty:
        raise ToolError(f"La serie {codigo} no tiene datos entre {desde} y {hasta}. Revisen las fechas con serie.")

    def punto(i):
        return {"periodo": d.periodo[i], "valor": round(float(d.valor[i]), 4)}

    primero, ultimo = d.valor.iloc[0], d.valor.iloc[-1]
    return {"codigo": codigo, "nombre": s["nombre"], "frecuencia": s["frecuencia"], "n": len(d),
            "primero": punto(d.index[0]), "ultimo": punto(d.index[-1]),
            "cambio": round(float(ultimo - primero), 4),
            "variacion_pct": round(float((ultimo / primero - 1) * 100), 4) if primero else None,
            "promedio": round(float(d.valor.mean()), 4),
            "maximo": punto(d.valor.idxmax()), "minimo": punto(d.valor.idxmin()), "fuente": s["fuente"]}


# Herramienta propia 1 · agregar_anual: del dato mensual al año de la ENAHO ----------------------------------------

OPERACIONES = {"promedio": lambda v: v.mean(), "suma": lambda v: v.sum(), "fin": lambda v: v.iloc[-1],
               "inicio": lambda v: v.iloc[0], "maximo": lambda v: v.max(), "minimo": lambda v: v.min()}


def _anio_de(periodo):
    return int(str(periodo)[:4])


def _completo(grupo, frecuencia):
    """Un año está completo si tiene todos sus periodos (12 meses, 4 trimestres) o, si es diaria, de enero a
    diciembre."""
    if frecuencia in PERIODOS_POR_ANIO:
        return len(grupo) == PERIODOS_POR_ANIO[frecuencia]
    meses = grupo.periodo.str[5:7].astype(int)
    return bool(meses.min() == 1 and meses.max() == 12)


@mcp.tool(annotations=SOLO_LECTURA)
def agregar_anual(codigo: str, desde: int, hasta: int, operacion: str = "promedio") -> dict:
    """Convierte una serie mensual, trimestral o diaria del BCRP en valores anuales, calculados en Python.

    Úsenla cuando la pregunta sea por año o haya que comparar con datos anuales como la ENAHO (pobreza 2024):
    «inflación promedio de 2024», «exportaciones de todo 2023», «inflación a diciembre de cada año».
    operacion: "promedio" (tasas, precios, tipo de cambio), "suma" (flujos en millones, como exportaciones),
    "fin" (último dato del año: inflación a 12 meses de diciembre, saldos), "inicio", "maximo" o "minimo".
    Ejemplo: agregar_anual(codigo="PN09822PM", desde=2019, hasta=2024, operacion="promedio").
    Devuelve por año el valor, cuántos periodos tuvo, si el año está completo, el cambio y la variación % frente al
    año anterior. Los años incompletos se marcan con completo=false y se listan en "advertencias": no los
    comparen con años completos. Si la serie ya es anual, usen serie o resumen.
    """
    if operacion not in OPERACIONES:
        raise ToolError(f"Operación no válida: {operacion!r}. Usen una de {', '.join(OPERACIONES)}.")
    if hasta < desde:
        raise ToolError(f"El año final ({hasta}) es anterior al inicial ({desde}).")
    frecuencia = _ficha(codigo)["frecuencia"]
    if frecuencia == "Anual":
        raise ToolError(f"La serie {codigo} ya es anual: usen serie o resumen con desde={desde}, hasta={hasta}.")
    s = _serie(codigo, str(desde), str(hasta))
    d = pd.DataFrame(s["datos"])
    if d.empty:
        raise ToolError(f"La serie {codigo} no tiene datos entre {desde} y {hasta}.")
    d["anio"] = d.periodo.map(_anio_de)

    anios, advertencias, anterior = [], [], None
    for anio, g in d.groupby("anio", sort=True):
        valor = round(float(OPERACIONES[operacion](g.valor)), 4)
        completo = _completo(g, frecuencia)
        fila = {"anio": int(anio), "valor": valor, "n_periodos": len(g), "completo": completo,
                "desde": g.periodo.iloc[0], "hasta": g.periodo.iloc[-1]}
        if anterior is not None and anterior["anio"] == anio - 1:
            fila["cambio"] = round(valor - anterior["valor"], 4)
            fila["variacion_pct"] = round((valor / anterior["valor"] - 1) * 100, 4) if anterior["valor"] else None
        if not completo:
            advertencias.append(f"{anio} está incompleto: {len(g)} periodos, de {fila['desde']} a {fila['hasta']}.")
        anios.append(fila)
        anterior = fila
    return {"codigo": codigo, "nombre": s["nombre"], "frecuencia_original": frecuencia, "operacion": operacion,
            "anios": anios, "advertencias": advertencias, "fuente": s["fuente"]}


# Herramienta propia 2 · graficar_series: el gráfico del BCRP para el informe ----------------------------------------

def _a_fecha(periodo):
    """ "2024" -> 2024-07-01 (mitad del año), "2024-T2" -> 2024-05-15, "2024-03" -> 2024-03-01, "2024-03-05"."""
    p = str(periodo)
    if re.fullmatch(r"\d{4}", p):
        return pd.Timestamp(int(p), 7, 1)
    if m := re.fullmatch(r"(\d{4})-T(\d)", p):
        return pd.Timestamp(int(m[1]), 3 * int(m[2]) - 1, 15)
    return pd.Timestamp(p)


def _nombre_archivo(archivo):
    base = re.sub(r"[^a-z0-9_-]+", "_", _sin_tildes(Path(archivo).stem)).strip("_")
    if not base:
        raise ToolError(f"Nombre de archivo no válido: {archivo!r}.")
    return f"{base}.png"


@mcp.tool(annotations={"readOnlyHint": False, "openWorldHint": True})
def graficar_series(codigos: list[str], desde: str, hasta: str, titulo: str, archivo: str, unidad: str = "",
                    etiquetas: list[str] | None = None) -> dict:
    """Grafica una o varias series del BCRP (misma frecuencia) y guarda el PNG en figuras/ para el informe.

    Úsenla cuando pidan un gráfico de indicadores del BCRP. codigos: hasta 4 códigos, por ejemplo
    ["PN01273PM", "PN09822PM"]; desde/hasta con el formato de serie ("2019-01", "2024-12"); titulo: lo que muestra
    y cuándo; archivo: nombre corto, por ejemplo "bcrp_inflacion_alimentos" (se guarda como figuras/<archivo>.png);
    unidad: la del eje, por ejemplo "var. % 12 meses"; etiquetas: nombres cortos para la leyenda.
    El gráfico lleva la fuente con los códigos. Devuelve la ruta del archivo, las URL de la API y el primer y último
    dato de cada serie, para citarlos en el texto.
    """
    if not 1 <= len(codigos) <= 4:
        raise ToolError("Grafiquen entre 1 y 4 series a la vez.")
    if etiquetas and len(etiquetas) != len(codigos):
        raise ToolError("Debe haber una etiqueta por cada código.")
    series = [_serie(c, desde, hasta) for c in codigos]
    frecuencias = {s["frecuencia"] for s in series}
    if len(frecuencias) > 1:
        raise ToolError(f"Las series tienen frecuencias distintas ({', '.join(sorted(frecuencias))}): "
                        "llévenlas a años con agregar_anual o grafiquen por separado.")
    vacias = [s["codigo"] for s in series if not s["datos"]]
    if vacias:
        raise ToolError(f"Sin datos entre {desde} y {hasta} para {', '.join(vacias)}.")

    FIGURAS.mkdir(exist_ok=True)
    ruta = FIGURAS / _nombre_archivo(archivo)
    colores = ["#1f4e79", "#c0504d", "#6a8e23", "#7f6084"]
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    resumen_series = []
    for i, s in enumerate(series):
        d = pd.DataFrame(s["datos"])
        x = d.periodo.map(_a_fecha)
        nombre = etiquetas[i] if etiquetas else s["nombre"].split(" - ")[-1]
        marcador = "o" if len(d) <= 30 else None
        ax.plot(x, d.valor, color=colores[i], lw=2, marker=marcador, ms=4, label=f"{nombre} ({s['codigo']})")
        ax.annotate(f"{d.valor.iloc[-1]:.1f}", (x.iloc[-1], d.valor.iloc[-1]), textcoords="offset points",
                    xytext=(6, 0), va="center", fontsize=8, color=colores[i])
        resumen_series.append({"codigo": s["codigo"], "nombre": s["nombre"], "n": len(d),
                               "primero": s["datos"][0], "ultimo": s["datos"][-1], "fuente": s["fuente"]})
    if ax.get_ylim()[0] < 0 < ax.get_ylim()[1]:
        ax.axhline(0, color="#555555", lw=0.8)
    if frecuencias == {"Anual"}:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    ax.set_ylabel(unidad)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="best")
    fig.text(0.01, 0.01, f"Fuente: BCRP, series {', '.join(codigos)} (estadisticas.bcrp.gob.pe). "
                         f"Periodo: {desde} a {hasta}.", fontsize=7, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(ruta)
    plt.close(fig)
    archivo_rel = ruta.relative_to(RAIZ).as_posix() if ruta.is_relative_to(RAIZ) else str(ruta)
    return {"archivo": archivo_rel, "frecuencia": frecuencias.pop(), "series": resumen_series,
            "fuente": [s["fuente"] for s in series]}


# Contexto internacional (de la clase 7): Banco Mundial ------------------------------------------------------------

@mcp.tool(annotations=SOLO_LECTURA)
def comparar_paises(indicador: str = "NY.GDP.MKTP.KD.ZG", paises: str = "PER;CHL;COL;MEX;BRA",
                    desde: int = 2015, hasta: int = 2025) -> dict:
    """Compara al Perú con otros países con un indicador anual del Banco Mundial.

    Úsenla cuando la pregunta compare países o pida contexto internacional («¿creció el Perú más que Chile?»);
    para cifras del Perú usen las series del BCRP. Indicadores útiles: "NY.GDP.MKTP.KD.ZG" (crecimiento del PBI
    real, %), "FP.CPI.TOTL.ZG" (inflación, %), "NY.GDP.PCAP.CD" (PBI per cápita, US$), "SL.UEM.TOTL.ZS"
    (desempleo, %), "NV.AGR.TOTL.ZS" (agricultura, % del PBI). paises: códigos ISO3 separados por ";".
    Devuelve por país los datos, el promedio y el último dato; el ranking por promedio; y la URL de la fuente.
    """
    if not re.fullmatch(r"[A-Za-z0-9.]+", indicador) or not re.fullmatch(r"[A-Za-z]{2,3}(;[A-Za-z]{2,3})*", paises):
        raise ToolError(f"Revisen el indicador {indicador!r} y los países {paises!r} (por ejemplo PER;CHL;COL).")
    url = f"{BANCO_MUNDIAL}/country/{paises.upper()}/indicator/{indicador}?format=json&date={desde}:{hasta}&per_page=2000"
    try:
        r = httpx.get(url, timeout=60).json()
    except (httpx.HTTPError, ValueError):
        raise ToolError("El Banco Mundial no respondió. Reintenten en unos segundos.")
    filas = r[1] if len(r) > 1 and r[1] else []
    filas = [f for f in filas if f["value"] is not None]
    if not filas:
        raise ToolError(f"El Banco Mundial no tiene datos de {indicador!r} para {paises!r} entre {desde} y {hasta}.")

    por_pais = {}
    for f in sorted(filas, key=lambda f: f["date"]):
        p = por_pais.setdefault(f["countryiso3code"], {"pais": f["country"]["value"], "codigo": f["countryiso3code"],
                                                       "datos": []})
        p["datos"].append({"periodo": f["date"], "valor": round(f["value"], 4)})
    for p in por_pais.values():
        p["promedio"] = round(sum(x["valor"] for x in p["datos"]) / len(p["datos"]), 4)
        p["ultimo"] = p["datos"][-1]
    ranking = sorted(por_pais.values(), key=lambda p: p["promedio"], reverse=True)
    return {"indicador": indicador, "nombre": filas[0]["indicator"]["value"], "paises": list(por_pais.values()),
            "ranking_promedio": [p["codigo"] for p in ranking], "fuente": url}


# Recursos -------------------------------------------------------------------------------------------------------

@mcp.resource("bcrp://serie/{codigo}", mime_type="application/json")
def ficha(codigo: str) -> str:
    """Ficha de una serie del BCRP: nombre, categoría, frecuencia, desde cuándo hay datos y última actualización."""
    return json.dumps(_ficha(codigo), ensure_ascii=False)


@mcp.resource("bcrp://series-clave", mime_type="application/json")
def series_clave() -> str:
    """Los códigos de las series que más usa este proyecto, para no tener que buscarlos."""
    return json.dumps({
        "PN01273PM": "Inflación de Lima Metropolitana, var. % 12 meses (mensual)",
        "PN09822PM": "IPC Alimentos y Bebidas de Lima Metropolitana, var. % 12 meses (mensual)",
        "PN01271PM": "IPC de Lima Metropolitana, var. % mensual (mensual)",
        "PM04968AA": "PBI agropecuario, var. % real (anual)",
        "PM04983AA": "PBI, var. % real (anual)",
        "PN01713AM": "PBI agropecuario, var. % interanual (mensual)",
        "PM40121BA": "Exportaciones no tradicionales agropecuarias, millones US$ FOB (anual)",
        "PM40076BA": "Exportaciones tradicionales agrícolas, millones US$ FOB (anual)",
        "PD04722MM": "Tasa de referencia de la política monetaria, % (mensual)",
        "PD04638PD": "Tipo de cambio interbancario venta, S/ por US$ (diaria)",
        "PN38714BM": "Exportaciones FOB, millones US$ (mensual)",
        "PN38063GM": "Tasa de desempleo de Lima Metropolitana, % (mensual)",
    }, ensure_ascii=False, indent=1)


# Prompts --------------------------------------------------------------------------------------------------------

@mcp.prompt
def informe(tema: str) -> str:
    """Informe de 5 viñetas sobre un tema económico del Perú, con cada cifra verificable."""
    return (f"Escribe un informe de 5 viñetas sobre «{tema}» con datos oficiales del BCRP. "
            "Primero busca los códigos con buscar_series; para cada cifra usa resumen, serie o agregar_anual, nunca "
            "calcules a mano. En cada viñeta cita el código de la serie, el periodo y la URL de la fuente. Si hace "
            "falta contexto internacional, usa comparar_paises. Si una cifra no está disponible, dilo en vez de "
            "estimarla.")


@mcp.prompt
def investigacion(pregunta: str) -> str:
    """Investigación que combina las series del BCRP (este MCP) con la ENAHO 2024 (las skills del proyecto)."""
    return (f"Investiga: «{pregunta}».\n"
            "1. Escribe primero un plan corto: qué cifras salen del BCRP y cuáles de la ENAHO 2024.\n"
            "2. BCRP: busca los códigos con buscar_series y saca cada cifra con resumen, serie o agregar_anual; "
            "guarda al menos un gráfico con graficar_series.\n"
            "3. ENAHO: usa las skills limpiando-enaho, graficando-enaho y mapeando-enaho; toda cifra ponderada.\n"
            "4. Escribe informes/informe_final.md con pregunta, fuentes y metodología, al menos 3 hallazgos, los "
            "gráficos y el mapa, interpretación, limitaciones y reproducibilidad (códigos de serie, scripts y "
            "archivos).\n"
            "5. No presentes asociaciones como causas. Si una herramienta falla o no hay datos, dilo; no inventes.")


if __name__ == "__main__":
    mcp.run()
