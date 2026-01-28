from aiogram import Router, types, F
from aiogram.filters import Command
from config.settings import OWNER_ID
from database.db import AsyncSessionLocal
from database.models import User, MessageLog, Group, RedeemCode
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import datetime, timedelta
import asyncio

router = Router()

def is_owner(user_id: int):
    return user_id == OWNER_ID

@router.message(Command("extend"))
async def cmd_extend(message: types.Message):
    """Usage: /extend <user_id> <days>"""
    if not is_owner(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: /extend <user_id> <days>")
        return

    try:
        target_user_id = int(args[1])
        days = int(args[2])
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == target_user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                await message.answer("❌ User not found.")
                return
            
            current_expiry = user.plan_expiry if user.plan_expiry and user.plan_expiry > datetime.utcnow() else datetime.utcnow()
            user.plan_expiry = current_expiry + timedelta(days=days)
            await db.commit()
            
        await message.answer(f"❉ **PLAN EXTENDED** ❉\n━━━━━━━━━━━━━━━━━━━━\n◈ Target: `{target_user_id}`\n◈ Added: `{days} days`\n◈ New Expiry: `{user.plan_expiry.strftime('%Y-%m-%d')}`")
    except ValueError:
        await message.answer("Invalid arguments. Both User ID and Days must be numbers.")

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    """Usage: /broadcast <text>"""
    if not is_owner(message.from_user.id):
        return

    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Usage: /broadcast <your message>")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User.id))
        user_ids = result.scalars().all()

    sent = 0
    failed = 0
    msg = await message.answer(f"🚀 Starting broadcast to {len(user_ids)} users...")

    for uid in user_ids:
        try:
            await message.bot.send_message(uid, text)
            sent += 1
        except Exception:
            failed += 1
        
        # Avoid flood
        await asyncio.sleep(0.05)
        
        if (sent + failed) % 10 == 0:
            try:
                await msg.edit_text(f"🚀 Broadcast in progress...\n✅ Sent: {sent}\n❌ Failed: {failed}\nRemaining: {len(user_ids) - (sent + failed)}")
            except Exception:
                pass

    await msg.edit_text(f"✅ **Broadcast Completed**\n\nTotal Users: {len(user_ids)}\n✅ Successfully Sent: {sent}\n❌ Failed/Blocked: {failed}")

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if not is_owner(message.from_user.id):
        return

    async with AsyncSessionLocal() as db:
        # User Stats
        user_count = (await db.execute(select(func.count(User.id)))).scalar()
        
        # Group Stats
        group_count = (await db.execute(select(func.count(Group.id)))).scalar()
        active_groups = (await db.execute(select(func.count(Group.id)).where(Group.is_enabled == True))).scalar()

        # Message Stats (Last 24h)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        msgs_24h = (await db.execute(select(func.count(MessageLog.id)).where(MessageLog.sent_at >= last_24h))).scalar()
        success_24h = (await db.execute(select(func.count(MessageLog.id)).where(MessageLog.sent_at >= last_24h, MessageLog.status == "success"))).scalar()
        
        # Total Success
        total_success = (await db.execute(select(func.count(MessageLog.id)).where(MessageLog.status == "success"))).scalar()

    stats_text = (
        "❉ **SYSTEM STATISTICS** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ **Total Users**: `{user_count}`\n"
        f"◈ **Total Groups**: `{group_count}` (`{active_groups}` active)\n"
        f"◈ **Total Success**: `{total_success}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 **Last 24 Hours**:\n"
        f"◈ **Total Attempts**: `{msgs_24h}`\n"
        f"◈ **Successful**: `{success_24h}`\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await message.answer(stats_text)

@router.message(Command("gencode"))
async def cmd_gencode(message: types.Message):
    """Usage: /gencode <days> <amount>"""
    if not is_owner(message.from_user.id):
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: /gencode <days> <amount>")
        return

    try:
        days = int(args[1])
        amount = int(args[2])
        
        import secrets
        import string
        
        codes = []
        async with AsyncSessionLocal() as db:
            for _ in range(amount):
                code = "ADS-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                new_code = RedeemCode(code=code, duration_days=days)
                db.add(new_code)
                codes.append(code)
            await db.commit()
            
        codes_str = "\n".join([f"`{c}`" for c in codes])
        await message.answer(f"✅ **Generated {amount} codes ({days} days)**:\n\n{codes_str}")
    except ValueError:
        await message.answer("Invalid arguments. Both Days and Amount must be numbers.")
