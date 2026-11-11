#!/usr/bin/env python3
"""
Master Earning Daemon - STRICT ZERO PENDING EDITION
Only runs 100% Instant Cash engines (Zero Pending Review, Instant Credit to Wallet).

Active Instant Engines:
1. RewardJoy (CoinPayU) - Dollar / Satoshi Instant Surf Ads
2. Socpublic Instant Visits - Direct Rubles, 0-sec review
3. Aviso YouTube Auto-Player - Direct Rubles, 0-sec review

Author: Antigravity Cortex System
"""

import os
import sys
import time
import subprocess
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def run_script(script_name, timeout=180):
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        return
    log(f"[*] Starting instant cash engine: {script_name}...")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in proc.stdout:
            clean = line.strip()
            if clean:
                print(f"[{script_name}] {clean}", flush=True)
        proc.wait(timeout=timeout)
        log(f"[+] Engine {script_name} completed.")
    except subprocess.TimeoutExpired:
        proc.kill()
        log(f"[-] Engine {script_name} timed out after {timeout}s.")
    except Exception as e:
        log(f"[-] Engine {script_name} error: {e}")

def main():
    log("==================================================")
    log("⚡ Master Daemon (STRICT ZERO-PENDING INSTANT ENGINE)")
    log("🎯 Mode: 100% Instant Cash Only (Zero Pending Review)")
    log("==================================================")
    
    cycle = 1
    while True:
        log(f"\n=================== ZERO-PENDING CYCLE #{cycle} ===================")
        
        # 1. RewardJoy / CoinPayU Instant Dollar/Satoshi Surf Ads
        if os.path.exists(os.path.join(BASE_DIR, "rewardjoy_bot.py")):
            run_script("rewardjoy_bot.py", timeout=300)
            time.sleep(random.uniform(2, 4))
            
        # 2. Socpublic Instant Visits (Direct balance credit)
        if os.path.exists(os.path.join(BASE_DIR, "socpublic_visits_bot.py")):
            run_script("socpublic_visits_bot.py", timeout=90)
            time.sleep(random.uniform(2, 4))

        # 3. Aviso YouTube Auto-Player (Direct balance credit, if session active)
        if os.path.exists(os.path.join(BASE_DIR, "aviso_bot.py")):
            run_script("aviso_bot.py", timeout=120)
            time.sleep(random.uniform(2, 4))
            
        log(f"[+] Zero-Pending Cycle #{cycle} completed.")
        cycle += 1
        
        # Fast cycle interval (90 to 120 seconds) to catch newly published ads instantly
        sleep_sec = random.randint(90, 120)
        log(f"[*] Polling interval: sleeping {sleep_sec}s until next instant cash sweep...")
        time.sleep(sleep_sec)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Master Instant Daemon stopped.")
