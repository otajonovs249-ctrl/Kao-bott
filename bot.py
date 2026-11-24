import asyncio
import csv
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "SHU_YERGA_TOKEN")
# Bir nechta admin bo'lsa vergul bilan qo'shing: [111, 222]
ADMIN_IDS = [7352664827]

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

ITEMS = ["Divan", "Shkaf", "Oshxona", "Krovat", "Stol-stul", "Boshqa"]


class Order(StatesGroup):
    name = State()
    phone = State()
    item = State()
    address = State()


def phone_kb():def location_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="📍 Manzilni yuborish",
                request_location=True
            )
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="📞 Raqamni yuborish",
                request_contact=True
            )
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def location_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="📍 Manzilni yuborish",
                request_location=True
            )
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def save_order(row):
    new = not os.path.exists("orders.csv")
    with open("orders.csv", "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["Vaqt", "Ism", "Telefon", "Mebel", "Manzil", "Telegram"])
        w.writerow(row)


@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(
        "Assalomu alaykum! KAO MEBEL ga xush kelibsiz 🛋\n"
        "Buyurtma berish uchun ismingizni yozing:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Order.name)


@dp.message(Order.name, F.text)
async def get_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer(
        "Telefon raqamingizni yuboring (tugmani bosing yoki yozing):",
        reply_markup=phone_kb(),
    )
    await state.set_state(Order.phone)


@dp.message(Order.phone, F.contact | F.text)
async def get_phone(m: Message, state: FSMContext):
    phone = m.contact.phone_number if m.contact else m.text
    await state.update_data(phone=phone)
    await m.answer("Qanday mebel kerak? Tanlang yoki yozing:", reply_markup=items_kb())
    await state.set_state(Order.item)


@dp.message(Order.item, F.text)
async def get_item(m: Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer(
        "📍 Manzilingizni yuborish uchun tugmani bosing:",
        reply_markup=location_kb()
    )
    await state.set_state(Order.address)

@dp.message(Order.address, F.text)
@dp.message(Order.address, F.location)
async def get_address(m: Message, state: FSMContext):
    loc = m.location

    address = f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}"

    data = await state.update_data(address=address)
    await state.clear()

    user = f"@{m.from_user.username}" if m.from_user.username else "username yo'q"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_order([
        now, data["name"], data["phone"],
        data["item"], address, user
    ])

    await m.answer(
        "✅ Buyurtmangiz qabul qilindi!\n"
        "Tez orada siz bilan bog'lanamiz.",
        reply_markup=ReplyKeyboardRemove()
    )

    text = (
        "🆕 Yangi buyurtma!\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📞 Telefon: {data['phone']}\n"
        f"🛋 Mebel: {data['item']}\n"
        f"📍 Manzil: {address}\n"
        f"🔗 Telegram: {user}\n"
        f"🕒 {now}"
    )

    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, text)
        except Exception as e:
            print(f"Xatolik: {e}")
    user = f"@{m.from_user.username}" if m.from_user.username else "username yo'q"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    await m.answer(
        "✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.\n"
        "Yangi buyurtma uchun /start yozing."
    )

    save_order([now, data["name"], data["phone"], data["item"], data["address"], user])

    text = (
        "🆕 Yangi buyurtma!\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📞 Telefon: {data['phone']}\n"
        f"🛋 Mebel: {data['item']}\n"
        f"📍 Manzil: {data['address']}\n"
        f"🔗 Telegram: {user}\n"
        f"🕒 {now}"
    )
    for admin in ADMIN_IDS:
        try:
            await bot.send_message(admin, text)
        except Exception as e:
            print(f"Adminga yuborib bo'lmadi ({admin}): {e}")


@dp.message(StateFilter(None))
async def greet(m: Message, state: FSMContext):
    await start(m, state)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
