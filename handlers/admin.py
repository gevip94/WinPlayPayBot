from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from sqlalchemy import select
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import async_session
from database.models import WithdrawalRequest, User

router = Router()

ADMIN_ID = 220977591  # 🔐 Укажи здесь свой Telegram ID

# 📋 Показать все ожидающие заявки
@router.message(Command("withdraw_requests"))
async def show_withdraw_requests(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён.")
        return

    async with async_session() as session:
        result = await session.execute(
            select(WithdrawalRequest).where(WithdrawalRequest.status == "pending")
        )
        requests = result.scalars().all()

        if not requests:
            await message.answer("📭 Нет заявок на вывод.")
            return

        for request in requests:
            user = await session.get(User, request.user_id)
            text = (
                f"🔹 <b>Заявка #{request.id}</b>\n"
                f"👤 {user.full_name}\n"
                f"💰 {request.amount}₽\n"
                f"💳 {request.card_number}\n"
            )
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Выполнено", callback_data=f"done_{request.id}")
            kb.button(text="❌ Отклонить", callback_data=f"reject_{request.id}")
            await message.answer(text, reply_markup=kb.as_markup())

# ✅ Подтвердить заявку
@router.callback_query(F.data.startswith("done_"))
async def mark_done(callback: types.CallbackQuery, bot: Bot):
    request_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        request = await session.get(WithdrawalRequest, request_id)
        user = await session.get(User, request.user_id)

        request.status = "done"
        await session.commit()

        try:
            await bot.send_message(
                chat_id=user.id,
                text=(
                    f"💸 Ваша заявка на вывод <b>{request.amount}₽</b> выполнена.\n"
                    f"Деньги отправлены на карту 💳 {request.card_number}"
                )
            )
        except Exception as e:
            print(f"⚠️ Не удалось уведомить пользователя {user.id}: {e}")
            await callback.message.answer(f"⚠️ Не удалось уведомить пользователя.")

    await callback.message.edit_text("✅ Выполнено. Заявка закрыта.")
    await callback.answer("Заявка помечена как выполненная ✅")

# ❌ Отклонить заявку
@router.callback_query(F.data.startswith("reject_"))
async def reject_withdraw(callback: types.CallbackQuery, bot: Bot):
    request_id = int(callback.data.split("_")[1])

    async with async_session() as session:
        request = await session.get(WithdrawalRequest, request_id)
        user = await session.get(User, request.user_id)

        request.status = "rejected"
        await session.commit()

        try:
            await bot.send_message(
                chat_id=user.id,
                text=(
                    f"🚫 Ваша заявка на вывод <b>{request.amount}₽</b> отклонена.\n"
                    f"Если вы считаете это ошибкой — свяжитесь с админом."
                )
            )
        except:
            await callback.message.answer(f"⚠️ Не удалось уведомить пользователя.")

    await callback.message.edit_text("❌ Заявка отклонена.")
    await callback.answer("Заявка помечена как отклонённая ❌")
