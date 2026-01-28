# Auto Message Scheduler (Spinify)

A powerful multi-user Telegram automation system that allows users to schedule messages from their "Saved Messages" to their groups automatically.

## 🚀 Features

-   **User-Specific Automation**: Each user connects their **Own Telegram Account** using their unique API ID/Hash.
-   **Security**: No shared sessions or API keys. Your data is isolated.
-   **Auto-Sending**: Reads the latest message from your "Saved Messages" and sends it to your configured groups.
-   **Intervals**: Set custom intervals (min 25 mins).
-   **Night Mode**: Automatically pauses between 12 AM - 6 AM to simulate human behavior.
-   **Plans**: 7-day free trial on signup. Extend via Redeem Codes.
-   **Safety**: FloodWait handling, Sequential sending, and Smart delays (55s gap).

## 🛠 Installation & Deployment

### 1. Prerequisites
-   Python 3.9+
-   VPS with at least 2GB RAM

### 2. Setup
1.  Clone the repository.
    ```bash
    git clone https://github.com/nodeadcode/autoforward.git
    cd autoforward/auto_message_scheduler
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure `config/secrets.env`:
    ```env
    BOT_TOKEN_MAIN=123456:ABC-DEF...   # From @BotFather (Main Bot)
    BOT_TOKEN_LOGIN=123456:GHI-JKL...  # From @BotFather (Login Bot)
    OWNER_ID=123456789                # Your Telegram ID (For Admin Commands)
    DATABASE_URL=sqlite+aiosqlite:///auto_message_scheduler.db
    # API_ID and API_HASH are NOT needed here. Users provide them via the Login Bot.
    ```

### 3. Running the System
You need to run three separate processes. Use `screen`, `tmux`, or `systemd`.

**Process 1: Main Bot** (User Dashboard)
```bash
python -m bots.main_bot.bot
```

**Process 2: Login Bot** (Authentication)
```bash
python -m bots.login_bot.bot
```

**Process 3: Worker** (Automation Engine)
```bash
python -m worker.worker
```

## 📚 User Guide

1.  **Start Main Bot**: Check your status and get a plan.
2.  **Login**: Use the Login Bot to connect your Telegram account. You will need your **API ID** and **API Hash** from [my.telegram.org](https://my.telegram.org).
3.  **Add Groups**: In the Main Bot, add the groups you want to send messages to.
4.  **Schedule**: Post a message in your **Saved Messages**, and the bot will pick it up and forward it to your groups based on your interval.

## 👑 Admin Commands
-   `/gencode <days>`: Generate a redeem code (Owner only).
