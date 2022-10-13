from loader import bot
from telebot.types import Message


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    bot.reply_to(message, f"{message.from_user.full_name}, я тебя не понял...\n"
                          f"\nЧетко следуй моим инструкциям "
                          f"или выбери подходящую тебе команду из меню ниже и начни заново.")
