# handlers/game.py
import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import Question, User, GameResult  # 👈 добавили GameResult

router = Router()

# Команда для ручного запуска игры
@router.message(Command("game_now"))
async def start_game(message: types.Message, bot: Bot):
    user_id = message.from_user.id

    async with async_session() as session:
        questions = await session.execute(
            select(Question).where(Question.game_number == 1)
        )
        questions = questions.scalars().all()

    if len(questions) < 5:
        await message.answer("❌ Недостаточно вопросов для этой игры.")
        return

    await message.answer("🎮 Игра начинается!")

    for question in questions:
        await send_question(bot, user_id, question)
        await asyncio.sleep(17)

    await message.answer("✅ Игра завершена. Спасибо за участие!")

# Функция отправки вопроса
async def send_question(bot: Bot, user_id: int, question: Question):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=question.option_1, callback_data=f"ans:{question.id}:1")],
        [InlineKeyboardButton(text=question.option_2, callback_data=f"ans:{question.id}:2")],
        [InlineKeyboardButton(text=question.option_3, callback_data=f"ans:{question.id}:3")],
        [InlineKeyboardButton(text=question.option_4, callback_data=f"ans:{question.id}:4")],
    ])

    await bot.send_message(
        user_id,
        f"❓ <b>{question.text}</b>\n\n⏱ У тебя 15 секунд!",
        reply_markup=keyboard
    )

# Обработка ответа
@router.callback_query(lambda c: c.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery):
    data = callback.data.split(":")
    q_id = int(data[1])
    selected = int(data[2])
    user_id = callback.from_user.id

    async with async_session() as session:
        question = await session.get(Question, q_id)
        user = await session.get(User, user_id)

        if not question or not user:
            await callback.answer("Ошибка. Попробуй позже.", show_alert=True)
            return

        if selected == question.correct_option:
            user.correct_answers += 1
            await callback.message.answer("✅ Правильно!")

            # ⬇️ Сохраняем очко в таблицу game_results
            result = GameResult(
                user_id=user.id,
                score=1,
                game_number=question.game_number
            )
            session.add(result)

        else:
            user.wrong_answers += 1
            await callback.message.answer(
                f"❌ Неправильно! Правильный ответ: <b>{getattr(question, f'option_{question.correct_option}')}</b>"
            )

        user.games_played += 1
        await session.commit()

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("⏳ Ожидайте следующий вопрос...")
