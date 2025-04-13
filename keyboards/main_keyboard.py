# keyboards/main_keyboard.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="📢 Реклама")],
        [KeyboardButton(text="ℹ️ О нас")]
    ],
    resize_keyboard=True
)
