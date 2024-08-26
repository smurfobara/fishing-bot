from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

acceptKeyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Да')],
    [KeyboardButton(text='Нет')]
], resize_keyboard=True)

menuKb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Написать в поддержку')],
    [KeyboardButton(text='Перейти на сайт')],
    [KeyboardButton(text='Подписаться на рыбака')]
], resize_keyboard=True)

toSiteKb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Перейти на сайт', url='https://our.fishing')]
])

yes_or_no_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Да')],
    [KeyboardButton(text='Нет')]
])

cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отменить')]
])

getOrNo = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Взять')],
    [KeyboardButton(text='Оставить другим')]
])

changes = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить/изменить автора')],
    [KeyboardButton(text='Удалить автора')]
])

async def kbBuild(list):
    keyboard = ReplyKeyboardBuilder()
    for button in list:
        keyboard.add(KeyboardButton(text=button))
    keyboard.add(KeyboardButton(text='Отменить'))
    return keyboard.adjust(1).as_markup()