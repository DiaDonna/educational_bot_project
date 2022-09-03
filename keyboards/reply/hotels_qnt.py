from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def request_hotels_qnt() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder='Здесь ничего не пиши')

    keyboard.add(KeyboardButton('1'))
    keyboard.add(KeyboardButton('2'))
    keyboard.add(KeyboardButton('3'))
    keyboard.add(KeyboardButton('4'))
    keyboard.add(KeyboardButton('5'))

    return keyboard
