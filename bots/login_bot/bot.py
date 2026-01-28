import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN_LOGIN
from bots.login_bot.handlers import start, api, phone, otp
from database.db import init_db

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Database
    await init_db()

    bot = Bot(token=BOT_TOKEN_LOGIN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(api.router)
    dp.include_router(phone.router)
    dp.include_router(otp.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
