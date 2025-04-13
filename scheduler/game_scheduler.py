# scheduler/game_scheduler.py
import asyncio
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database.db import async_session
from database.models import User, Question
from handlers.game import send_question
from scheduler.daily_summary import calculate_daily_results  # 👈 добавили

Moscow = timezone("Europe/Moscow")

# Время начала игр (МСК)
game_schedule = {
    1: "11:00",
    2: "12:00",
    3: "13:00",
    4: "14:00",
    5: "15:00"
}

# ID игроков (загружаем всех)
async def get_all_users():
    async with async_session() as session:
        result = await session.execute(User.__table__.select())
        return result.fetchall()

# Отправка уведомления
async def notify_users(bot: Bot, text: str):
    users = await get_all_users()
    for row in users:
        user = row.User
        try:
            await bot.send_message(user.id, text)
        except:
            pass  # игнорируем блокировки

# Запуск игры
async def run_game(bot: Bot, game_number: int):
    questions = []
    async with async_session() as session:
        result = await session.execute(
            Question.__table__.select().where(Question.game_number == game_number)
        )
        questions = result.fetchall()

    if len(questions) < 5:
        return

    users = await get_all_users()
    for row in users:
        user = row.User
        try:
            await bot.send_message(user.id, "🎮 Игра начинается!")
            for q in questions:
                question = q.Question
                await send_question(bot, user.id, question)
                await asyncio.sleep(17)
            await bot.send_message(user.id, "✅ Игра завершена. Спасибо за участие!")
        except:
            continue

# Планировщик
def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone=Moscow)

    for game_number, time_str in game_schedule.items():
        hour, minute = map(int, time_str.split(":"))
        notify_hour = hour
        notify_minute = minute - 5

        if notify_minute < 0:
            notify_minute += 60
            notify_hour -= 1

        # Уведомление за 5 минут до игры
        scheduler.add_job(
            notify_users,
            "cron",
            args=[bot, f"🔔 Игра #{game_number} начнётся через 5 минут!"],
            hour=notify_hour,
            minute=notify_minute,
            id=f"notify_{game_number}"
        )

        # Сама игра
        scheduler.add_job(
            run_game,
            "cron",
            args=[bot, game_number],
            hour=hour,
            minute=minute,
            id=f"game_{game_number}"
        )

    # 🏆 Итоги дня в 15:05
    scheduler.add_job(
        calculate_daily_results,
        "cron",
        args=[bot],
        hour=15,
        minute=5,
        id="daily_results"
    )

    scheduler.start()
