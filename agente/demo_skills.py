"""Demuestra cómo se activan y coordinan las skills de la ENAHO en Claude Code (Parte 2 de la tarea).

    uv run agente/demo_skills.py

Tres pedidos, cada uno en una sesión nueva de `claude -p`:
  1. Invocación directa:        /limpiando-enaho 2024
  2. Lenguaje natural:          «Grafica la pobreza ... por sexo y por grupo de edad ...»  -> graficando-enaho
  3. Encadenamiento:            se borran los parquet y se pide «Haz un mapa de la pobreza monetaria por departamento
                                con ENAHO 2024»  -> limpiando-enaho y luego mapeando-enaho
Deja la transcripción de cada uno y un resumen en evidencias_ia/skills/.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente.registro import RAIZ, a_markdown, correr_claude, herramientas_shell, permisos_uv  # noqa: E402

DEMOS = [
    ("1_invocacion_directa", "/limpiando-enaho 2024", False,
     "limpiando-enaho, llamada a mano con /"),
    ("2_lenguaje_natural_graficos", "Grafica la pobreza monetaria de la ENAHO 2024 por sexo y por grupo de edad, y "
                                    "dime las cifras de cada grupo.", False,
     "graficando-enaho, activada por la descripción"),
    ("3_encadenamiento_mapa", "Haz un mapa de la pobreza monetaria por departamento con ENAHO 2024.", True,
     "limpiando-enaho y después mapeando-enaho, porque falta la base procesada"),
]


def main():
    carpeta = RAIZ / "evidencias_ia" / "skills"
    carpeta.mkdir(parents=True, exist_ok=True)
    herramientas = ",".join([*herramientas_shell(), "Read", "Glob", "Grep", "Skill"])
    flags = ["--strict-mcp-config", "--tools", herramientas, "--allowedTools", "Skill", *permisos_uv(), "Read",
             "Glob", "Grep"]
    resumen = []
    for nombre, pedido, borrar_base, esperado in DEMOS:
        if borrar_base:
            for f in (RAIZ / "salidas").glob("*.parquet"):
                f.unlink()
        r = correr_claude(pedido, cwd=RAIZ, modelo="sonnet", flags=flags, jsonl=carpeta / f"{nombre}.jsonl",
                          timeout=1200)
        (carpeta / f"{nombre}.md").write_text(a_markdown(r["eventos"], f"Skills · {nombre}", pedido), encoding="utf-8")
        skills = [u.split(":", 1)[1] for u in r["herramientas"] if u.startswith("Skill:")]
        scripts = [s for u in r["herramientas"] for s in ("limpiar.py", "graficar.py", "mapear.py") if s in u]
        resumen.append({"demo": nombre, "pedido": pedido, "base_borrada_antes": borrar_base, "esperado": esperado,
                        "skills_en_orden": skills, "scripts_en_orden": scripts, "segundos": r["segundos"],
                        "error": r["error"], "respuesta": r["resultado"]})
        print(f"{nombre}: skills {skills} · scripts {scripts} · {r['segundos']} s {r['error']}")
    (carpeta / "resumen_activacion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")


if __name__ == "__main__":
    main()
