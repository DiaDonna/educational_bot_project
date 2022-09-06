from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from hotel_requests import main_requests
from loader import bot


def request_location(message) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    locations_dict = main_requests.location_search(message)

    for address, city_id in locations_dict.items():
        keyboard.add(InlineKeyboardButton(text=address, callback_data=city_id))

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['locations_dict'] = locations_dict

    return keyboard
