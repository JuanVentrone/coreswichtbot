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

    trafo_temp = None
    for key in ("temperature_c", "temp_trafo", "temperatura", "temp_c", "temperature"):
        if data.get(key) is not None:
            trafo_temp = data.get(key)
            break

    ambient_temp = data.get("ambient_temperature_c")
    if trafo_temp is None and ambient_temp is None:
        for key in ("temp_ambiente", "ambient_temp", "ambient_temperature"):
            if data.get(key) is not None:
                ambient_temp = data.get(key)
                break

    if trafo_temp is not None or ambient_temp is not None:
        lines = ["🌡 <b>Temperatura</b>"]
        if trafo_temp is not None:
            lines.append(f"Trafo: <b>{_num(trafo_temp, 1)}</b> °C")
        if ambient_temp is not None:
            lines.append(f"Ambiente: <b>{_num(ambient_temp, 1)}</b> °C")
        return "\n".join(lines)

    return (
        "🌡 <b>Temperatura</b>\n"
        "Sin datos del sensor de temperatura disponible."
    )


def _normalize_contactor_state(value: Any) -> str:
    if isinstance(value, bool):
        return "ON" if value else "OFF"

    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in {"ON", "TRUE", "1", "ENCENDIDO", "ACTIVO"}:
            return "ON"
        if normalized in {"OFF", "FALSE", "0", "APAGADO", "INACTIVO"}:
            return "OFF"
        if normalized in {"UNKNOWN", "DESCONOCIDO", "UNDEFINED", "NULL", "NONE"}:
            return "UNKNOWN"
        return normalized if normalized else "UNKNOWN"

    if value is None:
        return "UNKNOWN"

    if int(value) == 1:
        return "ON"
    if int(value) == 0:
        return "OFF"

    return "UNKNOWN"


def _extract_contactors(status: dict[str, Any]) -> dict[str, Any]:
    """Extrae el dict de contactores aceptando formatos plano o anidado."""
    if not isinstance(status, dict):
        return {}
    if "contactors" in status and isinstance(status["contactors"], dict):
        return status["contactors"]
    return status


def format_contactors(status: dict[str, Any]) -> str:
    contactors = _extract_contactors(status)
    lines = ["📊 <b>Contactores</b>"]
    for key in ("C1", "C2", "C3"):
        entry = contactors.get(key) or {}
        state = _normalize_contactor_state(entry.get("state", "UNKNOWN"))
        name = entry.get("name", key)
        icon = "🟢" if state == "ON" else "🔴" if state == "OFF" else "⚪"
        lines.append(f"{icon} {key} ({name}): <b>{state}</b>")
        if entry.get("error"):
            lines.append(f"   ⚠ {entry['error']}")
    return "\n".join(lines)


def format_general_status(
    status: dict[str, Any],
    metrics: dict[str, Any],
    temperature_metrics: dict[str, Any] | None = None,
) -> str:
    parts = [
        "📋 <b>Estatus general</b>",
        "",
        format_contactors(status),
        "",
        format_voltage(metrics),
        "",
        format_consumption(metrics),
        "",
        format_temperature(temperature_metrics or metrics),
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
