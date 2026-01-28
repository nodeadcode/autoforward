from aiogram import Router, types, F
from database.db import AsyncSessionLocal
from sqlalchemy.future import select
from config.settings import OWNER_ID
from bots.main_bot.keyboards.inline import main_menu_kb

router = Router()

# This file might be redundant if merged with start.py, 
# but useful for separating logic if "Menu" becomes complex.
# For now, start.py handles the main menu display so this acts as a receiver for specific stats logic if needed.

@router.callback_query(F.data == "stats")
async def cb_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    async with AsyncSessionLocal() as db:
        from database.models import MessageLog, User, Group, Settings
        from sqlalchemy import func
        from datetime import datetime
        
        # Success/Failure counts today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        success_stmt = select(func.count(MessageLog.id)).where(MessageLog.user_id == user_id, MessageLog.status == "success", MessageLog.sent_at >= today_start)
        failed_stmt = select(func.count(MessageLog.id)).where(MessageLog.user_id == user_id, MessageLog.status == "failed", MessageLog.sent_at >= today_start)
        
        success_count = (await db.execute(success_stmt)).scalar()
        failed_count = (await db.execute(failed_stmt)).scalar()
        
        # User info
        user_stmt = select(User).where(User.id == user_id)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        
        # Group count
        group_stmt = select(func.count(Group.id)).where(Group.user_id == user_id, Group.is_enabled == True)
        active_groups = (await db.execute(group_stmt)).scalar()
        
        # Settings
        settings_stmt = select(Settings).where(Settings.user_id == user_id)
        settings = (await db.execute(settings_stmt)).scalar_one_or_none()
        
        status = "RUNNING" if settings and settings.active else "PAUSED"
        night_mode = "ENABLED" if settings and settings.night_mode_enabled else "DISABLED"
        
        expiry_str = user.plan_expiry.strftime("%Y-%m-%d") if user.plan_expiry else "N/A"

    stats_text = (
        "❉ **USER STATISTICS** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ **Status**: {status}\n"
        f"◈ **Plan Expiry**: `{expiry_str}`\n"
        f"◈ **Active Groups**: `{active_groups}/10`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ **Sent Today**: `{success_count}`\n"
        f"◈ **Failed Today**: `{failed_count}`\n"
        f"◈ **Night Mode**: {night_mode}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    
    # If Owner, show global stats
    if user_id == OWNER_ID:
        async with AsyncSessionLocal() as db:
            from database.models import User, MessageLog
            from sqlalchemy import func
            total_users = (await db.execute(select(func.count(User.id)))).scalar()
            active_users = (await db.execute(select(func.count(User.id)).where(User.plan_expiry > datetime.utcnow()))).scalar()
            total_sent = (await db.execute(select(func.count(MessageLog.id)).where(MessageLog.status == "success"))).scalar()
            
        stats_text += (
            "\n\n◈ **GLOBAL ADMIN STATS**\n"
            f"⊹ Total Users: `{total_users}`\n"
            f"⊹ Active Plans: `{active_users}`\n"
            f"⊹ Messages Sent: `{total_sent}`\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )

    # We can add a "Back" button here
    from bots.main_bot.keyboards.inline import back_home_kb
    await callback.message.edit_text(stats_text, reply_markup=back_home_kb())
