from aiogram import Router, types, F
from database.db import AsyncSessionLocal
from database.models import Session
from database.crud import get_or_create_user
from bots.main_bot.keyboards.inline import account_kb, back_home_kb
from sqlalchemy.future import select
from sqlalchemy import delete

router = Router()

@router.callback_query(F.data == "account")
async def cb_account(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        # Get User and Session
        await get_or_create_user(db, user_id) # Ensure user exists
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        session = result.scalar_one_or_none()
        
        is_connected = False
        if session and session.is_active:
            is_connected = True
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
    )
    
    if not is_connected:
        text += "⚠️ You are not connected. Click the button below to login."
    else:
        text += "To disconnect this account, click 'Remove Account' below."

    await callback.message.edit_text(text, reply_markup=account_kb(is_connected))

@router.callback_query(F.data == "remove_account")
async def cb_remove_account(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    async with AsyncSessionLocal() as db:
        # Delete Session
        await db.execute(delete(Session).where(Session.user_id == user_id))
        await db.commit()
        
    await callback.answer("✅ Account removed successfully.")
    # Refresh view
    await cb_account(callback)
