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
        from database.models import Session
        from sqlalchemy.future import select
        result = await db.execute(select(Session).where(Session.user_id == message.from_user.id))
        session = result.scalar_one_or_none()
        
        status_text = "❉ ACCOUNT CONNECTED" if session and session.is_active else "◊ ACCOUNT NOT CONNECTED"
    
    await message.answer(
        f"❉ **SPINIFY ADS** ❉\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Hello {message.from_user.first_name}!\n"
        f"Welcome to the most powerful scheduler.\n\n"
        f"◈ **Status**: {status_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Please select an option:",
        reply_markup=main_menu_kb(message.from_user.id)
    )

@router.callback_query(F.data == "home")
async def cb_home(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❉ **MAIN MENU** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Control your automated messages, groups, and settings here.",
        reply_markup=main_menu_kb(callback.from_user.id)
    )
