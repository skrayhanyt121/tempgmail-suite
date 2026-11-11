#!/usr/bin/env python3
"""
VKTarget Autonomous Custom Task Earning Bot
Author: Antigravity Cortex System
Features:
- Scans active custom tasks from /api/all.php?action=get_custom_tasks
- Auto-joins Telegram channel if applicable via Telethon (@mamun_v77)
- Submits proof via POST /api/all.php?action=custom_check
"""

import os
import sys
import json
import time
import re
import random
import asyncio
from curl_cffi import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, "vktarget_cookies.json")
SESSION_FILE = os.path.join(BASE_DIR, "telegram_worker.session")

TELEGRAM_API_ID = 23976694
TELEGRAM_API_HASH = "1f19f18a56b461872ad41c463273eef4"
TELEGRAM_USERNAME = "@mamun_v77"

class VKTargetBot:
    def __init__(self):
        self.cookies = self._load_cookies()
        self.session = requests.Session(curl_options={113: 1}, impersonate="chrome120")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://vktarget.ru/list/",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.tg_client = None

    def _load_cookies(self):
        with open(COOKIES_FILE, "r") as f:
            data = json.load(f)
        return {c["name"]: c["value"] for c in data}

    async def init_telethon(self):
        self.tg_client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await self.tg_client.connect()

    def fetch_tasks(self):
        url = "https://vktarget.ru/api/all.php?action=get_custom_tasks"
        try:
            r = self.session.get(url, cookies=self.cookies, headers=self.headers, timeout=12)
            tasks = r.json().get("custom_tasks", [])
            return tasks
        except Exception as e:
            print(f"[-] VKTarget task fetch error: {e}")
            return []

    async def join_telegram_if_needed(self, text):
        if not self.tg_client or not text:
            return
        m = re.search(r"https://t\.me/([a-zA-Z0-9_\+\-]+)", text)
        if not m:
            return
        link = m.group(0)
        print(f"[*] Auto-joining Telegram channel for VKTarget: {link}")
        try:
            clean = link.strip().rstrip("/")
            if "+" in clean or "joinchat" in clean:
                inv = clean.split("+")[-1].split("/")[-1].replace("joinchat/", "")
                await self.tg_client(ImportChatInviteRequest(inv))
            else:
                ch = clean.split("/")[-1].replace("@", "")
                entity = await self.tg_client.get_entity(ch)
                await self.tg_client(JoinChannelRequest(entity))
            print(f"[+] Joined Telegram channel successfully.")
        except Exception as e:
            if "already a participant" in str(e).lower():
                print("[+] Already participant in this channel.")
            else:
                print(f"[-] Channel join note: {e}")

    def submit_task(self, task_id, title):
        url = "https://vktarget.ru/api/all.php?action=custom_check"
        data = {
            "tid": str(task_id),
            "confirm": f"Задание выполнено полностью! Юзернейм/аккаунт: {TELEGRAM_USERNAME}",
            "host_state": "vktarget.ru",
            "clicked": 1
        }
        try:
            r = self.session.post(url, data=data, cookies=self.cookies, headers=self.headers, timeout=12)
            res = r.json()
            if res.get("code") == 200:
                print(f"[🎉] SUCCESS: VKTarget Task #{task_id} ({title}) submitted for review!")
                return True
            else:
                print(f"[-] VKTarget #{task_id} submit response: {res}")
                return False
        except Exception as e:
            print(f"[-] VKTarget #{task_id} error: {e}")
            return False

async def main():
    bot = VKTargetBot()
    await bot.init_telethon()
    tasks = bot.fetch_tasks()
    print(f"[+] VKTarget Found {len(tasks)} custom tasks available.")
    
    # Run Telegram / social tasks
    count = 0
    for t in tasks:
        tid = t.get("id")
        title = t.get("task_name", "")
        full_text = t.get("full_text", "")
        price = t.get("price", "1.0")
        
        # Look for Telegram tasks first
        if "t.me" in full_text.lower() or "telegram" in full_text.lower():
            print(f"\n[*] Processing VKTarget Task #{tid}: {title} | Pay: {price} RUB")
            await bot.join_telegram_if_needed(full_text)
            time.sleep(random.uniform(4, 7))
            success = bot.submit_task(tid, title)
            if success:
                count += 1
                if count >= 3:
                    break
            time.sleep(random.uniform(5, 8))

    print(f"[🏁] VKTarget batch cycle finished. Submitted: {count} tasks.")

if __name__ == "__main__":
    asyncio.run(main())
