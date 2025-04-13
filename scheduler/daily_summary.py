from datetime import date
from sqlalchemy import select, func, desc
from database.db import async_session
from database.models import GameResult, User

async def calculate_daily_results(bot):
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
            print("📭 Сегодня никто не играл.")
            return

        text = "🏆 <b>Итоги дня:</b>\n\n"
        prize_map = {0: 100, 1: 20, 2: 20, 3: 20, 4: 20}
        user_ids = []

        for i, row in enumerate(top_players):
            user_id = row.user_id
            score = row.total_score
            user_ids.append(user_id)

            user = await session.get(User, user_id)
            prize = prize_map.get(i, 0)

            user.balance += prize
            user.cups += 1

            text += f"{i+1}. {user.full_name} — <b>{score} баллов</b> +{prize}₽\n"

        await session.commit()

    # Рассылаем сообщение всем из топа
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
        except:
            continue
