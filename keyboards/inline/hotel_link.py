from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_link(hotel_id: int) -> InlineKeyboardMarkup:
    """ Кнопка для ссылки на карточку отеля

    :param hotel_id: ID отеля

    """

    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Больше информации об отеле', url=f'https://hotels.com/ho{hotel_id}'))

    return keyboard

