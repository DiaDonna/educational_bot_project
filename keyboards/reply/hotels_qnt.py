from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def request_hotels_qnt() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   row_width=3,
                                   input_field_placeholder='Здесь ничего не пиши')

    button1 = KeyboardButton('1')
    button2 = KeyboardButton('2')
    button3 = KeyboardButton('3')
    button4 = KeyboardButton('4')
    button5 = KeyboardButton('5')

    keyboard.add(button1, button2, button3, button4, button5)

    return keyboard
