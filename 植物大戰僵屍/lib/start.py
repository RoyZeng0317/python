# 啟動遊戲的初始介面
# pygame 遊戲庫
# pip install pygame
import pygame
# 定義視窗大小
def window_size():
    # 大小為 1000x600
    window_width, window_height = 1000, 600
    # 回傳視窗大小值
    return window_width, window_height
# 定義菜單背景
def menu_bg():
    # loading background picture
    m = pygame.image.load(r'')
    