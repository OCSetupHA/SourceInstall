import os
import sys
import time
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "https://opstore.site"
DEST_DIR = "/storage/emulated/0/Download/NexusHideout"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-S918B Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.51 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": BASE_URL,
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Sec-CH-UA": '"Chromium";v="140", "Google Chrome";v="140"',
    "Sec-CH-UA-Mobile": "?1",
    "Sec-CH-UA-Platform": '"Android"'
}

TITLE   = Fore.CYAN  + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR   = Fore.RED   + Style.BRIGHT

os.makedirs(DEST_DIR, exist_ok=True)

if not (hasattr(os, "geteuid") and os.geteuid() == 0):
    print(ERROR + "🐡 Root Not Detected, Exiting... 🔫")
    sys.exit(1)

def run(cmd):
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def download(url, dst, retries=6):
    delays = [5, 5, 10, 10, 15, 15]
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, stream=True, timeout=60)
            r.raise_for_status()
            with open(dst, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
            print(SUCCESS + f"📥 Downloaded: {os.path.basename(dst)}")
            return
        except Exception as e:
            if attempt < retries:
                wait = delays[attempt - 1]
                print(ERROR + f"🍂 Download Failed ({attempt}/{retries}): {e} — Retry In {wait}s")
                time.sleep(wait)
            else:
                print(ERROR + f"❌ Download Failed After {retries} Attempts: {url}")
                sys.exit(1)

def install(apk_path, retries=6):
    delays = [5, 5, 10, 10, 15, 15]
    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(["pm", "install", "-r", apk_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(SUCCESS + f"📲 Installed: {os.path.basename(apk_path)}")
                return
            else:
                raise Exception(result.stderr.decode().strip() or "Unknown error")
        except Exception as e:
            if attempt < retries:
                wait = delays[attempt - 1]
                print(ERROR + f"🍂 Install Failed ({attempt}/{retries}): {e} — Retry In {wait}s")
                time.sleep(wait)
            else:
                print(ERROR + f"❌ Install Failed After {retries} Attempts: {apk_path}")
                sys.exit(1)

def clear_package(p):
    run(["pm", "clear", "--user", "0", p])

def uninstall_package(p):
    run(["pm", "uninstall", "--user", "0", p])

def par_run(func, args_list, max_workers=16):
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        [f.result() for f in as_completed([ex.submit(func, *args) for args in args_list])]

print(TITLE + "🥗 Clearing/Uninstalling Roblox... 🍔")
roblox_clients = [f"com.roblox.client{i}" for i in range(0, 9)]
par_run(clear_package, [(pkg,) for pkg in roblox_clients], max_workers=8)
par_run(uninstall_package, [(pkg,) for pkg in roblox_clients], max_workers=8)
par_run(clear_package, [(pkg,) for pkg in roblox_clients], max_workers=8)
print(SUCCESS + "🍲 Cleared And Uninstalled! 🍛")
print(TITLE + "🎯 Installing 8 Tabs... 🍵")
files = [f"{i}.apk" for i in range(1, 9)]
paths = [os.path.join(DEST_DIR, fn) for fn in files]
with ThreadPoolExecutor(max_workers=2) as ex:
    [f.result() for f in as_completed(
        [ex.submit(download, f"{BASE_URL}/LiteN/{fn}", p) for fn, p in zip(files, paths)]
    )]
print(SUCCESS + "🥬 All Global Tabs Downloaded! ☕")
with ThreadPoolExecutor(max_workers=8) as ex:
    [f.result() for f in as_completed([ex.submit(install, p) for p in paths])]
print(SUCCESS + "🥩 All Global Tabs Installed! ☕")
