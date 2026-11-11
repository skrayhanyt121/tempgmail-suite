#!/usr/bin/env python3
"""
RewardJoy / CoinPayU Autonomous Surf Ads Earning Bot
Reverse-engineered AES encryption protocol + API runner.
Direct Instant Cash (Satoshi / USD). Zero pending review.
Author: Antigravity Cortex System
"""

import os
import sys
import time
import json
import random
import base64
from curl_cffi import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, "rewardjoy_cookies.json")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [RewardJoy] {msg}", flush=True)

def encrypt_setm(data_str, key_str):
    key = key_str.encode("utf-8")
    cipher = AES.new(key, AES.MODE_ECB)
    padded = pad(data_str.encode("utf-8"), AES.block_size, style="pkcs7")
    return base64.b64encode(cipher.encrypt(padded)).decode("utf-8")

def encrypt_str(cointoken, h_str):
    key = cointoken[3:19].encode("utf-8")
    plaintext = (cointoken[6:] + str(h_str)).encode("utf-8")
    cipher = AES.new(key, AES.MODE_ECB)
    padded = pad(plaintext, AES.block_size, style="pkcs7")
    return base64.b64encode(cipher.encrypt(padded)).decode("utf-8")

def encrypt_self(cointoken, data_obj):
    key = cointoken[3:19].encode("utf-8")
    plaintext = json.dumps(data_obj, separators=(",", ":")).encode("utf-8")
    cipher = AES.new(key, AES.MODE_ECB)
    padded = pad(plaintext, AES.block_size, style="pkcs7")
    return base64.b64encode(cipher.encrypt(padded)).decode("utf-8")

