from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def request_need_photos() -> InlineKeyboardMarkup:
    """ Клавиатура подтверждения необходимости вывода фото в подборке по каждому отелю (Да/Нет) """

    keyboard = InlineKeyboardMarkup()

    button1 = InlineKeyboardButton(text='Да', callback_data='Да')
    button2 = InlineKeyboardButton(text='Нет', callback_data='Нет')

    keyboard.add(button1, button2)

    return keyboard
