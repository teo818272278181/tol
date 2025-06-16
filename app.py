import requests
import time
import signal
import sys
from playwright.sync_api import sync_playwright

API_URL = "https://engine.hyperbeam.com/v0/vm"
START_URL = "https://akcgh.pages.dev"

# Đọc token từ file nếu có
try:
    with open("tokens.txt") as f:
        TOKENS = f.read().splitlines()
except FileNotFoundError:
    print("⚠️ File 'tokens.txt' không tồn tại. Sử dụng token mặc định.")
    TOKENS = []

# Token thêm thủ công ở đây
TOKENS += [
    "sk_live_Q2QodCQu_fYfSgykyVoLy4Bj4X1G132k0moZrSFw5s0",
    "sk_live_-FBDxjjgcXDsMdl1-WeenWOIth9iiKbs4AayQR3zcEs",
]

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'

sessions = []

def create_vm(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "start_url": START_URL,
        "timeout": {
            "absolute": 3600,
            "inactive": 3600,
            "offline": 3600,
            "warning": 60,
        },
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        vm_info = resp.json()
        vm_info["token"] = token
        print(f"{Color.GREEN}✔ VM created: {vm_info['session_id']}{Color.END}")
        return vm_info
    except Exception as e:
        print(f"{Color.RED}✘ Failed to create VM: {e}{Color.END}")
        return None

def delete_vm(session_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{API_URL}/{session_id}"
    try:
        resp = requests.delete(url, headers=headers)
        if resp.status_code == 204:
            print(f"{Color.GREEN}✔ VM {session_id} deleted successfully{Color.END}")
        else:
            print(f"{Color.RED}✘ Failed to delete VM {session_id}: {resp.status_code} {resp.text}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}✘ Exception deleting VM {session_id}: {e}{Color.END}")

def exit_handler(sig, frame):
    print(f"\n{Color.YELLOW}Exiting... Deleting all VMs{Color.END}")
    for vm in sessions:
        delete_vm(vm["session_id"], vm["token"])
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    NUM_CYCLES = 5
    for cycle in range(1, NUM_CYCLES + 1):
        print(f"\n{Color.YELLOW}========== CYCLE {cycle}/{NUM_CYCLES} =========={Color.END}")

        for token_index, token in enumerate(TOKENS, start=1):
            print(f"\n{Color.YELLOW}→ Token {token_index}/{len(TOKENS)}: Creating VMs{Color.END}")
            for i in range(10):
                vm = create_vm(token)
                if vm:
                    sessions.append(vm)
                else:
                    print(f"{Color.RED}✘ Skipping VM {i+1} for token {token_index}{Color.END}")

        print(f"{Color.YELLOW}→ Cycle {cycle} completed. Waiting 1 hour before next cycle...{Color.END}")
        if cycle < NUM_CYCLES:
            time.sleep(3600)  # Chờ 1 tiếng
        else:
            print(f"{Color.YELLOW}→ All cycles done. Cleaning up...{Color.END}")

    for vm in sessions:
        delete_vm(vm["session_id"], vm["token"])

    print(f"{Color.GREEN}✅ Program finished. All VMs deleted.{Color.END}")

if __name__ == "__main__":
    main()
