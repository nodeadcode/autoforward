import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN_MAIN
from bots.main_bot.handlers import start, menu, settings, groups, plans, redeem, account, owner
from database.db import init_db

async def main():
    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("main_bot.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Initialize Database (if strictly running this file)
    await init_db()

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

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

    async def global_error_handler(event: types.ErrorEvent):
        logging.error(f"Global Error: {event.exception}", exc_info=True)
        # Optionally notify admin
        # await bot.send_message(OWNER_ID, f"⚠️ **Bot Error!**\n\n`{str(event.exception)[:1000]}`")

    dp.errors.register(global_error_handler)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
