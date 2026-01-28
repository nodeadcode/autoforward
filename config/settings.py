import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'secrets.env'))

BOT_TOKEN_MAIN = os.getenv("BOT_TOKEN_MAIN")
BOT_TOKEN_LOGIN = os.getenv("BOT_TOKEN_LOGIN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
# API_ID and API_HASH are now user-specific and stored in DB
# API_ID = int(os.getenv("API_ID", 0))
# API_HASH = os.getenv("API_HASH")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///auto_message_scheduler.db")

# Limits
MAX_GROUPS_PER_USER = 10
MIN_MESSAGE_INTERVAL_MINUTES = 25
MESSAGE_DELAY_SECONDS = 200
GROUP_GAP_SECONDS = 55

# Night Mode (12 AM - 6 AM)
NIGHT_MODE_START = 0  # 00:00
NIGHT_MODE_END = 6    # 06:00
