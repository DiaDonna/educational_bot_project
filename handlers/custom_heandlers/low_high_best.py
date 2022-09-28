from loader import bot
from states.lowprice_command import CommandState
from hotel_requests import main_requests
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from googletrans import Translator
from datetime import date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from keyboards.inline.hotel_link import get_link
from keyboards.inline.pagination_first import pagination_first
from keyboards.inline.pagination_last import pagination_last
from keyboards.inline.pagination_others import pagination_others
from keyboards.inline.confirmation import request_confirmation
from keyboards.inline.locations import request_location
from keyboards.inline.need_photos import request_need_photos
from keyboards.reply.from_1_to_5 import request_quantity
from keyboards.reply.from_3_to_10 import request_photos_quantity

import json


# объект класса Translator из библиотеки googletrans для всех действий, касающихся перевода
translator = Translator()

data_template = {
    'sort_order': 'параметр сортировки',
    'city_name': 'название города',
    'selected_address': 'уточненная локация',
    'location_id': 'id локации',
    'distance': 'максимальное расстояние до центра города',
    'price_min': 'минимальная цена за ночь',
    'price_max': 'максимальная цена за ночь',
    'hotels_quantity': 'кол-во отелей',
    'is_photos': ' фото: Да/Нет',
    'photos_quantity': 'если Да: кол-во фото',
    'check_in': 'дата заезда (для запроса)',
    'arrival_date': 'дата заезда (для пользователя)',
    'check_out': 'дата выезда (для запроса)',
    'departure_date': 'дата выезда (для пользователя)',
}


@bot.message_handler(commands=['lowprice'])
def command(message: Message) -> None:
    """ Здесь ловим команду lowprice, устанавливаем 1 состояние city_to_search,
    и спрашиваем в каком городе будем искать """

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, CommandState.city_to_search, message.chat.id)

    bot.send_message(message.from_user.id,
                     f'{message.from_user.first_name}, в каком городе будем искать самые дешёвые отели?'
                     f'\n\n _На данный момент поиск по территориям РФ и РБ недоступен._ '
                     f'_Названия городов для поиска в других странах можно вводить как на русском языке,_ '
                     f'_так и на английском._', parse_mode='Markdown')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort_order'] = 'PRICE'


@bot.message_handler(commands=['highprice'])
def command(message: Message) -> None:
    """ Здесь ловим команду highprice, устанавливаем 1 состояние city_to_search,
    и спрашиваем в каком городе будем искать """

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, CommandState.city_to_search, message.chat.id)

    bot.send_message(message.from_user.id,
                     f'{message.from_user.first_name}, в каком городе будем искать самые дорогие отели?'
                     f'\n\n _На данный момент поиск по территориям РФ и РБ недоступен._ '
                     f'_Названия городов для поиска в других странах можно вводить как на русском языке,_ '
                     f'_так и на английском._', parse_mode='Markdown')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort_order'] = 'PRICE_HIGHEST_FIRST'


@bot.message_handler(commands=['bestdeal'])
def command(message: Message) -> None:
    """ Здесь ловим команду bestdeal, устанавливаем 1 состояние city_to_search,
    и спрашиваем в каком городе будем искать """

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, CommandState.city_to_search, message.chat.id)

    bot.send_message(message.from_user.id,
                     f'{message.from_user.first_name}, в каком городе будем искать отели по удаленности от центра '
                     f'и диапазону цены?'
                     f'\n\n _На данный момент поиск по территориям РФ и РБ недоступен._ '
                     f'_Названия городов для поиска в других странах можно вводить как на русском языке,_ '
                     f'_так и на английском._', parse_mode='Markdown')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['sort_order'] = 'DISTANCE_FROM_LANDMARK'


