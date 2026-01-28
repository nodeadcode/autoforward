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
from utils.telegram_utils import get_saved_messages

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

            # 1. Get Saved Messages using utility
            saved_messages, error = await get_saved_messages(session_file, user.session.api_id, user.session.api_hash)
            
            if error:
                logger.warning(f"User {user.id}: Could not fetch saved messages: {error}")
                await client.disconnect()
                return

            if not saved_messages:
                 logger.warning(f"User {user.id}: Saved Messages are empty.")
                 await client.disconnect()
                 return

            # Pick message sequentially (Round-Robin)
            # Reversing because get_messages returns newest first, but we want to go oldest to newest usually?
            # Or just use them as is. Let's go newest to oldest for simplicity or reverse for chronological.
            # User said "in a sequenceny row", usually means top to bottom (oldest to newest).
            saved_messages.reverse() # Now index 0 is the oldest of the tail
            
            current_idx = user.settings.last_msg_index % len(saved_messages)
            message_to_send = saved_messages[current_idx]
            
            logger.info(f"User {user.id}: Sequential Mode - Sending message index {current_idx} (Total: {len(saved_messages)})")
            
            # 2. Iterate groups
            groups = user.groups
            if not groups:
                logger.info(f"User {user.id}: No groups to send to.")
                await client.disconnect()
                return

            logger.info(f"User {user.id}: Starting send cycle to {len(groups)} groups.")

            sent_count = 0
            for index, group in enumerate(groups):
                if not group.is_enabled:
                    continue
                    
                # 1. Group Gap (55s) - Applied BEFORE each group except the first
                if sent_count > 0:
                    logger.info(f"User {user.id}: Waiting {GROUP_GAP_SECONDS}s (Group Gap)...")
                    await asyncio.sleep(GROUP_GAP_SECONDS)

                retry_count = 0
                max_retries = 2
                while retry_count <= max_retries:
                    try:
                        # 2. Message Delay (200s) - Applied ALWAYS before send to simulate "typing" or prepare
                        logger.info(f"User {user.id}: Waiting {MESSAGE_DELAY_SECONDS}s (Message Delay)...")
                        await asyncio.sleep(MESSAGE_DELAY_SECONDS)

                        await client.send_message(group.group_id, message_to_send)
                        logger.info(f"User {user.id}: ✅ Sent to {group.group_id}")
                        sent_count += 1
                        
                        # Log success
                        log = MessageLog(user_id=user_id, group_id=group.group_id, status="success")
                        db.add(log)
                        await db.commit()
                        break # Success, exit retry loop

                    except FloodWaitError as e:
                        logger.warning(f"User {user.id}: ⏳ FloodWait {e.seconds}s. Sleeping.")
                        # Log failure
                        log = MessageLog(user_id=user_id, group_id=group.group_id, status="failed", error_info=f"FloodWait: {e.seconds}s")
                        db.add(log)
                        await db.commit()
                        await asyncio.sleep(e.seconds + 5) # Extra buffer
                        retry_count += 1
                    except Exception as e:
                        error_str = str(e)
                        logger.error(f"User {user.id}: ❌ Failed to send to {group.group_id}. Error: {error_str}")
                        
                        if "permission" in error_str.lower() or "chat_write_forbidden" in error_str.lower():
                            logger.warning(f"User {user.id}: Skipping group {group.group_id} due to permissions.")
                            # Log failure
                            log = MessageLog(user_id=user_id, group_id=group.group_id, status="failed", error_info="Missing Permissions")
                            db.add(log)
                            await db.commit()
                            break # Don't retry permissions issues
                        
                        # Other errors retry
                        retry_count += 1
                        if retry_count > max_retries:
                            log = MessageLog(user_id=user_id, group_id=group.group_id, status="failed", error_info=error_str)
                            db.add(log)
                            await db.commit()
            
            # Update last_run only if we attempted sending
            if sent_count > 0:
                user.settings.last_run = datetime.utcnow()
                user.settings.last_msg_index += 1
                await db.commit()
                logger.info(f"User {user.id}: Cycle completed. Updated last_run and last_msg_index to {user.settings.last_msg_index}.")

        except Exception as e:
            logger.error(f"User {user.id}: Global process error: {e}", exc_info=True)
        finally:
            await client.disconnect()
