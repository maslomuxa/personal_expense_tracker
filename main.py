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
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")



@dp.message(Command('help'))
async def command_help_handler(message: Message):
    await message.answer('''
here are commands you can use:
/start - to start a program
/add_expense - to add an expense
/show_expenses - to view your expenses
''')


@dp.message(Command('add_expense'))
async def command_add_expense_handler(message: Message, state: FSMContext):
    await message.answer("enter the date of expense (YYYY-MM-DD): ")
    await state.set_state(ExpenseState.date)


@dp.message(ExpenseState.date)
async def date_input_handler(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Enter the category of expense: ")
    await state.set_state(ExpenseState.category)


@dp.message(ExpenseState.category)
async def category_input_handler(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Enter the amount of expense: ")
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

        await message.answer(f"Expense added successfully! \ndate: {date} \ncategory: {category} \namount: {amount}")
    except ValueError:
        await message.answer("Enter a number for amount")
    finally:
        await state.clear()



@dp.message(Command('show_expenses'))
async def show_expenses_handler(message: Message, state: FSMContext):
    cursor.execute('SELECT * FROM expenses ORDER BY date')
    expenses = cursor.fetchall()
    response = "your expenses: \n\n"
    for expense in expenses:
        response += f"date: {expense[1]} \ncategory: {expense[2]} \namount: {expense[3]}\n\n"
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