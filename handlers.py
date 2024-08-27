import aiogram.exceptions
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
import sqlite3
import re 
from datetime import datetime


import requests
from bs4 import BeautifulSoup


from itertools import product

import re

from words  import BAD_WORDS

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

c.execute("""CREATE TABLE IF NOT EXISTS subscriptions(
          profile1 text,
          link1 text,
          profile2 text,
          link2 text,
          profile3 text,
          link3 text,
          user_id integer
)""")



router = Router()



cleaned_autors = []
cleaned_links = []

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

class subscribeFisherman(StatesGroup):
    getMessage = State()
    choosing = State()
    menu = State()
    menu2 = State()



@router.message(Command('start'))
async def startCmd(message: Message, state: FSMContext):
    if message.chat.type == 'private':
        status = await message.bot.get_chat_member(chat_id=-1002246594000, user_id=message.from_user.id)
        if str(status.status) == 'ChatMemberStatus.MEMBER' or 'ChatMemberStatus.CREATOR' or 'ChatMemberStatus.ADMINISTRATOR':
            c.execute('SELECT user_id FROM baseusers')
            userIDs = c.fetchall()
            if str(message.from_user.id) not in str(userIDs):
                c.execute(f'INSERT INTO baseusers (name, surname, username, user_id, user_accept, is_admin) VALUES ("{message.from_user.first_name}", "{message.from_user.last_name}", "{message.from_user.username}", {message.from_user.id}, 0, 0)')
            if str(message.from_user.id) not in str(c.execute('SELECT user_id FROM subscriptions').fetchall()):
                c.execute(f'INSERT INTO subscriptions (profile1, link1, profile2, link2, profile3, link3, user_id) VALUES ("0", "0", "0", "0", "0", "0", {message.chat.id})')
                #c.execute(f'INSERT INTO userMessage (msgText, msgId, user_id) VALUES ("0", 0, {message.chat.id})')
                db.commit()

            await message.reply('Здравствуйте, это меню бота портала our.fishing. Используйте кнопки ниже, если требуется что-то сделать.', reply_markup=kb.menuKb)
            await state.set_state(menuStates.waiting)

        else:
            await message.answer('Чтобы использовать бот нужно подписаться на <a href="https://t.me/our_fishing_official">официальный канал Our.fishing</a>\nЕсли вы подписались, нажмите здесь --> /start', parse_mode='HTML')


    else:
        await message.reply('С ботом можно разговаривать только в личных сообщениях🚫')



@router.message(menuStates.waiting, F.text == 'Написать в поддержку')
async def messageToAdmins(message: Message, state: FSMContext):
    await message.answer('Напишите свое сообщение, или отправьте фото(подпись к фото тоже будет передана) для команды our.fishing. Если требуется, укажите контакты для обратной связи - электронную почту или телеграм.', reply_markup=kb.cancel)
    await state.set_state(sendingMessageToAdmins.getMessage)

