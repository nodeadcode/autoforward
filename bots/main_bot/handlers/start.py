from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import AsyncSessionLocal
from database.crud import get_or_create_user
from bots.main_bot.keyboards.inline import main_menu_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, message.from_user.id, message.from_user.username)
        # We could check if they have a session connected here, but that checks "other db" or same db
        # If user.session is missing, we could prompt them to use Login Bot
    
    await message.answer(
        f"👋 Hello {message.from_user.first_name}!\n\n"
        "Welcome to **Auto Message Scheduler**.\n"
        "Control your automated messages, groups, and settings here.\n\n"
        "👇 Choose an option from the menu:",
        reply_markup=main_menu_kb(message.from_user.id)
    )

@router.callback_query(F.data == "home")
async def cb_home(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "👋 **Main Menu**\n\n"
        "Control your automated messages, groups, and settings here.",
        reply_markup=main_menu_kb(callback.from_user.id)
    )
