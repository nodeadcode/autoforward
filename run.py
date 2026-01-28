import sys
import os
import subprocess

def run_main_bot():
    print("🚀 Starting Main Bot...")
    subprocess.run([sys.executable, "-m", "bots.main_bot.bot"])

def run_login_bot():
    print("🚀 Starting Login Bot...")
    subprocess.run([sys.executable, "-m", "bots.login_bot.bot"])

def run_worker():
    print("🚀 Starting Worker...")
    subprocess.run([sys.executable, "-m", "worker.worker"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py [main|login|worker]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    if cmd == "main":
        run_main_bot()
    elif cmd == "login":
        run_login_bot()
    elif cmd == "worker":
        run_worker()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python run.py [main|login|worker]")