@router.message(menuStates.waiting, F.text == 'Подписаться на рыбака')
async def fisherRedic(message: Message, state: FSMContext):
    await message.reply('Нажмите здесь --> /subs чтобы открыть меню подписок', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
    await state.clear()

profiles = []

@router.message(Command('subs'))
async def subscribeToFisherman(message: Message, state: FSMContext):
    global profiles
    for i in range(3):
        print(i)
        if str(c.execute(f'SELECT profile{i + 1} FROM subscriptions WHERE user_id = {message.from_user.id}').fetchone()[0]) != '0':
            profiles.append(f'Слот {str(i + 1)} {str(c.execute(f"SELECT profile{i + 1} FROM subscriptions WHERE user_id = {message.from_user.id}").fetchone()[0])}')
        else:
            profiles.append(f'Слот {i + 1} Пусто')
    await message.answer('Меню ваших подписок. Выберите слот ниже', reply_markup=await kb.kbBuild(list=profiles))
    await state.set_state(subscribeFisherman.menu)

changesProfile = ''

@router.message(subscribeFisherman.menu, F.text)
async def menuFishs(message: Message, state: FSMContext):
    if message.text != 'Отменить':
        global profiles
        global changesProfile
        for profile in profiles:
            if message.text == profile:
                await message.answer(f'Выберите действие со слотом {profile}', reply_markup=kb.changes)
                changesProfile = profile
                await state.set_state(subscribeFisherman.menu2)
                profiles = []
                break
    else:
        await message.answer('Отменяю', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()

id_ = 0
@router.message(subscribeFisherman.menu2, F.text)
async def menuFishs2(message: Message, state: FSMContext):
    global id_
    id_ = 0
    if 'Слот 1' in changesProfile:
        id_ = 1
    elif 'Слот 2' in changesProfile:
        id_ = 2
    elif 'Слот 3' in changesProfile:
        id_ = 3
    else:
        await message.answer('Что-то пошло не так, начните сначала')

    if message.text == 'Добавить/изменить автора':
        await message.answer('Начните вводить имя автора, или нажмите кнопку Отменить, если нужно.', reply_markup=kb.cancel)
        await state.set_state(subscribeFisherman.getMessage)
    elif message.text == 'Удалить автора':
        c.execute(f'UPDATE subscriptions SET profile{str(id_)} = ? WHERE user_id = {message.from_user.id}', ('0',))
        c.execute(f'UPDATE subscriptions SET link{str(id_)} = ? WHERE user_id = {message.from_user.id}', ('0',))
        db.commit()
        await message.answer('Готово!', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()
@router.message(subscribeFisherman.getMessage, F.text)
async def getTextSub(message: Message, state: FSMContext):
    mbAutors = []
    if message.text != 'Отменить':
        if len(message.text) >= 4:
            for autor in cleaned_autors:
                if message.text.lower().strip() in autor.lower().strip():
                    print(autor)
                    mbAutors.append(autor)
            await message.answer('Выберите нужного автора из списка ниже.', reply_markup= await kb.kbBuild(mbAutors))
            await state.set_state(subscribeFisherman.choosing)

        else:
            await message.answer('Введите как минимум 4 символа!')

    else:
        await message.answer('Отменяю', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()

@router.message(subscribeFisherman.choosing, F.text)
async def choosingFisher(message: Message, state: FSMContext):
    try:
        if message.text != 'Отменить':
            isFinded = False
            iterat = 0
            for autor in cleaned_autors:
                if message.text == autor:
                    c.execute(f'UPDATE subscriptions SET profile{str(id_)} = ? WHERE user_id = {message.from_user.id}', (autor,))
                    c.execute(f'UPDATE subscriptions SET link{str(id_)} = ? WHERE user_id = {message.from_user.id}', (cleaned_links[iterat],))
                    db.commit()
                    await message.answer('Готово!', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
                    await state.clear()
                    isFinded = True
                iterat = iterat + 1
            if isFinded == False:
                await message.answer('К сожалению не удалось ничего найти :( Попробуйте другой запрос')
                iterat = iterat + 1
        else:
            await message.answer('Отменяю', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
            await state.clear()
    except Exception as ex:
        await message.answer(f'Ошибка! Пожалуйста, скопируйте текст ниже и передайте в поддержку\n\n{ex}', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        await state.clear()


@router.message(sendingMessageToAdmins.getMessage, F.text)
async def sendMessageToAdmins(message: Message, state: FSMContext):
   if message.text != 'Отменить':
        IDs = c.execute('SELECT user_id FROM baseusers WHERE is_admin = 1').fetchall()
        print(IDs)
        userID = 0
        userUsname = ''
        userName = ''
        userID = message.chat.id
        userUsname = message.from_user.username
        userName = message.from_user.first_name
        for user in IDs:
            await message.bot.send_message(int(user[0]),f'Новое сообщение в поддержку: {message.text}', reply_markup=kb.getOrNo)
        # #c.execute(f'UPDATE userMessage SET msgText = ? WHERE user_id = {message.chat.id}', (f'{message.text}'))
        # db.commit()
        await message.answer('Ваше сообщение уже передано ответственным, спасибо!')
        await state.clear()
   else:
       await message.answer('Отменяю операцию, Вы можете перейти в главное меню по команде /start', reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
       await state.clear()



@router.message(sendingMessageToAdmins.getMessage, F.photo)
async def sendPhotoToadmins(message: Message, state: FSMContext):
    photo_ID = message.photo[-1].file_idё
    photoCaption = message.caption
    IDs = c.execute('SELECT user_id FROM baseusers WHERE is_admin = 1').fetchall()
    print(IDs)
    for user in IDs:
        await message.bot.send_photo(int(user[0]),photo=photo_ID, caption=f'Новое сообщение в поддержку:{photoCaption}', parse_mode='HTML')
    await message.answer('Ваше фото уже передано ответственным, спасибо!')
    await state.clear()


@router.message(menuStates.waiting, F.text == 'Перейти на сайт')
async def goToSite(message: Message):
    await message.answer('Чтобы перейти на наш рыболовный портал нажмите кнопку ниже', reply_markup=kb.toSiteKb)


@router.message(Command('showbase', prefix='$'))
async def showbaseCmd(message: Message):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
        await message.answer(str(c.execute('SELECT * FROM baseusers').fetchall()))
        await message.answer(str(c.execute('SELECT * FROM subscriptions').fetchall()))

last_article = ''
new_article = ''

last_articles_sub = []
last_autors_sub = []

new_articles_sub = []
new_autors_sub = []



@router.message(Command('sendmessage', prefix='$'))
async def getmessageforusers(message: Message, state: FSMContext):
    if int(c.execute(f'SELECT is_admin FROM baseusers WHERE user_id = {message.from_user.id}').fetchone()[0]) == 1:
        await message.answer('Напишите ваше сообщение или фото(с подписью) для пользователей, если нужно отменить операцию, введите 0\nМожно использовать теги HTML')
        await state.set_state(messageToUsers.getMessage)



@router.message(messageToUsers.getMessage, F.text)
async def sendingtousers(message: Message, state: FSMContext):
    try:
        numus = 0
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
    except aiogram.exceptions.TelegramBadRequest as ex:
        pass

@router.message(messageToUsers.getMessage, F.photo)
async def sendingtousersPhoto(message: Message, state: FSMContext):
    try:
        numus = 0
        if message.caption != '0':
            await message.answer('Фото распознано, начинаю рассылку.')
            photoID = message.photo[-1].file_id
            textForUsers = message.caption
            IDs = c.execute('SELECT user_id FROM baseusers').fetchall()
            for user in IDs:
                await message.bot.send_photo(int(user[0]), photo=photoID, caption=textForUsers, parse_mode='HTML')
                numus = numus + 1
            await message.answer(f'Рассылка завершена, сообщение отправлено {numus} юзерам.')
            await state.clear()
        elif message.text == '0':
            await message.answer('Операция отменена!')
            await state.clear()
    except aiogram.exceptions.TelegramBadRequest as ex:
        pass



    response = requests.get('https://our.fishing/blog/')
    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        last_article = soup.find('div', class_='card-block-info').find('h5').text.strip()
        linksProfiles = []
        namesProfiles = []
        for i in range(3):
            linksProfiles.append(c.execute(f'SELECT link{str(i + 1)} FROM subscriptions').fetchall()[0][0])
        for profile in linksProfiles:
            response = requests.get(profile)
            if response.status_code == 200:
                print(f'Парс ссылки {profile}, 200')
                soup = BeautifulSoup(response.content, 'html.parser')
                autor = soup.find('h2', class_ = 'mob-center').text
                autor = ' '.join(autor.split())
                autor = autor.split()
                autor = ' '.join(autor[:2])
                article = soup.find('div', class_ = 'card-block-info').find('a').text.strip()
                last_autors_sub.append(autor)
                last_articles_sub.append(article)

        print(last_articles_sub)



    else:
        print(f"Ошибка: статус-код {response.status_code}")
        print(f"Ошибка запроса: {e}")




response = requests.get('https://our.fishing/blog/')
    # Проверяем, что запрос успешен (статус-код 200)
print(response.status_code)
if response.status_code == 200:
    code = response.text
else:
    print(f"Ошибка: статус-код {response.status_code}")
    print(f"Ошибка запроса: {e}")
soup = BeautifulSoup(response.content, 'html.parser')
last_article = soup.find('div', class_='card-block-info').find('h5').text.strip()

it = 1
autors = []
links = []
link = ''
    # Получаем первую страницу для инициализации
response = requests.get(f'https://our.fishing/fishermans/?page={it}')
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    numbers = soup.find_all('a', class_='pager-number')
    pages = [int(number.text.strip()) for number in numbers]

    for page in pages:
        print(f'Парсинг страницы {page}')
        response = requests.get(f'https://our.fishing/fishermans/?page={page}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            autorsPage = soup.find_all('div', class_='card-profile pt-10')

            for autorPage in autorsPage:
                autor = autorPage.find('h5').text.strip()
                autors.append(autor)
                link = autorPage.find('a').get('href')
                full_link = f'https://our.fishing{link}'
                links.append(full_link)

    cleaned_autors = [' '.join(item.split()).strip() for item in autors]
    cleaned_links = [' '.join(item.split()).strip() for item in links]
    print(cleaned_autors)
    print(cleaned_links)





code = ''


@router.channel_post(F.text == 'update')
async def updatingSched(message: Message):
    isNight = False
    current_time = datetime.now().time()
    start_time = datetime.strptime("00:00", "%H:%M").time()
    end_time = datetime.strptime("07:00", "%H:%M").time()
    if start_time <= current_time < end_time:
        isNight = True
    else:
        isNight = False
    linksProfiles = []
    global last_article
    global new_article
    code = ''
    autor = ''
    link = ''
    new_article_el = None
    try:
        response = requests.get('https://our.fishing/blog/')
        # Проверяем, что запрос успешен (статус-код 200)
    except Exception as ex:
        print(ex)

    if response.status_code == 200:
        iter_ = 0
        print('starting check')
        code = response.text
        soup = BeautifulSoup(response.content, 'html.parser')
        new_article = soup.find('div', class_='card-block-info').find('h5').text
        new_article_el = soup.find('div', class_='card-block-info').find('h5')
        if new_article != last_article:
            print(f"New article detected: {new_article}")
            autor = soup.find('div', class_='info-right-img').find('span', class_='font-sm font-bold color-brand-1 op-70').text.strip()
            autorObj = soup.find('div', class_='info-right-img').find('span', class_='font-sm font-bold color-brand-1 op-70')
            link = new_article_el.find('a').get('href')
            response = requests.get(f'https://our.fishing/blog/{link}')
            soup = BeautifulSoup(response.content, 'html.parser')
            autorLink = soup.find('div', class_='author d-flex align-items-center mr-30').find('a').get('href')
            autorLink = f'https://our.fishing{autorLink}'
            print(autorLink)
            autor = ' '.join(autor.split())
            IDs = c.execute(f'SELECT user_id FROM subscriptions WHERE link1 = "{autorLink}" OR link2 = "{autorLink}" OR link3 = "{autorLink}"').fetchall()
            if IDs:
                print('subscribes detected, starting send...')
                for user in IDs:
                    await message.bot.send_message(user[0], f'Вышла новая <a href="{autorLink}">статья</a> {new_article} у {autor}!', parse_mode='HTML')
                print('fine')
            last_article = new_article

            await message.bot.send_message(-1002246594000,f'Вышла новая статья "{new_article}"\n от {autor}!\nЧитать: https://our.fishing/blog/{link}', disable_notification=isNight)
        else:
            print("No new article detected.")

    else:
        print(f"Ошибка: статус-код {response.status_code}")









@router.channel_post(F.text == 'autorsUpdate')
async def updateAutors(message: Message):
    it = 1
    autors = []
    global cleaned_autors
    global cleaned_links
    links = []
    link = ''
    # Получаем первую страницу для инициализации
    response = requests.get(f'https://our.fishing/fishermans/?page={it}')
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        numbers = soup.find_all('a', class_='pager-number')
        pages = [int(number.text.strip()) for number in numbers]

        for page in pages:
            print(f'Парсинг страницы {page}')
            response = requests.get(f'https://our.fishing/fishermans/?page={page}')
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                autorsPage = soup.find_all('div', class_='card-profile pt-10')

                for autorPage in autorsPage:
                    autor = autorPage.find('h5').text.strip()
                    autors.append(autor)
                    link = autorPage.find('a').get('href')
                    full_link = f'https://our.fishing{link}'
                    links.append(full_link)

        cleaned_autors = [' '.join(item.split()).strip() for item in autors]
        cleaned_links = [' '.join(item.split()).strip() for item in links]
        print(cleaned_autors)
        print(cleaned_links)


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


@router.message(Command('getId', prefix='$'))
async def getChatId(message: Message):
    await message.answer(str(message.chat.id))

@router.message(F.text)
async def check(message: Message):
    try:
        translated_text = ''
        char_map = {'а': ['а', 'a', '@'],
             'б': ['б', '6', 'b'],
             'в': ['в', 'b', 'v'],
             'г': ['г', 'r', 'g'],
             'д': ['д', 'd', 'g'],
             'е': ['е', 'e'],
             'ё': ['ё', 'e'],
             'ж': ['ж', 'zh', '*'],
             'з': ['з', '3', 'z'],
             'и': ['и', 'u', 'i'],
             'й': ['й', 'u', 'i'],
             'к': ['к', 'k', 'i{', '|{'],
             'л': ['л', 'l', 'ji'],
             'м': ['м', 'm'],
             'н': ['н', 'h', 'n'],
             'о': ['о', 'o', '0'],
             'п': ['п', 'n', 'p'],
             'р': ['р', 'r', 'p'],
             'с': ['с', 'c', 's'],
             'т': ['т', 'm', 't'],
             'у': ['у', 'y', 'u'],
             'ф': ['ф', 'f'],
             'х': ['х', 'x', 'h', '}{'],
             'ц': ['ц', 'c', 'u,'],
             'ч': ['ч', 'ch'],
             'ш': ['ш', 'sh'],
             'щ': ['щ', 'sch'],
             'ь': ['ь', 'b'],
             'ы': ['ы', 'bi'],
             'ъ': ['ъ'],
             'э': ['э', 'e'],
             'ю': ['ю', 'io'],
             'я': ['я', 'ya']
             }

        if str(message.chat.id) == '-1002163980111':
            print('chat')
            for word in BAD_WORDS:
                print(f'checking{word}')
                translated_texts = [''.join(variant) for variant in product(*(char_map.get(char, [char]) for char in word))]
                for translated_text in translated_texts:
                    if translated_text in message.text.lower():
                        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                for word in BAD_WORDS:
                    print(f'checking{word}')
                    translated_texts = [''.join(variant) for variant in product(*(char_map.get(char, [char]) for char in word))]
                    for translated_text in translated_texts:
                        if translated_text in message.from_user.full_name.lower():
                            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                    else:
                        url_pattern = re.compile(r'(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b)')
                        urls = re.findall(url_pattern, message.text.lower())
                        if urls:
                            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                        else:
                            username_pattern = re.compile(r'@\w+')
                            usernames = re.findall(username_pattern, message.text.lower())
                            if usernames:
                                await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


    except Exception as ex:
        pass





