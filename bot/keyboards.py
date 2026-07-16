from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 Apagado (10-2)", callback_data="cmd:off"),
                InlineKeyboardButton(text="🟢 Encendido (10-6)", callback_data="cmd:on"),
            ],
            [
                InlineKeyboardButton(text="C1", callback_data="cmd:c1"),
                InlineKeyboardButton(text="C2", callback_data="cmd:c2"),
                InlineKeyboardButton(text="C3", callback_data="cmd:c3"),
            ],
            [
                InlineKeyboardButton(text="📊 Estatus general", callback_data="cmd:status"),
            ],
            [
                InlineKeyboardButton(text="⚡ Voltaje", callback_data="cmd:voltage"),
                InlineKeyboardButton(text="🔌 Consumo", callback_data="cmd:consumption"),
            ],
            [
                InlineKeyboardButton(text="🌡 Temp", callback_data="cmd:temp"),
                InlineKeyboardButton(text="📡 Ping", callback_data="cmd:ping"),
            ],
            [
                InlineKeyboardButton(text="💡 Luces", callback_data="cmd:luces"),
                InlineKeyboardButton(text="📢 Bocina", callback_data="cmd:bocina"),
            ],
        ]
    )


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirmar", callback_data=f"confirm:{action}"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data="cmd:menu"),
            ]
        ]
    )


def on_off_keyboard(target: str) -> InlineKeyboardMarkup:
    """target: c1, c2, c3, luces, bocina"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢 Encender", callback_data=f"set:{target}:1"),
                InlineKeyboardButton(text="🔴 Apagar", callback_data=f"set:{target}:0"),
            ],
            [InlineKeyboardButton(text="⬅️ Menú", callback_data="cmd:menu")],
        ]
    )
