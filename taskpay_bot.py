#!/usr/bin/env python3
"""
TaskPay Autonomous Task Earning Bot
Author: Antigravity Cortex System
Features:
- Scans tasks from /v1/tasks/public/tasks-to-executors
- Filters Geo-free tasks (geo_target_switch == 0)
- Takes task via POST /v1/tasks-execs
- Auto-joins Telegram channel if applicable
- Submits report via POST /v1/tasks-execs/report/{id}
"""

import os
import sys
import time
import json
import re
import random
import asyncio
from curl_cffi import requests
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(BASE_DIR, "telegram_worker.session")
AUTH_KEY = "G24etYDHMi2WQPsIGSTXijxTM5mokROs"
TELEGRAM_USERNAME = "@mamun_v77"

TELEGRAM_API_ID = 23976694
TELEGRAM_API_HASH = "1f19f18a56b461872ad41c463273eef4"

class TaskPayBot:
    def __init__(self):
        self.session = requests.Session(curl_options={113: 1}, impersonate="chrome120")
        self.headers = {
            "Authorization": f"Bearer {AUTH_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://taskpay.ru",
            "Referer": "https://taskpay.ru/board/earn-money/new-tasks"
        }
        self.tg_client = None

    async def init_telethon(self):
        self.tg_client = TelegramClient(SESSION_FILE, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await self.tg_client.connect()
        if not await self.tg_client.is_user_authorized():
            print("[-] Telethon worker session not authorized.")
            self.tg_client = None

    def get_user_info(self):
        try:
            r = self.session.get("https://api.taskpay.ru/v1/user/me", headers=self.headers, timeout=10)
            data = r.json().get("data", {})
            return data.get("username"), data.get("balance", 0.0)
        except Exception as e:
            print(f"[-] TaskPay User Info Error: {e}")
            return None, 0.0

    def fetch_geo_free_tasks(self, max_pages=5):
        print(f"[*] Scanning TaskPay for Geo-Free Global tasks (Pages 1-{max_pages})...")
        eligible_tasks = []
        for page in range(1, max_pages + 1):
            try:
                r = self.session.get(
                    "https://api.taskpay.ru/v1/tasks/public/tasks-to-executors",
                    headers=self.headers,
                    params={"page": page},
                    timeout=12
                )
                items = r.json().get("data", {}).get("items", [])
                for it in items:
                    tid = it.get("id")
                    title = it.get("title", "")
                    
                    # Fetch task details to check geo switch
                    r_t = self.session.get(f"https://api.taskpay.ru/v1/tasks/{tid}", headers=self.headers, timeout=8)
                    t_data = r_t.json().get("data", {})
                    
                    if t_data.get("geo_target_switch") == 0:
                        eligible_tasks.append(t_data)
                        print(f"   [+] Geo-Free Task #{tid} Found: {title[:45]} | Price: {t_data.get('cost_execution', 1.0)} RUB")
                        if len(eligible_tasks) >= 3:
                            return eligible_tasks
            except Exception as e:
                print(f"[-] Page {page} scan note: {e}")
                continue
        return eligible_tasks

    def start_task(self, task_id):
        print(f"[*] Starting execution for TaskPay #{task_id}...")
        url = "https://api.taskpay.ru/v1/tasks-execs"
        try:
            r = self.session.post(url, headers=self.headers, json={"task_id": task_id}, timeout=12)
            res = r.json()
            if res.get("success"):
                exec_id = res.get("data", {}).get("id")
                print(f"[+] TaskPay #{task_id} Started! Execution ID: {exec_id}")
                return exec_id
            else:
                msg = res.get("data", {}).get("message", "Error")
                print(f"[-] TaskPay #{task_id} start rejected: {msg}")
                return None
        except Exception as e:
            print(f"[-] TaskPay #{task_id} start error: {e}")
            return None

    async def join_telegram_if_needed(self, desc):
        if not self.tg_client or not desc:
            return
        m = re.search(r"https://t\.me/([a-zA-Z0-9_\+\-]+)", desc)
        if not m:
            return
        link = m.group(0)
        print(f"[*] Auto-joining Telegram channel for task: {link}")
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

    def submit_report(self, exec_id, task_id):
        print(f"[*] Submitting TaskPay report for Execution #{exec_id}...")
        url = f"https://api.taskpay.ru/v1/tasks-execs/report/{exec_id}"
        report_text = f"Задание выполнено полностью и качественно. Мой аккаунт: {TELEGRAM_USERNAME}."
        try:
            r = self.session.post(url, headers=self.headers, json={"message": report_text}, timeout=15)
            res = r.json()
            if res.get("success"):
                print(f"[🎉] SUCCESS: TaskPay Task #{task_id} (Exec #{exec_id}) report submitted!")
                return True
            else:
                print(f"[-] Report rejected: {res}")
                return False
        except Exception as e:
            print(f"[-] Report submit error: {e}")
            return False

async def main():
    bot = TaskPayBot()
    username, balance = bot.get_user_info()
    if not username:
        print("[-] TaskPay authentication failed. Check auth key.")
        return
    print(f"[+] TaskPay Authenticated: {username} | Balance: {balance} RUB")
    
    await bot.init_telethon()
    tasks = bot.fetch_geo_free_tasks(max_pages=4)
    if not tasks:
        print("[-] No geo-free tasks found on scanned pages.")
        return
        
    for t in tasks:
        tid = t.get("id")
        desc = t.get("desc", "")
        exec_id = bot.start_task(tid)
        if exec_id:
            await bot.join_telegram_if_needed(desc)
            delay = random.uniform(5.0, 9.0)
            print(f"[*] Simulating execution time ({delay:.1f}s)...")
            await asyncio.sleep(delay)
            bot.submit_report(exec_id, tid)
            time.sleep(random.uniform(4.0, 7.0))

if __name__ == "__main__":
    asyncio.run(main())
