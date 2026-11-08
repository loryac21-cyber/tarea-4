"""Comprueba las respuestas esperadas del BCRP por un camino independiente del MCP.

    uv run evaluacion/verificar_verdades.py

No importa mcp/server.py: pide cada serie directo a la API pública del BCRP con httpx, hace la cuenta con Python
puro y la compara con la columna `verdad` de preguntas.csv. Imprime también el enlace a la tabla HTML del BCRP para
mirarla a mano. Las verdades de la ENAHO no se recalculan aquí: vienen de la tabla de validación de la sesión 16
y del informe técnico del INEI (ver la columna fuente_verdad), no de nuestras skills.
"""
import csv
import statistics
import time
from pathlib import Path

import httpx

AQUI = Path(__file__).parent
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/json/{desde}/{hasta}"
WEB = "https://estadisticas.bcrp.gob.pe/estadisticas/series/{frec}/resultados/{codigo}/html/{desde}/{hasta}/"

# Cómo se obtiene cada verdad del BCRP: (código, desde, hasta, operación, frecuencia de la web)
CALCULOS = {
    "bcrp_agro_2024": ("PM04968AA", "2024", "2024", "unico", "anuales"),
    "bcrp_alim_dic24": ("PN09822PM", "2024-12", "2024-12", "unico", "mensuales"),
    "bcrp_alim_prom22": ("PN09822PM", "2022-1", "2022-12", "promedio", "mensuales"),
    "bcrp_agroexport_2024": ("PM40121BA", "2024", "2024", "unico", "anuales"),
    "mix_alim_rural": ("PN09822PM", "2024-12", "2024-12", "unico", "mensuales"),
    "mix_agro_brecha": ("PM04968AA", "2024", "2024", "unico", "anuales"),
}


def valores(codigo, desde, hasta):
    """La API limita los pedidos seguidos (responde HTML en vez de JSON): se espera y se reintenta."""
    for intento in range(6):
        try:
            r = httpx.get(API.format(codigo=codigo, desde=desde, hasta=hasta), timeout=60).json()
            return [float(p["values"][0]) for p in r["periods"] if p["values"][0] not in ("n.d.", "")]
        except (httpx.HTTPError, ValueError):
            time.sleep(3 * (intento + 1))
    raise SystemExit(f"El BCRP no respondió con datos para {codigo}. Reintenten en unos minutos.")


def main():
    preguntas = {f["id"]: f for f in csv.DictReader(open(AQUI / "preguntas.csv", encoding="utf-8"))}
    todo_ok = True
    for id_, (codigo, desde, hasta, op, frec) in CALCULOS.items():
        v = valores(codigo, desde, hasta)
        calculado = statistics.fmean(v) if op == "promedio" else v[0]
        columna = "verdad_bcrp" if id_.startswith("mix_") else "verdad"
        texto = preguntas[id_][columna]
        esperado = float(texto)
        decimales = len(texto.split(".")[1]) if "." in texto else 0
        ok = round(calculado, decimales) == round(esperado, decimales)   # la verdad está redondeada a esos decimales
        todo_ok &= ok
        print(f"{'OK ' if ok else 'MAL'} {id_:22} {codigo} {desde}..{hasta} ({op}, {len(v)} datos): {calculado:.4f} "
              f"frente a {esperado:.4f}\n    {WEB.format(frec=frec, codigo=codigo, desde=desde, hasta=hasta)}")
    print("\nTodas las verdades del BCRP coinciden con la API." if todo_ok else "\nHay verdades que no coinciden.")


if __name__ == "__main__":
    main()
