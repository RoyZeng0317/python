# pip install pyautogui
import pyautogui    # 自動按鍵
import time         # 時間紀錄
import random       # 隨機打亂順序
import pyperclip    # 複製粘貼

list = ['Danel', 'I Love you', 'I miss you']
time.sleep(5)
for _ in range(6):
    sent = random.choice(list)
    pyperclip.copy(sent)    # copy the goal
    pyautogui.hotkey('ctrl', 'v')   # auto press past
    pyautogui.press('enter') # auto press enter
    time.sleep(random.uniform(0.5, 0.2))    # stio 0.5 to 2 second