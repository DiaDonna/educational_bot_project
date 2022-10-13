from loader import bot
import schedule
import time


def notification(chat_id):
    """ Функция для отправки сообщения-напоминания пользователю """

    bot.send_message(chat_id, 'Самое время подобрать идеальный отель для отдыха!', allow_sending_without_reply=True)


def sending_notification(chat_id):
    """ Функция для установки расписания напоминаний """

    schedule.every().day.at("12:00").do(notification, chat_id)
    while True:
        schedule.run_pending()
        time.sleep(1)