@bot.message_handler(state=CommandState.city_to_search)
def get_city(message: Message) -> None:
    """ Здесь ловим ответ пользователя (в каком городе искать отели), проверяем на корректность,
    устанавливаем 2 состояние concretize_location и просим пользователя уточнить локацию с помощью inline-клавиатуры """

    # проверка на корректность введенных пользователем данных
    correct_city = True
    for sym in message.text:
        if sym.isalpha():
            continue
        else:
            if sym in [' ', '-']:
                continue
            else:
                correct_city = False
                break

    # если первичная проверка на корректность пройдена
    if correct_city:
        bot.set_state(message.from_user.id, CommandState.concretize_location, message.chat.id)

        # если город был написан на английском
        if translator.translate(message.text).src == 'en':
            keyboard = request_location(country=message.text, message=message)

            # если такой город существует и возвращается клавиатура с вариантами локаций
            if keyboard:
                bot.send_message(message.from_user.id,
                                 'Я нашел несколько подходящих вариантов. Выбери тот, который больше подходит:',
                                 reply_markup=keyboard)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['city_name'] = translator.translate(message.text, dest='ru').text.capitalize()

            # если возвращается None, то просим заново ввести город
            else:
                bot.send_message(message.from_user.id,
                                 'Я не нашёл подходящих вариантов по твоему запросу. '
                                 'Попробуй заново ввести название города.')
                bot.set_state(message.from_user.id, CommandState.city_to_search, message.chat.id)

        # если город был написан на русском
        else:
            keyboard = request_location(country=translator.translate(message.text, dest='en').text,
                                        message=message)

            # если возвращается клавиатура с вариантами локаций
            if keyboard:
                bot.send_message(message.from_user.id,
                                 'Я нашел несколько подходящих вариантов. Выбери тот, который больше подходит:',
                                 reply_markup=keyboard)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['city_name'] = message.text.capitalize()

            # если возвращается None, то просим заново ввести город
            else:
                bot.send_message(message.from_user.id,
                                 'Я не нашёл подходящих вариантов по твоему запросу. '
                                 'Попробуй заново ввести название города.')
                bot.set_state(message.from_user.id, CommandState.city_to_search, message.chat.id)

    # если пользователь ввел что-то не прошедшее проверку на корректность
    else:
        bot.send_message(message.from_user.id,
                         'Название города может содержать только буквы, а также знаки пробела или дефиса.'
                         '\n\nПопробуем еще раз!')


@bot.message_handler(state=[CommandState.concretize_location,
                            CommandState.is_photos,
                            CommandState.arrival_date,
                            CommandState.departure_date,
                            CommandState.the_end,
                            CommandState.searching])
def control_manual_input(message: Message):
    """ Если пользователь вместо нажатия на кнопку inline-клавиатуры воспользовался ручным вводом, то попадаем сюда и
        ничего не происходит пока пользователь все-таки не нажмёт на кнопку """
    if message:
        pass


@bot.callback_query_handler(func=lambda call: call.data.isdigit() is True or call.data == 'Другой город')
def callback_query_get_location(call: CallbackQuery) -> None:
    """ Здесь ловим ответ с inline-клавиатуры (уточнение локации), устанавливаем состояние и задаем следующий вопрос
     в зависимости от команды, сценарий которой проходит пользователь """

    # Если ответ с инлайн-клавиатуры касался конкретной локации (т.е. в call.data лежит id выбранной локации)
    if call.data.isdigit():

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:

            for address, loc_id in data['locations_dict'].items():
                if loc_id == call.data:
                    selected_address = address
                    break

            data['selected_address'] = selected_address
            data['location_id'] = call.data
            data.pop('locations_dict')

            bot.edit_message_text(message_id=call.message.message_id,
                                  inline_message_id=call.inline_message_id,
                                  chat_id=call.message.chat.id,
                                  text=f'{call.message.text[:-1]}.'
                                       f'\n\nТвой выбор: \n{selected_address}')

            # Если идет сценарий команды Lowprice или highprice, то устанавливаем состояние hotels_quantity и задаем
            # вопрос о кол-ве отелей в подборке
            if data['sort_order'] == 'PRICE_HIGHEST_FIRST' or data['sort_order'] == 'PRICE':
                bot.set_state(call.from_user.id, CommandState.hotels_quantity, call.message.chat.id)
                bot.send_message(call.from_user.id,
                                 'Отлично! Сколько отелей хочешь видеть в подборке? (не более 5)',
                                 reply_markup=request_quantity())

            # Иначе если идет сценарий команды bestdeal, то устанавливаем состояние distance и задаем вопрос
            # о максимальном расстоянии от центра города до отеля
            elif data['sort_order'] == 'DISTANCE_FROM_LANDMARK':
                bot.set_state(call.from_user.id, CommandState.distance, call.message.chat.id)
                bot.send_message(call.message.chat.id,
                                 'Отлично! На каком максимальном расстоянии от центра (в км) будем искать отели?'
                                 '\n_В ответ напиши ЦЕЛОЕ число_', parse_mode='Markdown')

    # Иначе если ответ с инлайн-клавиатуры НЕ локация, а вариант с повторным выбором города
    elif call.data == 'Другой город':
        bot.set_state(call.from_user.id, CommandState.city_to_search, call.message.chat.id)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text=f'Хорошо, попробуй ввести название другого города.')


