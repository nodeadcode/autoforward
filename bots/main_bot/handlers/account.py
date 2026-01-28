from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from database.db import AsyncSessionLocal
from database.models import User, Session
from database.crud import get_or_create_user
from bots.main_bot.keyboards.inline import back_home_kb
from sqlalchemy.future import select

router = Router()

@router.callback_query(F.data == "account")
async def cb_account(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        # Get User and Session
        user = await get_or_create_user(db, user_id)
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        session = result.scalar_one_or_none()
        
        if session and session.is_active:
            status = "✅ Connected"
            phone = session.phone_number
            api_id = session.api_id
        else:
            status = "❌ Not Connected"
            phone = "N/A"
            api_id = "N/A"

    text = (
        f"👤 **Manage Account**\n\n"
        f"**User ID**: `{user_id}`\n"
        f"**Status**: {status}\n"
        f"**Phone**: `{phone}`\n"
        f"**API ID**: `{api_id}`\n\n"
        "To switch accounts or update details, please use the **Login Bot** (@SpinifyLoginBot)."
    )
    
    await callback.message.edit_text(text, reply_markup=back_home_kb())
