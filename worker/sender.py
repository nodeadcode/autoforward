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

async def process_user(user_id: int):
    """
    Handles the sending cycle for a single user.
    Fetches user fresh from DB to ensure attached session for updates.
    """
    async with AsyncSessionLocal() as db:
        # Re-fetch user with session and groups to attach to this DB session
        stmt = select(User).options(
            selectinload(User.session),
            selectinload(User.groups),
            selectinload(User.settings)
        ).where(User.id == user_id)
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.session:
            return

        session_file = user.session.session_path
        client = TelegramClient(session_file, user.session.api_id, user.session.api_hash)
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                logger.warning(f"User {user.id} session invalid/expired. Disabling.")
                user.session.is_active = False
                await db.commit()
                return

            # 1. Get latest Saved Message using utility
            from utils.telegram_utils import get_latest_saved_message
            saved_msg, error = await get_latest_saved_message(session_file, user.session.api_id, user.session.api_hash)
            
            if error:
                logger.warning(f"User {user.id}: Could not fetch saved message: {error}")
                await client.disconnect()
                return

            message_to_send = saved_msg
            
            # 2. Iterate groups
            groups = user.groups
            if not groups:
                logger.info(f"User {user.id}: No groups to send to.")
                await client.disconnect()
                return

            logger.info(f"User {user.id}: Starting send cycle to {len(groups)} groups.")

            sent_count = 0
            for group in groups:
                if not group.is_enabled:
                    continue
                    
                try:
                    # Message Delay (200s) - Applying before each send as per requirement
                    if sent_count > 0:
                         await asyncio.sleep(MESSAGE_DELAY_SECONDS)

                    await client.send_message(group.group_id, message_to_send)
                    logger.info(f"User {user.id}: Sent to {group.group_id}")
                    sent_count += 1
                    
                    # Log success
                    log = MessageLog(user_id=user_id, group_id=group.group_id, status="success")
                    db.add(log)
                    await db.commit()
                    
                    # Group Gap (55s)
                    await asyncio.sleep(GROUP_GAP_SECONDS)
                    
                    # Group Gap (55s)
                    await asyncio.sleep(GROUP_GAP_SECONDS)

                except FloodWaitError as e:
                    logger.warning(f"User {user.id}: FloodWait {e.seconds}s. Sleeping.")
                    # Log failure
                    log = MessageLog(user_id=user_id, group_id=group.group_id, status="failed", error_info=f"FloodWait: {e.seconds}s")
                    db.add(log)
                    await db.commit()
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    error_str = str(e)
                    logger.error(f"User {user.id}: Failed to send to {group.group_id}. Error: {error_str}")
                    # Log failure
                    log = MessageLog(user_id=user_id, group_id=group.group_id, status="failed", error_info=error_str)
                    db.add(log)
                    await db.commit()
                    
                    if "permission" in error_str.lower() or "chat_write_forbidden" in error_str.lower():
                        logger.warning(f"User {user.id}: Skipping group {group.group_id} due to permissions.")
                    elif "too many requests" in error_str.lower():
                         # Another way flood wait might manifest
                         await asyncio.sleep(60)
            
            # Update last_run only if we attempted sending
            if sent_count > 0:
                user.settings.last_run = datetime.utcnow()
                await db.commit()
                logger.info(f"User {user.id}: Cycle completed. Updated last_run.")

        except Exception as e:
            logger.error(f"User {user.id}: Client error: {e}")
        finally:
            await client.disconnect()
