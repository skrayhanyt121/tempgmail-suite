"""
Configuration settings for TempGmail Suite.
Can be configured via environment variables or modified here.
"""

import os

# Server configuration
HOST = os.environ.get("TEMPGMAIL_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", os.environ.get("TEMPGMAIL_PORT", 5050)))

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Facebook Messenger configuration
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "tempgmail_verify_token_2026")

# Polling intervals & timeouts
OTP_WAIT_TIMEOUT = 120  # seconds
OTP_POLL_INTERVAL = 3   # seconds
