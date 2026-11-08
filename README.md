# 🚀 TempGmail Suite (Website, Telegram & Facebook Messenger)

A production-ready suite for generating authentic `@gmail.com` temporary addresses and automatically extracting OTP verification codes without any ads or popups.

---

## 📁 Project Structure

```
/root/scripted/
├── tempgmail.py         # Core API Client & Smart OTP Regex Extractor
├── config.py            # Central Configuration (Tokens, Ports, Timers)
├── web_app.py           # Flask Web Dashboard & Facebook Messenger Webhook
├── telegram_bot.py      # Standalone Telegram Long-Polling Bot
├── run.py               # Master CLI Launcher (CLI / Web / TG / Both)
├── templates/
│   └── index.html       # Ultra-modern, responsive Web UI (Dark Studio)
└── README.md
```

---

## ⚡ Quick Start

### 1. Interactive Terminal Mode (CLI)
Run directly inside your Linux/Termux terminal:
```bash
python3 run.py cli
# or simply
python3 run.py
```

### 2. Website & Facebook Messenger Webhook
Start the Web App on port 5050:
```bash
python3 run.py web
```
- Open in browser: `http://localhost:5050` (or `http://<your-ip>:5050`)
- Features:
  - ⚡ 1-Tap Copy Gmail
  - 🔄 Change Mail with 1 click
  - 🔢 Live OTP Highlight Banner & 1-Tap Copy Code
  - 📭 Full Email Viewer modal
  - 📱 100% Mobile & Touch responsive

### 3. Telegram Bot
Configure your bot token in `config.py` or export via environment variable:
```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
python3 run.py telegram
```
- Features:
  - `/new`: Instant fresh Gmail (tap monospace text to copy)
  - `/inbox`: View latest 5 emails with senders and codes
  - `/otp`: Auto-monitors inbox for 90 seconds and alerts as soon as code arrives
  - Interactive Inline Keyboards (no typing required)

### 4. Facebook Messenger Bot
Configure Facebook Page token and verify token in `config.py`:
- `FB_PAGE_ACCESS_TOKEN`: Page Access Token from Meta Developer Console.
- `FB_VERIFY_TOKEN`: Verification token (default: `tempgmail_verify_token_2026`).
- Webhook URL in Meta Dashboard: `https://your-domain-or-ngrok/webhook`
- Supported Messenger commands & Quick Replies:
  - `⚡ New Gmail`
  - `📥 Check Inbox`
  - `🔢 Get OTP`

### 5. Run Both Concurrently
```bash
python3 run.py both
```

---

## 🔌 Direct REST APIs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/email/new` | Generate new `@gmail.com` address |
| `GET` | `/api/email/new?exclude=email` | Generate a different Gmail |
| `GET` | `/api/email/inbox?email=...` | Get inbox messages |
| `GET` | `/api/email/message/<msg_id>` | Get email body & extracted OTP |
| `GET` | `/api/email/wait-otp?email=...` | Wait for OTP (long polling) |
| `DELETE` | `/api/email/clear?email=...` | Clear mailbox |
