"""
Telegram Bot for TempGmail Suite.
Lightweight, standalone long-polling bot using direct Telegram Bot API.
Features:
- /start: Interactive menu with Inline Keyboards
- /new: Instant fresh Gmail with 1-tap copy
- /inbox: Check latest emails & extracted OTPs
- /otp: Auto-watch for new OTPs
- Interactive callback buttons
"""

import time
import re
from typing import Dict, Any, Optional
from curl_cffi import requests
from tempgmail import TempGmailClient
import config


class TelegramBot:
    def __init__(self, token: str):
        self.token = token.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session = requests.Session()
        self.client = TempGmailClient()
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
        self.offset = 0

    def api_call(self, method: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make call to Telegram Bot API."""
        url = f"{self.base_url}/{method}"
        try:
            resp = self.session.post(url, json=data or {}, timeout=30)
            return resp.json()
        except Exception as e:
            print(f"[TG API Error] {method}: {e}")
            return {"ok": False, "error": str(e)}

    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None, parse_mode: str = "HTML"):
        """Send message with optional inline keyboard."""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.api_call("sendMessage", payload)

    def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None, parse_mode: str = "HTML"):
        """Edit existing message in-place."""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.api_call("editMessageText", payload)

    def answer_callback_query(self, callback_id: str, text: Optional[str] = None):
        """Acknowledge button click."""
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text
        return self.api_call("answerCallbackQuery", payload)

    def get_main_keyboard(self) -> Dict[str, Any]:
        """Generate inline keyboard controls."""
        return {
            "inline_keyboard": [
                [
                    {"text": "⚡ New Gmail", "callback_data": "btn_new"},
                    {"text": "📥 Check Inbox", "callback_data": "btn_inbox"}
                ],
                [
                    {"text": "🔢 Auto-Detect OTP", "callback_data": "btn_otp"},
                    {"text": "🔄 Change Mail", "callback_data": "btn_change"}
                ],
                [
                    {"text": "🗑 Clear Inbox", "callback_data": "btn_clear"}
                ]
            ]
        }

    def handle_start(self, chat_id: int):
        """Handle /start command."""
        text = (
            "<b>👋 Welcome to TempGmail Bot!</b>\n\n"
            "Generate authentic, disposable <b>@gmail.com</b> addresses and receive OTP codes directly inside Telegram.\n\n"
            "✨ <b>Features:</b>\n"
            "• Real @gmail.com pool (passes strict filters)\n"
            "• Zero ads & instantaneous message delivery\n"
            "• Automatic OTP detection & extraction\n\n"
            "<i>Tap '⚡ New Gmail' below to get started!</i>"
        )
        self.send_message(chat_id, text, self.get_main_keyboard())

    def handle_new_email(self, chat_id: int, message_id: Optional[int] = None, exclude_current: bool = False):
        """Generate new temp Gmail for user."""
        current_email = self.user_sessions.get(chat_id, {}).get("email") if exclude_current else None
        
        try:
            data = self.client.get_random_email(exclude=current_email)
            email = data.get("email")
            self.user_sessions[chat_id] = {"email": email, "updated_at": time.time()}

            text = (
                f"✅ <b>Your Active Temp Gmail:</b>\n\n"
                f"<code>{email}</code>\n\n"
                f"👆 <i>Tap the email above to copy it instantly.</i>\n\n"
                f"Send verification code or signup links to this address, then tap <b>'📥 Check Inbox'</b> or <b>'🔢 Auto-Detect OTP'</b>."
            )

            if message_id:
                self.edit_message(chat_id, message_id, text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, text, self.get_main_keyboard())
        except Exception as e:
            err_text = f"❌ <b>Error:</b> Failed to generate Gmail ({e})"
            if message_id:
                self.edit_message(chat_id, message_id, err_text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, err_text, self.get_main_keyboard())

    def handle_check_inbox(self, chat_id: int, message_id: Optional[int] = None):
        """Check messages in user's active email."""
        email = self.user_sessions.get(chat_id, {}).get("email")
        if not email:
            msg = "⚠️ <b>No active Gmail found!</b>\nTap <b>'⚡ New Gmail'</b> to generate one first."
            if message_id:
                self.edit_message(chat_id, message_id, msg, self.get_main_keyboard())
            else:
                self.send_message(chat_id, msg, self.get_main_keyboard())
            return

        try:
            inbox = self.client.get_inbox(email)
            messages = inbox.get("messages", [])

            if not messages:
                text = (
                    f"📭 <b>Inbox is empty</b> for:\n<code>{email}</code>\n\n"
                    f"<i>Waiting for incoming emails... Send your verification code and check again.</i>"
                )
            else:
                text = f"📬 <b>Inbox for <code>{email}</code></b> ({len(messages)} messages):\n\n"
                for idx, m in enumerate(messages[:5], 1):
                    sender = m.get("sender", "Unknown")
                    subject = m.get("subject", "(No Subject)")
                    
                    # Fetch full message for OTP
                    full = self.client.get_message(m.get("id"))
                    otp = full.get("extracted_otp")

                    text += f"<b>{idx}. From:</b> {sender}\n"
                    text += f"<b>Subject:</b> {subject}\n"
                    if otp:
                        text += f"🔥 <b>OTP CODE:</b> <code>{otp}</code> (Tap to copy)\n"
                    text += "━━━━━━━━━━━━━━━━━━━━\n"

            if message_id:
                self.edit_message(chat_id, message_id, text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, text, self.get_main_keyboard())
        except Exception as e:
            err_text = f"❌ <b>Error fetching inbox:</b> {e}"
            if message_id:
                self.edit_message(chat_id, message_id, err_text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, err_text, self.get_main_keyboard())

    def handle_auto_otp(self, chat_id: int):
        """Poll inbox and notify as soon as OTP arrives."""
        email = self.user_sessions.get(chat_id, {}).get("email")
        if not email:
            self.send_message(chat_id, "⚠️ No active Gmail. Tap '⚡ New Gmail' first!", self.get_main_keyboard())
            return

        status_msg = self.send_message(
            chat_id,
            f"⏳ <b>Watching for OTP...</b>\nTarget: <code>{email}</code>\n\n<i>Waiting for incoming code (up to 90s)...</i>"
        )
        msg_id = status_msg.get("result", {}).get("message_id")

        result = self.client.wait_for_otp(email, timeout=90, interval=3)
        if result:
            otp = result.get("otp", "N/A")
            sender = result.get("sender", "Unknown")
            subject = result.get("subject", "")

            success_text = (
                f"🎉 <b>VERIFICATION CODE RECEIVED!</b>\n\n"
                f"🔑 <b>Code:</b> <code>{otp}</code> (Tap to copy)\n"
                f"👤 <b>From:</b> {sender}\n"
                f"📝 <b>Subject:</b> {subject}\n"
                f"📧 <b>Target:</b> <code>{email}</code>"
            )
            if msg_id:
                self.edit_message(chat_id, msg_id, success_text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, success_text, self.get_main_keyboard())
        else:
            timeout_text = (
                f"⏰ <b>Wait timed out.</b>\nNo new OTP detected in <code>{email}</code>.\n"
                f"Please ensure you clicked 'Send Code' on the target website, then tap <b>'🔢 Auto-Detect OTP'</b> again."
            )
            if msg_id:
                self.edit_message(chat_id, msg_id, timeout_text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, timeout_text, self.get_main_keyboard())

    def handle_clear_inbox(self, chat_id: int, message_id: Optional[int] = None):
        """Clear all messages from mailbox."""
        email = self.user_sessions.get(chat_id, {}).get("email")
        if not email:
            self.send_message(chat_id, "⚠️ No active Gmail found.", self.get_main_keyboard())
            return

        try:
            self.client.clear_inbox(email)
            text = f"🗑 <b>Inbox cleared successfully</b> for <code>{email}</code>."
            if message_id:
                self.edit_message(chat_id, message_id, text, self.get_main_keyboard())
            else:
                self.send_message(chat_id, text, self.get_main_keyboard())
        except Exception as e:
            self.send_message(chat_id, f"❌ Failed to clear inbox: {e}", self.get_main_keyboard())

    def start_polling(self):
        """Long-polling main loop."""
        print(f"[*] Starting Telegram Bot polling (token ending with ...{self.token[-6:]})...")

        # Verify bot identity
        me = self.api_call("getMe")
        if not me.get("ok"):
            print(f"[TG Error] Invalid Bot Token or Telegram API unreachable: {me}")
            return
        bot_user = me["result"].get("username", "UnknownBot")
        print(f"[TG Success] Connected as @{bot_user}")

        while True:
            try:
                updates = self.api_call("getUpdates", {"offset": self.offset, "timeout": 25})
                if updates.get("ok"):
                    for u in updates.get("result", []):
                        self.offset = u["update_id"] + 1

                        # 1. Message event
                        if "message" in u:
                            msg = u["message"]
                            chat_id = msg.get("chat", {}).get("id")
                            text = msg.get("text", "").strip()

                            if not chat_id:
                                continue

                            if text.startswith("/start") or text.startswith("/help"):
                                self.handle_start(chat_id)
                            elif text.startswith("/new"):
                                self.handle_new_email(chat_id)
                            elif text.startswith("/inbox"):
                                self.handle_check_inbox(chat_id)
                            elif text.startswith("/otp") or text.startswith("/code"):
                                self.handle_auto_otp(chat_id)
                            elif text.startswith("/clear"):
                                self.handle_clear_inbox(chat_id)
                            else:
                                self.handle_start(chat_id)

                        # 2. Callback Query event
                        elif "callback_query" in u:
                            cq = u["callback_query"]
                            cq_id = cq["id"]
                            chat_id = cq["message"]["chat"]["id"]
                            message_id = cq["message"]["message_id"]
                            data = cq.get("data", "")

                            self.answer_callback_query(cq_id)

                            if data == "btn_new":
                                self.handle_new_email(chat_id, message_id, exclude_current=False)
                            elif data == "btn_change":
                                self.handle_new_email(chat_id, message_id, exclude_current=True)
                            elif data == "btn_inbox":
                                self.handle_check_inbox(chat_id, message_id)
                            elif data == "btn_otp":
                                self.handle_auto_otp(chat_id)
                            elif data == "btn_clear":
                                self.handle_clear_inbox(chat_id, message_id)

            except Exception as e:
                print(f"[TG Loop Error] {e}")
                time.sleep(3)


if __name__ == "__main__":
    if not config.TELEGRAM_BOT_TOKEN:
        print("[!] Error: TELEGRAM_BOT_TOKEN is not configured in config.py or environment variables.")
        print("Please edit config.py or export TELEGRAM_BOT_TOKEN='your_token'")
    else:
        bot = TelegramBot(config.TELEGRAM_BOT_TOKEN)
        bot.start_polling()
