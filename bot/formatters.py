from __future__ import annotations

from typing import Any


def _num(value: Any, digits: int = 1) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "N/A"


def format_voltage(metrics: dict[str, Any]) -> str:
    data = metrics.get("data") or {}
    if not metrics.get("success") or not data:
        err = metrics.get("error") or "Sin datos de multímetro"
        return f"⚡ Voltaje\n❌ {err}"

    return (
        "⚡ <b>Voltaje trifásico</b>\n"
        f"L1: <b>{_num(data.get('v_l1'))}</b> V\n"
        f"L2: <b>{_num(data.get('v_l2'))}</b> V\n"
        f"L3: <b>{_num(data.get('v_l3'))}</b> V\n"
        f"Fuente: {data.get('source', 'N/A')}"
    )


def format_consumption(metrics: dict[str, Any]) -> str:
    data = metrics.get("data") or {}
    if not metrics.get("success") or not data:
        err = metrics.get("error") or "Sin datos de multímetro"
        return f"🔌 Consumo\n❌ {err}"

    return (
        "🔌 <b>Consumo</b>\n"
        f"Potencia: <b>{_num(data.get('potencia_kw'), 2)}</b> kW\n"
        f"A L1: {_num(data.get('a_l1'), 2)} A\n"
        f"A L2: {_num(data.get('a_l2'), 2)} A\n"
        f"A L3: {_num(data.get('a_l3'), 2)} A\n"
        f"FP: {_num(data.get('factor_potencia'), 3)}\n"
        f"f: {_num(data.get('frecuencia'), 2)} Hz"
    )


def format_temperature(metrics: dict[str, Any]) -> str:
    data = metrics.get("data") or {}
    # Core Swicht V2 aún no expone sensor de temperatura del trafo.
    # Si aparece en metrics, lo mostramos; si no, aviso claro.
    for key in ("temp_trafo", "temperatura", "temp_c", "temperature"):
        if data.get(key) is not None:
            return f"🌡 <b>Temperatura trafo</b>\n{_num(data.get(key), 1)} °C"

    return (
        "🌡 <b>Temperatura trafo</b>\n"
        "Sensor pendiente en Core Swicht V2 "
        "(igual que en Pain Farm: aún no hay endpoint real)."
    )


def format_contactors(status: dict[str, Any]) -> str:
    lines = ["📊 <b>Contactores</b>"]
    for key in ("C1", "C2", "C3"):
        entry = status.get(key) or {}
        state = entry.get("state", "UNKNOWN")
        name = entry.get("name", key)
        icon = "🟢" if state == "ON" else "🔴" if state == "OFF" else "⚪"
        lines.append(f"{icon} {key} ({name}): <b>{state}</b>")
        if entry.get("error"):
            lines.append(f"   ⚠ {entry['error']}")
    return "\n".join(lines)


def format_general_status(status: dict[str, Any], metrics: dict[str, Any]) -> str:
    parts = [
        "📋 <b>Estatus general</b>",
        "",
        format_contactors(status),
        "",
        format_voltage(metrics),
        "",
        format_consumption(metrics),
        "",
        format_temperature(metrics),
    ]
    return "\n".join(parts)


def format_switch_result(title: str, result: dict[str, Any]) -> str:
    if result.get("accepted") is False:
        return f"❌ {title}\n{result.get('message', 'Rechazado')}"
    if result.get("success") is False:
        return f"❌ {title}\n{result.get('error', 'Fallo')}"
    if result.get("accepted") is True:
        msg = result.get("message") or "Aceptado"
        return f"✅ {title}\n{msg}"
    if result.get("success") is True:
        return f"✅ {title}\nEstado solicitado: {result.get('requested_state', 'OK')}"
    return f"✅ {title}\n{result}"


HELP_TEXT = (
    "⚡ <b>Core Swicht Bot</b>\n\n"
    "Comandos:\n"
    "/menu — Menú con botones\n"
    "/10_2 — Apagado general\n"
    "/10_6 — Encendido general\n"
    "/C1 /C2 /C3 — Contactor (pide ON/OFF)\n"
    "/Voltaje — Voltajes L1 L2 L3\n"
    "/consumo — Potencia y corrientes\n"
    "/temp — Temperatura trafo\n"
    "/EstatusGeneral — Resumen completo\n"
    "/ping — Health / heartbeat API\n"
    "/help — Esta ayuda"
)
