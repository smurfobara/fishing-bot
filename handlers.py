from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
from config import admin
import sqlite3
import re 
from datetime import *

#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from chromedriver_py import binary_path
#from selenium.webdriver.common.by import By
#path_ = webdriver.ChromeService(executable_path=binary_path)
#options = Options()
#options.add_argument("--headless=new")
import requests
from bs4 import BeautifulSoup

db = sqlite3.connect('base.db')
c = db.cursor()

data = None
import keyboards as kb

c.execute("""CREATE TABLE IF NOT EXISTS baseusers(
          name text,
          surname text,
          username text,
          user_id integer,
          user_accept integer,
          is_admin integer
)""")



router = Router()


class accepting(StatesGroup):
    acceptNofs = State()

class menuStates(StatesGroup):
     waiting = State()
     disablingNofs = State()
     messageToS = State()
     toSite = State()

class messageToUsers(StatesGroup):
    getMessage = State()

class makingNewAdmin(StatesGroup):
    getUsername = State()
    approving = State()

class sendingMessageToAdmins(StatesGroup):
    getMessage = State()

@router.message(Command('start'))
async def startCmd(message: Message, state: FSMContext):
    c.execute('SELECT user_id FROM baseusers')
    userIDs = c.fetchall()
    if str(message.from_user.id) in str(userIDs):
        await message.reply('Здравствуйте, это меню бота портала our.fishing. Используйте кнопки ниже, если требуется что-то сделать.', reply_markup=kb.menuKb)
        await state.set_state(menuStates.waiting)
    else:
        c.execute(f'INSERT INTO baseusers (name, surname, username, user_id, user_accept, is_admin) VALUES ("{message.from_user.first_name}", "{message.from_user.last_name}", "{message.from_user.username}", {message.from_user.id}, 0, 0)')
        db.commit()
        await message.answer('Привет! Это бот сайта our.fishing\nЗдесь вы можете получать уведомления о новых статьях. Вы хотите получать их?', reply_markup=kb.acceptKeyboard)
        await state.set_state(accepting.acceptNofs)
    #if int(message.from_user.id) == int(admin):
     #   c.execute(f'UPDATE baseusers SET is_admin = ? WHERE user_id = {message.from_user.id}', ('1'))
      #  await message.answer('Теперь вы админ!')

