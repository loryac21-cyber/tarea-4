"""¿Mejoran el MCP y las skills las respuestas de Claude Code? Las mismas 10 preguntas en dos modos.

    uv run evaluacion/evaluar.py                     # los dos modos, con sonnet
    uv run evaluacion/evaluar.py --modos con --solo enaho_cusco --modelo haiku

Modo A, «sin»: Claude Code sin herramientas (--tools ""), sin MCP (--strict-mcp-config) y en una carpeta temporal
vacía, fuera del proyecto: no ve el CLAUDE.md, las skills, los datos ni los resultados ya calculados.
Modo B, «con»: Claude Code con el MCP bcrp, las skills del proyecto y las herramientas mínimas para correrlas
(PowerShell/Bash para «uv run», Read, Glob, Grep, Skill), en una copia del proyecto SIN la carpeta evaluacion/ (las
respuestas esperadas), informes/ ni evidencias_ia/.

En los dos modos: el mismo modelo, la misma instrucción, una sesión nueva por pregunta (--no-session-persistence) y
una respuesta en JSON validada con --json-schema. Escribe evaluacion/resultados.csv, evaluacion/resumen.md y la
transcripción de cada pregunta en evidencias_ia/evaluacion/.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente.registro import RAIZ, a_markdown, correr_claude, herramientas_shell, permisos_uv  # noqa: E402

AQUI = Path(__file__).parent
EVIDENCIAS = RAIZ / "evidencias_ia" / "evaluacion"
TEMPORAL = Path(tempfile.gettempdir()) / "tarea4_evaluacion"

INSTRUCCION = ("Responde la pregunta con datos oficiales. Si no puedes saber una cifra con certeza, pon null: no "
               "estimes. En «fuente» di de dónde sale cada cifra (código de serie, archivo, documento o cálculo).\n\n")
ESQUEMA_SIMPLE = {"type": "object", "required": ["valor", "fuente"],
                  "properties": {"valor": {"type": ["number", "null"]}, "unidad": {"type": "string"},
                                 "fuente": {"type": "string"}}}
ESQUEMA_MIXTO = {"type": "object", "required": ["valor_bcrp", "valor_enaho", "afirmacion", "interpretacion", "fuente"],
                 "properties": {"valor_bcrp": {"type": ["number", "null"]}, "valor_enaho": {"type": ["number", "null"]},
                                "afirmacion": {"type": ["boolean", "null"]}, "interpretacion": {"type": "string"},
                                "fuente": {"type": "string"}}}
NO_COPIAR = {".git", ".venv", "evaluacion", "informes", "evidencias_ia", "__pycache__", ".pytest_cache"}


def preparar_espacios():
    """Carpeta vacía para el modo «sin» y copia del proyecto sin respuestas para el modo «con»."""
    sin = TEMPORAL / "sin_herramientas"
    con = TEMPORAL / "con_herramientas"
    shutil.rmtree(TEMPORAL, ignore_errors=True)
    sin.mkdir(parents=True)
    shutil.copytree(RAIZ, con, ignore=lambda d, nombres: [n for n in nombres if n in NO_COPIAR])
    if not (con / "salidas" / "hogares_2024.parquet").exists():
        print("Aviso: no hay salidas/*.parquet; en el modo «con» la skill de limpieza tendrá que correr primero.")
    return {"sin": sin, "con": con}


def flags(modo, espacio):
    if modo == "sin":
        return ["--tools", "", "--strict-mcp-config"]
    herramientas = ",".join([*herramientas_shell(), "Read", "Glob", "Grep", "Skill"])
    return ["--strict-mcp-config", "--mcp-config", str(espacio / ".mcp.json"), "--tools", herramientas,
            "--allowedTools", "mcp__bcrp", "Skill", *permisos_uv(), "Read", "Glob", "Grep"]


def dentro(valor, verdad, tolerancia):
    return valor is not None and abs(float(valor) - float(verdad)) <= float(tolerancia) + 1e-9


def calificar(q, r):
    """Simples: acierta / se equivoca / no sabe. Mixtas: las dos cifras dentro de su tolerancia Y la afirmación
    correcta (exactitud de los datos y coherencia de la interpretación); si solo una parte está bien, «parcial»."""
    if r is None:
        return "sin respuesta", ""
    if q.tipo != "mixta":
        if r.get("valor") is None:
            return "no sabe", ""
        return ("acierta" if dentro(r["valor"], q.verdad, q.tolerancia) else "se equivoca"), ""
    partes = {"bcrp": dentro(r.get("valor_bcrp"), q.verdad_bcrp, q.tolerancia_bcrp),
              "enaho": dentro(r.get("valor_enaho"), q.verdad_enaho, q.tolerancia_enaho),
              "interpretacion": r.get("afirmacion") is not None
              and r.get("afirmacion") == (str(q.afirmacion_esperada).lower() == "true")}
    detalle = ", ".join(f"{k} {'bien' if v else 'mal'}" for k, v in partes.items())
    if all(partes.values()):
        return "acierta", detalle
    if all(r.get(k) is None for k in ("valor_bcrp", "valor_enaho")):
        return "no sabe", detalle
    return ("parcial" if any(partes.values()) else "se equivoca"), detalle


def preguntar(q, modo, espacios, modelo):
    esquema = ESQUEMA_MIXTO if q.tipo == "mixta" else ESQUEMA_SIMPLE
    prompt = INSTRUCCION + q.pregunta
    r = correr_claude(prompt, cwd=espacios[modo], modelo=modelo, flags=flags(modo, espacios[modo]),
                      jsonl=EVIDENCIAS / f"{q.id}__{modo}.jsonl", timeout=900, esquema=esquema)
    (EVIDENCIAS / f"{q.id}__{modo}.md").write_text(a_markdown(r["eventos"], f"Evaluación · {q.id} · modo {modo}", prompt),
                                                  encoding="utf-8")
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modos", nargs="+", default=["sin", "con"], choices=["sin", "con"])
    ap.add_argument("--modelo", default="sonnet")
    ap.add_argument("--paralelo", type=int, default=3)
    ap.add_argument("--solo", nargs="*", help="ids de preguntas, para probar")
    a = ap.parse_args()

    preguntas = pd.read_csv(AQUI / "preguntas.csv", dtype={"afirmacion_esperada": str})
    if a.solo:
        preguntas = preguntas[preguntas.id.isin(a.solo)]
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    espacios = preparar_espacios()
    os.environ["UV_PROJECT_ENVIRONMENT"] = str(RAIZ / ".venv")   # la copia usa el mismo entorno de uv
    casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
    print(f"{len(casos)} llamadas a claude -p con {a.modelo}, {a.paralelo} a la vez...")
    with ThreadPoolExecutor(a.paralelo) as ex:
        respuestas = list(ex.map(lambda c: preguntar(c[0], c[1], espacios, a.modelo), casos))

    filas = []
    for (q, modo), r in zip(casos, respuestas):
        est = r["estructurado"]
        resultado, detalle = calificar(q, est)
        usadas = r["herramientas"]
        if q.tipo == "mixta":
            esperada = f"BCRP {q.verdad_bcrp} · ENAHO {q.verdad_enaho} · afirmación {q.afirmacion_esperada}"
            generada = (f"BCRP {est.get('valor_bcrp')} · ENAHO {est.get('valor_enaho')} · afirmación "
                        f"{est.get('afirmacion')}" if est else None)
        else:
            esperada, generada = q.verdad, (est or {}).get("valor")
        filas.append({
            "id": q.id, "tipo": q.tipo, "modo": modo, "modelo": a.modelo, "pregunta": q.pregunta,
            "respuesta_esperada": esperada, "respuesta_generada": generada,
            "interpretacion": (est or {}).get("interpretacion", ""), "fuente": (est or {}).get("fuente", ""),
            "herramientas_mcp": ";".join(sorted({u.split("__")[-1] for u in usadas if u.startswith("mcp__")})),
            "skills": ";".join(sorted({u.split(":", 1)[1] for u in usadas if u.startswith("Skill:")})),
            "n_llamadas_herramientas": len(usadas), "resultado": resultado, "detalle_mixta": detalle,
            "segundos": r["segundos"], "turnos": r["turnos"], "costo_usd": r["costo_usd"],
            "error": r["error"], "transcripcion": f"evidencias_ia/evaluacion/{q.id}__{modo}.md"})
    res = pd.DataFrame(filas)
    salida = AQUI / ("resultados.csv" if not a.solo else "resultados_prueba.csv")
    res.to_csv(salida, index=False, encoding="utf-8")

    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos_promedio"] = res.groupby("modo").segundos.mean().round(1)
    tabla["turnos_promedio"] = res.groupby("modo").turnos.mean().round(1)
    por_tipo = res.assign(ok=res.resultado.eq("acierta")).pivot_table(index="tipo", columns="modo", values="ok",
                                                                       aggfunc="sum")
    pivote = res.pivot(index="id", columns="modo", values="resultado")
    texto = ["# Resumen automático de la evaluación", "", f"Modelo: `{a.modelo}`. Archivo: `{salida.name}`.", "",
             "## Por modo", "", tabla.to_markdown(), "", "## Aciertos por tipo de pregunta", "", por_tipo.to_markdown(),
             "", "## Resultado por pregunta", "", pivote.to_markdown(), ""]
    (AQUI / ("resumen.md" if not a.solo else "resumen_prueba.md")).write_text("\n".join(texto), encoding="utf-8")
    print("\n".join(texto))


if __name__ == "__main__":
    main()
