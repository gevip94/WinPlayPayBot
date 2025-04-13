# handlers/menu.py
from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.db import async_session
from database.models import User

router = Router()

@router.message(lambda m: m.text == "👤 Профиль")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Вы ещё не зарегистрированы.")
            return

        text = (
            f"👤 <b>{user.full_name}</b>\n\n"
            f"💰 Баланс: <b>{user.balance}₽</b>\n"
            f"🎮 Игр сыграно: <b>{user.games_played}</b>\n"
            f"✅ Правильных ответов: <b>{user.correct_answers}</b>\n"
            f"❌ Неправильных ответов: <b>{user.wrong_answers}</b>\n"
            f"🏆 Кубков: <b>{user.cups}</b>"
        )

        withdraw_button = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Вывести деньги", callback_data="withdraw_money")]
        ])

        await message.answer(text, reply_markup=withdraw_button)

@router.message(lambda m: m.text == "📢 Реклама")
async def ads_handler(message: types.Message):
    await message.answer("📢 Здесь будет ваша реклама. Связь: @your_channel")

@router.message(lambda m: m.text == "ℹ️ О нас")
async def about_handler(message: types.Message):
    await message.answer("ℹ️ WinPlayPay — спортивный квиз с денежными призами. Участвуй, побеждай, получай!")
