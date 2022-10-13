from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def pagination_others(count: int, page: int, hotel_info, hotel_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура пагинация для вывода фото (на все остальные фото кроме первого и последнего)

    :param count: общее количество фото в пагинации;
    :param page: номер страницы на главном фото в данный момент;
    :param hotel_info: идентификационный номер отеля, чтобы вытащить из MemoryStorage необходимую информацию (которая
                       не влезает в call.data по размеру самостоятельно);
    :param hotel_id: ID отеля для ссылки на карточку отеля.

    """

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(text=f'Предыдущее',
                             callback_data="{\"NumberPage\":" + str(page - 1) +
                                           ",\"CountPage\":" + str(count) +
                                           ",\"HotelInfo\":" + str(hotel_info) + "}"),

        InlineKeyboardButton(text=f'{page}/{count}',
                             callback_data=f' '),

        InlineKeyboardButton(text=f'Следующее',
                             callback_data="{\"NumberPage\":" + str(page + 1) +
                                           ",\"CountPage\":" + str(count) +
                                           ",\"HotelInfo\":" + str(hotel_info) + "}")
    )

    markup.add(InlineKeyboardButton(text='Больше информации об отеле', url=f'https://hotels.com/ho{hotel_id}'))

    return markup