@bot.message_handler(state=CommandState.distance)
def get_distance_from_city_center(message: Message) -> None:
    """ Здесь ловим ответ от пользователя (на каком расстоянии от центра города искать отели),
    устанавливаем состояние price_min и спрашиваем минимальную цену за ночь """

    if message.text.isdigit() and int(message.text) > 0:
        bot.set_state(message.from_user.id, CommandState.price_min, message.chat.id)
        bot.send_message(message.from_user.id,
                         'Хорошо. От какой цены за ночь искать отели?')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance'] = int(message.text)

    else:
        bot.send_message(message.from_user.id,
                         'Я не понимаю, что ты имеешь в виду. Пожалуйста, напиши в ответ целое число больше 0.')


@bot.message_handler(state=CommandState.price_min)
def get_price_min(message: Message) -> None:
    """ Здесь ловим ответ от пользователя (начальный диапазон цены за ночь в отеле),
    устанавливаем состояние price_max и спрашиваем максимальную цену за ночь """

    if message.text.isdigit() and int(message.text) > 0:
        bot.set_state(message.from_user.id, CommandState.price_max, message.chat.id)
        bot.send_message(message.from_user.id,
                         'Хорошо. До какой цены за ночь искать отели?')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = int(message.text)

    else:
        bot.send_message(message.from_user.id,
                         'Я не понимаю, что ты имеешь в виду. Пожалуйста, напиши в ответ целое число.')


@bot.message_handler(state=CommandState.price_max)
def get_price_max(message: Message) -> None:
    """ Здесь ловим ответ от пользователя (конечный диапазон цены за ночь в отеле),
    устанавливаем состояние hotels_quantity и спрашиваем сколько отелей выводить в подборке """

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) > data['price_min']:
                bot.set_state(message.from_user.id, CommandState.hotels_quantity, message.chat.id)
                bot.send_message(message.from_user.id,
                                 'Отлично! Сколько отелей хочешь видеть в подборке? (не более 5)',
                                 reply_markup=request_quantity())

                data['price_max'] = int(message.text)

            else:
                bot.send_message(message.from_user.id,
                                 'Цена максимум должна быть больше цены минимум.')
    else:
        bot.send_message(message.from_user.id,
                         'Я не понимаю, что ты имеешь в виду. '
                         'Пожалуйста, напиши в ответ целое число большее, чем начальный диапазон цены.')


@bot.message_handler(state=CommandState.hotels_quantity)
def get_quantity(message: Message) -> None:
    """ Здесь ловим ответ пользователя (какое кол-во отелей выводить в подборке от 1 до 5), проверяем корректность,
    устанавливаем 4 состояние is_photos и спрашиваем нужны ли фото отелей """

    # Пробуем преобразовать введенный пользователем текст к типу int, чтобы проверить корректность введенных данных
    # по двум критериям: число (int) и диапазон от 1 до 5 включительно.
    try:
        qnt = int(message.text)

        if 0 < qnt < 6:
            # Если пользователь ввёл вручную либо с помощью reply-клавиатуры число в диапазоне от 1 до 5 включительно
            bot.set_state(message.from_user.id, CommandState.is_photos, message.chat.id)
            bot.send_message(message.from_user.id,
                             'Прекрасный выбор! \nЕсли нужны фотографии каждого отеля из подборки, нажми "Да", '
                             'в противном случае - выбери "Нет"',
                             reply_markup=request_need_photos())

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['hotels_quantity'] = message.text

        else:
            # если пользователь ввел вручную число, но оно либо меньше 1, либо больше 5
            bot.send_message(message.from_user.id,
                             'Пожалуйста, нажми на кнопку, не используя ручной ввод текста'
                             '\nЛибо введи число от 1 до 5.')

    except ValueError:
        # Если пользователь ввел вручную что угодно, кроме числа
        bot.send_message(message.from_user.id,
                         'Пожалуйста, нажми на кнопку, не используя ручной ввод текста'
                         '\nЛибо введи число от 1 до 5.')


