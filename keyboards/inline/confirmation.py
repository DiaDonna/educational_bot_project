from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def request_confirmation() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    button_correct = InlineKeyboardButton(text='Всё верно!', callback_data='Верно')
    button_again = InlineKeyboardButton(text='Хочу заново', callback_data='Заново')

    keyboard.add(button_correct, button_again)

    return keyboard
