import telebot
bot = telebot.TeleBot('7107331036:AAF0-AgnOPA5_UTEprnfQ3YznRFau15sLdE')

import sched

import time
# Создаем объект планировщика
scheduler = sched.scheduler(time.time, time.sleep)



def print_message():
    print('working')
    bot.send_message(-1002192441889, 'update')
    # Планируем следующее выполнение через 1 минуту
    scheduler.enter(60, 1, print_message)
# Планируем первое выполнение через 2 минуты
scheduler.enter(1, 1, print_message)

def print_message():
    print('working autors')
    bot.send_message(-1002192441889, 'autorsUpdate')
    # Планируем следующее выполнение через 1 минуту
    scheduler.enter(3600, 1, print_message)
# Планируем первое выполнение через 2 минуты
scheduler.enter(3600, 1, print_message)

# Запускаем планировщик
scheduler.run()

#test
bot.infinity_polling()