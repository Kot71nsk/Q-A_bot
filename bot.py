import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from quiz_data import quiz_data
from database import create_table, get_quiz_index, update_quiz_index, save_result, get_stats

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
@dp.message(F.text =="Старт")
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Старт"))
    builder.add(types.KeyboardButton(text="Статистика"))
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text =="Статистика")
async def cmd_stats(message: types.Message):
    await message.answer("Статистика:")
    await message.answer(await get_stats(message.from_user.id))

@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем викторину!")
    await new_quiz(message)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer:" + option if option == right_answer else "wrong_answer:" + option)
        )
    builder.adjust(1)
    return builder.as_markup()

@dp.callback_query(lambda c: c.data and c.data.startswith("right_answer"))
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer("Вы выбрали: " + callback.data.split(":")[1])
    await callback.message.answer("Верно!")
    await save_result(callback.from_user.id, "Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

@dp.callback_query(lambda c: c.data and c.data.startswith("wrong_answer"))
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer("Вы выбрали: " + callback.data.split(":")[1])
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    await save_result(callback.from_user.id, "Неправильно.")
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    await message.answer("Статистика:")
    await message.answer(await get_stats(message.from_user.id))