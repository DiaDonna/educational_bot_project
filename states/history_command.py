from telebot.handler_backends import State, StatesGroup


class HistoryCommandState(StatesGroup):
    collections_quantity = State()
    search_date = State()
    search_from = State()
    search_to = State()
