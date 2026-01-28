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

Follow these steps to get your automation running:

### 1. Initial Setup
- **Start Main Bot**: Send `/start` to your main bot.
- **Get Trial**: You will automatically receive a 7-day trial.
- **Login**: Use the **Login Bot** to link your Telegram account. Enter your `API ID` and `API Hash` from [my.telegram.org](https://my.telegram.org).

### 2. Configure Groups
- Open the **Main Bot** and click on **Manage Groups**.
- Add the numeric ID or Username (e.g., `@groupname`) of the groups you want to message.
- Ensure you have joined these groups with the account you connected.

### 3. Setting Your Ad Message (SEQUENTIAL)
The bot reads your **Saved Messages** chat in Telegram and rotates through them sequentially.

1.  Open **Telegram**.
2.  Go to the **Saved Messages** chat.
3.  **Forward or Send multiple messages** that you want to use as ads.
    -   The bot will fetch the last 50 messages and send them one by one, per interval.
    -   **Cycle 1**: Sends Message #1 (oldest in the list).
    -   **Cycle 2**: Sends Message #2.
    -   ... and so on, looping back to Message #1 when the end is reached.
4.  This allows you to have a "rotation" of different ads without manual intervention.

### 4. Enable Scheduler
- In the **Main Bot**, go to **Settings**.
- Click **Resume Scheduler** to start the automatic sending cycle.
- The worker will now check your Saved Messages and start sending to your groups based on your interval.

## 👑 Owner Features
-   `/gencode <days> <amount>`: Generate redeem codes for users.
-   `/stats`: View global system analytics.
-   `/broadcast <text>`: Send a message to all bot users.
-   `/extend <user_id> <days>`: Manually extend a user's plan.
