import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from bot import router  # handlers du bot
import bot as bot_module



TOKEN = "7500348646:AAHlWacjJCBP0NYDViHKl4sLLnbVkOAGYXs"
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = "https://mine2-lksn.onrender.com" + WEBHOOK_PATH

# Initialisation du bot et dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

# Enregistre le bot dans le module pour l'utiliser ailleurs
bot_module.bot = bot

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook installé avec succès.")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    print("Webhook supprimé.")

@app.post(WEBHOOK_PATH)
async def handle_webhook(request: Request):
    body = await request.body()
    update = Update.model_validate_json(body.decode())
    await dp.feed_update(bot, update)
    return {"ok": True}
