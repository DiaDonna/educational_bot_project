import sqlite3

from loader import bot
from states.history_command import HistoryCommandState
from telebot.types import Message, CallbackQuery

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, datetime
from googletrans import Translator

from keyboards.reply.choice_for_history import request_choice_for_history


# создаем соединение с базой данных SQLite и возвращаем объект, представляющий ее
conn = sqlite3.connect(r'database/database.db', check_same_thread=False)
# создаем объект cursor для SQL-запросов к базе
cur = conn.cursor()

# объект класса Translator из библиотеки googletrans для всех действий, касающихся перевода
translator = Translator()


@bot.message_handler(commands=['history'])
def command(message: Message) -> None:
    """ Здесь ловим команду history, устанавливаем состояние collections_quantity и спрашиваем за какой период
    выводить историю поиска """

    try:
        bot.set_state(message.from_user.id, HistoryCommandState.collections_quantity, message.chat.id)

        bot.send_message(message.chat.id,
                         'За какой период вывести историю поиска?',
                         reply_markup=request_choice_for_history())

    except BaseException as except_name:
        # вносим информацию об ошибке в базу данных
        cur.execute('INSERT INTO logging (datetime, except_name) VALUES (?, ?)',
                    (datetime.now(), str(except_name)))
        conn.commit()

        # пишем сообщение пользователю об ошибке и обнуляем состояние
        bot.send_message(message.from_user.id,
                         'Что-то пошло не так... Пожалуйста выбери команду заново.')
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=HistoryCommandState.collections_quantity)
def show_all_history(message: Message) -> None:
    """  Здесь ловим ответ с inline-клавиатуры (период вывода истории поиска) и производим дальнейшие действия
    в зависимости от ответа пользователя """

    try:
        # если пользователь хочет посмотреть историю поиска в конкретный день, то устанавливаем состояние search_date
        #  и отправляем календарь для ввода даты
        if message.text == 'Выбрать конкретный день поиска':
            bot.set_state(message.from_user.id, HistoryCommandState.search_date, message.chat.id)

            calendar, step = DetailedTelegramCalendar(calendar_id=3,
                                                      max_date=date.today()).build()
            bot.send_message(message.chat.id,
                             f"Выбери дату поиска ({translator.translate(LSTEP[step], dest='ru').text}):",
                             reply_markup=calendar)

        # если пользователь хочет посмотреть историю поиска за определенный период,
        # то устанавливаем состояние search_from и отправляем первый календарь для ввода начальной даты поиска
        elif message.text == 'Выбрать период поиска':
            bot.set_state(message.from_user.id, HistoryCommandState.search_from, message.chat.id)

            calendar, step = DetailedTelegramCalendar(calendar_id=4,
                                                      max_date=date.today()).build()
            bot.send_message(message.chat.id,
                             f"Выбери начальную дату поиска ({translator.translate(LSTEP[step], dest='ru').text}):",
                             reply_markup=calendar)

        # если пользователь хочет посмотреть всю историю поиска (делаем SQL запрос к БД и выводим результат)
        elif message.text == 'Вывести всю историю поиска':

            # SQL запрос к БД по user_id
            cur.execute('SELECT `datetime`, `command`, `location`, `hotels` '
                        'FROM `history` '
                        'WHERE `user_id`=?', (message.from_user.id,))
            result = cur.fetchall()
            conn.commit()

            # вывод полученных результатов пользователю, если есть хотя бы один результат
            if len(result) > 0:
                for i_result in result:
                    text = f'*Дата поиска:* {i_result[0][:-10]}\n' \
                           f'*Что искали:* {i_result[1]}\n' \
                           f'*Где искали:* {i_result[2]}\n' \
                           f'*Результат поиска:*\n {i_result[3]}'
                    bot.send_message(message.chat.id, text, allow_sending_without_reply=True, parse_mode='Markdown')

            # если ни одного результата нет, то сообщаем об этом пользователю и просим выбрать другие даты
            else:
                bot.send_message(message.chat.id,
                                 'На эту дату нет ни одного результата поиска. '
                                 '\nПопробуй ввести другую дату или диапазон дат.',
                                 allow_sending_without_reply=True, parse_mode='Markdown')

        # иначе если пользователь ввел что-то вручную, а не нажал на одну из inline-кнопок, ожидаем выбора
        else:
            bot.send_message(message.chat.id,
                             'Я не понимаю тебя. Пожалуйста, нажми на кнопку выбора на клавиатуре.')

    except BaseException as except_name:
        # вносим информацию об ошибке в базу данных
        cur.execute('INSERT INTO logging (datetime, except_name) VALUES (?, ?)',
                    (datetime.now(), str(except_name)))
        conn.commit()

        # пишем сообщение пользователю об ошибке и обнуляем состояние
        bot.send_message(message.from_user.id,
                         'Что-то пошло не так... Пожалуйста выбери команду заново.')
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
def callback_query_search_date(call: CallbackQuery):
    """  Здесь ловим ответ с inline-клавиатуры (конкретный день в истории поиска) и выполняем SQL запрос к БД
    по параметрам user_id и выбранной дате """

    try:
        result, key, step = DetailedTelegramCalendar(calendar_id=3,
                                                     locale='ru',
                                                     max_date=date.today()).process(call.data)

        if not result and key:
            bot.edit_message_text(f"Выбери дату ({translator.translate(LSTEP[step], dest='ru').text})",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"Выбранная дата: {result.strftime('%d-%m-%Y')}",
                                  call.message.chat.id,
                                  call.message.message_id)

            date_from = result.strftime('%Y-%m-%d') + ' 00:00:00'
            date_to = result.strftime('%Y-%m-%d') + ' 23:59:59'

            # запрос к БД
            cur.execute('SELECT `datetime`, `command`, `location`, `hotels` '
                        'FROM `history` '
                        'WHERE (`datetime` BETWEEN ? AND ?) AND `user_id`=?',
                        (date_from, date_to, call.from_user.id)
                        )

            history_result = cur.fetchall()
            conn.commit()

            # если на выбранную дату есть хотя бы один результат, то выводим результат(ы)
            if len(history_result) > 0:
                for i_result in history_result:
                    text = f'*Дата поиска:* {i_result[0][:-10]}\n' \
                           f'*Что искали:* {i_result[1]}\n' \
                           f'*Где искали:* {i_result[2]}\n' \
                           f'*Результат поиска:*\n {i_result[3]}'
                    bot.send_message(call.message.chat.id, text, allow_sending_without_reply=True, parse_mode='Markdown')

            # иначе отправляем сообщение, что ничего не найдено и просим выбрать другой день
            else:
                bot.send_message(call.message.chat.id,
                                 'На эту дату нет ни одного результата поиска. '
                                 '\nПопробуй ввести другую дату или диапазон дат.',
                                 allow_sending_without_reply=True, parse_mode='Markdown')

    except BaseException as except_name:
        # вносим информацию об ошибке в базу данных
        cur.execute('INSERT INTO logging (datetime, except_name) VALUES (?, ?)',
                    (datetime.now(), str(except_name)))
        conn.commit()

        # пишем сообщение пользователю об ошибке и обнуляем состояние
        bot.send_message(call.message.chat.id,
                         'Что-то пошло не так... Пожалуйста выбери команду заново.')
        bot.delete_state(call.message.from_user.id, call.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
def callback_query_date_from(call: CallbackQuery):
    """  Здесь ловим ответ с inline-клавиатуры (начальный день периода истории поиска), устанавливаем
    состояние search_to и отправляем еще один календарь для выбора конечной даты периода поиска """

    try:
        result, key, step = DetailedTelegramCalendar(calendar_id=4,
                                                     locale='ru',
                                                     max_date=date.today()).process(call.data)

        if not result and key:
            bot.edit_message_text(f"Выбери начальную дату поиска ({translator.translate(LSTEP[step], dest='ru').text})",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"Выбранная начальная дата: {result.strftime('%d-%m-%Y')}",
                                  call.message.chat.id,
                                  call.message.message_id)

            # заносим начальный день периода поиска в MemoryStorage
            with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                data['date_from'] = result.strftime('%Y-%m-%d') + ' 00:00:00'

            bot.set_state(call.from_user.id, HistoryCommandState.search_to, call.message.chat.id)

            calendar, step = DetailedTelegramCalendar(calendar_id=5,
                                                      max_date=date.today()).build()
            bot.send_message(call.message.chat.id,
                             f"Выбери конечную дату поиска ({translator.translate(LSTEP[step], dest='ru').text}):",
                             reply_markup=calendar)

    except BaseException as except_name:
        # вносим информацию об ошибке в базу данных
        cur.execute('INSERT INTO logging (datetime, except_name) VALUES (?, ?)',
                    (datetime.now(), str(except_name)))
        conn.commit()

        # пишем сообщение пользователю об ошибке и обнуляем состояние
        bot.send_message(call.message.chat.id,
                         'Что-то пошло не так... Пожалуйста выбери команду заново.')
        bot.delete_state(call.message.from_user.id, call.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
def callback_query_search_date(call: CallbackQuery):
    """  Здесь ловим ответ с inline-клавиатуры (конечный день периода истории поиска) и выполняем SQL запрос к БД
    по параметрам user_id и периоду дат поиска """

    try:
        result, key, step = DetailedTelegramCalendar(calendar_id=5,
                                                     locale='ru',
                                                     max_date=date.today()).process(call.data)

        if not result and key:
            bot.edit_message_text(f"Выбери конечную дату поиска ({translator.translate(LSTEP[step], dest='ru').text})",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"Выбранная конечная дата: {result.strftime('%d-%m-%Y')}",
                                  call.message.chat.id,
                                  call.message.message_id)

            date_to = result.strftime('%Y-%m-%d') + ' 23:59:59'
            # заносим конечный день периода поиска в MemoryStorage и "достаем" начальный день периода поиска
            with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                data['date_to'] = date_to
                date_from = data['date_from']

            # запрос к БД
            cur.execute('SELECT `datetime`, `command`, `location`, `hotels` '
                        'FROM `history` '
                        'WHERE (`datetime` BETWEEN ? AND ?) AND `user_id`=?',
                        (date_from, date_to, call.from_user.id)
                        )

            history_result = cur.fetchall()
            conn.commit()

            # если на выбранную дату есть хотя бы один результат, то выводим результат(ы)
            if len(history_result) > 0:
                for i_result in history_result:
                    text = f'*Дата поиска:* {i_result[0][:-10]}\n' \
                           f'*Что искали:* {i_result[1]}\n' \
                           f'*Где искали:* {i_result[2]}\n' \
                           f'*Результат поиска:*\n {i_result[3]}'
                    bot.send_message(call.message.chat.id, text, allow_sending_without_reply=True, parse_mode='Markdown')

            # иначе отправляем сообщение, что ничего не найдено и просим выбрать другой день/период
            else:
                with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                    bot.send_message(call.message.chat.id,
                                     f'На даты с {data["date_from"][:-9]} по {data["date_to"][:-9]} '
                                     f'нет ни одного результата поиска.'
                                     '\nПопробуй ввести другой диапазон дат.',
                                     allow_sending_without_reply=True, parse_mode='Markdown')

    except BaseException as except_name:
        # вносим информацию об ошибке в базу данных
        cur.execute('INSERT INTO logging (datetime, except_name) VALUES (?, ?)',
                    (datetime.now(), str(except_name)))
        conn.commit()

        # пишем сообщение пользователю об ошибке и обнуляем состояние
        bot.send_message(call.message.chat.id,
                         'Что-то пошло не так... Пожалуйста выбери команду заново.')
        bot.delete_state(call.message.from_user.id, call.message.chat.id)
