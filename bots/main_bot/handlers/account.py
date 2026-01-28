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
        await get_or_create_user(db, user_id)
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        session = result.scalar_one_or_none()
        
        is_connected = session and session.is_active
        status_text = "❉ CONNECTED" if is_connected else "◊ NOT CONNECTED"
        phone = f"`{session.phone_number}`" if is_connected else "`N/A`"
        api_id = f"`{session.api_id}`" if is_connected else "`N/A`"

    text = (
        "❉ **ACCOUNT MANAGEMENT** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ **User ID**: `{user_id}`\n"
        f"◈ **Status**: {status_text}\n"
        f"◈ **Phone**: {phone}\n"
        f"◈ **API ID**: {api_id}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    if not is_connected:
        text += "◊ **WARNING**: You are not connected.\n⊹ Click below to link your account."
    else:
        text += "⊹ To disconnect, click 'Remove Account'."

    await callback.message.edit_text(text, reply_markup=account_kb(is_connected))

@router.callback_query(F.data == "remove_account")
async def cb_remove_account(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Session).where(Session.user_id == user_id))
        await db.commit()
        
    await callback.answer("◈ Account removed successfully.")
    await cb_account(callback)
