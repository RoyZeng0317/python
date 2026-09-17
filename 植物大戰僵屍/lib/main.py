# 環境: pip install pygame
import pygame
pygame.init()       # 初始化
screen = pygame.display.set_mode((800, 600))    # 建立 800x600 的視窗
running = True      # 保持一直執行
while running:
    for event in pygame.event.get():    # 取得所有事件如點擊關閉按鈕等
        if event.type == pygame.QUIT:   # 如果按了右上角的關閉按鈕
            running = False             # 關閉視窗

pygame.quit()