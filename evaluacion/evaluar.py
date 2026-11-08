"""¿Mejoran el MCP y las skills las respuestas de Claude Code? Las mismas 10 preguntas en dos modos.

    uv run evaluacion/evaluar.py                                    # experimento principal, los dos modos
    uv run evaluacion/evaluar.py --con-salidas --etiqueta con_salidas_previas    # variante: salidas ya calculadas
    uv run evaluacion/evaluar.py --modos sin --sin-null --etiqueta sin_null     # experimento: sin la salida «null»
    uv run evaluacion/evaluar.py --modos con --solo enaho_cusco --etiqueta prueba

Modo A, «sin»: Claude Code sin herramientas (--tools ""), sin MCP (--strict-mcp-config) y en una carpeta temporal
vacía, fuera del proyecto: no ve el CLAUDE.md, las skills, los datos ni los resultados ya calculados.
Modo B, «con»: Claude Code con el MCP bcrp, las skills del proyecto y las herramientas mínimas para correrlas
(PowerShell/Bash para «uv run», Read, Glob, Grep, Skill). Cada pregunta corre en su propia copia del proyecto SIN
evaluacion/ (las respuestas esperadas), informes/, evidencias_ia/ ni salidas/, figuras/ o mapas/: solo el código y
los datos originales del INEI, así que las cifras de la ENAHO tienen que salir de las skills en esa misma sesión.

En los dos modos: el mismo modelo, la misma instrucción, una sesión nueva por pregunta (--no-session-persistence) y
una respuesta en JSON validada con --json-schema. Escribe evaluacion/resultados[_etiqueta].csv,
evaluacion/resumen[_etiqueta].md y la transcripción de cada pregunta en evidencias_ia/evaluacion/<etiqueta>/.
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
from agente.registro import (RAIZ, a_markdown, correr_claude, herramientas_shell, herramientas_usadas,  # noqa: E402
                             permisos_uv, resumen_herramientas)

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


def preparar_espacios(ids, con_salidas):
    """Carpeta vacía para el modo «sin» y, para el modo «con», una copia del proyecto por pregunta, sin respuestas.

    Por defecto la copia tampoco lleva salidas/, figuras/ ni mapas/: solo los datos originales del INEI y el código,
    así que para responder sobre la ENAHO el agente tiene que correr las skills (empezando por limpiando-enaho).
    Con --con-salidas se copian también las salidas ya calculadas (la primera corrida del experimento).
    """
    shutil.rmtree(TEMPORAL, ignore_errors=True)
    sin = TEMPORAL / "sin_herramientas"
    sin.mkdir(parents=True)
    excluir = NO_COPIAR | (set() if con_salidas else {"salidas", "figuras", "mapas"})
    con = {}
    for id_ in ids:
        con[id_] = TEMPORAL / f"con_{id_}"
        shutil.copytree(RAIZ, con[id_], ignore=lambda d, nombres: [n for n in nombres if n in excluir])
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


def preguntar(q, modo, espacios, modelo, instruccion, carpeta):
    esquema = ESQUEMA_MIXTO if q.tipo == "mixta" else ESQUEMA_SIMPLE
    prompt = instruccion + q.pregunta
    espacio = espacios["sin"] if modo == "sin" else espacios["con"][q.id]
    r = correr_claude(prompt, cwd=espacio, modelo=modelo, flags=flags(modo, espacio),
                      jsonl=carpeta / f"{q.id}__{modo}.jsonl", timeout=900, esquema=esquema)
    (carpeta / f"{q.id}__{modo}.md").write_text(a_markdown(r["eventos"], f"Evaluación · {q.id} · modo {modo}", prompt),
                                               encoding="utf-8")
    return r


def leer_transcripcion(ruta, anterior, id_, modo):
    """Lo mismo que devuelve correr_claude, pero leído de un .jsonl guardado. El tiempo se toma del CSV anterior si
    existe (se midió de punta a punta); si no, de la duración que informa Claude Code."""
    eventos = [json.loads(x) for x in ruta.read_text(encoding="utf-8").splitlines() if x.strip()]
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    segundos = round((final.get("duration_ms") or 0) / 1000, 1)
    if anterior is not None and (id_, modo) in anterior.index:
        segundos = float(anterior.loc[(id_, modo), "segundos"])
    return {"eventos": eventos, "resultado": final.get("result", ""), "estructurado": final.get("structured_output"),
            "segundos": segundos, "turnos": final.get("num_turns"), "costo_usd": final.get("total_cost_usd"),
            "error": "" if final and not final.get("is_error") else "sin resultado",
            "herramientas": herramientas_usadas(eventos)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modos", nargs="+", default=["sin", "con"], choices=["sin", "con"])
    ap.add_argument("--modelo", default="sonnet")
    ap.add_argument("--paralelo", type=int, default=3)
    ap.add_argument("--solo", nargs="*", help="ids de preguntas, para probar")
    ap.add_argument("--con-salidas", action="store_true",
                    help="modo «con» con salidas/ ya calculadas (por defecto, solo datos originales)")
    ap.add_argument("--sin-null", action="store_true",
                    help="experimento: quitar de la instrucción la salida «pon null, no estimes»")
    ap.add_argument("--etiqueta", default="", help="sufijo de resultados_<etiqueta>.csv y carpeta de evidencias")
    ap.add_argument("--solo-resumen", action="store_true", help="rehacer el resumen desde el CSV, sin preguntar")
    ap.add_argument("--desde-transcripciones", action="store_true",
                    help="rehacer el CSV desde los .jsonl ya guardados, sin volver a llamar a Claude")
    a = ap.parse_args()
    sufijo = f"_{a.etiqueta}" if a.etiqueta else ""
    salida = AQUI / f"resultados{sufijo}.csv"
    if a.solo_resumen:
        res = pd.read_csv(salida)
        return resumir(res, res.modelo.iloc[0], salida)

    preguntas = pd.read_csv(AQUI / "preguntas.csv", dtype={"afirmacion_esperada": str})
    if a.solo:
        preguntas = preguntas[preguntas.id.isin(a.solo)]
    carpeta = EVIDENCIAS / (a.etiqueta or "principal")
    carpeta.mkdir(parents=True, exist_ok=True)
    instruccion = INSTRUCCION.replace("Si no puedes saber una cifra con certeza, pon null: no estimes. ", "") \
        if a.sin_null else INSTRUCCION
    casos = [(q, m) for q in preguntas.itertuples() for m in a.modos]
    if a.desde_transcripciones:
        anterior = pd.read_csv(salida).set_index(["id", "modo"]) if salida.exists() else None
        respuestas = [leer_transcripcion(carpeta / f"{q.id}__{m}.jsonl", anterior, q.id, m) for q, m in casos]
    else:
        espacios = preparar_espacios(list(preguntas.id) if "con" in a.modos else [], a.con_salidas)
        os.environ["UV_PROJECT_ENVIRONMENT"] = str(RAIZ / ".venv")   # las copias usan el mismo entorno de uv
        print(f"{len(casos)} llamadas a claude -p con {a.modelo}, {a.paralelo} a la vez...")
        with ThreadPoolExecutor(a.paralelo) as ex:
            respuestas = list(ex.map(lambda c: preguntar(c[0], c[1], espacios, a.modelo, instruccion, carpeta),
                                     casos))

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
            "scripts_de_skills": ";".join(resumen_herramientas(usadas)["scripts_skills"]),
            "n_llamadas_herramientas": len(usadas), "resultado": resultado, "detalle_mixta": detalle,
            "segundos": r["segundos"], "turnos": r["turnos"], "costo_usd": r["costo_usd"],
            "error": r["error"], "transcripcion": f"{carpeta.relative_to(RAIZ).as_posix()}/{q.id}__{modo}.md"})
    res = pd.DataFrame(filas)
    res.to_csv(salida, index=False, encoding="utf-8")
    resumir(res, a.modelo, salida)


def resumir(res, modelo, salida):
    """Tablas de aciertos por modo, por tipo y por pregunta, en evaluacion/resumen.md."""
    tabla = res.groupby("modo").resultado.value_counts().unstack(fill_value=0)
    tabla["segundos_promedio"] = res.groupby("modo").segundos.mean().round(1)
    tabla["turnos_promedio"] = res.groupby("modo").turnos.mean().round(1)
    por_tipo = (res.assign(ok=res.resultado.eq("acierta").astype(int)).groupby(["tipo", "modo"]).ok.sum()
                .unstack(fill_value=0))
    pivote = res.pivot(index="id", columns="modo", values="resultado")
    texto = ["# Resumen automático de la evaluación", "", f"Modelo: `{modelo}`. Archivo: `{salida.name}`.", "",
             "## Por modo", "", tabla.to_markdown(), "", "## Aciertos por tipo de pregunta", "", por_tipo.to_markdown(),
             "", "## Resultado por pregunta", "", pivote.to_markdown(), ""]
    (AQUI / salida.name.replace("resultados", "resumen").replace(".csv", ".md")).write_text("\n".join(texto),
                                                                                             encoding="utf-8")
    print("\n".join(texto))


if __name__ == "__main__":
    main()
