from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from loader import bot
from hotel_requests import main_requests


def request_location(country: str, message: Message) -> InlineKeyboardMarkup | None:
    """
    Клавиатура с вариантами локаций

    :param country: название города для API запроса на поиск приближенных локаций;
    :param message: объект Message

    :return: Клавиатура, где каждая инлайн-кнопка это найденная приближенная локация
             ИЛИ None, если локаций не найдено

    """

    keyboard = InlineKeyboardMarkup()
    locations_dict = main_requests.location_search(country)

    if locations_dict:

        for address, city_id in locations_dict.items():
            keyboard.add(InlineKeyboardButton(text=address, callback_data=city_id))

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['locations_dict'] = locations_dict

        keyboard.add(InlineKeyboardButton(text='Мне ничего не подходит, хочу ввести город заново',
                                          callback_data='Другой город'))

        return keyboard

    else:
        return None
