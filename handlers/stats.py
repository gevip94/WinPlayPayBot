from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, func
from database.db import async_session
from database.models import WithdrawalRequest

router = Router()

ADMIN_ID = 220977591  # укажи свой Telegram ID

@router.message(Command("withdraw_stats"))
async def withdraw_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён.")
        return

    async with async_session() as session:
        total_q = select(func.count()).select_from(WithdrawalRequest)
        done_q = select(func.count()).select_from(WithdrawalRequest).where(WithdrawalRequest.status == "done")
        pending_q = select(func.count()).select_from(WithdrawalRequest).where(WithdrawalRequest.status == "pending")
        rejected_q = select(func.count()).select_from(WithdrawalRequest).where(WithdrawalRequest.status == "rejected")
        sum_q = select(func.sum(WithdrawalRequest.amount)).where(WithdrawalRequest.status == "done")

        total = (await session.execute(total_q)).scalar()
        done = (await session.execute(done_q)).scalar()
        pending = (await session.execute(pending_q)).scalar()
        rejected = (await session.execute(rejected_q)).scalar()
        total_sum = (await session.execute(sum_q)).scalar() or 0

        text = (
            "<b>📊 Статистика по заявкам:</b>\n\n"
            f"🔢 Всего заявок: <b>{total}</b>\n"
            f"✅ Выполнено: <b>{done}</b>\n"
            f"⏳ В ожидании: <b>{pending}</b>\n"
            f"❌ Отклонено: <b>{rejected}</b>\n"
            f"💸 Сумма выводов: <b>{total_sum}₽</b>"
        )

        await message.answer(text)
