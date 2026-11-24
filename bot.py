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
        "🛋 Buyurtma berish uchun tugmani bosing.",
        reply_markup=keyboard
    )


# BOG'LANISH
@dp.message(F.text == "📞 Bog‘lanish")
async def contact(message: Message):

    await message.answer(
        "📞 KAO MEBEL\n\n"
        "Buyurtma berish uchun 🛋 Buyurtma berish tugmasini bosing."
    )


# MINI APP BUYURTMASI
@dp.message(F.web_app_data)
async def get_order(message: Message):

    try:
        data = json.loads(message.web_app_data.data)

        if data.get("type") != "order":
            await message.answer("❌ Buyurtma ma'lumotlari noto'g'ri.")
            return

        name = str(data.get("name", "")).strip()[:100]
        phone = str(data.get("phone", "")).strip()[:30]
        items = data.get("items", [])

        if not name or not phone or not isinstance(items, list) or not items:
            await message.answer("❌ Ma'lumotlarni to'liq kiriting.")
            return

        user_id = message.from_user.id

        orders[user_id] = {
            "name": name,
            "phone": phone,
            "items": items
        }

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📍 Joylashuvni yuborish",
                        request_location=True
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(
            "✅ Buyurtmangiz qabul qilindi!\n\n"
            "📍 Yetkazib berish manzilingizni yuboring.",
            reply_markup=keyboard
        )

    except (ValueError, TypeError, KeyError):
        await message.answer(
            "❌ Xatolik yuz berdi. Qayta urinib ko'ring."
        )


# JOYLASHUVNI QABUL QILISH
@dp.message(F.location)
async def get_location(message: Message):

    user_id = message.from_user.id

    if user_id not in orders:
        await message.answer("Avval buyurtma berishingiz kerak.")
        return

    order = orders.pop(user_id)

        order_text = (
    f"🛍 YANGI BUYURTMA | KAO MEBEL\n\n"
    f"👤 Ism: {order['name']}\n"
    f"📞 Telefon: {order['phone']}\n"
    f"🛋 Mahsulotlar:\n"
    f"{json.dumps(order['items'], ensure_ascii=False)}\n\n"
    f"🆔 Telegram ID: {user_id}\n"
    f"📍 Mijoz joylashuvi:"
    
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_text)

            await bot.send_location(
                admin_id,
                latitude=message.location.latitude,
                longitude=message.location.longitude
            )

        except Exception as error:
            print("Admin xatosi:", error)

    await message.answer(
        "🎉 Buyurtmangiz muvaffaqiyatli yuborildi!\n\n"
        "KAO MEBEL jamoasi tez orada siz bilan bog'lanadi. ❤️",
        reply_markup=ReplyKeyboardRemove()
    )


# BOTNI ISHGA TUSHIRISH
async def main():

    print("🚀 KAO MEBEL BOT ISHGA TUSHDI!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
