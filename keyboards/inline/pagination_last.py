from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Tuple


def pagination_last(count: int, page: int, hotel_info, hotel_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(text=f'Предыдущее',
                             callback_data="{\"NumberPage\":" + str(page - 1) +
                                           ",\"CountPage\":" + str(count) +
                                           ",\"HotelInfo\":" + str(hotel_info) + "}"),

        InlineKeyboardButton(text=f'{page}/{count}',
                             callback_data=f' ')
    )

    markup.add(InlineKeyboardButton(text='Больше информации об отеле', url=f'https://hotels.com/ho{hotel_id}'))

    return markup