@bot.callback_query_handler(func=lambda call: call.data == 'Да' or call.data == 'Нет')
def callback_query_need_photos(call: CallbackQuery) -> None:
    """ Здесь ловим ответ пользователя с inline-клавиатуры (нужны фото отелей в подборке или нет),
    устанавливаем состояние в зависимости от ответа пользователя:
    - Если фото нужны, то устанавливаем состояние photos_quantity и спрашиваем сколько фото нужно вывести в подборке;
    - Если не нужны, то устанавливаем состояние arrival_date и уточняем дату заезда """

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['is_photos'] = call.data

    if call.data == 'Да':
        bot.set_state(call.from_user.id, CommandState.photos_quantity, call.message.chat.id)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text=f'Нужны ли фото отелей в подборке? \nТвой ответ: Да', )
        bot.send_message(call.from_user.id, 'А сколько фото хочешь видеть в подборке? \nОтветь цифрой от 3 до 10',
                         reply_markup=request_photos_quantity())

    elif call.data == 'Нет':
        bot.set_state(call.from_user.id, CommandState.arrival_date, call.message.chat.id)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text='Нужны ли фото отелей в подборке? \nТвой ответ: Нет', )

        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
        bot.send_message(call.message.chat.id,
                         f"Выбери дату заезда ({translator.translate(LSTEP[step], dest='ru').text})",
                         reply_markup=calendar)


