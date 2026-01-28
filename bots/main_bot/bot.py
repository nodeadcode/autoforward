import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN_MAIN
from bots.main_bot.handlers import start, menu, settings, groups, plans, redeem
from database.db import init_db

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Database (if strictly running this file)
    await init_db()

    bot = Bot(token=BOT_TOKEN_MAIN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(settings.router)
    dp.include_router(groups.router)
    dp.include_router(plans.router)
    dp.include_router(redeem.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
