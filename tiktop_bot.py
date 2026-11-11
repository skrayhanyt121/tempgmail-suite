#!/usr/bin/env python3
"""
TikTop-Free.com Autonomous Task & Account Automation Bot
Engineered for Termux / Linux with curl_cffi TLS impersonation.
Author: Antigravity Cortex Engine
"""

import os
import sys
import json
import time
import random
import argparse
from bs4 import BeautifulSoup
from curl_cffi import requests

# ANSI Styling
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
BOLD = "\033[1m"
RESET = "\033[0m"

COOKIE_FILE = "/root/scripted/tiktop_cookies.json"
BASE_URL = "https://tiktop-free.com"

class TikTopClient:
    def __init__(self, cookie_file=COOKIE_FILE):
        self.cookie_file = cookie_file
        self.session = requests.Session(impersonate="chrome120")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": f"{BASE_URL}/en/tasks/",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.load_cookies()

    def load_cookies(self):
        if not os.path.exists(self.cookie_file):
            print(f"{RED}[!] Cookie file not found: {self.cookie_file}{RESET}")
            sys.exit(1)
        with open(self.cookie_file, "r") as f:
            cookies = json.load(f)
        for c in cookies:
            self.session.cookies.set(c["name"], c["value"], domain="tiktop-free.com")

    def get_status(self):
        """Fetches user status, balance, and account state"""
        url = f"{BASE_URL}/lightning-action.php?action=tiktopfree_get_tasks_info"
        res = self.session.get(url, headers=self.headers)
        if res.status_code != 200:
            return {"error": f"HTTP {res.status_code}"}
        try:
            return res.json()
        except Exception as e:
            return {"error": str(e), "raw": res.text[:200]}

    def get_task_page_html(self):
        """Fetches the full /en/tasks/ HTML to extract dynamic nonces"""
        res = self.session.get(f"{BASE_URL}/en/tasks/", headers={"User-Agent": self.headers["User-Agent"]})
        return res.text

    def add_tiktok_account(self, tiktok_username):
        """Searches and links a TikTok account to TikTop-Free profile"""
        html = self.get_task_page_html()
        soup = BeautifulSoup(html, "html.parser")
        
        add_form = soup.find("form", id="add_account_form")
        if not add_form:
            return {"status": False, "summary": "Could not find add_account_form in page"}
        
        nonce_input = add_form.find("input", {"name": "UserAddAccount[nonce]"})
        nonce = nonce_input["value"] if nonce_input else ""
        
        print(f"{CYAN}[*] Searching TikTok profile: @{tiktok_username}...{RESET}")
        search_url = f"{BASE_URL}/wp-admin/admin-ajax.php?action=tiktokfree_user_add_account"
        payload = {
            "UserAddAccount[nonce]": nonce,
            "UserAddAccount[network]": "1",
            "UserAddAccount[referrer]": f"{BASE_URL}/en/tasks/",
            "UserAddAccount[username]": tiktok_username
        }
        res = self.session.post(search_url, data=payload, headers=self.headers)
        try:
            data = res.json()
            if not data.get("status"):
                return {"status": False, "summary": data.get("summary", "Account search failed")}
            
            confirm_form_html = data.get("confirm_form", "")
            conf_soup = BeautifulSoup(confirm_form_html, "html.parser")
            acc_id = conf_soup.find("input", {"name": "UserAddAccountConfirm[id]"})["value"]
            conf_nonce = conf_soup.find("input", {"name": "UserAddAccountConfirm[nonce]"})["value"]
            
            print(f"{GREEN}[+] Account found! ID: {acc_id}. Confirming addition...{RESET}")
            confirm_url = f"{BASE_URL}/wp-admin/admin-ajax.php?action=tiktokfree_user_add_account_confirm"
            confirm_payload = {
                "UserAddAccountConfirm[nonce]": conf_nonce,
                "UserAddAccountConfirm[id]": acc_id,
                "UserAddAccountConfirm[is_redirect]": "0",
                "UserAddAccountConfirm[submit]": "submit"
            }
            conf_res = self.session.post(confirm_url, data=confirm_payload, headers=self.headers)
            return conf_res.json()
        except Exception as e:
            return {"status": False, "summary": f"Parse error: {e}, raw: {res.text[:200]}"}

    def parse_tasks(self, html_content):
        """Parses active tasks from tasks info HTML"""
        soup = BeautifulSoup(html_content, "html.parser")
        tasks = []
        task_forms = soup.find_all("form", attrs={"name": "UserPerformTask"})
        for f in task_forms:
            tid_elem = f.find("input", attrs={"name": "UserPerformTask[id]"})
            exec_elem = f.find("input", attrs={"name": "UserPerformTask[task_execution_id]"})
            nonce_elem = f.find("input", attrs={"name": "UserPerformTask[nonce]"})
            
            tid = tid_elem.get("value") if tid_elem else None
            exec_id = exec_elem.get("value") if exec_elem else None
            nonce = nonce_elem.get("value") if nonce_elem else None
            
            title_elem = f.find(class_=lambda x: x and "task-item--title" in x)
            title = title_elem.text.strip() if title_elem else "Task"
            
            # Action button
            complete_btn = f.find("a", class_=lambda x: x and "btn--complete" in x)
            link = complete_btn.get("href") if complete_btn else None
            
            # Type (Like / Follow)
            task_type = "1" if "like" in title.lower() else "2"
            
            if tid:
                tasks.append({
                    "id": tid,
                    "execution_id": exec_id,
                    "nonce": nonce,
                    "title": title,
                    "type": task_type,
                    "target_url": link
                })
        return tasks

    def perform_task(self, task):
        """Submits task check to claim coins"""
        url = f"{BASE_URL}/lightning-action.php?action=tiktokfree_user_perform_task"
        payload = {
            "UserPerformTask[id]": str(task["id"]),
            "UserPerformTask[task_execution_id]": str(task["execution_id"]),
            "UserPerformTask[nonce]": str(task["nonce"]),
            "UserPerformTask[submit]": "check"
        }
        res = self.session.post(url, data=payload, headers=self.headers)
        try:
            return res.json()
        except Exception as e:
            return {"status": False, "summary": str(e)}

    def skip_task(self, task):
        """Skips / hides task if uncompletable"""
        url = f"{BASE_URL}/lightning-action.php?action=tiktokfree_user_perform_task"
        payload = {
            "UserPerformTask[id]": str(task["id"]),
            "UserPerformTask[task_execution_id]": str(task["execution_id"]),
            "UserPerformTask[nonce]": str(task["nonce"]),
            "UserPerformTask[submit]": "hide"
        }
        res = self.session.post(url, data=payload, headers=self.headers)
        try:
            return res.json()
        except Exception as e:
            return {"status": False, "summary": str(e)}


