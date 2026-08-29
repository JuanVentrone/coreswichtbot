from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api import CoreSwitchClient
from bot.formatters import (
    HELP_TEXT,
    format_consumption,
    format_general_status,
    format_switch_result,
    format_temperature,
    format_voltage,
)
from bot.keyboards import main_menu_keyboard, on_off_keyboard

logger = logging.getLogger(__name__)
router = Router(name="commands")


@router.message(Command("start", "help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML", reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer(
        "⚡ <b>Core Swicht V2</b>\nSelecciona una acción:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        health = await core_api.health()
        hb = await core_api.heartbeat()
        text = (
            "📡 <b>API OK</b>\n"
            f"Health: {health}\n"
            f"Heartbeat: status={hb.get('status')} · "
            f"RS485={hb.get('rs485_status')} · "
            f"uptime={hb.get('uptime_seconds')}s"
        )
        await message.answer(text, parse_mode="HTML")
    except Exception as exc:
        logger.exception("ping failed")
        await message.answer(f"❌ No se pudo contactar la API:\n{exc}")


@router.message(Command("10_2", "apagado"))
async def cmd_off(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        result = await core_api.switch_general(False)
        await message.answer(
            format_switch_result("Apagado general (10-2)", result),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("general off failed")
        await message.answer(f"❌ Error apagado general:\n{exc}")


@router.message(Command("10_6", "encendido"))
async def cmd_on(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        result = await core_api.switch_general(True)
        await message.answer(
            format_switch_result("Encendido general (10-6)", result),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("general on failed")
        await message.answer(f"❌ Error encendido general:\n{exc}")


@router.message(Command("C1"))
async def cmd_c1(message: Message) -> None:
    await message.answer(
        "Contactor <b>C1</b> — elige estado:",
        parse_mode="HTML",
        reply_markup=on_off_keyboard("c1"),
    )


@router.message(Command("C2"))
async def cmd_c2(message: Message) -> None:
    await message.answer(
        "Contactor <b>C2</b> — elige estado:",
        parse_mode="HTML",
        reply_markup=on_off_keyboard("c2"),
    )


@router.message(Command("C3"))
async def cmd_c3(message: Message) -> None:
    await message.answer(
        "Contactor <b>C3</b> — elige estado:",
        parse_mode="HTML",
        reply_markup=on_off_keyboard("c3"),
    )


@router.message(Command("Voltaje", "voltaje"))
async def cmd_voltage(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        metrics = await core_api.power_metrics()
        await message.answer(format_voltage(metrics), parse_mode="HTML")
    except Exception as exc:
        logger.exception("voltage failed")
        await message.answer(f"❌ Error voltaje:\n{exc}")


@router.message(Command("consumo", "Consumo"))
async def cmd_consumption(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        metrics = await core_api.power_metrics()
        await message.answer(format_consumption(metrics), parse_mode="HTML")
    except Exception as exc:
        logger.exception("consumption failed")
        await message.answer(f"❌ Error consumo:\n{exc}")


@router.message(Command("temp", "Temp", "temperatura"))
async def cmd_temp(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        metrics = await core_api.temperature_metrics()
        await message.answer(format_temperature(metrics), parse_mode="HTML")
    except Exception as exc:
        logger.exception("temp failed")
        await message.answer(f"❌ Error temperatura:\n{exc}")


@router.message(Command("EstatusGeneral", "estatus", "status"))
async def cmd_status(message: Message, core_api: CoreSwitchClient) -> None:
    try:
        status = await core_api.general_status()
        metrics = await core_api.power_metrics()
        temperature_metrics = await core_api.temperature_metrics()
        await message.answer(
            format_general_status(status, metrics, temperature_metrics),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("status failed")
        await message.answer(f"❌ Error estatus:\n{exc}")