@router.message(menuStates.waiting, F.text == 'Выключить/Выключить уведомления')
async def changeOffOn(message: Message, state: FSMContext):
    try:
        if int(c.execute(f'SELECT user_accept FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
            c.execute(f'UPDATE baseusers SET user_accept = ? WHERE user_id = {message.from_user.id}', ('0'))
            db.commit()
            await message.answer('Успешно! Теперь Вам <b>не будут</b> приходить уведомления о новых статьях. Если нужно вернуться в меню, введите /start', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove(), parse_mode='HTML')
            await state.clear()
        elif int(c.execute(f'SELECT user_accept FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 0:
            c.execute(f'UPDATE baseusers SET user_accept = ? WHERE user_id = {message.from_user.id}', ('1'))
            db.commit()
            await message.answer('Успешно! Теперь Вам <b>будут</b> приходить уведомления о новых статьях. Если нужно вернуться в меню, введите /start', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove(), parse_mode='HTML')
            await state.clear()

    except Exception as ex:
        await message.answer(f'Ой! Возникла ошибка. Скопируйте текст снизу и сообщите в поддержку, пожалуйста\n\n{str(ex)}')
@router.message(menuStates.waiting, F.text == 'Написать в поддержку')
async def messageToAdmins(message: Message, state: FSMContext):
    await message.answer('Напишите свое сообщение для команды our.fishing. Если требуется, укажите контакты для обратной связи - электронную почту или телеграм.', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
    await state.set_state(sendingMessageToAdmins.getMessage)

@router.message(sendingMessageToAdmins.getMessage, F.text)
async def sendMessageToAdmins(message: Message, state: FSMContext):
    IDs = c.execute('SELECT user_id FROM baseusers WHERE is_admin = 1').fetchall()
    print(IDs)
    for user in IDs:
        await message.bot.send_message(int(user[0]),f'Новое сообщение в поддержку: {message.text}')
    await message.answer('Ваше сообщение уже передано ответственным, спасибо!')
    await state.clear()

@router.message(menuStates.waiting, F.text == 'Перейти на сайт')
async def goToSite(message: Message):
    await message.answer('Чтобы перейти на наш рыболовный портал нажмите кнопку ниже', reply_markup=kb.toSiteKb)

@router.message(accepting.acceptNofs, F.text == 'Да')
async def answerYes(message: Message, state: FSMContext):
    c.execute(f'UPDATE baseusers SET user_accept = ? WHERE user_id = {message.from_user.id}', ('1'))
    db.commit()
    await state.clear()
    await message.answer('Успешно! Теперь вам будут приходить уведомления о новых статьях.', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())

@router.message(Command('showbase', prefix='$'))
async def showbaseCmd(message: Message):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
        await message.answer(str(c.execute('SELECT * FROM baseusers').fetchall()))

last_article = ''

new_article = ''



@router.message(Command('sendmessage', prefix='$'))
async def getmessageforusers(message: Message, state: FSMContext):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
        await message.answer('Напишите ваше сообщение для пользователей, если нужно отменить операцию, введите 0\nМожно использовать теги HTML')
        await state.set_state(messageToUsers.getMessage)



@router.message(messageToUsers.getMessage, F.text)
async def sendingtousers(message: Message, state: FSMContext):
    numus = 0
    try:
        if message.text != '0':
            await message.answer('Сообщение распознано, начинаю рассылку.')
            textForUsers = message.text
            IDs = c.execute('SELECT user_id FROM baseusers').fetchall()
            for user in IDs:
                await message.bot.send_message(int(user[0]), f'{textForUsers}', parse_mode='HTML')
                numus = numus + 1
            await message.answer(f'Рассылка завершена, сообщение отправлено {numus} юзерам.')
            await state.clear()
        elif message.text == '0':
            await message.answer('Операция отменена!')
            await state.clear()
    except Exception as ex:
            await message.answer(f'ERROR!\n\n{ex}')
            print(ex)
            await state.clear()
code = ''
try:
    url = 'https://our.fishing/blog/'
    response = requests.get(url)
    # Проверяем, что запрос успешен (статус-код 200)
    print(response.status_code)
    if response.status_code == 200:
        code = response.text
    else:
        print(f"Ошибка: статус-код {response.status_code}")
        print(f"Ошибка запроса: {e}")
    soup = BeautifulSoup(response.content, 'html.parser')
    last_article = soup.find('div', class_='card-block-info').find('h5').text.strip()
except Exception as ex:
    print(ex)
@router.message(Command('update', prefix='$'))
async def updating(message: Message):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
        global last_article
        global new_article
        code = ''
        autor = ''
        link = ''
        new_article_el = None
        try:
            response = requests.get(url)
            # Проверяем, что запрос успешен (статус-код 200)
            if response.status_code == 200:
                print('starting check')
                code = response.text
                soup = BeautifulSoup(response.content, 'html.parser')
                new_article = soup.find('div', class_='card-block-info').find('h5').text
                new_article_el = soup.find('div', class_='card-block-info').find('h5')
                if new_article != last_article:
                    print(f"New article detected: {new_article}")
                    autor = soup.find('div', class_='info-right-img').find('span', class_='font-sm font-bold color-brand-1 op-70').text.strip()
                    link = new_article_el.find('a').get('href')
                    last_article = new_article
                    IDs = c.execute('SELECT user_id FROM baseusers WHERE user_accept = 1').fetchall()
                    autor = ' '.join(autor.split())
                    print(IDs)
                    for user in IDs:
                        await message.bot.send_message(int(user[0]),f'Новая статья "{new_article}" от {autor}!\nПерейти к статье: https://our.fishing/blog/{link}')
                    await message.answer('Сообщение разослано!')
                else:
                    print("No new article detected.")
            else:
                print(f"Ошибка: статус-код {response.status_code}")

        except Exception as ex:
            print(ex)

@router.channel_post()
async def updatingSched(message: Message):
    global last_article
    global new_article
    code = ''
    autor = ''
    link = ''
    new_article_el = None
    try:
        response = requests.get(url)
        # Проверяем, что запрос успешен (статус-код 200)
        if response.status_code == 200:
            print('starting check')
            code = response.text
            soup = BeautifulSoup(response.content, 'html.parser')
            new_article = soup.find('div', class_='card-block-info').find('h5').text
            new_article_el = soup.find('div', class_='card-block-info').find('h5')
            if new_article != last_article:
                print(f"New article detected: {new_article}")
                autor = soup.find('div', class_='info-right-img').find('span',
                                                                       class_='font-sm font-bold color-brand-1 op-70').text.strip()
                link = new_article_el.find('a').get('href')
                last_article = new_article
                IDs = c.execute('SELECT user_id FROM baseusers WHERE user_accept = 1').fetchall()
                autor = ' '.join(autor.split())
                print(IDs)
                for user in IDs:
                    await message.bot.send_message(int(user[0]),
                                                   f'Новая статья "{new_article}" от {autor}!\nПерейти к статье: https://our.fishing/blog/{link}')
            else:
                print("No new article detected.")
        else:
            print(f"Ошибка: статус-код {response.status_code}")

    except Exception as ex:
        print(ex)


id_of_new_adm = 0
@router.message(Command('makeadmin', prefix='$'))
async def set_new_admin(message: Message, state: FSMContext):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
        await message.answer('Введите юзернэйм аккаунта, которого нужно сделать/убрать админом БЕЗ СОБАЧКИ!!!\nАккаунт должен был когда-либо прописать /start в боте.')
        await state.set_state(makingNewAdmin.getUsername)
@router.message(makingNewAdmin.getUsername, F.text)
async def set_new_admin_main(message: Message, state: FSMContext):
    global id_of_new_adm
    action = ''
    username = ''
    username = message.text
    if '@' in username:
        await message.answer('В юзернейме не должно быть собачки!! Начните заново')
        await state.clear()
    else:
        name_and_surname_of_new_adm = c.execute(f'SELECT name FROM baseusers WHERE username = ?', (username,)).fetchone()[0]
        name_and_surname_of_new_adm = name_and_surname_of_new_adm + ' '
        name_and_surname_of_new_adm = name_and_surname_of_new_adm + c.execute(f'SELECT surname FROM baseusers WHERE username = ?', (username,)).fetchone()[0]
        id_of_new_adm = c.execute(f'SELECT user_id FROM baseusers WHERE username = ?', (username,)).fetchone()[0]
        if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {int(id_of_new_adm)}').fetchone()[0]) == 0:
            action = 'дать'
        else:
            action = 'убрать'

        await message.answer(f'Вы уверены, что хотите {action} права админа {str(name_and_surname_of_new_adm)}, с id аккаунта {str(id_of_new_adm)}', reply_markup=kb.acceptKeyboard)
        await state.set_state(makingNewAdmin.approving)

@router.message(makingNewAdmin.approving, F.text == 'Да')
async def making_new_admin_final(message: Message, state: FSMContext):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {int(id_of_new_adm)}').fetchone()[0]) == 0:
        c.execute(f'UPDATE baseusers SET is_admin = ? WHERE user_id = {int(id_of_new_adm)}', ('1'))
        db.commit()
        await message.answer('Админ поставлен!', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        await message.bot.send_message(int(id_of_new_adm), 'Теперь Вы админ этого бота! Ниже список команд, доступных только админам\n\n$update(не рекомендуется использовать, обновления происходят автоматически - проверяет наличие новых статей, и при их наличии отправляет уведомления всем юзерам, которые их разрешили.\n$showbase - выводит базу данных в строке.\n$sendmessage - Отправка сообщения всем юзерам\n$makeadmin - Добавить/убрать админа.')
        await state.clear()

    elif int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {int(id_of_new_adm)}').fetchone()[0]) == 1:
        c.execute(f'UPDATE baseusers SET is_admin = ? WHERE user_id = {int(id_of_new_adm)}', ('0'))
        db.commit()
        await message.answer('Админ снят!', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        await message.bot.send_message(int(id_of_new_adm), 'Вы больше не админ!')
        await state.clear()

@router.message(makingNewAdmin.approving, F.text == 'Нет')
async def cancel_admin(message: Message, state: FSMContext):
    await message.answer('Отменяю')
    await state.clear()

#@router.message()
#async def catch_all(message: Message):
 #   await message.reply("Я вас не понял, давайте начнем заново? Нажмите здесь /start")


