from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot


def pagination_first(count: int, page: int, hotel_info: int, hotel_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),

        InlineKeyboardButton(text=f'Следующее',
                             callback_data="{\"NumberPage\":" + str(page + 1) +
                                           ",\"CountPage\":" + str(count) +
                                           ",\"HotelInfo\":" + str(hotel_info) + "}")
    )

    markup.add(InlineKeyboardButton(text='Больше информации об отеле', url=f'https://hotels.com/ho{hotel_id}'))

    return markup
