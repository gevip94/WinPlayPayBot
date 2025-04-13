# handlers/start.py
from aiogram import Router, types
from aiogram.filters import CommandStart
from database.db import async_session
from database.models import User
from keyboards.main_keyboard import main_menu  # главное меню с кнопками

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, full_name=full_name)
            session.add(user)
            await session.commit()

    await message.answer(
        "👋 Привет! Это спортивный квиз WinPlayPay.\n\n"
        "📌 Каждый день — 5 игр\n"
        "❓ В каждой игре — 5 вопросов, по 15 секунд на ответ\n"
        "💰 Призы — каждый день\n\n"
        "🎯 Отвечай быстро, набирай баллы и побеждай!\n\n"
        "Удачи! 🍀",
        reply_markup=main_menu
    )
