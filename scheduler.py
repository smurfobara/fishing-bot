import telebot
bot = telebot.TeleBot('7107331036:AAF0-AgnOPA5_UTEprnfQ3YznRFau15sLdE')

import sched

import time
# Создаем объект планировщика
scheduler = sched.scheduler(time.time, time.sleep)



def print_message():
    pass
    bot.send_message(-1002192441889, 'new update')
    # Планируем следующее выполнение через 2 минуты
    scheduler.enter(120, 1, print_message)
# Планируем первое выполнение через 2 минуты
scheduler.enter(1, 1, print_message)

# Запускаем планировщик
scheduler.run()


bot.infinity_polling()