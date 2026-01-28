from typing import Dict
from telethon import TelegramClient

# Global dictionary to hold active login clients
# Key: Telegram User ID (of the user chatting with the bot)
# Value: TelegramClient instance
active_clients: Dict[int, TelegramClient] = {}

def get_client(user_id: int) -> TelegramClient:
    return active_clients.get(user_id)

def add_client(user_id: int, client: TelegramClient):
    active_clients[user_id] = client

async def remove_client(user_id: int):
    client = active_clients.pop(user_id, None)
    if client:
        await client.disconnect()
