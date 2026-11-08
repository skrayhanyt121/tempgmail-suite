#!/usr/bin/env python3
"""
Master launcher for TempGmail Suite.
Supports:
1. Web Dashboard & Facebook Messenger Webhook
2. Telegram Bot
3. Both services concurrently
4. Interactive Terminal Mode
"""

import sys
import threading
import time
import config
from tempgmail import TempGmailClient


def run_web():
    """Start Flask Web App & Messenger Webhook."""
    from web_app import app
    print(f"\n🚀 [Web] Starting Web Dashboard & Messenger Webhook on http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=False)


def run_telegram():
    """Start Telegram Bot."""
    if not config.TELEGRAM_BOT_TOKEN:
        print("\n⚠️ [Telegram] Error: TELEGRAM_BOT_TOKEN is not configured in config.py!")
        print("Please configure your bot token in config.py or export TELEGRAM_BOT_TOKEN")
        return
    from telegram_bot import TelegramBot
    bot = TelegramBot(config.TELEGRAM_BOT_TOKEN)
    bot.start_polling()


def run_both():
    """Start both Web and Telegram in separate threads."""
    t_web = threading.Thread(target=run_web, daemon=True)
    t_web.start()
    time.sleep(1)
    run_telegram()


def run_cli_interactive():
    """Interactive command-line tool directly in terminal."""
    client = TempGmailClient()
    active_email = None

    print("\n" + "=" * 55)
    print("🔥 TempGmail Suite - Terminal Interactive Mode")
    print("=" * 55)

    while True:
        print("\nSelect an action:")
        print(" [1] ⚡ Generate New Temp Gmail")
        print(" [2] 📥 Check Inbox Messages")
        print(" [3] 🔢 Wait / Auto-detect Incoming OTP")
        print(" [4] 🗑  Clear Current Inbox")
        print(" [5] 🌐 Start Web Server & Facebook Webhook")
        print(" [0] ❌ Exit")

        choice = input("\n👉 Enter choice (0-5): ").strip()

        if choice == "1":
            print("\n⏳ Requesting fresh Gmail from pool...")
            try:
                res = client.get_random_email(exclude=active_email)
                active_email = res["email"]
                print(f"✅ Active Temp Gmail: \033[1;32m{active_email}\033[0m")
                print(f"📊 Existing messages: {res['message_count']}")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            if not active_email:
                print("⚠️ Please generate a Gmail first (Option 1).")
                continue
            print(f"\n🔍 Fetching inbox for {active_email}...")
            try:
                res = client.get_inbox(active_email)
                messages = res.get("messages", [])
                if not messages:
                    print("📭 Inbox is currently empty.")
                else:
                    print(f"📬 Found {len(messages)} message(s):")
                    for idx, m in enumerate(messages, 1):
                        full = client.get_message(m["id"])
                        otp = full.get("extracted_otp")
                        print(f"\n--- Message #{idx} ---")
                        print(f"From: {full.get('sender')}")
                        print(f"Subject: {full.get('subject')}")
                        if otp:
                            print(f"🔥 Extracted OTP: \033[1;33m{otp}\033[0m")
                        print(f"Preview: {full.get('body_plain', '')[:160]}...")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            if not active_email:
                print("⚠️ Please generate a Gmail first (Option 1).")
                continue
            print(f"\n⏳ Watching for incoming OTP on {active_email} (waiting up to 90s)...")
            res = client.wait_for_otp(active_email, timeout=90, interval=3)
            if res:
                print("\n🎉 \033[1;32mNEW VERIFICATION CODE DETECTED!\033[0m")
                print(f"🔑 Code: \033[1;33m{res['otp']}\033[0m")
                print(f"👤 Sender: {res['sender']}")
                print(f"📝 Subject: {res['subject']}")
            else:
                print("⏰ Timed out. No new OTP arrived.")

        elif choice == "4":
            if not active_email:
                print("⚠️ No active Gmail.")
                continue
            client.clear_inbox(active_email)
            print(f"🗑 Inbox cleared for {active_email}.")

        elif choice == "5":
            run_web()
            break

        elif choice == "0":
            print("👋 Bye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "web":
            run_web()
        elif arg == "telegram" or arg == "tg":
            run_telegram()
        elif arg == "both" or arg == "all":
            run_both()
        elif arg == "cli":
            run_cli_interactive()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python3 run.py [web | telegram | both | cli]")
    else:
        run_cli_interactive()
