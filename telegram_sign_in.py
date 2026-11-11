#!/usr/bin/env python3
import sys
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
PHONE = "+8801608426997"
SESSION_PATH = "/root/scripted/telegram_worker"

async def main(code, password=None):
    with open("/root/scripted/tg_auth_state.txt", "r") as f:
        phone_code_hash = f.read().strip()

    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
    await client.connect()
    
    try:
        await client.sign_in(PHONE, code=code, phone_code_hash=phone_code_hash)
        me = await client.get_me()
        print(f"SUCCESS_LOGIN: Name: {me.first_name} | Username: @{me.username} | ID: {me.id}")
        # Save username
        with open("/root/scripted/tg_username.txt", "w") as f:
            f.write(me.username or str(me.id))
    except SessionPasswordNeededError:
        if password:
            await client.sign_in(password=password)
            me = await client.get_me()
            print(f"SUCCESS_LOGIN_2FA: Name: {me.first_name} | Username: @{me.username} | ID: {me.id}")
            with open("/root/scripted/tg_username.txt", "w") as f:
                f.write(me.username or str(me.id))
        else:
            print("NEED_2FA_PASSWORD")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 telegram_sign_in.py <code> [2fa_password]")
        sys.exit(1)
    code = sys.argv[1]
    pwd = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(main(code, pwd))
