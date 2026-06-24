import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from utils.db import init_db
from handlers import moderation, admin

async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(moderation.router)
    dp.include_router(admin.router)
    print("Group Manager Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
