"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
import os

from aiogram import Bot, Dispatcher, executor, types

import exceptions
import expenses
from categories import Categories
from middlewares import AccessMiddleware


logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для учёта пива и шавермы\n\n"
        "Добавить расход: 250 шаверма\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Статистика за все время: /statistic\n"
        "Статистика за лето: /summer\n"
        "Последние внесённые расходы: /expenses")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id,message.from_user.id)
    answer_message = "Удалил"
    await message.answer(answer_message)

@dp.message_handler(commands=['summer'])
async def full_statistics(message: types.Message):
    """Отправляет количество выпитого пива и съеденых шаверм"""
    # print(type(message.from_user.id))
    answer_message = expenses.get_summer_statistics(message.from_user.id)
    await message.answer(answer_message)

@dp.message_handler(commands=['statistic'])
async def full_statistics(message: types.Message):
    """Отправляет количество выпитого пива и съеденых шаверм"""
    answer_message = expenses.get_full_statistics(message.from_user.id)
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = expenses.get_today_statistics(message.from_user.id)
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    """Отправляет статистику трат текущего месяца"""
    answer_message = expenses.get_month_statistics(message.from_user.id)
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last(message.from_user.id)
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Добавляет новый расход"""
    try:
        expense = expenses.add_expense(message.text, message.from_user.id)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics(message.from_user.id)}")
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
