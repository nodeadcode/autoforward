import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.settings import BOT_TOKEN_MAIN
from bots.main_bot.handlers import start, menu, settings, groups, plans, redeem, account, owner, guide
from database.db import init_db

async def main():
    # Setup Structured Logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("logs/main_bot.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("MainBot")
    logger.info("Starting Main Bot...")

    # Ensure logs directory exists
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Initialize Database
    await init_db()

    bot = Bot(token=BOT_TOKEN_MAIN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(settings.router)
    dp.include_router(groups.router)
    dp.include_router(plans.router)
    dp.include_router(redeem.router)
    dp.include_router(account.router)
    dp.include_router(owner.router)
    dp.include_router(guide.router)

    @dp.errors()
    async def global_error_handler(event: types.ErrorEvent):
        logger.error(f"⚠️ GLOBAL ERROR: {event.exception}", exc_info=True)
        return True # Handled

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
