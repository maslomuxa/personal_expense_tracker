import sqlite3
import asyncio
import logging
import sys
from datetime import date

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

TOKEN = ""
bot = Bot(token=TOKEN)
dp = Dispatcher()



this_month_btn = InlineKeyboardButton(text="за этот месяц", callback_data="this_month")
this_year_btn = InlineKeyboardButton(text="за этот год", callback_data="this_year")
all_time_btn = InlineKeyboardButton(text="за все время", callback_data="all_time")
show_expenses_kbd = InlineKeyboardMarkup(inline_keyboard=[
    [this_month_btn, this_year_btn],
    [all_time_btn],
])


today_btn = InlineKeyboardButton(text="сегодня", callback_data="date_today")
other_day_btn = InlineKeyboardButton(text="ввести вручную", callback_data="date_custom")
add_date_kbd = InlineKeyboardMarkup(inline_keyboard=[
    [today_btn, other_day_btn],
])


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
    await message.answer(text="Выберите дату расхода: ", reply_markup=add_date_kbd)



@dp.callback_query(F.data == 'date_today')
async def date_today_handler(callback: CallbackQuery, state: FSMContext):
    today = date.today()
    await state.update_data(date=today)
    await callback.message.answer("Введите категорию расхода: ")
    await state.set_state(ExpenseState.category)
    await callback.answer()



@dp.callback_query(F.data == 'date_custom')
async def date_custom_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите дату расхода (ГГГГ-ММ-ДД): ")
    await state.set_state(ExpenseState.date)
    await callback.answer()



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
        user_id = message.from_user.id

        cursor.execute('INSERT INTO expenses (user_id, date, category, amount) VALUES (?, ?, ?, ?)', (user_id, date, category, amount))
        conn.commit()

        await message.answer(f"Расход успешно добавлен! \nДата: {date} \nКатегория: {category} \nСумма: {amount}")
    except ValueError:
        await message.answer("Введите число для суммы")
    finally:
        await state.clear()



@dp.message(Command('show_expenses'))
async def show_expenses_handler(message: Message, state: FSMContext):
    await message.answer(text="выберите период расходов: ", reply_markup=show_expenses_kbd)


@dp.callback_query(F.data == 'this_month')
async def this_month_handler(callback: CallbackQuery):
    summ = 0
    user_id = callback.from_user.id
    today = date.today()
    month_start = today.replace(day=1)

    cursor.execute('SELECT * FROM expenses '
                   'WHERE user_id = ? AND date >= ? AND date <= ?'
                   'ORDER BY date',
                   (user_id, month_start, today))
    expenses = cursor.fetchall()
    response = "Ваши расходы: \n\n"
    for expense in expenses:
        response += f"Дата: {expense[2]} \nКатегория: {expense[3]} \nСумма: {expense[4]}\n\n"
        summ += expense[4]
    response += f'Общая сумма расходов: {summ}\n'
    await callback.message.edit_text(response)



@dp.callback_query(F.data == 'this_year')
async def this_year_handler(callback: CallbackQuery):
    summ = 0
    user_id = callback.from_user.id
    today = date.today()
    year_start = today.replace(day=1, month=1)
    cursor.execute('SELECT * FROM expenses '
                   'WHERE user_id = ? AND date >= ? AND date <= ?'
                   'ORDER BY date',
                   (user_id, year_start, today))
    expenses = cursor.fetchall()
    response = "Ваши расходы: \n\n"
    for expense in expenses:
        response += f"Дата: {expense[2]} \nКатегория: {expense[3]} \nСумма: {expense[4]}\n\n"
        summ += expense[4]
    response += f'Общая сумма расходов: {summ}\n'
    await callback.message.edit_text(response)



@dp.callback_query(F.data == 'all_time')
async def all_time_handler(callback: CallbackQuery):

    summ = 0
    user_id = callback.from_user.id
    cursor.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date', (user_id, ))
    expenses = cursor.fetchall()
    response = "Ваши расходы: \n\n"
    for expense in expenses:
        response += f"Дата: {expense[2]} \nКатегория: {expense[3]} \nСумма: {expense[4]}\n\n"
        summ += expense[4]
    response += f'Общая сумма расходов: {summ}\n'
    await callback.message.edit_text(response)








def view_expense_by_period():
    print()

def view_expense_by_category():
    print()



















async def main() -> None:
    global conn, cursor
    conn = sqlite3.connect('expenses2.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL)
    """)
    conn.commit()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
