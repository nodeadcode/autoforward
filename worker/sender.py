import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from database.db import AsyncSessionLocal
from database.models import User, Session, Settings, MessageLog
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from config.settings import GROUP_GAP_SECONDS, MESSAGE_DELAY_SECONDS

logger = logging.getLogger(__name__)

from utils.telegram_client import get_client

async def process_user(user_id: int):
    """
    Handles the sending cycle for a single user.
    """
    async with AsyncSessionLocal() as db:
        stmt = select(User).options(
            selectinload(User.session),
            selectinload(User.groups),
            selectinload(User.settings)
        ).where(User.id == user_id)
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.session or not user.session.is_active:
            return

        # Use centralized client factory
        client = await get_client(user_id)
        
        try:
            # Update sender status: Connecting
            user.session.sender_status = "🔄 CONNECTING"
            await db.commit()

            await client.connect()
            if not await client.is_user_authorized():
                # Try starting with password if possible
                if user.session.two_fa_password:
                    await client.start(password=user.session.two_fa_password)
                else:
                    await client.start()

            if not await client.is_user_authorized():
                logger.warning(f"User {user.id} session invalid. Disabling.")
                user.session.is_active = False
                user.session.sender_status = "🔴 UNAUTHORIZED"
                await db.commit()
                return

            # Update sender status: Active
            user.session.sender_last_seen = datetime.utcnow()
            user.session.sender_status = "🟢 ACTIVE"
            await db.commit()

            # 1. Get Saved Messages (me)
            # User wants: Read Saved Messages via get_entity("me")
            me = await client.get_entity("me")
            messages = await client.get_messages(me, limit=50)
            
            if not messages:
                 logger.warning(f"User {user.id}: Saved Messages are empty.")
                 user.session.sender_status = "🟠 EMPTY SAVED MSGS"
                 await db.commit()
                 return

            # Sequential Mode - use last_msg_index
            msg_list = list(messages)
            msg_list.reverse() # Oldest of the tail first
            
            current_idx = user.settings.last_msg_index % len(msg_list)
            message_to_send = msg_list[current_idx]
            
            logger.info(f"User {user.id}: Sending message index {current_idx}")
            
            groups = user.groups
            if not groups:
                user.session.sender_status = "🟠 NO GROUPS"
                await db.commit()
                return

            sent_count = 0
            for group in groups:
                if not group.is_enabled:
                    continue
                    
                if sent_count > 0:
                    await asyncio.sleep(GROUP_GAP_SECONDS)

                retry_count = 0
                while retry_count < 2:
                    try:
                        # Resolve entity and check membership
                        try:
                            # User wants: Resolve each group using get_entity()
                            entity = await client.get_entity(group.group_id)
                        except Exception as e:
                            logger.warning(f"User {user.id}: Group {group.group_id} not accessible: {e}")
                            group.is_enabled = False # Disable on error
                            await db.commit()
                            break

                        await asyncio.sleep(MESSAGE_DELAY_SECONDS)
                        await client.send_message(entity, message_to_send)
                        
                        sent_count += 1
                        log = MessageLog(user_id=user_id, group_id=group.group_id, status="success")
                        db.add(log)
                        
                        # Update sender last seen every successful send
                        user.session.sender_last_seen = datetime.utcnow()
                        await db.commit()
                        break

                    except FloodWaitError as e:
                        logger.warning(f"User {user.id}: FloodWait {e.seconds}s")
                        user.session.sender_status = f"⏳ FLOODWAIT ({e.seconds}s)"
                        await db.commit()
                        await asyncio.sleep(e.seconds + 5)
                        retry_count += 1
                    except Exception as e:
                        logger.error(f"User {user.id}: Send error to {group.group_id}: {e}")
                        retry_count += 1
                        if retry_count >= 2:
                            log = MessageLog(user_id=user_id, group_id=group.group_id, status="failed", error_info=str(e))
                            db.add(log)
                            await db.commit()
            
            if sent_count > 0:
                user.settings.last_run = datetime.utcnow()
                user.settings.last_msg_index += 1
                user.session.sender_status = "🟢 CYCLE FINISHED"
                await db.commit()

        except Exception as e:
            logger.error(f"User {user.id}: Sender error: {e}", exc_info=True)
            user.session.sender_status = f"🔴 ERROR: {str(e)[:50]}"
            await db.commit()
        finally:
            await client.disconnect()
