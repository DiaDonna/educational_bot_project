from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def request_choice_for_history() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   row_width=1,
                                   input_field_placeholder='Здесь ничего не пиши')

    button1 = KeyboardButton('Выбрать конкретный день поиска')
    button2 = KeyboardButton('Выбрать период поиска')
    button3 = KeyboardButton('Вывести всю историю поиска')

    keyboard.add(button1, button2, button3)

    return keyboard
