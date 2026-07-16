from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.api import CoreSwitchClient
from bot.formatters import (
    format_consumption,
    format_general_status,
    format_switch_result,
    format_temperature,
    format_voltage,
)
from bot.keyboards import confirm_keyboard, main_menu_keyboard, on_off_keyboard

logger = logging.getLogger(__name__)
router = Router(name="menu")

ACTION_LABELS = {
    "off": "Apagado general (10-2)",
    "on": "Encendido general (10-6)",
    "c1": "Contactor C1",
    "c2": "Contactor C2",
    "c3": "Contactor C3",
    "luces": "Luces",
    "bocina": "Bocina",
}


async def _show_menu(callback: CallbackQuery) -> None:
    text = "⚡ <b>Core Swicht V2</b>\nSelecciona una acción:"
    if callback.message:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )


@router.callback_query(F.data == "cmd:menu")
async def cb_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    await _show_menu(callback)


@router.callback_query(F.data.startswith("cmd:"))
async def cb_menu_action(callback: CallbackQuery, core_api: CoreSwitchClient) -> None:
    action = (callback.data or "").split(":", 1)[1]

    if action in ("off", "on"):
        await callback.answer()
        label = ACTION_LABELS[action]
        if callback.message:
            await callback.message.edit_text(
                f"⚠️ ¿Confirmas <b>{label}</b>?",
                parse_mode="HTML",
                reply_markup=confirm_keyboard(action),
            )
        return

    if action in ("c1", "c2", "c3", "luces", "bocina"):
        await callback.answer()
        label = ACTION_LABELS[action]
        if callback.message:
            await callback.message.edit_text(
                f"<b>{label}</b> — elige estado:",
                parse_mode="HTML",
                reply_markup=on_off_keyboard(action),
            )
        return

    await callback.answer()
    try:
        if action == "status":
            status = await core_api.general_status()
            metrics = await core_api.power_metrics()
            text = format_general_status(status, metrics)
        elif action == "voltage":
            text = format_voltage(await core_api.power_metrics())
        elif action == "consumption":
            text = format_consumption(await core_api.power_metrics())
        elif action == "temp":
            text = format_temperature(await core_api.power_metrics())
        elif action == "ping":
            health = await core_api.health()
            hb = await core_api.heartbeat()
            text = (
                "📡 <b>API OK</b>\n"
                f"Health: {health}\n"
                f"RS485={hb.get('rs485_status')} · uptime={hb.get('uptime_seconds')}s"
            )
        else:
            text = "Acción desconocida"
    except Exception as exc:
        logger.exception("menu read action failed: %s", action)
        text = f"❌ Error:\n{exc}"

    if callback.message:
        await callback.message.answer(text, parse_mode="HTML")
        await callback.message.answer("Menú:", reply_markup=main_menu_keyboard())


@router.callback_query(F.data.startswith("set:"))
async def cb_set_state(callback: CallbackQuery) -> None:
    parts = (callback.data or "").split(":")
    if len(parts) != 3:
        await callback.answer("Datos inválidos", show_alert=True)
        return

    _, target, state_raw = parts
    on = state_raw == "1"
    confirm_key = f"{target}_{'on' if on else 'off'}"
    label = ACTION_LABELS.get(target, target)
    state_label = "ENCENDER" if on else "APAGAR"

    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"⚠️ ¿Confirmas <b>{state_label}</b> {label}?",
            parse_mode="HTML",
            reply_markup=confirm_keyboard(confirm_key),
        )


@router.callback_query(F.data.startswith("confirm:"))
async def cb_confirm(callback: CallbackQuery, core_api: CoreSwitchClient) -> None:
    action = (callback.data or "").split(":", 1)[1]
    await callback.answer("Ejecutando...")

    try:
        if action == "off":
            result = await core_api.switch_general(False)
            text = format_switch_result("Apagado general (10-2)", result)
        elif action == "on":
            result = await core_api.switch_general(True)
            text = format_switch_result("Encendido general (10-6)", result)
        elif action.endswith("_on") or action.endswith("_off"):
            target, state = action.rsplit("_", 1)
            on = state == "on"
            if target in ("c1", "c2", "c3"):
                cid = target.upper()
                result = await core_api.switch_contactor(cid, on)
                text = format_switch_result(f"Contactor {cid}", result)
            elif target == "luces":
                result = await core_api.switch_luces(on)
                text = format_switch_result("Luces", result)
            elif target == "bocina":
                result = await core_api.switch_bocina(on)
                text = format_switch_result("Bocina", result)
            else:
                text = "Acción inválida"
        else:
            text = "Acción inválida"
    except Exception as exc:
        logger.exception("confirm action failed: %s", action)
        text = f"❌ Error:\n{exc}"

    if callback.message:
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.message.answer("Menú:", reply_markup=main_menu_keyboard())
