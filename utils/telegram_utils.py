from telethon import TelegramClient
from telethon.sessions import StringSession
import os

async def get_saved_messages(session_path: str, api_id: int, api_hash: str, limit: int = 50):
    """
    Connects to Telegram and fetches the last N messages from 'Saved Messages'.
    """
    client = TelegramClient(session_path, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return None, "Unauthorized"

        # Get 'me' (Saved Messages)
        messages = await client.get_messages('me', limit=limit)
        if not messages:
            return None, "Empty"

        return list(messages), None
    except Exception as e:
        return None, str(e)
    finally:
        await client.disconnect()
