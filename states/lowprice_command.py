from telebot.handler_backends import State, StatesGroup


class CommandState(StatesGroup):
    city_to_search = State()
    concretize_location = State()
    hotels_quantity = State()
    is_photos = State()
    photos_quantity = State()
    the_end = State()
    start_parsing = State()
