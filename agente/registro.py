"""Correr Claude Code en modo no interactivo y dejar registro de todo lo que hizo.

Lo usan agente/ejecutar_agente.py (la investigación integrada) y evaluacion/evaluar.py (el experimento). Cada corrida
guarda la salida stream-json completa de `claude -p` (cada mensaje, cada llamada a una herramienta y su resultado) y
una versión legible en Markdown, que son la evidencia de qué herramientas usó el agente.
"""
import json
import os
import subprocess
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
HERRAMIENTAS_ARCHIVOS = "Read,Write,Edit,Glob,Grep"


def herramientas_shell():
    """En Windows Claude Code ejecuta comandos con PowerShell; en Linux y macOS, con Bash."""
    return ["PowerShell", "Bash"] if os.name == "nt" else ["Bash"]


def permisos_uv():
    return [f"{s}(uv run:*)" for s in herramientas_shell()]


def correr_claude(prompt, *, cwd, modelo, flags, jsonl=None, timeout=1800, esquema=None):
    """Corre `claude -p` con salida stream-json. Devuelve un dict con el resultado, las herramientas usadas y el tiempo.

    Si `jsonl` es una ruta, guarda ahí la transcripción completa (una línea JSON por evento).
    """
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", modelo,
           "--no-session-persistence", *flags]
    if esquema:
        cmd += ["--json-schema", json.dumps(esquema, ensure_ascii=False)]
    entorno = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    inicio = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout, cwd=cwd, env=entorno)
        salida, error = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        salida = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        error = f"TIMEOUT después de {timeout} s"
    segundos = round(time.time() - inicio, 1)
    eventos = []
    for linea in salida.splitlines():
        try:
            eventos.append(json.loads(linea))
        except json.JSONDecodeError:
            pass
    if jsonl:
        Path(jsonl).parent.mkdir(parents=True, exist_ok=True)
        Path(jsonl).write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in eventos) + "\n", encoding="utf-8")
    final = next((e for e in reversed(eventos) if e.get("type") == "result"), {})
    return {"eventos": eventos, "resultado": final.get("result", ""), "estructurado": final.get("structured_output"),
            "segundos": segundos, "turnos": final.get("num_turns"), "costo_usd": final.get("total_cost_usd"),
            "error": "" if final and not final.get("is_error") else (error or "sin resultado")[-500:],
            "herramientas": herramientas_usadas(eventos)}


def _bloques(evento, tipo):
    msg = evento.get("message") or {}
    contenido = msg.get("content") if isinstance(msg, dict) else None
    return [b for b in contenido if isinstance(b, dict) and b.get("type") == tipo] if isinstance(contenido, list) else []


def herramientas_usadas(eventos):
    """Lista ordenada de llamadas: «mcp__bcrp__resumen», «Skill:limpiando-enaho», «PowerShell: uv run ...»."""
    usadas = []
    for e in eventos:
        if e.get("type") != "assistant":
            continue
        for b in _bloques(e, "tool_use"):
            nombre, entrada = b.get("name", ""), b.get("input") or {}
            if nombre == "Skill":
                usadas.append(f"Skill:{entrada.get('skill') or entrada.get('command') or entrada}")
            elif nombre in ("Bash", "PowerShell"):
                usadas.append(f"{nombre}: {str(entrada.get('command', ''))[:120]}")
            else:
                usadas.append(nombre)
    return usadas


def resumen_herramientas(usadas):
    mcp = sorted({u.split("__")[-1] for u in usadas if u.startswith("mcp__")})
    skills = sorted({u.split(":", 1)[1] for u in usadas if u.startswith("Skill:")})
    scripts = sorted({s for u in usadas for s in ("limpiar.py", "graficar.py", "mapear.py") if s in u})
    return {"mcp": mcp, "skills": skills, "scripts_skills": scripts}


def _texto(x, limite=4000):
    if isinstance(x, list):
        x = "\n".join(b.get("text", json.dumps(b, ensure_ascii=False)) if isinstance(b, dict) else str(b) for b in x)
    x = str(x)
    return x if len(x) <= limite else x[:limite] + f"\n… [{len(x) - limite} caracteres más en el .jsonl]"


def a_markdown(eventos, titulo, prompt):
    """Transcripción legible: el pedido, cada mensaje del agente, cada herramienta con su entrada y su resultado."""
    md = [f"# {titulo}", "", "## Pedido", "", "```text", prompt, "```", ""]
    for e in eventos:
        tipo = e.get("type")
        if tipo == "system" and e.get("subtype") == "init":
            md += ["## Configuración de la sesión", "",
                   f"- Modelo: `{e.get('model')}`",
                   f"- Herramientas disponibles: {', '.join(f'`{t}`' for t in e.get('tools', []))}",
                   f"- Servidores MCP: {', '.join(f'`{s.get('name')}` ({s.get('status')})' for s in e.get('mcp_servers', []))}",
                   f"- Skills: {', '.join(f'`{s}`' for s in e.get('skills', []) or [])}", ""]
        elif tipo == "assistant":
            for b in (e.get("message") or {}).get("content", []):
                if b.get("type") == "text" and b.get("text", "").strip():
                    md += ["### Agente", "", b["text"].strip(), ""]
                elif b.get("type") == "tool_use":
                    md += [f"### Llamada a `{b.get('name')}`", "", "```json",
                           json.dumps(b.get("input"), ensure_ascii=False, indent=1), "```", ""]
        elif tipo == "user":
            for b in _bloques(e, "tool_result"):
                md += ["<details><summary>Resultado</summary>", "", "```text", _texto(b.get("content")), "```", "",
                       "</details>", ""]
        elif tipo == "result":
            md += ["## Resultado final", "", f"- Turnos: {e.get('num_turns')}",
                   f"- Duración: {round((e.get('duration_ms') or 0) / 1000, 1)} s",
                   f"- Costo informado por Claude Code: US$ {e.get('total_cost_usd')}", "", str(e.get("result", "")), ""]
    return "\n".join(md)
