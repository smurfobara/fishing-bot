import telebot
bot = telebot.TeleBot('7107331036:AAF0-AgnOPA5_UTEprnfQ3YznRFau15sLdE')

import sched

import time
# Создаем объект планировщика
scheduler = sched.scheduler(time.time, time.sleep)


def updateArts():
    bot.send_message(-1002192441889, 'update')
    print('articles')
    # Планируем повторное выполнение через минуту
    scheduler.enter(60, 1, updateArts)

def updateAutors():
    bot.send_message(-1002192441889, 'autorsUpdate')
    print('autors')
    # Планируем повторное выполнение через час
    scheduler.enter(3600, 1, updateAutors)

# Запускаем начальные задачи
scheduler.enter(0, 1, updateArts)
scheduler.enter(0, 1, updateAutors)

# Запускаем планировщик
scheduler.run()