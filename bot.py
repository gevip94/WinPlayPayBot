
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage  # ✅ FSM в Redis
from config import settings
from handlers import start, menu, withdraw, game, top, profile, admin, stats
from scheduler.game_scheduler import setup_scheduler

print("✅ Бот запущен — лог работает!")

async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Подключаем Redis-хранилище для FSM
    storage = RedisStorage.from_url("redis://localhost:6379")
    dp = Dispatcher(storage=storage)

    # Подключаем все роутеры
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(withdraw.router)
    dp.include_router(game.router)
    dp.include_router(top.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)
    dp.include_router(stats.router)


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Подключаем Redis-хранилище для FSM
    storage = RedisStorage.from_url("redis://localhost:6379")
    dp = Dispatcher(storage=storage)

    # Подключаем все роутеры
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(withdraw.router)
    dp.include_router(game.router)
    dp.include_router(top.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)
    dp.include_router(stats.router)


    # Запуск планировщика игр
    setup_scheduler(bot)

    # Удаляем старые апдейты и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