def main():
    parser = argparse.ArgumentParser(description="TikTop-Free.com Automation Bot")
    parser.add_argument("command", choices=["status", "add-account", "tasks", "run"], help="Action to perform")
    parser.add_argument("--account", "-a", type=str, help="TikTok username to link")
    args = parser.parse_args()

    client = TikTopClient()

    if args.command == "status":
        print(f"{CYAN}{BOLD}=== TikTop-Free Account Status ==={RESET}")
        st = client.get_status()
        if "error" in st:
            print(f"{RED}[!] Error: {st['error']}{RESET}")
            return
        
        print(f"Username : {GREEN}{st.get('username')}{RESET}")
        print(f"Balance  : {YELLOW}{st.get('balance')} coins{RESET}")
        
        html = st.get("html", "")
        soup = BeautifulSoup(html, "html.parser")
        active_acc = soup.find(class_=lambda x: x and "executor--username" in x)
        if active_acc:
            print(f"Active TikTok : {GREEN}{active_acc.text.strip()}{RESET}")
        else:
            print(f"{YELLOW}[!] No TikTok account active yet.{RESET}")
        
        tasks = client.parse_tasks(html)
        print(f"Active Tasks  : {BOLD}{len(tasks)}{RESET}")

    elif args.command == "add-account":
        if not args.account:
            print(f"{RED}[!] Please specify TikTok username: -a <username>{RESET}")
            return
        res = client.add_tiktok_account(args.account)
        print(f"Result: {res.get('summary', res)}")

    elif args.command == "tasks":
        st = client.get_status()
        html = st.get("html", "")
        tasks = client.parse_tasks(html)
        print(f"{CYAN}[*] Available tasks: {len(tasks)}{RESET}")
        for t in tasks:
            print(f" - #{t['id']} | {t['title']} | URL: {t['target_url']}")

    elif args.command == "run":
        st = client.get_status()
        html = st.get("html", "")
        tasks = client.parse_tasks(html)
        if not tasks:
            print(f"{YELLOW}[!] No tasks available right now.{RESET}")
            return
        
        print(f"{GREEN}[*] Found {len(tasks)} tasks. Starting execution...{RESET}")
        for t in tasks:
            print(f"\n{CYAN}[*] Processing Task #{t['id']}: {t['title']}{RESET}")
            print(f"    Target URL: {t['target_url']}")
            print(f"{YELLOW}    Checking task completion with TikTokFree server...{RESET}")
            time.sleep(random.uniform(2.0, 3.5))
            res = client.perform_task(t)
            status = res.get("status")
            if status:
                print(f"{GREEN}    [SUCCESS] {res.get('summary', 'Task completed!')}{RESET}")
                if "balance" in res:
                    print(f"    New Balance: {YELLOW}{res['balance']} coins{RESET}")
            else:
                print(f"{RED}    [FAILED] {res.get('summary', 'Not verified on TikTok')}{RESET}")

if __name__ == "__main__":
    main()
