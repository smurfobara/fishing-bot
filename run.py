import asyncio
import logging

from aiogram import Bot, Dispatcher#, F
from handlers import router
import sqlite3

from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()



db = sqlite3.connect('base.db')
db.close()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Programm closed')