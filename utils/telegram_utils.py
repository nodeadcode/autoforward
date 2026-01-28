from telethon import TelegramClient
from telethon.sessions import StringSession
import os

async def get_latest_saved_message(session_path: str, api_id: int, api_hash: str):
    """
    Connects to Telegram using the provided session file and fetches the latest message 
    from 'Saved Messages' (me).
    """
    # Ensure session path is absolute or correct relative path
    # Telethon session_path shouldn't include .session if it's already in the file name?
    # Actually if we pass 'path/to/file.session', it works.
    
    client = TelegramClient(session_path, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return None, "Unauthorized"

        # Get 'me' (Saved Messages)
        messages = await client.get_messages('me', limit=1)
        if not messages:
            return None, "Empty"

        msg = messages[0]
        if not msg.text:
             return None, "Not Text"
             
        return msg, None
    except Exception as e:
        return None, str(e)
    finally:
        await client.disconnect()
