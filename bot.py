import os
import json
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    ReplyKeyboardRemove
)

# SOZLAMALAR
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

ADMIN_IDS = [7352664827]

if not BOT_TOKEN or not WEBAPP_URL:
    raise ValueError("BOT_TOKEN yoki WEBAPP_URL kiritilmagan!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

orders = {}


# ASOSIY MENYU
@dp.message(CommandStart())
async def start(message: Message):

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛋 Buyurtma berish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                KeyboardButton(text="📞 Bog‘lanish")
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🏠 KAO MEBEL'ga xush kelibsiz!\n\n"
        "✨ Zamonaviy mebellar va sifatli xizmat!\n\n"
        "
