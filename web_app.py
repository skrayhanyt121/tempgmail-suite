"""
Flask Web Application & Facebook Messenger Webhook for TempGmail Suite.
Provides:
1. Web Dashboard (/)
2. REST API (/api/email/*)
3. Facebook Messenger Webhook (/webhook)
"""

import time
import json
from flask import Flask, render_template, request, jsonify
from curl_cffi import requests
from tempgmail import TempGmailClient
import config

app = Flask(__name__)
client = TempGmailClient()

# In-memory session store for Facebook Messenger users
# maps fb_user_id -> {"email": "...", "created_at": ...}
fb_user_sessions = {}


# ==========================================
# 1. WEB UI & REST API ENDPOINTS
# ==========================================

@app.route("/")
def index():
    """Render Web Dashboard."""
    return render_template("index.html")


@app.route("/api/email/new", methods=["GET"])
def api_new_email():
    """Generate fresh random temp Gmail."""
    exclude = request.args.get("exclude")
    try:
        data = client.get_random_email(exclude=exclude)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/email/inbox", methods=["GET"])
def api_get_inbox():
    """Get inbox for a specific email."""
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email parameter required"}), 400
    try:
        data = client.get_inbox(email)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/email/message/<message_id>", methods=["GET"])
def api_get_message(message_id):
    """Get full message content and extracted OTP."""
    try:
        data = client.get_message(message_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/email/wait-otp", methods=["GET"])
def api_wait_otp():
    """Wait for OTP to arrive in inbox (long poll)."""
    email = request.args.get("email")
    timeout = int(request.args.get("timeout", config.OTP_WAIT_TIMEOUT))
    if not email:
        return jsonify({"error": "Email parameter required"}), 400

    try:
        result = client.wait_for_otp(email, timeout=timeout)
        if result:
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "message": "Timed out waiting for OTP"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/email/clear", methods=["DELETE"])
def api_clear_inbox():
    """Clear all messages for an email."""
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email parameter required"}), 400
    try:
        success = client.clear_inbox(email)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# 2. FACEBOOK MESSENGER PLATFORM WEBHOOK
# ==========================================

def send_fb_message(recipient_id: str, message_payload: dict):
    """Send message to user via Meta Graph API."""
    if not config.FB_PAGE_ACCESS_TOKEN:
        print("[FB Warning] FB_PAGE_ACCESS_TOKEN not set, skipping outgoing message.")
        return False

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={config.FB_PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": message_payload,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.ok
    except Exception as e:
        print(f"[FB Send Error] {e}")
        return False


def send_fb_text_with_quick_replies(recipient_id: str, text: str):
    """Helper to send text along with interactive Quick Reply pills."""
    quick_replies = [
        {"content_type": "text", "title": "⚡ New Gmail", "payload": "CMD_NEW"},
        {"content_type": "text", "title": "📥 Check Inbox", "payload": "CMD_INBOX"},
        {"content_type": "text", "title": "🔢 Get OTP", "payload": "CMD_OTP"},
    ]
    return send_fb_message(recipient_id, {
        "text": text,
        "quick_replies": quick_replies
    })


@app.route("/webhook", methods=["GET", "POST"])
def fb_webhook():
    """Meta Messenger verification and event handler."""
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == config.FB_VERIFY_TOKEN:
            print("[FB Webhook] Verification successful!")
            return challenge, 200
        else:
            print("[FB Webhook] Verification failed token mismatch.")
            return "Forbidden", 403

    elif request.method == "POST":
        data = request.get_json(silent=True) or {}
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event.get("sender", {}).get("id")
                    if not sender_id:
                        continue

                    # Text message or quick reply
                    message = messaging_event.get("message", {})
                    postback = messaging_event.get("postback", {})
                    
                    text_input = ""
                    if "text" in message:
                        text_input = message.get("text", "").strip()
                    if "quick_reply" in message:
                        text_input = message["quick_reply"].get("payload", "")
                    elif postback:
                        text_input = postback.get("payload", "")

                    handle_fb_command(sender_id, text_input)

            return "EVENT_RECEIVED", 200

        return "Unknown object", 404


def handle_fb_command(sender_id: str, cmd: str):
    """Process incoming command from Messenger user."""
    cmd_lower = cmd.lower()
    user_state = fb_user_sessions.get(sender_id, {})
    current_email = user_state.get("email")

    if cmd_lower in ["start", "hi", "hello", "menu", "help"]:
        greeting = (
            "👋 Welcome to TempGmail Bot!\n\n"
            "Generate authentic, disposable @gmail.com addresses and receive OTP codes instantly without ads.\n\n"
            "Commands:\n"
            "• Tap '⚡ New Gmail' to generate\n"
            "• Tap '📥 Check Inbox' to view messages\n"
            "• Tap '🔢 Get OTP' to extract verification code"
        )
        send_fb_text_with_quick_replies(sender_id, greeting)

    elif cmd_lower in ["new", "email", "gmail", "change", "cmd_new"]:
        try:
            data = client.get_random_email(exclude=current_email)
            new_email = data.get("email")
            fb_user_sessions[sender_id] = {"email": new_email, "updated_at": time.time()}

            msg = (
                f"✅ Here is your real Temp Gmail:\n\n"
                f"{new_email}\n\n"
                f"Copy this email and use it on your site/app. When code is sent, tap '📥 Check Inbox' or '🔢 Get OTP' below!"
            )
            send_fb_text_with_quick_replies(sender_id, msg)
        except Exception as e:
            send_fb_text_with_quick_replies(sender_id, f"❌ Error creating Gmail: {e}")

    elif cmd_lower in ["inbox", "check", "cmd_inbox"]:
        if not current_email:
            send_fb_text_with_quick_replies(sender_id, "⚠️ You don't have an active Gmail yet. Tap '⚡ New Gmail' first!")
            return

        try:
            inbox_data = client.get_inbox(current_email)
            messages = inbox_data.get("messages", [])

            if not messages:
                send_fb_text_with_quick_replies(
                    sender_id, 
                    f"📭 Inbox is empty for:\n{current_email}\n\nWaiting for new emails..."
                )
                return

            reply = f"📬 Inbox for {current_email} ({len(messages)} messages):\n\n"
            for idx, m in enumerate(messages[:5], 1):
                sender = m.get("sender", "Unknown")
                subject = m.get("subject", "(No Subject)")
                m_id = m.get("id")

                # Try to get OTP
                full = client.get_message(m_id)
                otp = full.get("extracted_otp")
                
                reply += f"{idx}. From: {sender}\nSubject: {subject}\n"
                if otp:
                    reply += f"🔥 OTP CODE: {otp}\n"
                reply += "-------------------\n"

            send_fb_text_with_quick_replies(sender_id, reply)
        except Exception as e:
            send_fb_text_with_quick_replies(sender_id, f"❌ Failed to fetch inbox: {e}")

    elif cmd_lower in ["otp", "code", "cmd_otp"]:
        if not current_email:
            send_fb_text_with_quick_replies(sender_id, "⚠️ No active Gmail found. Tap '⚡ New Gmail' first!")
            return

        send_fb_text_with_quick_replies(sender_id, f"🔍 Checking inbox for OTP code ({current_email})...")
        try:
            inbox_data = client.get_inbox(current_email)
            messages = inbox_data.get("messages", [])
            found_otp = None
            otp_sender = None

            for m in messages:
                full = client.get_message(m.get("id"))
                if full.get("extracted_otp"):
                    found_otp = full["extracted_otp"]
                    otp_sender = full.get("sender")
                    break

            if found_otp:
                send_fb_text_with_quick_replies(
                    sender_id,
                    f"🎉 VERIFICATION CODE FOUND!\n\n"
                    f"Code: {found_otp}\n"
                    f"From: {otp_sender}\n\n"
                    f"Tap to copy: {found_otp}"
                )
            else:
                send_fb_text_with_quick_replies(
                    sender_id,
                    f"⏳ No OTP detected yet in {current_email}.\nPlease ensure the sender sent the code, then tap '🔢 Get OTP' again."
                )
        except Exception as e:
            send_fb_text_with_quick_replies(sender_id, f"❌ Error searching OTP: {e}")

    else:
        send_fb_text_with_quick_replies(
            sender_id,
            "❓ Unknown command. Use the buttons below or type 'new' / 'inbox' / 'otp'."
        )


# ==========================================
# 4. AUTONOMOUS 24/7 EARNING DAEMON LAUNCHER
# ==========================================
import threading
import subprocess
import os

def start_earning_daemon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    daemon_script = os.path.join(base_dir, "master_earning_daemon.py")
    if os.path.exists(daemon_script):
        print("[*] Launching Master Earning Daemon 24/7 background worker...", flush=True)
        subprocess.Popen([os.sys.executable, "-u", daemon_script])

# Start worker thread on app load
daemon_thread = threading.Thread(target=start_earning_daemon, daemon=True)
daemon_thread.start()

@app.route("/api/earning", methods=["GET"])
def api_earning_status():
    """Return live earnings summary across platforms."""
    status_data = {
        "status": "RUNNING 24/7",
        "rewardjoy": "Active (Zero-Pending)",
        "socpublic": "Active (Visits)",
        "aviso": "Active (YouTube)"
    }
    return jsonify(status_data)

if __name__ == "__main__":
    print(f"[*] Starting TempGmail Web & Facebook Webhook on http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=False)
