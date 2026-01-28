import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from database.models import User
from config.settings import GROUP_GAP_SECONDS, MESSAGE_DELAY_SECONDS

logger = logging.getLogger(__name__)

async def process_user(user: User, session_string: str):
    """
    Handles the sending cycle for a single user.
    """
    client = TelegramClient(StringSession(session_string), user.session.api_id, user.session.api_hash)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            logger.warning(f"User {user.id} session invalid/expired.")
            return

        # 1. Get latest Saved Message
        # "me" refers to Saved Messages in Telethon
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

        for group in groups:
            try:
                # Send message
                # We forward the message to keep formatting/media easily? 
                # Or copy? "Text messages only (for now)" says spec.
                # "Messages are read only from Saved Messages... Text messages only"
                # But forwarding is safer and supports media if expanded later.
                # However, "Sender" is the user.
                # Let's use `send_message` with text content to avoid forward tag if unwanted, 
                # OR `forward_messages` if forward tag is okay.
                # Usually "Auto Message Scheduler" implies "Native Post".
                # If text only:
                if message_to_send.text:
                    await client.send_message(group.group_id, message_to_send.text)
                    logger.info(f"User {user.id}: Sent to {group.group_id}")
                else:
                    logger.warning(f"User {user.id}: Latest saved message has no text. Skipping.")
                
                # Group Gap
                await asyncio.sleep(GROUP_GAP_SECONDS)

            except FloodWaitError as e:
                logger.warning(f"User {user.id}: FloodWait {e.seconds}s. Sleeping.")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"User {user.id}: Failed to send to {group.group_id}. Error: {e}")
        
        logger.info(f"User {user.id}: Cycle completed.")

    except Exception as e:
        logger.error(f"User {user.id}: Client error: {e}")
    finally:
        await client.disconnect()
