from keyboards.reply.hotels_qnt import request_hotels_qnt
from keyboards.reply.need_photos import request_need_photos
from loader import bot
from states.lowprice_command import LowpriceCommandState
from telebot.types import Message, CallbackQuery


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """ Здесь ловим команду lowprice, устанавливаем 1 состояние city_to_search """

    bot.set_state(message.from_user.id, LowpriceCommandState.city_to_search, message.chat.id)
    bot.send_message(message.from_user.id,
                     f'{message.from_user.first_name}, в каком городе будем искать самые дешевые отели?')


@bot.message_handler(state=LowpriceCommandState.city_to_search)
def get_city(message: Message) -> None:
    """ Здесь ловим ответ пользователя (в каком городе искать отели), проверяем на корректность
    и устанавливаем 2 состояние hotels_quantity"""

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
        bot.set_state(message.from_user.id, LowpriceCommandState.hotels_quantity, message.chat.id)
        bot.send_message(message.from_user.id,
                         'Отлично! Чтобы выбрать количество отелей в подборке, нажми на кнопку ниже.',
                         reply_markup=request_hotels_qnt())

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text

    else:
        bot.send_message(message.from_user.id,
                         'Название города может содержать только буквы, а также знаки пробела или дефиса.'
                         '\n\nПопробуем еще раз!')


@bot.message_handler(state=LowpriceCommandState.hotels_quantity)
def get_quantity(message: Message) -> None:
    """ Здесь ловим ответ пользователя (какое кол-во отелей выводить в подборке от 1 до 5), проверяем корректность
    и устанавливаем 3 состояние is_photos """

    # Пробуем преобразовать введенный пользователем текст к типу int, чтобы проверить корректность введенных данных
    # по двум критериям: число (int) и диапазон от 1 до 5 включительно.
    try:
        qnt = int(message.text)

        if 0 < qnt < 6:
            # Если пользователь ввёл вручную либо с помощью reply-клавиатуры число в диапазоне от 1 до 5 включительно
            bot.set_state(message.from_user.id, LowpriceCommandState.is_photos, message.chat.id)
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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    """ Здесь хочу отловить ответ от инлайн-клавиатуры (нужно ли выгружать фото к отелям)
    и проверить действительно ли пользователь нажимал именно на кнопки, а в случае, если был случайный ввод чего-либо,
    то тоже отловить это и сказать пользователю, что так не пойдет и попросить снова нажать на кнопку
    (либо же каким-то образом 'закрыть' пользователю обычный ручной ввод) """

    if call.data == 'Да':
        print('ok')
    else:
        print('ne ok')



