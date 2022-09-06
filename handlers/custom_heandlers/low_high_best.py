from keyboards.inline.confirmation import request_confirmation
from keyboards.inline.locations import request_location
from keyboards.reply.hotels_qnt import request_hotels_qnt
from keyboards.inline.need_photos import request_need_photos
from loader import bot
from states.lowprice_command import CommandState
from telebot.types import Message, CallbackQuery


commands_text = {
    "lowrice": 'в каком городе будем искать самые дешевые отели?',
    "highprice": 'в каком городе будем искать самые дорогие отели?'
}


@bot.message_handler(commands=['lowprice'])
def command(message: Message) -> None:
    """ Здесь ловим команду lowprice, устанавливаем 1 состояние city_to_search,
    и спрашиваем в каком городе будем искать """

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, CommandState.city_to_search, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'{message.from_user.first_name}, {commands_text["lowrice"]}')


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

    if correct_city:
        bot.set_state(message.from_user.id, CommandState.concretize_location, message.chat.id)
        bot.send_message(message.from_user.id,
                         'Я нашел несколько подходящих вариантов. Выбери тот, который больше подходит:',
                         reply_markup=request_location(message))
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text

    else:
        bot.send_message(message.from_user.id,
                         'Название города может содержать только буквы, а также знаки пробела или дефиса.'
                         '\n\nПопробуем еще раз!')


@bot.message_handler(state=CommandState.concretize_location)
def control_manual_input(message: Message):
    """ Если пользователь вместо нажатия на кнопку inline-клавиатуры воспользовался ручным вводом, то попадаем сюда и
        ничего не происходит пока пользователь все-таки не нажмёт на кнопку """
    if message:
        pass


@bot.callback_query_handler(func=lambda call: call.data.isdigit() is True)
def callback_query_get_location(call: CallbackQuery) -> None:
    """ Здесь ловим ответ с inline-клавиатуры (уточнение локации), устанавливаем 3 состояние hotels_quantity
     и спрашиваем какое кол-во отелей нужно вывести в подборке """

    bot.set_state(call.from_user.id, CommandState.hotels_quantity, call.message.chat.id)

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

    bot.send_message(call.from_user.id,
                     'Отлично! Сколько отелей хочешь видеть в подборке? (не более 5)',
                     reply_markup=request_hotels_qnt())


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
                             'Пожалуйста, нажмите на кнопку, не используя ручной ввод текста'
                             '\nЛибо введите число от 1 до 5.')

    except ValueError:
        # Если пользователь ввел вручную что угодно, кроме числа
        bot.send_message(message.from_user.id,
                         'Пожалуйста, нажмите на кнопку, не используя ручной ввод текста'
                         '\nЛибо введите число от 1 до 5.')


@bot.message_handler(state=CommandState.is_photos)
def control_manual_input(message: Message) -> None:
    """ Если пользователь вместо нажатия на кнопку inline-клавиатуры воспользовался ручным вводом, то попадаем сюда и
    ничего не происходит пока пользователь все-таки не нажмёт на кнопку """
    if message:
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'Да' or call.data == 'Нет')
def callback_query_need_photos(call: CallbackQuery) -> None:
    """ Здесь ловим ответ пользователя с inline-клавиатуры (нужны фото отелей в подборке или нет),
    устанавливаем состояние в зависимости от ответа пользователя:
    - Если фото нужны, то устанавливаем состояние photos_quantity и спрашиваем сколько фото нужно вывести в подборке;
    - Если не нужны, то устанавливаем состояние the_end, подводим итог и спрашиваем 'Все верно или начать заново?' """

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['is_photos'] = call.data

    if call.data == 'Да':
        bot.set_state(call.from_user.id, CommandState.photos_quantity, call.message.chat.id)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text=f'Нужны ли фото отелей в подборке? \nТвой ответ: Да', )
        bot.send_message(call.from_user.id, 'А сколько фото хочешь видеть в подборке? \nОтветь цифрой от 1 до 7')

    elif call.data == 'Нет':
        bot.set_state(call.from_user.id, CommandState.the_end, call.message.chat.id)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text='Нужны ли фото отелей в подборке? \nТвой ответ: Нет', )
        bot.send_message(call.from_user.id,
                         'Подведём итог!'
                         f'\n\nИщем в городе: {data["city_name"]}'
                         f'\nУточненное местоположение: {data["selected_address"]}'
                         f'\nКоличество отелей в подборке: {data["hotels_quantity"]} '
                         f'\nФото нужны: {data["is_photos"]}',
                         reply_markup=request_confirmation())


@bot.message_handler(state=CommandState.photos_quantity)
def get_photos_qnt(message: Message) -> None:
    """  Здесь ловим ответ от пользователя (сколько фото по отелям), проверяем корректность,
    устанавливаем состояние the_end и спрашиваем 'Все верно или начать заново?' """

    try:
        qnt = int(message.text)

        if 0 < qnt < 8:
            bot.set_state(message.from_user.id, CommandState.the_end, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['photos_quantity'] = message.text

            bot.send_message(message.from_user.id,
                             'Подведём итог!'
                             f'\n\nИщем в городе: {data["city_name"]}'
                             f'\nУточненное местоположение: {data["selected_address"]}'
                             f'\nКоличество отелей в подборке: {data["hotels_quantity"]} '
                             f'\nФото нужны: {data["is_photos"]}'
                             f'\nКоличество фото по каждому отелю: {data["photos_quantity"]}',
                             reply_markup=request_confirmation())

        else:
            bot.send_message(message.from_user.id,
                             'Пожалуйста, введи *число от 1 до 7*.', parse_mode='Markdown')

    except ValueError:
        bot.send_message(message.from_user.id,
                         'Чтобы я правильно тебя понял, отправь ответ *цифрой* от 1 до 7.', parse_mode='Markdown')


@bot.message_handler(state=CommandState.the_end)
def control_manual_input(message: Message):
    """ Если пользователь вместо нажатия на кнопку inline-клавиатуры воспользовался ручным вводом, то попадаем сюда и
        ничего не происходит пока пользователь все-таки не нажмёт на кнопку """
    if message:
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'Верно' or call.data == 'Заново')
def callback_query_get_confirmation(call: CallbackQuery) -> None:
    """  Здесь ловим ответ пользователя с inline-клавиатуры (подтверждение или начать заново):
    - Если все верно, то готовим подборку
    - Если начать заново, то 'обнуляем' состояние пользователя """

    if call.data == 'Верно':
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text=f'{call.message.text}.'
                                   f'\n\n*Отлично! Начинаю подготовку подборки...*',
                              parse_mode='Markdown')

    elif call.data == 'Заново':
        bot.set_state(call.from_user.id, CommandState.city_to_search)
        bot.edit_message_text(message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id,
                              chat_id=call.message.chat.id,
                              text='*Хорошо, давай начнем сначала!*', parse_mode='Markdown')
        bot.send_message(call.from_user.id,
                         f'{call.from_user.first_name}, в каком городе будем искать самые дешевые отели?')
