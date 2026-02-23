import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# Токен бота
BOT_TOKEN = "7995281142:AAGyqRVl9yRE6H1Jjry743Y8wRkXtY2WA64"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие"""
    await message.answer("Привет! Я бот для подтверждения заявок в канал.\n"
                         "После отправки заявки на вступление я напишу тебе.")

@dp.chat_join_request()
async def process_join_request(event: types.ChatJoinRequest):
    """Обработка запроса на вступление"""
    user = event.from_user
    chat = event.chat

    logging.info(f"Заявка от {user.full_name} (id: {user.id}) в чат {chat.title}")

    # Создаём кнопку, в callback_data сохраняем id пользователя и чата
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я не бот", callback_data=f"approve:{user.id}:{chat.id}")]
    ])

    try:
        # Отправляем сообщение пользователю
        await bot.send_message(
            chat_id=user.id,
            text="Для подтверждения, что вы не бот, нажмите кнопку ниже:",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение пользователю {user.id}: {e}")

@dp.callback_query(lambda c: c.data.startswith("approve"))
async def process_callback(callback: types.CallbackQuery):
    """Обработка нажатия кнопки"""
    await callback.answer()  # убираем "часики"

    # Разбираем данные
    data = callback.data.split(":")
    if len(data) != 3:
        await callback.message.edit_text("Неверный запрос.")
        return

    try:
        user_id = int(data[1])
        chat_id = int(data[2])
    except ValueError:
        await callback.message.edit_text("Ошибка в данных запроса.")
        return

    # Проверяем, что кнопку нажал тот же пользователь
    if callback.from_user.id != user_id:
        await callback.message.edit_text("Это не ваша заявка.")
        return

    try:
        # Принимаем заявку
        await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        await callback.message.edit_text("✅ Заявка принята! Добро пожаловать в канал.")
        logging.info(f"Заявка пользователя {user_id} принята в чат {chat_id}")
    except Exception as e:
        logging.error(f"Ошибка при принятии заявки: {e}")
        await callback.message.edit_text("❌ Не удалось принять заявку. Возможно, она уже устарела или вы уже в канале.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
