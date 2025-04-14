from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from database.db import async_session
from database.models import User, WithdrawalRequest

router = Router()

@router.message(lambda msg: msg.text == "👤 Профиль")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        user = await session.get(User, user_id)

        if not user:
            await message.answer("❌ Профиль не найден.")
            return

        # Основной текст профиля
        text = (
            f"👤 <b>{user.full_name}</b>\n\n"
            f"💰 Баланс: <b>{user.balance}₽</b>\n"
            f"🎮 Игр сыграно: <b>{user.games_played}</b>\n"
            f"✅ Правильных: <b>{user.correct_answers}</b>\n"
            f"❌ Неправильных: <b>{user.wrong_answers}</b>\n"
            f"🏆 Кубков: <b>{user.cups}</b>\n\n"
        )

        # Последние 3 заявки
        result = await session.execute(
            select(WithdrawalRequest)
            .where(WithdrawalRequest.user_id == user_id)
            .order_by(WithdrawalRequest.created_at.desc())
            .limit(3)
        )
        withdrawals = result.scalars().all()

        if withdrawals:
            text += "📄 <b>Последние заявки:</b>\n"
            for w in withdrawals:
                status = {
                    "done": "✅ Выполнено",
                    "pending": "⏳ В ожидании",
                    "rejected": "❌ Отклонено"
                }.get(w.status, "⏺ Неизвестно")

                masked_card = f"****{w.card_number[-4:]}" if w.card_number else "N/A"
                text += f"• 💰 {w.amount}₽ – карта {masked_card} – {status}\n"

        # Кнопки
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="💰 Вывести деньги", callback_data="withdraw")
        keyboard.button(text="📜 Вся история", callback_data="history")
        print("📥 Профиль отправлен с кнопкой 'Вывести деньги'")
        await message.answer(text, reply_markup=keyboard.as_markup())

# 📜 Вся история заявок
@router.callback_query(F.data == "history")
async def show_full_history(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    async with async_session() as session:
        result = await session.execute(
            select(WithdrawalRequest)
            .where(WithdrawalRequest.user_id == user_id)
            .order_by(WithdrawalRequest.created_at.desc())
        )
        withdrawals = result.scalars().all()

        if not withdrawals:
            await callback.message.answer("📭 История пуста.")
            await callback.answer()
            return

        text = "<b>📜 Вся история заявок:</b>\n"
        for w in withdrawals:
            status = {
                "done": "✅ Выполнено",
                "pending": "⏳ В ожидании",
                "rejected": "❌ Отклонено"
            }.get(w.status, "⏺ Неизвестно")

            masked = f"****{w.card_number[-4:]}" if w.card_number else "N/A"
            text += f"• 💰 {w.amount}₽ – карта {masked} – {status}\n"

        await callback.message.answer(text)
        await callback.answer()
