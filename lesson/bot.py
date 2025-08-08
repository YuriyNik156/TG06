import asyncio
import random

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN6, EXCHANGE_API_KEY

from dotenv import load_dotenv
import sqlite3
import aiohttp
import logging
import os
import requests

from pyexpat.errors import messages

bot = Bot(token=TOKEN6)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_register = KeyboardButton(text="Регистрация в телеграм-боте")
button_exchange_rate = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")

keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_register, button_exchange_rate],
    [button_tips, button_finances]
    ], resize_keyboard=True)

conn = sqlite3.connect("user.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
    )
''')

conn.commit()

class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()

@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:", reply_markup=keyboards)

@dp.message(F.text == "Регистрация в телеграм-боте")
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer("Вы уже зарегистрированы!")
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.answer("Вы успешно зарегистрированы!")

@ dp.message(F.text == "Курс валют")
async def exchange_rate(message: Message):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data["conversion_rates"]["RUB"]
        eur_to_usd = data["conversion_rates"]["EUR"]

        euro_to_rub = eur_to_usd * usd_to_rub

        await message.answer(f"1 USD - {usd_to_rub:.2f} RUB\n"
                             f"1 EUR - {euro_to_rub:.2f} RUB")

    except:
        await message.answer("Произошла ошибка")

@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    tips = [
        "Совет 1: Ведите бюджет и следите за своими расходами.",
        "Совет 2: Откладывайте часть доходов на сбережения.",
        "Совет 3: Покупайте товары по скидкам и распродажам."
    ]
    tip = random.choice(tips)
    await message.answer(tip)



async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
