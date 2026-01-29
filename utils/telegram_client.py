from telethon import TelegramClient
from database.db import AsyncSessionLocal
from database.models import Session
from sqlalchemy.future import select
import os
import logging

logger = logging.getLogger(__name__)

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

async def get_client(user_id: int) -> TelegramClient:
    """
    Returns a configured TelegramClient for the given user_id.
    It does NOT connect or start the client.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        session_data = result.scalar_one_or_none()
        
        if not session_data:
            raise ValueError(f"No session found for user {user_id}")
            
        # Telethon session path should not have .session extension
        session_path = os.path.join(SESSION_DIR, f"user_{user_id}")
        
        client = TelegramClient(
            session_path,
            session_data.api_id,
            session_data.api_hash,
            device_model="AutoForward Bot",
            system_version="4.16.30-vxCUSTOM",
            app_version="1.0.0"
        )
        return client

async def get_client_session(user_id: int):
    """Returns the session record from DB for the user."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        return result.scalar_one_or_none()
