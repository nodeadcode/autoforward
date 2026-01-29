from aiogram import Router, types, F
from database.db import AsyncSessionLocal
from database.models import Session
from sqlalchemy.future import select
from datetime import datetime, timedelta
from utils.telegram_client import get_client
import logging

logger = logging.getLogger(__name__)
router = Router()

def get_status_text(last_seen):
    if not last_seen:
        return "🔴 OFFLINE"
    now = datetime.utcnow()
    diff = now - last_seen
    if diff < timedelta(minutes=10): # 10 min window
        return "🟢 ACTIVE"
    
    minutes = int(diff.total_seconds() // 60)
    if minutes < 60:
        return f"🟠 IDLE ({minutes}m ago)"
    return f"🔴 INACTIVE ({minutes // 60}h ago)"

@router.message(F.text == ".status")
async def cmd_status(message: types.Message):
    user_id = message.from_user.id
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        session_data = result.scalar_one_or_none()
        
        if not session_data or not session_data.is_active:
            await message.answer("❌ You are not logged in. Use /start to login.")
            return

        worker_status = get_status_text(session_data.worker_last_seen)
        sender_status = get_status_text(session_data.sender_last_seen)
        
        # Update session status fields (for DB sync)
        session_data.worker_status = worker_status
        session_data.sender_status = sender_status
        session_data.last_status_check = datetime.utcnow()
        session_data.remark = f"Checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await db.commit()

        # Connect to user's Telegram to send message to Saved Messages
        try:
            client = await get_client(user_id)
            await client.connect()
            
            if not await client.is_user_authorized():
                await message.answer("❌ Session expired. Please /start again.")
                session_data.is_active = False
                await db.commit()
                return

            status_msg = (
                f"❉ **SYSTEM STATUS** ❉\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"◈ **Worker**: {worker_status}\n"
                f"◈ **Sender**: {sender_status}\n"
                f"◈ **Last Seen (W)**: `{session_data.worker_last_seen or 'Never'}`\n"
                f"◈ **Last Seen (S)**: `{session_data.sender_last_seen or 'Never'}`\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⊹ Status check complete."
            )
            
            await client.send_message("me", status_msg)
            await client.disconnect()
            
            await message.answer("✅ Status logic executed. Check your **Saved Messages**.")
            
        except Exception as e:
            logger.error(f"Error in .status for {user_id}: {e}")
            await message.answer(f"❌ Error during status check: {str(e)}")
