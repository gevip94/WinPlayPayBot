import logging
import ssl
import json
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile, Update
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from config import settings
from handlers import start, menu, withdraw, game, top, profile, admin, stats
from scheduler.game_scheduler import setup_scheduler

# Настроим логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = RedisStorage.from_url("redis://localhost:6379")
dp = Dispatcher(storage=storage)

# Регистрируем роутеры
dp.include_router(start.router)
dp.include_router(menu.router)
dp.include_router(withdraw.router)
dp.include_router(game.router)
dp.include_router(top.router)
dp.include_router(profile.router)
dp.include_router(admin.router)
dp.include_router(stats.router)

async def on_startup(app):
    logging.info("Setting webhook...")
    await bot.set_webhook(
        url=f"https://109.73.194.188:8443/webhook",
        certificate=FSInputFile("/root/certs/webhook.pem")
    )
    logging.info("Webhook set successfully.")

async def handle_webhook(request):
    try:
        data = await request.json()
        logging.info(f"Received raw data: {json.dumps(data, indent=2)}")

        update = Update.model_validate(data)  # 🟢 Исправлено!
        await dp.feed_update(bot, update)

        logging.info("✅ Webhook processed successfully.")
        return web.Response(status=200, text="OK")

    except Exception as e:
        logging.exception(f"❌ Error processing webhook: {e}")
        return web.Response(status=500, text=f"Server Error: {e}")

app = web.Application()
app.router.add_post("/webhook", handle_webhook)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('/root/certs/webhook.pem', '/root/certs/webhook.key')
    logging.info("🚀 Starting server on https://0.0.0.0:8443")
    web.run_app(app, host="0.0.0.0", port=8443, ssl_context=ssl_context)
