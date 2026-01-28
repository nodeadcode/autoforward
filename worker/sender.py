import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from database.db import AsyncSessionLocal
from database.models import User, Session, Settings
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

        session_string = user.session.session_string
        client = TelegramClient(StringSession(session_string), user.session.api_id, user.session.api_hash)
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                logger.warning(f"User {user.id} session invalid/expired. Disabling.")
                user.session.is_active = False
                await db.commit()
                return

            # 1. Get latest Saved Message
            saved_msgs = await client.get_messages("me", limit=1)
            if not saved_msgs:
                logger.info(f"User {user.id}: No saved messages found.")
                await client.disconnect()
                return

            message_to_send = saved_msgs[0]
            
            # 2. Iterate groups
            groups = user.groups
            if not groups:
                logger.info(f"User {user.id}: No groups to send to.")
                await client.disconnect()
                return

            logger.info(f"User {user.id}: Starting send cycle to {len(groups)} groups.")

            sent_count = 0
            for group in groups:
                try:
                    if message_to_send.text:
                        await client.send_message(group.group_id, message_to_send.text)
                        logger.info(f"User {user.id}: Sent to {group.group_id}")
                        sent_count += 1
                    else:
                        logger.warning(f"User {user.id}: Latest saved message has no text. Skipping.")
                    
                    await asyncio.sleep(GROUP_GAP_SECONDS)

                except FloodWaitError as e:
                    logger.warning(f"User {user.id}: FloodWait {e.seconds}s. Sleeping.")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    logger.error(f"User {user.id}: Failed to send to {group.group_id}. Error: {e}")
            
            # Update last_run only if we attempted sending
            if sent_count > 0:
                user.settings.last_run = datetime.utcnow()
                await db.commit()
                logger.info(f"User {user.id}: Cycle completed. Updated last_run.")

        except Exception as e:
            logger.error(f"User {user.id}: Client error: {e}")
        finally:
            await client.disconnect()