@bot.message_handler(state=CommandState.photos_quantity)
def get_photos_qnt(message: Message) -> None:
    """  Здесь ловим ответ от пользователя (сколько фото по отелям), проверяем корректность,
    устанавливаем состояние arrival_date и уточняем дату заезда """

    try:
        qnt = int(message.text)

        if 2 < qnt < 11:
            bot.set_state(message.from_user.id, CommandState.arrival_date, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photos_quantity'] = int(message.text)

            calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
            bot.send_message(message.chat.id,
                             f"Выбери дату заезда ({translator.translate(LSTEP[step], dest='ru').text})",
                             reply_markup=calendar)

        else:
            bot.send_message(message.from_user.id,
                             'Пожалуйста, введи *число от 3 до 10* или просто нажми нужную кнопку.',
                             parse_mode='Markdown')

    except ValueError:
        bot.send_message(message.from_user.id,
                         'Чтобы я правильно тебя понял, отправь ответ *цифрой* или просто нажми нужную кнопку.',
                         parse_mode='Markdown')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_query_arrival_date(call: CallbackQuery):
    """ Здесь ловим ответ от пользователя (дата заезда), устанавливаем состояние departure_date
    и уточняем дату выезда """

    bot.set_state(call.from_user.id, CommandState.departure_date, call.message.chat.id)

    result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                 locale='ru',
                                                 min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выбери дату заезда ({translator.translate(LSTEP[step], dest='ru').text})",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Выбранная дата заезда: {result.strftime('%d-%m-%Y')}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data["check_in"] = result
            data["arrival_date"] = result.strftime('%d-%m-%Y')

        correct_min_data = result + timedelta(days=1)
        calendar, step = DetailedTelegramCalendar(calendar_id=2,
                                                  locale='ru',
                                                  min_date=correct_min_data).build()
        bot.send_message(call.message.chat.id,
                         f"Выбери дату выезда ({translator.translate(LSTEP[step], dest='ru').text})",
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_query_departure_date(call: CallbackQuery):
    """ Здесь ловим ответ от пользователя (дата выезда), устанавливаем состояние the_end, подводим итог
    и спрашиваем пользователя: 'Всё верно или начать заново?' """

    bot.set_state(call.from_user.id, CommandState.the_end, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:

        correct_min_data = data["check_in"] + timedelta(days=1)
        result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                     locale='ru',
                                                     min_date=correct_min_data).process(call.data)

        if not result and key:
            bot.edit_message_text(f"Выбери дату выезда ({translator.translate(LSTEP[step], dest='ru').text})",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"Выбранная дата выезда: {result.strftime('%d-%m-%Y')}",
                                  call.message.chat.id,
                                  call.message.message_id)
            data["check_out"] = result
            data["departure_date"] = result.strftime('%d-%m-%Y')

            if data['sort_order'] == 'PRICE_HIGHEST_FIRST' or data['sort_order'] == 'PRICE':

                if data["is_photos"] == 'Да':
                    bot.send_message(call.from_user.id,
                                     'Подведём итог!'
                                     f'\n\nИщем в городе: {data["city_name"]}'
                                     f'\nУточненное местоположение: {data["selected_address"]}'
                                     f'\nКоличество отелей в подборке: {data["hotels_quantity"]} '
                                     f'\nФото нужны: {data["is_photos"]}'
                                     f'\nКоличество фото по каждому отелю: {data["photos_quantity"]}'
                                     f'\nДата заезда: {data["arrival_date"]}'
                                     f'\nДата выезда: {data["departure_date"]}',
                                     reply_markup=request_confirmation())

                elif data["is_photos"] == 'Нет':
                    bot.send_message(call.from_user.id,
                                     'Подведём итог!'
                                     f'\n\nИщем в городе: {data["city_name"]}'
                                     f'\nУточненное местоположение: {data["selected_address"]}'
                                     f'\nКоличество отелей в подборке: {data["hotels_quantity"]} '
                                     f'\nФото нужны: {data["is_photos"]}'
                                     f'\nДата заезда: {data["arrival_date"]}'
                                     f'\nДата выезда: {data["departure_date"]}',
                                     reply_markup=request_confirmation())

            elif data['sort_order'] == 'DISTANCE_FROM_LANDMARK':

                if data["is_photos"] == 'Да':
                    bot.send_message(call.from_user.id,
                                     'Подведём итог!'
                                     f'\n\nИщем в городе: {data["city_name"]}'
                                     f'\nУточненное местоположение: {data["selected_address"]}'
                                     f'\nМаксимальное расстояние от центра: {data["distance"]}'
                                     f'\nМинимальная цена за ночь: {data["price_min"]}'
                                     f'\nМаксимальная цена за ночь: {data["price_max"]}'
                                     f'\nКоличество отелей в подборке: {data["hotels_quantity"]} '
                                     f'\nФото нужны: {data["is_photos"]}'
                                     f'\nКоличество фото по каждому отелю: {data["photos_quantity"]}'
                                     f'\nДата заезда: {data["arrival_date"]}'
                                     f'\nДата выезда: {data["departure_date"]}',
                                     reply_markup=request_confirmation())

                elif data["is_photos"] == 'Нет':
                    bot.send_message(call.from_user.id,
                                     'Подведём итог!'
                                     f'\n\nИщем в городе: {data["city_name"]}'
                                     f'\nУточненное местоположение: {data["selected_address"]}'
                                     f'\nМаксимальное расстояние от центра: {data["distance"]}км'
                                     f'\nМинимальная цена за ночь: {data["price_min"]}руб'
                                     f'\nМаксимальная цена за ночь: {data["price_max"]}руб'
                                     f'\nКоличество отелей в подборке: {data["hotels_quantity"]} '
                                     f'\nФото нужны: {data["is_photos"]}'
                                     f'\nДата заезда: {data["arrival_date"]}'
                                     f'\nДата выезда: {data["departure_date"]}',
                                     reply_markup=request_confirmation())


@bot.callback_query_handler(func=lambda call: call.data == 'Верно' or call.data == 'Заново')
def callback_query_get_confirmation(call: CallbackQuery) -> None:
    """  Здесь ловим ответ пользователя с inline-клавиатуры (подтверждение или начать заново):
    - Если все верно, то готовим подборку
    - Если начать заново, то 'обнуляем' состояние пользователя """

    if call.data == 'Верно':
        bot.set_state(call.from_user.id, CommandState.searching, call.message.chat.id)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text=f'{call.message.text}.'
                                   f'\n\n*Отлично! Начинаю подготовку подборки...*',
                              parse_mode='Markdown')

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:

            if data['sort_order'] == 'PRICE_HIGHEST_FIRST' or data['sort_order'] == 'PRICE':
                hotels = main_requests.hotels_search(destination_id=data['location_id'],
                                                     hotels_qnt=data['hotels_quantity'],
                                                     check_in=data['check_in'].strftime('%Y-%m-%d'),
                                                     check_out=data['check_out'].strftime('%Y-%m-%d'),
                                                     sort_order=data['sort_order'])

            elif data['sort_order'] == 'DISTANCE_FROM_LANDMARK':
                hotels = main_requests.hotels_search_bestdeal(destination_id=data['location_id'],
                                                              hotels_qnt=data['hotels_quantity'],
                                                              check_in=data['check_in'].strftime('%Y-%m-%d'),
                                                              check_out=data['check_out'].strftime('%Y-%m-%d'),
                                                              sort_order=data['sort_order'],
                                                              price_min=data['price_min'],
                                                              price_max=data['price_max'],
                                                              max_distance=data['distance'])

            count = 1
            for hotel_id, hotel_info in hotels.items():
                bot.send_message(call.message.chat.id,
                                 text=f'*{count} вариант:*',
                                 parse_mode='Markdown')

                if data['is_photos'] == 'Да':
                    bot.send_message(call.message.chat.id, hotel_info)

                    photos_url = main_requests.photos_search(hotel_id=hotel_id, photos_qnt=data['photos_quantity'])
                    data[count] = [photos_url, hotel_id]
                    bot.send_photo(call.message.chat.id,
                                   photo=photos_url[0],
                                   reply_markup=pagination_first(
                                       count=data['photos_quantity'],
                                       page=1,
                                       hotel_info=count,
                                       hotel_id=hotel_id),
                                   allow_sending_without_reply=True)

                else:
                    bot.send_message(call.message.chat.id,
                                     hotel_info,
                                     reply_markup=get_link(hotel_id=hotel_id))
                count += 1

            if len(hotels) > 0:
                bot.send_message(call.message.chat.id,
                                 'Это всё, что я нашел по твоим критериям.'
                                 '\n\nЕсли хочешь, чтобы я сделал для тебя новую подборку, '
                                 'выбери подходящую команду в меню ниже.',
                                 allow_sending_without_reply=True)
            else:
                bot.send_message(call.message.chat.id,
                                 'Я не смог ничего подобрать по твоим критериям.'
                                 '\n\nЕсли хочешь, чтобы я сделал для тебя другую подборку, '
                                 'выбери подходящую команду в меню ниже.',
                                 allow_sending_without_reply=True)

    elif call.data == 'Заново':
        bot.set_state(call.from_user.id, CommandState.city_to_search)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text='*Хорошо, давай начнем сначала!*'
                                   '\nВ каком городе будем искать отели?'
                                   f'\n\n _На данный момент поиск по территориям РФ и РБ недоступен._ '
                                   f'_Названия городов для поиска в других странах можно вводить как на русском языке,_'
                                   f'_так и на английском._', parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    json_string = json.loads(call.data)
    count = json_string['CountPage']
    page = json_string['NumberPage']
    hotel_info = json_string['HotelInfo']

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        current_photos = data[hotel_info][0]
        current_photo = InputMediaPhoto(media=current_photos[page - 1])

        hotel_id = data[hotel_info][1]

        if page == 1:
            keyboard = pagination_first(count=count,
                                        page=page,
                                        hotel_info=hotel_info,
                                        hotel_id=hotel_id)

        elif page == count:
            keyboard = pagination_last(count=count, page=page, hotel_info=hotel_info, hotel_id=hotel_id)

        else:
            keyboard = pagination_others(count=count, page=page, hotel_info=hotel_info, hotel_id=hotel_id)

        bot.edit_message_media(media=current_photo,
                               chat_id=call.message.chat.id,
                               message_id=call.message.message_id,
                               reply_markup=keyboard)
