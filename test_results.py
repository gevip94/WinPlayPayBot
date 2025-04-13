import asyncio
from config import settings
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from scheduler.daily_summary import calculate_daily_results

async def run():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await calculate_daily_results(bot)
    await bot.session.close()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run())
    finally:
        loop.close()
