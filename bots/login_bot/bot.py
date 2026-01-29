import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN_LOGIN
from bots.login_bot.handlers import start, api, phone, otp, status
from database.db import init_db

async def main():
    # Setup Structured Logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("logs/login_bot.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("LoginBot")
    logger.info("Starting Login Bot...")

    # Ensure logs directory exists
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Initialize Database
    await init_db()

    bot = Bot(token=BOT_TOKEN_LOGIN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(api.router)
    dp.include_router(phone.router)
    dp.include_router(otp.router)
    dp.include_router(status.router)

    @dp.errors()
    async def global_error_handler(event: types.ErrorEvent):
        logger.error(f"⚠️ GLOBAL LOGIN BOT ERROR: {event.exception}", exc_info=True)
        return True # Handled

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
