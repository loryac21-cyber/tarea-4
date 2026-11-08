"""El contrato del servidor: si estas pruebas pasan, Claude Code y evaluar.py pueden usarlo.

    uv run pytest -q

Llaman al servidor en memoria, igual que lo haría Claude Code, y piden datos reales al BCRP.
"""
import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from server import mcp


async def _con_cliente(f):
    async with Client(mcp) as c:
        return await f(c)


def llamar(herramienta, **args):
    return asyncio.run(_con_cliente(lambda c: c.call_tool(herramienta, args))).data


def test_buscar_encuentra_el_ipc():
    r = llamar("buscar_series", texto="ipc 12 meses", limite=5)
    assert "PN01273PM" in [x["codigo"] for x in r]
    assert {"codigo", "nombre", "frecuencia"} <= r[0].keys()


def test_cuatro_herramientas_como_minimo():
    nombres = {t.name for t in asyncio.run(_con_cliente(lambda c: c.list_tools()))}
    assert {"buscar_series", "serie", "resumen"} <= nombres
    assert len(nombres) >= 4, "falta su herramienta propia"


def test_serie_mensual():
    r = llamar("serie", codigo="PN01271PM", desde="2025-01", hasta="2025-12")
    assert len(r["datos"]) == 12
    assert r["datos"][0]["periodo"] == "2025-01"
    assert r["datos"][2]["valor"] == pytest.approx(0.81, abs=0.01)   # IPC de Lima, marzo de 2025
    assert r["fuente"].startswith("https://estadisticas.bcrp.gob.pe")


def test_serie_diaria():
    r = llamar("serie", codigo="PD04638PD", desde="2026-10-01", hasta="2026-10-15")
    assert r["datos"][0]["periodo"] == "2026-10-01"
    assert r["datos"][-1] == {"periodo": "2026-10-15", "valor": pytest.approx(3.428, abs=0.001)}


def test_resumen_sin_cuentas_a_mano():
    r = llamar("resumen", codigo="PN01273PM", desde="2025-12", hasta="2026-09")
    assert r["primero"]["valor"] == pytest.approx(1.51, abs=0.01)
    assert r["ultimo"]["valor"] == pytest.approx(4.55, abs=0.01)
    assert r["maximo"]["periodo"] == "2026-09"
    assert {"cambio", "variacion_pct", "promedio", "minimo"} <= r.keys()


def test_codigo_inexistente_da_un_error_claro():
    with pytest.raises(ToolError, match="XX999"):
        llamar("serie", codigo="XX999", desde="2025-01", hasta="2025-02")


def test_un_recurso():
    async def contar(c):
        return len(await c.list_resources()) + len(await c.list_resource_templates())
    assert asyncio.run(_con_cliente(contar)) >= 1


def test_un_prompt():
    assert len(asyncio.run(_con_cliente(lambda c: c.list_prompts()))) >= 1


# ----------------------------------------------------------------------------------------------------------------
# Pruebas propias (tarea 4). Las 8 de arriba son las del curso, sin cambios. Estas revisan las herramientas propias
# contra otra publicación oficial del BCRP, no contra cifras escritas a mano.
# ----------------------------------------------------------------------------------------------------------------

def test_agregar_anual_suma_coincide_con_la_serie_anual_oficial():
    """La suma de los 12 meses de exportaciones (PN38714BM) debe dar lo que el BCRP publica como dato anual
    (PM40027BA). Si agregar_anual perdiera o duplicara un mes, no coincidiría."""
    mensual = llamar("agregar_anual", codigo="PN38714BM", desde=2022, hasta=2024, operacion="suma")
    anual = {d["periodo"]: d["valor"] for d in llamar("serie", codigo="PM40027BA", desde="2022", hasta="2024")["datos"]}
    assert [a["anio"] for a in mensual["anios"]] == [2022, 2023, 2024]
    for a in mensual["anios"]:
        assert a["completo"] and a["n_periodos"] == 12
        assert a["valor"] == pytest.approx(anual[str(a["anio"])], rel=0.001)
    assert mensual["anios"][-1]["variacion_pct"] == pytest.approx((anual["2024"] / anual["2023"] - 1) * 100, abs=0.1)
    assert mensual["fuente"].startswith("https://estadisticas.bcrp.gob.pe")


def test_agregar_anual_avisa_anios_incompletos_y_no_inventa():
    """Un año a medias se marca como incompleto; "fin" devuelve el dato de diciembre tal cual lo da serie; y una
    serie que ya es anual o una operación inexistente dan un error claro en vez de un número."""
    r = llamar("agregar_anual", codigo="PN01273PM", desde=2024, hasta=2026, operacion="fin")
    por_anio = {a["anio"]: a for a in r["anios"]}
    diciembre = llamar("serie", codigo="PN01273PM", desde="2024-12", hasta="2024-12")["datos"][0]["valor"]
    assert por_anio[2024]["valor"] == pytest.approx(diciembre, abs=0.0001)
    assert por_anio[2024]["completo"] and por_anio[2025]["completo"]
    assert not por_anio[2026]["completo"] and por_anio[2026]["n_periodos"] < 12
    assert any("2026" in a for a in r["advertencias"])
    with pytest.raises(ToolError, match="ya es anual"):
        llamar("agregar_anual", codigo="PM04983AA", desde=2019, hasta=2024)
    with pytest.raises(ToolError, match="Operación no válida"):
        llamar("agregar_anual", codigo="PN01273PM", desde=2024, hasta=2024, operacion="mediana")


def test_graficar_series_guarda_el_png_con_su_fuente(tmp_path, monkeypatch):
    import server
    monkeypatch.setattr(server, "FIGURAS", tmp_path)
    r = llamar("graficar_series", codigos=["PM04968AA", "PM04983AA"], desde="2019", hasta="2024",
               titulo="Prueba", archivo="Prueba gráfico", unidad="var. %", etiquetas=["Agro", "PBI"])
    png = tmp_path / "prueba_grafico.png"
    assert png.exists() and png.stat().st_size > 10_000
    assert len(r["fuente"]) == 2 and all(u.startswith("https://estadisticas.bcrp.gob.pe") for u in r["fuente"])
    assert r["series"][0]["ultimo"]["periodo"] == "2024"
    with pytest.raises(ToolError, match="frecuencias distintas"):
        llamar("graficar_series", codigos=["PM04983AA", "PN01273PM"], desde="2019", hasta="2024",
               titulo="x", archivo="x")
