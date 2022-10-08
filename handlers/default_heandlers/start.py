from telebot.types import Message

import notifications
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\n"
                          f"\nЧтобы я подобрал идеальные варианты, выбери подходящую тебе команду из меню ниже.")

    notifications.sending_notification(chat_id=message.chat.id)
