from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def request_photos_quantity() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   row_width=4,
                                   input_field_placeholder='Здесь ничего не пиши')

    button1 = KeyboardButton('3')
    button2 = KeyboardButton('4')
    button3 = KeyboardButton('5')
    button4 = KeyboardButton('6')
    button5 = KeyboardButton('7')
    button6 = KeyboardButton('8')
    button7 = KeyboardButton('9')
    button8 = KeyboardButton('10')

    keyboard.add(button1, button2, button3, button4, button5, button6, button7, button8)

    return keyboard
