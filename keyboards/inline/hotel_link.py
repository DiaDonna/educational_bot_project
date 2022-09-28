from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_link(hotel_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Больше информации об отеле', url=f'https://hotels.com/ho{hotel_id}'))

    return keyboard

