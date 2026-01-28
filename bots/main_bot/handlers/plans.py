from aiogram import Router, types, F
from database.db import AsyncSessionLocal
from database.crud import get_or_create_user
from bots.main_bot.keyboards.inline import back_home_kb
from datetime import datetime

router = Router()

@router.callback_query(F.data == "plan")
async def cb_plan(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, user_id)
        
        expiry = user.plan_expiry
        is_active = expiry > datetime.utcnow()
        days_left = (expiry - datetime.utcnow()).days
        
        status_sym = "❉" if is_active else "◊"
        expiry_str = expiry.strftime('%Y-%m-%d %H:%M') if expiry else "N/A"
        
        text = (
            "❉ **MEMBERSHIP PLAN** ❉\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"◈ **User ID**: `{user_id}`\n"
            f"◈ **Expiry**: `{expiry_str}`\n"
            f"◈ **Status**: {status_sym} {'ACTIVE' if is_active else 'EXPIRED'}\n"
            f"◈ **Remaining**: `{days_left if is_active else 0}` days\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⊹ To extend your plan, use a redeem code or contact support."
        )
        
        await callback.message.edit_text(text, reply_markup=back_home_kb())
