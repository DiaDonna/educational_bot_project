from telebot.handler_backends import State, StatesGroup


class LowpriceCommandState(StatesGroup):
    city_to_search = State()
    hotels_quantity = State()
    is_photos = State()
    the_end = State()
