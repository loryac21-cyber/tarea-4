"""La investigación integrada: Claude Code responde una pregunta real con el MCP del BCRP y las skills de la ENAHO.

    uv run agente/ejecutar_agente.py                       # la pregunta del proyecto, desde cero
    uv run agente/ejecutar_agente.py --pregunta "..." --modelo opus --conservar-salidas

Por defecto borra salidas/, figuras/ y mapas/ antes de empezar, para que todo lo que quede lo produzca el agente en
esta corrida (y para que tenga que encadenar limpiando-enaho antes de graficar y mapear). Deja en
evidencias_ia/integracion/ la transcripción completa (.jsonl), una versión legible (.md) y el resumen de qué
herramientas MCP y qué skills usó.
"""
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente.registro import (HERRAMIENTAS_ARCHIVOS, RAIZ, a_markdown, correr_claude, herramientas_shell,  # noqa: E402
                             permisos_uv, resumen_herramientas)

PREGUNTA = ("Entre 2019 y 2024, ¿cómo evolucionaron la actividad agropecuaria y los precios de los alimentos en el "
            "Perú, y qué tan grande era en 2024 la brecha de pobreza monetaria entre el área rural y la urbana y entre "
            "departamentos?")

INSTRUCCIONES = """
Responde esta pregunta de investigación siguiendo el flujo de CLAUDE.md:

1. Empieza con un plan corto: qué series del BCRP necesitas, qué indicadores de la ENAHO 2024 y qué archivos vas a
   generar.
2. BCRP: encuentra las series con buscar_series y saca cada cifra con resumen, serie o agregar_anual (la ENAHO es
   anual: lleva las series mensuales a años). Guarda al menos un gráfico con graficar_series.
3. ENAHO 2024: usa las skills del proyecto. Si no existe la base procesada, primero limpiando-enaho (y revisa su
   validación); luego graficando-enaho (al menos área urbana/rural y la distribución de las personas pobres) y
   mapeando-enaho (mapa departamental).
4. Escribe informes/informe_final.md con estas secciones: 1. Pregunta de investigación (tema, objetivo y
   delimitación), 2. Fuentes y metodología, 3. Resultados (al menos 3 hallazgos con cifras), 4. Visualizaciones
   (inserta el gráfico del BCRP, el de la ENAHO y el mapa con rutas relativas desde informes/, por ejemplo
   ../figuras/archivo.png), 5. Interpretación, 6. Limitaciones, 7. Reproducibilidad (códigos de serie con su URL,
   scripts, comandos y archivos de salida).
5. Cada cifra del informe debe salir de una herramienta o script de esta sesión, con su fuente al lado. No afirmes
   causalidad entre las series del BCRP y la pobreza. Si algo falla o no hay datos, dilo en el informe.
6. Termina con un resumen de 5 líneas y la lista de herramientas MCP y skills que usaste.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pregunta", default=PREGUNTA)
    ap.add_argument("--modelo", default="sonnet")
    ap.add_argument("--conservar-salidas", action="store_true", help="no borrar salidas/, figuras/ ni mapas/")
    ap.add_argument("--timeout", type=int, default=3600)
    a = ap.parse_args()

    if not a.conservar_salidas:
        for carpeta in ("salidas", "figuras", "mapas"):
            shutil.rmtree(RAIZ / carpeta, ignore_errors=True)
            (RAIZ / carpeta).mkdir()
        (RAIZ / "informes" / "informe_final.md").unlink(missing_ok=True)

    prompt = f"Pregunta de investigación: {a.pregunta}\n{INSTRUCCIONES}"
    herramientas = ",".join([*herramientas_shell(), HERRAMIENTAS_ARCHIVOS, "Skill"])
    flags = ["--strict-mcp-config", "--mcp-config", str(RAIZ / ".mcp.json"), "--tools", herramientas,
             "--allowedTools", "mcp__bcrp", "Skill", *permisos_uv(), *HERRAMIENTAS_ARCHIVOS.split(",")]
    sello = datetime.now().strftime("%Y%m%d_%H%M")
    carpeta = RAIZ / "evidencias_ia" / "integracion"
    jsonl = carpeta / f"ejecucion_{sello}.jsonl"
    print(f"Corriendo claude -p con {a.modelo} (puede tardar varios minutos)...")
    r = correr_claude(prompt, cwd=RAIZ, modelo=a.modelo, flags=flags, jsonl=jsonl, timeout=a.timeout)

    usadas = resumen_herramientas(r["herramientas"])
    (carpeta / f"ejecucion_{sello}.md").write_text(
        a_markdown(r["eventos"], f"Ejecución integrada del agente · {sello}", prompt), encoding="utf-8")
    resumen = {"fecha": sello, "modelo": a.modelo, "pregunta": a.pregunta, "segundos": r["segundos"],
               "turnos": r["turnos"], "costo_usd": r["costo_usd"], "error": r["error"],
               "herramientas_mcp": usadas["mcp"], "skills": usadas["skills"], "scripts_de_skills": usadas["scripts_skills"],
               "llamadas": r["herramientas"],
               "cumple_integracion": len(usadas["mcp"]) >= 2 and len(usadas["skills"]) >= 2,
               "informe": (RAIZ / "informes" / "informe_final.md").exists()}
    (carpeta / f"ejecucion_{sello}_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1),
                                                             encoding="utf-8")
    print(r["resultado"])
    print(f"\nHerramientas MCP: {usadas['mcp']}\nSkills: {usadas['skills']}\nScripts: {usadas['scripts_skills']}")
    print(f"¿2 MCP y 2 skills en la misma ejecución? {resumen['cumple_integracion']} · informe: {resumen['informe']}")
    print(f"Transcripción: {jsonl.relative_to(RAIZ)} y .md · {r['segundos']} s, {r['turnos']} turnos")
    if r["error"]:
        print(f"ERROR: {r['error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
