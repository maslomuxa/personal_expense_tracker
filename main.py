import sqlite3
import asyncio
import logging
import sys


from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

TOKEN = "7589991747:AAF7n9YULutwvM4_D9z88-LT0yRlOhpCECQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()



class ExpenseState(StatesGroup):
    date = State()
    category = State()
    amount = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    sanitized_name = html.quote(message.from_user.full_name)
    await message.answer(f"Привет, {html.bold(sanitized_name)}!", parse_mode="HTML")
    await message.answer('''
Доступные команды:
/start - запустить программу
/add_expense - добавить новый расход
/show_expenses - посмотреть свои расходы
''')




@dp.message(Command('help'))
async def command_help_handler(message: Message):
    await message.answer('''
Доступные команды:
/start - запустить программу
/add_expense - добавить новый расход
/show_expenses - посмотреть свои расходы
''')


@dp.message(Command('add_expense'))
async def command_add_expense_handler(message: Message, state: FSMContext):
    await message.answer("Введите дату расхода (ГГГГ-ММ-ДД): ")
    await state.set_state(ExpenseState.date)


@dp.message(ExpenseState.date)
async def date_input_handler(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Введите категорию расхода: ")
    await state.set_state(ExpenseState.category)


@dp.message(ExpenseState.category)
async def category_input_handler(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введите сумму расхода: ")
    await state.set_state(ExpenseState.amount)


@dp.message(ExpenseState.amount)
async def amount_input_handler(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        user_data = await state.get_data()
        date = user_data["date"]
        category = user_data["category"]

        cursor.execute('INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)', (date, category, amount))
        conn.commit()

        await message.answer(f"Расход успешно добавлен! \nДата: {date} \nКатегория: {category} \nСумма: {amount}")
    except ValueError:
        await message.answer("Введите число для суммы")
    finally:
        await state.clear()



@dp.message(Command('show_expenses'))
async def show_expenses_handler(message: Message, state: FSMContext):
    cursor.execute('SELECT * FROM expenses ORDER BY date')
    expenses = cursor.fetchall()
    response = "Ваши расходы: \n\n"
    for expense in expenses:
        response += f"Дата: {expense[1]} \nКатегория: {expense[2]} \nСумма: {expense[3]}\n\n"
    await message.answer(response)







def view_expenses():
    cursor.execute('SELECT * FROM expenses WHERE date < ? AND date >= ? ORDER BY date', ("2025-06-01", "2025-05-01"))
    expenses = cursor.fetchall()

    for expense in expenses:
        print(expense)

def view_expense_by_period():
    print()

def view_expense_by_category():
    print()



















async def main() -> None:
    global conn, cursor
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL)
    """)
    conn.commit()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())