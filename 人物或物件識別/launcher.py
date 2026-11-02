"""人物或物件識別 - 主啟動器"""
import subprocess, sys, os

TOOLS = [
    ("人臉識別 (靜態圖片)", "人臉識別.py"),
    ("即時人臉偵測", "即時識別.py"),
    ("即時汽車識別系統", "即時汽車識別系統.py"),
    ("汽車識別 (靜態圖片)", "汽車識別.py"),
    ("手指擦玻璃", "手指擦玻璃.py"),
    ("3D 粒子手勢", "3D粒子手勢.py"),
    ("量子空間", "量子空間.py"),
    ("偵測手掌數據", "偵測手掌數據.py"),
    ("電阻色環識別", "電阻識別.py"),
    ("多物件追蹤", "opencv 多物件追蹤.py"),
]

def main():
    while True:
        print("\n" + "=" * 40)
        print("    人物或物件識別 工具集")
        print("=" * 40)
        for i, (name, _) in enumerate(TOOLS, 1):
            print(f"  {i:2d}. {name}")
        print(f"   0. 離開")
        print("-" * 40)

        choice = input("請選擇功能 (0-10): ").strip()
        if choice == "0":
            break
        if not choice.isdigit() or not 1 <= int(choice) <= len(TOOLS):
            print("輸入錯誤，請重新選擇")
            continue

        idx = int(choice) - 1
        _, script = TOOLS[idx]
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
        if not os.path.exists(script_path):
            print(f"找不到 {script}")
            continue

        print(f"\n啟動 {TOOLS[idx][0]}...\n")
        subprocess.run([sys.executable, script_path], cwd=os.path.dirname(script_path))

if __name__ == "__main__":
    main()
