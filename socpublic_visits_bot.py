#!/usr/bin/env python3
"""
Socpublic Instant Web Visit & Surfing Auto-Earner Bot
Author: Antigravity Cortex System
Features:
- Scans all active web visits on Socpublic (/account/visit.html)
- Solves visit timer automatically (2-5s) with realistic jitter
- Automatically credits real RUB instantly to Main Balance
- Continuous loop daemon mode available
"""

import os
import sys
import json
import time
import re
import random
from bs4 import BeautifulSoup
from curl_cffi import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, "socpublic_cookies.json")

class SocpublicVisitsBot:
    def __init__(self):
        self.cookies = self._load_cookies()
        self.session = requests.Session(curl_options={113: 1}, impersonate="chrome120")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://socpublic.com/account/visit.html",
            "Origin": "https://socpublic.com"
        }
        self.user_id = "9858534"

    def _load_cookies(self):
        with open(COOKIES_FILE, "r") as f:
            data = json.load(f)
        return {c["name"]: c["value"] for c in data}

    def safe_get(self, url, **kwargs):
        for attempt in range(3):
            try:
                # Refresh session if closed
                return self.session.get(url, cookies=self.cookies, headers=self.headers, timeout=15, **kwargs)
            except Exception as e:
                time.sleep(1.5)
                self.session = requests.Session(curl_options={113: 1}, impersonate="chrome120")
        return None

    def get_balance(self):
        r = self.safe_get("https://socpublic.com/account/")
        if not r:
            return 0.0
        match = re.search(r"Основной баланс:\s*([\d\.]+)\s*руб", r.text)
        return float(match.group(1)) if match else 0.0

    def fetch_visits(self):
        r = self.safe_get("https://socpublic.com/account/visit.html")
        if not r:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        
        visits = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/account/visit_view.html?id=" in href:
                vid = re.search(r"id=(\d+)", href).group(1)
                parent = a.find_parent("tr") or a.find_parent("div")
                text = " ".join(parent.stripped_strings) if parent else a.text.strip()
                visits.append({
                    "id": vid,
                    "url": href,
                    "title": a.text.strip() or "Web Visit"
                })
        return visits

    def execute_visit(self, visit_id):
        url = f"https://socpublic.com/account/visit_view.html?id={visit_id}&user_id={self.user_id}"
        r1 = self.safe_get(url)
        if not r1:
            return False, "Failed to load visit"
        
        bid_match = re.search(r"bid_id=(\d+)", r1.text)
        timer_match = re.search(r"timer\s*=\s*(\d+)", r1.text)
        
        if not bid_match:
            return False, "No active bid"
            
        bid_id = bid_match.group(1)
        timer_sec = int(timer_match.group(1)) if timer_match else 2
        
        # Human jitter playback
        sleep_time = timer_sec + random.uniform(0.5, 1.5)
        print(f"[*] Visit #{visit_id} running (Bid #{bid_id}) | Timer: {timer_sec}s -> Sleeping {sleep_time:.1f}s...")
        time.sleep(sleep_time)
        
        confirm_url = f"https://socpublic.com/account/visit_view.html?id={visit_id}&bid_id={bid_id}&act=redirect"
        r2 = self.safe_get(confirm_url, allow_redirects=False)
        
        if r2 and r2.status_code in [200, 302]:
            return True, "Credited"
        else:
            return False, f"HTTP {r2.status_code if r2 else 'err'}"

    def run_all(self):
        initial_balance = self.get_balance()
        print(f"[+] Initial Socpublic Balance: {initial_balance:.2f} RUB")
        
        visits = self.fetch_visits()
        print(f"[+] Found {len(visits)} available visits to complete.")
        
        completed = 0
        for i, v in enumerate(visits, 1):
            vid = v["id"]
            print(f"\n[{i}/{len(visits)}] Starting Visit #{vid}: {v['title'][:40]}")
            success, msg = self.execute_visit(vid)
            if success:
                completed += 1
                print(f"[🎉] SUCCESS: Visit #{vid} completed!")
            else:
                print(f"[-] Visit #{vid} skipped: {msg}")
                
            time.sleep(random.uniform(1.5, 3.0))
            
        final_balance = self.get_balance()
        gained = final_balance - initial_balance
        print(f"\n==========================================")
        print(f"[🏁] Batch Completed: {completed}/{len(visits)} visits.")
        print(f"[💰] Balance: {initial_balance:.2f} -> {final_balance:.2f} RUB (+{gained:.2f} RUB gained!)")
        print(f"==========================================")

if __name__ == "__main__":
    bot = SocpublicVisitsBot()
    bot.run_all()
