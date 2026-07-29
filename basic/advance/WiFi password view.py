"""
WiFi 已儲存密碼檢視器（僅支援 Windows）
讀取本機「曾經連線並儲存過」的 WiFi 設定檔名稱與明文密碼，
底層呼叫系統內建的 netsh wlan 指令。

注意：
- 只能看到「這台電腦」存過的網路，不是駭入別人的 WiFi。
- 公司/學校電腦若被群組原則鎖住，netsh 可能會執行失敗。
"""

import platform
import re
import subprocess
import sys
from locale import getpreferredencoding


def run_netsh(args):
    """執行 netsh 指令，並用系統目前的編碼解碼輸出（避免中文亂碼或解碼錯誤）"""
    raw = subprocess.check_output(["netsh", *args])
    encoding = getpreferredencoding(False)
    return raw.decode(encoding, errors="replace")


def list_wifi_profiles():
    """列出所有已儲存的 WiFi 設定檔名稱

    不用固定比對英文字串「All User Profile」，因為 Windows 語系不同時
    這段文字會變成「所有使用者設定檔」等在地化文字而抓不到。
    改用縮排結構判斷：設定檔那幾行一定是「  標籤 : 名稱」的格式。
    """
    output = run_netsh(["wlan", "show", "profiles"])
    profiles = []
    for line in output.splitlines():
        if not line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        name = line.split(":", 1)[1].strip()
        if name and name != "<None>":
            profiles.append(name)
    return profiles


def get_profile_password(profile_name):
    """取得指定 WiFi 設定檔的明文密碼

    用參數清單呼叫 netsh（而非把名稱拼進 shell 字串），
    避免設定檔名稱含特殊字元時造成指令注入或執行失敗。
    """
    output = run_netsh(["wlan", "show", "profile", profile_name, "key=clear"])
    match = re.search(r"Key Content\s*:\s*(.+)", output)
    password = match.group(1).strip() if match else None
    return password, output


def choose_profile(profiles):
    """讓使用者從清單挑一個設定檔，輸入錯誤時回傳 None"""
    print("已儲存的 WiFi 設定檔：\n")
    for i, name in enumerate(profiles, 1):
        print(f"[{i}] {name}")

    choice = input("\n請輸入要查看的編號：").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(profiles)):
        return None
    return profiles[int(choice) - 1]


def main():
    if platform.system() != "Windows":
        print("此工具僅支援 Windows（需要系統內建的 netsh 指令）。")
        sys.exit(1)

    try:
        profiles = list_wifi_profiles()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("執行 netsh 失敗，請確認 WiFi 服務已啟動，或改用系統管理員身分重新執行。")
        print(f"錯誤訊息：{e}")
        sys.exit(1)

    if not profiles:
        print("找不到任何已儲存的 WiFi 設定檔。")
        sys.exit(0)

    target = choose_profile(profiles)
    if target is None:
        print("輸入錯誤，請輸入清單中列出的編號。")
        sys.exit(1)

    try:
        password, raw = get_profile_password(target)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"查詢「{target}」失敗：{e}")
        sys.exit(1)

    print(f"\nWiFi 名稱：{target}")
    if password:
        print(f"密碼：{password}")
    else:
        print("找不到「Key Content」欄位（可能是介面語系不同，或此網路本來就沒有密碼），完整資訊如下：\n")
        print(raw)


if __name__ == "__main__":
    main()
