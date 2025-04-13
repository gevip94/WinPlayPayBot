# handlers/top.py
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, func, desc
from datetime import date
from database.db import async_session
from database.models import GameResult, User

router = Router()

@router.message(Command("top"))
async def top_handler(message: types.Message):
    today = date.today()

    async with async_session() as session:
        stmt = (
            select(GameResult.user_id, func.sum(GameResult.score).label("total_score"))
            .where(GameResult.date == today)
            .group_by(GameResult.user_id)
            .order_by(desc("total_score"))
            .limit(5)
        )
        top_players = await session.execute(stmt)
        top_players = top_players.fetchall()

        if not top_players:
            await message.answer("Сегодня ещё никто не играл 🕒")
            return

        text = "🏆 <b>Топ игроков за сегодня:</b>\n\n"
        for i, row in enumerate(top_players):
            user = await session.get(User, row.user_id)
            text += f"{i+1}. {user.full_name} — <b>{row.total_score} баллов</b>\n"

        await message.answer(text)
