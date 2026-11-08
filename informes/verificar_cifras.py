"""Verifica cifras del informe final por un camino independiente del agente.

    uv run informes/verificar_cifras.py

ENAHO: no usa las skills ni sus bases. Lee los .dta directamente de los zip del INEI con pandas, aplica el criterio
oficial (pobreza <= 2, área por estrato, factor07 × mieperho) en pocas líneas y compara con lo que dice el informe y
con la cifra publicada por el INEI / la sesión 16.
BCRP: no usa el MCP. Pide las series a la API pública con httpx y deja el enlace a la tabla HTML para revisarla a mano.
Escribe informes/verificacion_cifras.csv; la tabla comentada está en informes/verificacion_cifras.md.
"""
import io
import statistics
import time
import zipfile
from pathlib import Path

import httpx
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{c}/json/{d}/{h}"


def bcrp(codigo, desde, hasta):
    for intento in range(6):
        try:
            r = httpx.get(API.format(c=codigo, d=desde, h=hasta), timeout=60).json()
            return [float(p["values"][0]) for p in r["periods"]]
        except (httpx.HTTPError, ValueError):
            time.sleep(3 * (intento + 1))
    raise SystemExit(f"El BCRP no respondió para {codigo}")


def sumaria():
    with zipfile.ZipFile(RAIZ / "datos" / "enaho" / "966-Modulo34.zip") as z:
        df = pd.read_stata(io.BytesIO(z.read("966-Modulo34/sumaria-2024.dta")), convert_categoricals=False)
    df.columns = [c.lower() for c in df.columns]
    df["peso"] = df.factor07 * df.mieperho
    df["pobre"] = df.pobreza <= 2
    return df


def pct(d):
    return float((d.pobre * d.peso).sum() / d.peso.sum() * 100)


def main():
    s = sumaria()
    rural, urbana = pct(s[s.estrato >= 6]), pct(s[s.estrato <= 5])
    caj = pct(s[s.ubigeo.str[:2] == "06"])
    pobres = s.assign(pp=s.pobre * s.peso)
    urbana_share = float(pobres[pobres.estrato <= 5].pp.sum() / pobres.pp.sum() * 100)
    alim = bcrp("PN09822PM", "2022-1", "2022-12")
    alim_dic24 = bcrp("PN09822PM", "2024-12", "2024-12")[0]
    agro = bcrp("PM04968AA", "2024", "2024")[0]

    filas = [
        ("ENAHO", "Pobreza rural 2024: 39.30 %", 39.30, rural, 39.3,
         "Recalculado de sumaria-2024.dta (estrato >= 6, factor07 × mieperho); INEI publica 39.3 %"),
        ("ENAHO", "Pobreza urbana 2024: 24.81 %", 24.81, urbana, 24.8,
         "Recalculado de sumaria-2024.dta (estrato <= 5); INEI publica 24.8 %"),
        ("ENAHO", "Cajamarca, la más alta: 45.01 %", 45.01, caj, 45.0,
         "Recalculado de sumaria-2024.dta (ubigeo[:2] == '06'); referencia de la sesión 16: 45.0 %"),
        ("ENAHO", "El 72.74 % de las personas pobres vive en el área urbana", 72.74, urbana_share, None,
         "Recalculado: pobres urbanos expandidos / total de pobres expandidos"),
        ("BCRP", "Inflación de alimentos y bebidas de Lima, promedio 2022: 10.78 %", 10.78, statistics.fmean(alim),
         None, "Promedio de los 12 datos de PN09822PM en 2022, pedidos a la API sin el MCP"),
        ("BCRP", "Inflación de alimentos y bebidas de Lima a diciembre de 2024: 1.25 %", 1.25, alim_dic24, None,
         "PN09822PM, 2024-12, API del BCRP sin el MCP"),
        ("BCRP", "PBI agropecuario: +5.57 % en 2024", 5.57, agro, None,
         "Serie anual oficial PM04968AA (el informe lo calculó con el índice mensual PN01755AM)"),
    ]
    out = pd.DataFrame(filas, columns=["fuente", "afirmacion", "valor_informe", "valor_recalculado",
                                       "valor_publicado", "procedimiento"])
    out["valor_recalculado"] = out.valor_recalculado.round(4)
    out["diferencia"] = (out.valor_informe - out.valor_recalculado).round(4)
    out["coincide"] = out.diferencia.abs() <= 0.005 + 1e-9
    out.to_csv(RAIZ / "informes" / "verificacion_cifras.csv", index=False, encoding="utf-8")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