class RewardJoyBot:
    def __init__(self):
        self.cointoken = None
        self.session = None
        self.headers = {}
        self.total_earned = 0.0

    def init_session(self):
        if not os.path.exists(COOKIES_PATH):
            log(f"[-] Cookies file missing: {COOKIES_PATH}")
            return False

        with open(COOKIES_PATH, "r") as f:
            cookies = json.load(f)

        self.session = requests.Session(curl_options={113: 1})
        for c in cookies:
            self.session.cookies.set(c["name"], c["value"], domain=".rewardjoy.com")
            self.session.cookies.set(c["name"], c["value"], domain=".ssd.rewardjoy.com")
            self.session.cookies.set(c["name"], c["value"], domain="ssd.rewardjoy.com")
            if c["name"] == "coinPayU-cointoken":
                self.cointoken = c["value"]

        if not self.cointoken:
            log("[-] coinPayU-cointoken not found in cookies!")
            return False

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.rewardjoy.com",
            "Referer": "https://www.rewardjoy.com/dashboard/ads_surf",
            "version": "20260710152612",
            "app-language": "us",
            "cointoken": self.cointoken,
            "cts": str(int(time.time() * 1000)),
        }
        log(f"[+] Session Initialized. CoinToken: {self.cointoken[:10]}...")
        return True

    def get_surf_ads(self):
        url = "https://ssd.rewardjoy.com/ag/viewags?lang=en-us"
        self.headers["cts"] = str(int(time.time() * 1000))
        try:
            r = self.session.post(url, json={"type": 2}, headers=self.headers, impersonate="chrome120", timeout=15)
            if r.status_code != 200:
                log(f"[-] Failed to fetch ads: HTTP {r.status_code}")
                return None, 4

            res = r.json()
            if res.get("code") != 201 and res.get("code") != 200:
                log(f"[-] API error fetching ads: {res}")
                return None, 4

            data = res.get("data", {})
            ads = data.get("ad_list", [])
            captcha_comb = data.get("captcha_combination", 4)
            return ads, captcha_comb
        except Exception as e:
            log(f"[-] Exception fetching ads: {e}")
            return None, 4

    def run_ad(self, ad, captcha_comb):
        ad_id = str(ad.get("id"))
        duration = int(ad.get("duration", 15))
        title = ad.get("description", "Untitled Ad")
        cpc = ad.get("cpc", 0)

        log(f"▶ Starting Ad #{ad_id} | '{title[:40]}' | Duration: {duration}s | Est. Pay: {cpc}")

        # 1. Turn on timer
        self.headers["cts"] = str(int(time.time() * 1000))
        ontimer_url = "https://ssd.rewardjoy.com/ag/ontimer?lang=en-us"
        try:
            r = self.session.post(ontimer_url, json={"adsid": ad_id}, headers=self.headers, impersonate="chrome120", timeout=15)
            res = r.json()
            if res.get("code") != 200:
                log(f"[-] Ontimer failed for Ad #{ad_id}: {res.get('msg')}")
                return False
        except Exception as e:
            log(f"[-] Error calling ontimer: {e}")
            return False

        # 2. Simulate viewing
        start_time = int(time.time() * 1000)
        sleep_duration = duration + random.uniform(1.5, 3.0)
        log(f"⏳ Viewing ad for {sleep_duration:.1f}s...")
        time.sleep(sleep_duration)

        # 3. Encrypt and settle
        recaptcha = {"g": "", "q": "", "h": "", "s": "", "t": ""}
        h_str = str(captcha_comb) + recaptcha["g"] + recaptcha["q"] + recaptcha["h"] + recaptcha["s"] + recaptcha["t"]
        hash_code = encrypt_str(self.cointoken, h_str)
        a_str = self.cointoken + "20260710152612" + ad_id
        x_val = encrypt_setm(a_str, "1234adsjf32348509120012klfew3212")

        click_state = {
            "scrollState": 0,
            "page": "",
            "num": "",
            "allClick": "",
            "button_status": 9,
            "screen": "",
            "position": "",
            "top_distance": "",
            "roll_distance": "",
            "adsNextStartTime": start_time,
            "adsPreviousEndTime": "",
            "cap": 0,
            "adsTime": duration,
            "version": "20260710152612",
            "pwc": ""
        }
        click_state_val = encrypt_self(self.cointoken, click_state)

        settle_payload = {
            "type": 2,
            "adsid": ad_id,
            "status": 0,
            "recaptcha": recaptcha,
            "hash_code": hash_code,
            "captcha_combination": captcha_comb,
            "top": 1,
            "x": x_val,
            "clickState": click_state_val
        }

        self.headers["cts"] = str(int(time.time() * 1000))
        settle_url = "https://ssd.rewardjoy.com/ag/settlement?lang=en-us"
        try:
            r = self.session.post(settle_url, json=settle_payload, headers=self.headers, impersonate="chrome120", timeout=15)
            res = r.json()
            if res.get("code") == 200:
                reward = res.get("data", {}).get("ad_earn", 0)
                self.total_earned += float(reward)
                log(f"✓ Claimed: +{reward} Satoshi | Total Session Earned: {self.total_earned:.2f} Satoshi")
                return True
            else:
                log(f"[-] Settlement failed for Ad #{ad_id}: {res}")
                return False
        except Exception as e:
            log(f"[-] Error settling ad: {e}")
            return False

    def run_batch(self):
        log("==========================================")
        log("🚀 Starting RewardJoy Surf Ads Batch")
        log("==========================================")

        ads, captcha_comb = self.get_surf_ads()
        if not ads:
            log("[!] No ads available or failed to fetch.")
            return

        unclicked = [a for a in ads if a.get("isclick") == 0]
        log(f"[+] Total Ads: {len(ads)} | Unclicked: {len(unclicked)}")

        completed = 0
        for i, ad in enumerate(unclicked, 1):
            log(f"[{i}/{len(unclicked)}] Processing Ad #{ad.get('id')}...")
            success = self.run_ad(ad, captcha_comb)
            if success:
                completed += 1
            # Random delay between ads
            time.sleep(random.uniform(2.5, 5.0))

        log("==========================================")
        log(f"🏁 Batch Finished. Completed: {completed}/{len(unclicked)} ads.")
        log(f"💰 Session Total: {self.total_earned:.2f} Satoshi claimed!")
        log("==========================================")

def main():
    bot = RewardJoyBot()
    if bot.init_session():
        bot.run_batch()

if __name__ == "__main__":
    main()
