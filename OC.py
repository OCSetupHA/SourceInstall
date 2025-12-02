import os
import sys
import time
import shutil
import subprocess
import requests
import urllib.parse
import zipfile

from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

init(autoreset=True)
BASE_URL = "https://opstore.site"
FINAL_DIR = "/storage/emulated/0/"
DEST_DIR = "/storage/emulated/0/Download/NexusHideout"
ZIP_NAME = "Codex.zip"
ZIP_PATH = os.path.join(DEST_DIR, ZIP_NAME)

os.makedirs(DEST_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

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

TITLE = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT

os.system("clear")

if not (hasattr(os, "geteuid") and os.geteuid() == 0):
    print(ERROR + "🐡 Root Not Detected, Exiting... 🔫")
    sys.exit(1)

lite_packages = [
    "com.wsh.toolkit","com.wsh.appstorage","com.wsh.launcher2","com.android.calculator2",
    "com.android.music","com.android.musicfx","com.sohu.inputmethod.sogou","com.google.android.gms",
    "net.sourceforge.opencamera","com.google.android.googlequicksearchbox",
    "com.google.android.gm","com.google.android.youtube","com.google.android.apps.docs",
    "com.android.chrome","com.google.android.apps.meetings","com.google.android.apps.maps",
    "com.google.android.apps.photos","com.google.android.contacts","com.google.android.calendar",
    "com.android.vending","com.google.ar.core","com.google.android.play.games",
    "com.google.android.apps.magazines","com.google.android.apps.subscriptions.red",
    "com.google.android.videos","com.google.android.apps.googleassistant",
    "com.google.android.apps.messaging","com.google.android.dialer","com.android.mms",
    "com.og.toolcenter","com.og.gamecenter","com.android.launcher3","com.android.contacts",
    "com.android.calendar","com.android.calllogbackup","com.wsh.appstore","com.android.tools",
    "com.android.quicksearchbox","com.google.android.apps.gallery",
    "com.google.android.apps.wellbeing","com.google.android.apps.googleone",
    "com.google.android.apps.nbu.files","com.og.launcher","com.sec.android.gallery3d",
    "com.miui.gallery","com.coloros.gallery3d","com.vivo.gallery","com.motorola.gallery",
    "com.transsion.gallery","com.sonyericsson.album","com.lge.gallery","com.htc.album",
    "com.huawei.photos","com.android.gallery3d","com.android.gallery",
    "com.google.android.deskclock","com.sec.android.app.clockpackage","com.miui.clock",
    "com.coloros.alarmclock","com.vivo.alarmclock","com.motorola.timeweatherwidget",
    "com.android.deskclock","com.huawei.clock","com.lge.clock","com.android.email",
    "com.android.printspooler","com.android.bookmarkprovider","com.android.bips",
    "com.android.cellbroadcastreceiver","com.android.cellbroadcastservice",
    "com.android.dreams.basic","com.android.dreams.phototable","com.android.wallpaperbackup",
    "com.android.wallpapercropper","com.android.statementservice",
    "com.android.hotwordenrollment.okgoogle","com.android.hotwordenrollment.xgoogle",
    "com.android.sharedstoragebackup","com.android.stk",
    "com.google.android.tag","com.android.bluetoothmidiservice","com.android.messaging",
    "com.samsung.android.messaging","com.android.mms.service","com.miui.smsservice",
    "com.coloros.mms","com.vivo.message","com.huawei.message","com.lge.message",
    "com.sonyericsson.conversations","com.motorola.messaging","com.transsion.message"
]

base_path = "/storage/emulated/0/Download"
shouko_path = os.path.join(base_path, "Shouko.dev")
os.makedirs(shouko_path, exist_ok=True)

server_file_path = os.path.join(shouko_path, "server-link.txt")
content = (
    "com.roblox.client1,roblox://placeID=142823291\n"
    "com.roblox.client2,roblox://placeID=142823291\n"
    "com.roblox.client3,roblox://placeID=142823291\n"
    "com.roblox.client4,roblox://placeID=142823291\n"
    "com.roblox.client5,roblox://placeID=142823291\n"
    "com.roblox.client6,roblox://placeID=142823291\n"
    "com.roblox.client7,roblox://placeID=142823291\n"
    "com.roblox.client8,roblox://placeID=142823291"
)

if os.path.exists(server_file_path):
    with open(server_file_path, "r", encoding="utf-8") as f:
        if f.read() != content:
            with open(server_file_path, "w", encoding="utf-8") as f2:
                f2.write(content)
else:
    with open(server_file_path, "w", encoding="utf-8") as f:
        f.write(content)

cookie_file_path = os.path.join(base_path, "Cookie.txt")
with open(cookie_file_path, "w", encoding="utf-8") as f:
    pass
    
def run(cmd):
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def download(url, dst, retries=6):
    delays = [5, 5, 10, 10, 15, 15]
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, stream=True)
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

