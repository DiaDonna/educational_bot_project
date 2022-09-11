from telebot.handler_backends import State, StatesGroup


class CommandState(StatesGroup):
    city_to_search = State()
    concretize_location = State()
    hotels_quantity = State()
    is_photos = State()
    photos_quantity = State()
    arrival_date = State()
    departure_date = State()
    the_end = State()
    searching = State()
