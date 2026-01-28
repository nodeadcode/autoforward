import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN_LOGIN
from bots.login_bot.handlers import start, api, phone, otp
from database.db import init_db

async def main():
    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("login_bot.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Initialize Database
    await init_db()

    bot = Bot(token=BOT_TOKEN_LOGIN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(api.router)
    dp.include_router(phone.router)
    dp.include_router(otp.router)

    async def global_error_handler(event: types.ErrorEvent):
        logging.error(f"Global Login Bot Error: {event.exception}", exc_info=True)

    dp.errors.register(global_error_handler)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