def install(p, retries=6):
    delays = [5, 5, 10, 10, 15, 15]
    for attempt in range(1, retries + 1):
        try:
            result = subprocess.run(["pm", "install", "-r", p], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(SUCCESS + f"📲 Installed: {os.path.basename(p)}")
                return
            else:
                raise Exception(result.stderr.decode().strip() or "Unknown error")
        except Exception as e:
            if attempt < retries:
                wait = delays[attempt - 1]
                print(ERROR + f"🍂 Install Failed ({attempt}/{retries}): {e} — Retry In {wait}s")
                time.sleep(wait)
            else:
                print(ERROR + f"❌ Install Failed After {retries} Attempts: {p}")
                sys.exit(1)
mini_path = os.path.join(DEST_DIR, "Mini.apk")
mtmanager_path = os.path.join(DEST_DIR, "MTManager.apk")

with ThreadPoolExecutor(max_workers=2) as ex:
    [f.result() for f in as_completed([
        ex.submit(download, f"{BASE_URL}/Mini.apk", mini_path),
        ex.submit(download, f"{BASE_URL}/MTManager.apk", mtmanager_path)
    ])]

with ThreadPoolExecutor(max_workers=2) as ex:
    [f.result() for f in as_completed([
        ex.submit(install, mini_path),
        ex.submit(install, mtmanager_path)
    ])]

def extract_and_move(zip_path, dest_folder, final_destination):
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            root_folder_name = os.path.commonpath(zip_ref.namelist())
            zip_ref.extractall(dest_folder)
            full_extracted_path = os.path.join(dest_folder, root_folder_name)
            target_path = os.path.join(final_destination, root_folder_name)
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.move(full_extracted_path, final_destination)
            print(SUCCESS + f"🚀 Moved: {root_folder_name} To {final_destination} 🥪")
    except Exception as e:
        print(ERROR + f"❌ Failed: {e} 🥩")
        sys.exit(1)

download(f"{BASE_URL}/{ZIP_NAME}", ZIP_PATH)
extract_and_move(ZIP_PATH, DEST_DIR, FINAL_DIR)
print(SUCCESS + "🥦 Moved! 🧴")

def disable_package(p): run(["pm", "disable-user", "--user", "0", p])
def uninstall_package(p): run(["pm", "uninstall", "--user", "0", p])
def clear_package(p): run(["pm", "clear", "--user", "0", p])

def par_run(func, args_list, max_workers=30):
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        [f.result() for f in as_completed([ex.submit(func, *args) for args in args_list])]

if os.path.exists(DEST_DIR): shutil.rmtree(DEST_DIR)
os.makedirs(DEST_DIR)

print(TITLE + "🌟 Cleaning Device...")
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(disable_package, [(p,) for p in lite_packages], 30)
par_run(disable_package, [(p,) for p in lite_packages], 30)
par_run(disable_package, [(p,) for p in lite_packages], 30)
par_run(uninstall_package, [(p,) for p in lite_packages], 30)
par_run(uninstall_package, [(p,) for p in lite_packages], 30)
par_run(uninstall_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(disable_package, [(p,) for p in lite_packages], 30)
par_run(disable_package, [(p,) for p in lite_packages], 30)
par_run(disable_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
par_run(clear_package, [(p,) for p in lite_packages], 30)
print(SUCCESS + "🧽 Device Cleaned Successfully! 🥑")

print(TITLE + "🎯 Installing 8 Global Tabs...")
files = [f"{i}.apk" for i in range(1, 9)]
paths = [os.path.join(DEST_DIR, f) for f in files]

with ThreadPoolExecutor(max_workers=2) as ex:
    [f.result() for f in as_completed([ex.submit(download, f"{BASE_URL}/LiteN/{fn}", p) for fn, p in zip(files, paths)])]
    print(SUCCESS + "🎯 All Global Tabs Downloaded!")

with ThreadPoolExecutor(max_workers=8) as ex:
    [f.result() for f in as_completed([ex.submit(install, p) for p in paths])]
    print(SUCCESS + "🎯 All Global Tabs Installed!")

os.system("clear")
print(SUCCESS + "🎉 All Tasks Completed! 🚀")
if os.path.exists(DEST_DIR): shutil.rmtree(DEST_DIR)
