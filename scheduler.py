import telebot
bot = telebot.TeleBot('7107331036:AAF0-AgnOPA5_UTEprnfQ3YznRFau15sLdE')

import sched

import time
# Создаем объект планировщика
scheduler = sched.scheduler(time.time, time.sleep)


def updateArts():
    bot.send_message(-1002192441889, 'update')
    # Планируем повторное выполнение через минуту
    scheduler.enter(60, 1, action1)

def updateAutors():
    bot.send_message(-1002192441889, 'autorsUpdate')
    # Планируем повторное выполнение через час
    scheduler.enter(3600, 1, action2)

# Запускаем начальные задачи
scheduler.enter(0, 1, action1)
scheduler.enter(0, 1, action2)

# Запускаем планировщик
scheduler.run()