#!/usr/bin/env python3
"""
Aviso.bz Autonomous YouTube Task Runner
Engineered for Termux / Linux with curl_cffi Chrome 120 TLS Impersonation.
Automates YouTube viewing tasks safely with natural human jitter.
"""

import os
import sys
import json
import time
import random
import re
import argparse
from bs4 import BeautifulSoup
from curl_cffi import requests

# ANSI Colors
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
MAGENTA = "\033[1;35m"
BOLD = "\033[1m"
RESET = "\033[0m"

COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aviso_cookies.json")

class AvisoBot:
    def __init__(self, cookie_path=COOKIE_FILE):
        self.cookie_path = cookie_path
        self.cookies = self.load_cookies()
        self.base_url = "https://aviso.bz"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://aviso.bz/tasks-youtube",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.session_earnings = 0.0
        self.completed_tasks = 0

    def load_cookies(self):
        if not os.path.exists(self.cookie_path):
            print(f"{RED}[Error]{RESET} Cookie file not found: {self.cookie_path}")
            sys.exit(1)
        with open(self.cookie_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        cookies["show_instruction_view"] = "1"
        return cookies

    def get_dashboard_info(self):
        """Fetch username, status and balance."""
        try:
            r = requests.get(
                f"{self.base_url}/tasks-youtube",
                cookies=self.cookies,
                headers=self.headers,
                impersonate="chrome120",
                timeout=15
            )
            if r.status_code != 200 or "login" in r.url:
                return None, None, None, None

            soup = BeautifulSoup(r.text, "html.parser")
            username_elem = soup.find(id="user-block-info-username")
            balance_elem = soup.find(id="new-money-ballans")
            
            # Extract SID
            sid_match = re.search(r'var sid\s*=\s*[\'"]([^\'"]+)[\'"]', r.text)
            sid = sid_match.group(1) if sid_match else None

            username = username_elem.get_text(strip=True) if username_elem else "sybervault"
            balance = balance_elem.get_text(strip=True) if balance_elem else "0 руб."
            return username, balance, sid, r.text
        except Exception as e:
            print(f"{RED}[Error]{RESET} Dashboard fetch failed: {e}")
            return None, None, None, None

    def execute_single_task(self, task_id, sid):
        """Execute a single YouTube task."""
        tab_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=25))
        view_url = f"{self.base_url}/go/create-task-view.php?id={task_id}&tabId={tab_id}&yt_checked=1"

        try:
            vr = requests.get(
                view_url,
                cookies=self.cookies,
                headers=self.headers,
                impersonate="chrome120",
                timeout=15
            )
        except Exception as e:
            print(f"{RED}[!] Request failed for task {task_id}: {e}{RESET}")
            return False

        # Check for hCaptcha
        if "Для продолжения подтвердите" in vr.text or "hcaptcha" in vr.text:
            print(f"{YELLOW}[⚠️ CAPTCHA DETECTED]{RESET} Aviso requires 1 manual browser verification.")
            return "CAPTCHA"

        # Extract parameters
        report_match = re.search(r'reportId:\s*[\'"]([^\'"]+)[\'"]', vr.text)
        hash_match = re.search(r'hash:\s*[\'"]([^\'"]+)[\'"]', vr.text)
        video_match = re.search(r'videoId:\s*[\'"]([^\'"]+)[\'"]', vr.text)
        timer_match = re.search(r'timer:\s*[\'"]([^\'"]+)[\'"]', vr.text)

        if not (report_match and hash_match and video_match and timer_match):
            print(f"{YELLOW}[-] Task {task_id} not available or already expired.{RESET}")
            return False

        report_id = report_match.group(1)
        hash_val = hash_match.group(1)
        video_id = video_match.group(1)
        timer = int(timer_match.group(1))

        # Human-like watch simulation
        jitter = round(random.uniform(1.2, 2.5), 2)
        total_wait = timer + jitter
        print(f"    {CYAN}▶ Watching Video:{RESET} {video_id} | {timer}s + {jitter}s jitter | Task #{task_id}")

        for sec in range(int(total_wait), 0, -1):
            sys.stdout.write(f"\r    ⏳ Simulating playback... {sec}s remaining   ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write(f"\r    ⏳ Simulating playback... Complete!           \n")
        sys.stdout.flush()

        # Send reward confirmation
        ajax_headers = self.headers.copy()
        ajax_headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })

        confirm_data = {
            "hash": hash_val,
            "sid": sid,
            "task_id": task_id,
            "report_id": report_id,
            "video_id": video_id,
            "timer": str(timer)
        }

        try:
            cr = requests.post(
                f"{self.base_url}/ajax/earnings/ajax-youtube-external.php",
                data=confirm_data,
                cookies=self.cookies,
                headers=ajax_headers,
                impersonate="chrome120",
                timeout=15
            )
            res = cr.json()
            if not res.get("error"):
                # Extract reward amount
                html_resp = res.get("html", "")
                reward_match = re.search(r'<b>([0-9\.]+)</b>', html_resp)
                reward = reward_match.group(1) if reward_match else "0.026"
                self.session_earnings += float(reward)
                self.completed_tasks += 1
                print(f"    {GREEN}✓ Reward Claimed:{RESET} +{reward} RUB | Total Earned: {self.session_earnings:.3f} RUB")
                return True
            else:
                print(f"    {RED}✗ Confirm rejected:{RESET} {res.get('html')}")
                return False
        except Exception as e:
            print(f"    {RED}✗ Confirmation error:{RESET} {e}")
            return False

    def run(self, max_tasks=None, continuous=False, cool_off=300):
        print(f"\n{BOLD}{CYAN}═════════════════════════════════════════════════════════{RESET}")
        print(f"{BOLD}{GREEN}           AVISO.BZ YOUTUBE AUTO-RUNNER v2.0            {RESET}")
        print(f"{BOLD}{CYAN}═════════════════════════════════════════════════════════{RESET}")

        username, balance, sid, html = self.get_dashboard_info()
        if not sid:
            print(f"{RED}[!] Session expired or blocked. Please refresh cookies.{RESET}")
            return

        print(f"{BOLD}User:{RESET} {username}  |  {BOLD}Balance:{RESET} {balance}")
        print(f"{CYAN}---------------------------------------------------------{RESET}")

        while True:
            # Parse available tasks
            soup = BeautifulSoup(html, "html.parser")
            tables = soup.find_all("table", id=lambda x: x and x.startswith("ads-link-"))
            task_ids = [t["id"].replace("ads-link-", "") for t in tables]
            print(f"{YELLOW}[i] Available YouTube tasks:{RESET} {len(task_ids)}")

            if not task_ids:
                print(f"{YELLOW}[i] No tasks currently available.{RESET}")
                if continuous:
                    print(f"Sleeping {cool_off}s before checking for new tasks...")
                    time.sleep(cool_off)
                    username, balance, sid, html = self.get_dashboard_info()
                    continue
                else:
                    break

            tasks_to_run = task_ids[:max_tasks] if max_tasks else task_ids

            for idx, task_id in enumerate(tasks_to_run, 1):
                print(f"\n[{idx}/{len(tasks_to_run)}] Processing Task ID: {BOLD}{task_id}{RESET}")
                status = self.execute_single_task(task_id, sid)

                if status == "CAPTCHA":
                    print(f"\n{RED}[PAUSED] Complete the verification on Aviso and re-run.{RESET}")
                    return

                # Human-like delay between tasks
                sleep_delay = round(random.uniform(3.0, 5.5), 1)
                time.sleep(sleep_delay)

            # Re-fetch balance
            username, balance, sid, html = self.get_dashboard_info()
            print(f"\n{BOLD}{GREEN}Batch Complete!{RESET} Updated Balance: {BOLD}{balance}{RESET} | Tasks: {self.completed_tasks}")

            if not continuous:
                break
            print(f"\nSleeping {cool_off}s until next check cycle...")
            time.sleep(cool_off)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aviso.bz YouTube Automation Bot")
    parser.add_argument("-n", "--limit", type=int, default=None, help="Maximum number of tasks to complete")
    parser.add_argument("-c", "--continuous", action="store_true", help="Run continuously in background loops")
    parser.add_argument("-s", "--sleep", type=int, default=300, help="Sleep duration in seconds between continuous cycles")
    args = parser.parse_args()

    bot = AvisoBot()
    try:
        bot.run(max_tasks=args.limit, continuous=args.continuous, cool_off=args.sleep)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Bot stopped by user. Total tasks: {bot.completed_tasks} | Total Earned: {bot.session_earnings:.3f} RUB{RESET}")
