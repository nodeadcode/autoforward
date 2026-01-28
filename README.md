# Auto Message Scheduler (Spinify)

A powerful multi-user Telegram automation system that allows users to schedule messages from their "Saved Messages" to their groups automatically.

## Components

1.  **Main Bot**: User dashboard for managing settings, groups, and plans.
2.  **Login Bot**: Securely logs in users to Telegram to act on their behalf.
3.  **Worker**: Background process that executes the message sending schedules.

## Installation & Deployment

### 1. Prerequisites
- Python 3.9+
- VPS with at least 2GB RAM
- Telegram API Credentials (for the implementation, using a main set of keys for the client login helper if needed, but users provide their own).

### 2. Setup
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure `config/secrets.env`:
    ```env
    BOT_TOKEN_MAIN=123456:ABC-DEF...   # From @BotFather
    BOT_TOKEN_LOGIN=123456:GHI-JKL...  # From @BotFather (Separate bot)
    OWNER_ID=123456789                # Your Telegram ID
    API_ID=12345                      # Your App ID (my.telegram.org)
    API_HASH=abcdef...                # Your App Hash
    DATABASE_URL=sqlite+aiosqlite:///auto_message_scheduler.db
    ```

### 3. Running the System
You need to run three separate processes. Use `screen`, `tmux`, or `systemd`.

**Process 1: Main Bot**
```bash
python -m bots.main_bot.bot
```

**Process 2: Login Bot**
```bash
python -m bots.login_bot.bot
```

**Process 3: Worker**
```bash
python -m worker.worker
```

## Features
- **Auto-Sending**: Reads the latest message from your "Saved Messages" and sends it to your configured groups.
- **Intervals**: Set custom intervals (min 25 mins).
- **Night Mode**: Automatically pauses between 12 AM - 6 AM.
- **Plans**: Free trial (7 days) and redeem code system for paid codes.
- **Safety**: FloodWait handling and sequential sending to prevent bans.

## Admin Commands
- `/gencode <days>`: Generate a redeem code (Owner only).
