import math, cv2
# 以下內容不可變更(刪除)
import tkinter as tk
import math
import random

# =========================================================================
# 3D 粒子類別與投影運算
# =========================================================================
class Particle3D:
    def __init__(self, x, y, z, color, size: float = 2, brightness=1.0):
        self.x = x  # 原始 3D 座標
        self.y = y
        self.z = z
        self.color = color  # Hex 顏色 (#RRGGBB)
        self.size = size
        self.brightness = brightness
        
        # 旋轉投影後的座標
        self.rx = x
        self.ry = y
        self.rz = z
        self.proj_x = 0
        self.proj_y = 0
        self.scale = 1.0

    def rotate(self, angle_x, angle_y, angle_z):
        """ 套用 3D 旋轉矩陣 """
        # Y 軸旋轉
        rad_y = math.radians(angle_y)
        cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
        x1 = self.x * cos_y + self.z * sin_y
        z1 = -self.x * sin_y + self.z * cos_y
        y1 = self.y

        # X 軸旋轉
        rad_x = math.radians(angle_x)
        cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
        y2 = y1 * cos_x - z1 * sin_x
        z2 = y1 * sin_x + z1 * cos_x
        x2 = x1

        # Z 軸旋轉
        rad_z = math.radians(angle_z)
        cos_z, sin_z = math.cos(rad_z), math.sin(rad_z)
        self.rx = x2 * cos_z - y2 * sin_z
        self.ry = x2 * sin_z + y2 * cos_z
        self.rz = z2

    def project(self, width, height, fov=400, viewer_dist=500):
        """ 透視投影 Perspective Projection """
        distance = viewer_dist + self.rz
        if distance < 1:
            distance = 1
        
        self.scale = fov / distance
        self.proj_x = width / 2 + self.rx * self.scale
        self.proj_y = height / 2 + self.ry * self.scale


# =========================================================================
# 3D 模型粒子生成器 (生成足夠質感的粒子密度)
# =========================================================================
def create_shuttlecock_particles(count=2500):
    """ 1. 羽球 (Badminton Shuttlecock) """
    particles = []
    
    # 1.1 軟木頭 (Cork Head) - 半球體
    cork_radius = 25
    cork_count = int(count * 0.3)
    for _ in range(cork_count):
        phi = random.uniform(0, math.pi / 2)  # 半球
        theta = random.uniform(0, math.pi * 2)
        r = cork_radius * (random.uniform(0.2, 1.0) ** (1/3))
        
        x = r * math.sin(phi) * math.cos(theta)
        y = -r * math.cos(phi) + 40  # 向上擺放
        z = r * math.sin(phi) * math.sin(theta)
        
        # 軟木色 / 白色漸層
        color = "#E0D5C1" if r < cork_radius * 0.8 else "#FFFFFF"
        particles.append(Particle3D(x, y, z, color, size=random.uniform(1.8, 2.5)))

    # 1.2 羽毛面與羽條 (Feathers) - 16根主羽條 + 錐形擴展面
    num_feathers = 16
    feather_particles = int(count * 0.7)
    
    for i in range(num_feathers):
        angle = (i / num_feathers) * math.pi * 2
        # 羽毛從軟木頭延伸開來
        for j in range(feather_particles // num_feathers):
            t = random.uniform(0, 1)  # 0: 底端, 1: 頂端
            
            # 圓錐形擴散比例
            top_radius = 65
            bot_radius = cork_radius * 0.9
            curr_radius = bot_radius + (top_radius - bot_radius) * (t ** 0.8)
            
            # 羽毛的微幅彎曲曲率
            spread = random.uniform(-4, 4)
            x = (curr_radius + spread) * math.cos(angle)
            y = 40 - t * 110  # 羽毛向上張開
            z = (curr_radius + spread) * math.sin(angle)
            
            # 顏色：羽毛軸心偏亮白，邊緣微透明灰白
            size = random.uniform(1.2, 2.2)
            color = "#FFFFFF" if abs(spread) < 1.5 else "#D8E2DC"
            particles.append(Particle3D(x, y, z, color, size=size))
            
    return particles


def create_neptune_particles(count=3000):
    """ 2. 海王星 (Neptune) - 深藍行星體 + 大暗斑 + 立體光環 """
    particles = []
    planet_radius = 70
    
    # 2.1 行星本體 (Sphere)
    planet_count = int(count * 0.65)
    for _ in range(planet_count):
        phi = random.uniform(0, math.pi)
        theta = random.uniform(0, math.pi * 2)
        r = planet_radius * (random.uniform(0.85, 1.0))
        
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.cos(phi)
        z = r * math.sin(phi) * math.sin(theta)
        
        # 判斷是否在大暗斑 (Great Dark Spot) 區域
        is_dark_spot = (-20 < y < 10) and (0.2 < math.atan2(z, x) < 1.2)
        
        if is_dark_spot:
            color = "#0B2545"  # 極深藍/暗斑
        else:
            # 依緯度給予不同藍色條紋 (Azure / Royal Blue / Cyan)
            lat = y / planet_radius
            if abs(lat) > 0.7:
                color = "#48CAE4"  # 極地淺藍
            elif abs(lat) < 0.25:
                color = "#0077B6"  # 赤道中藍
            else:
                color = "#023E8A"  # 深海藍
                
        particles.append(Particle3D(x, y, z, color, size=random.uniform(1.5, 2.5)))

    # 2.2 海王星環 (Rings)
    ring_count = int(count * 0.35)
    for _ in range(ring_count):
        r = random.uniform(90, 130)
        theta = random.uniform(0, math.pi * 2)
        
        # 光環帶有微微傾斜
        x = r * math.cos(theta)
        y = random.uniform(-2, 2)
        z = r * math.sin(theta)
        
        color = "#90E0EF" if r < 110 else "#00B4D8"
        particles.append(Particle3D(x, y, z, color, size=random.uniform(1.0, 1.8)))
        
    return particles


def create_pluto_particles(count=3000):
    """ 3. 冥王星 (Pluto) - 岩石冰雪質地 + 標誌性心形暗斑 (Tombaugh Regio) """
    particles = []
    radius = 80
    
    for _ in range(count):
        phi = random.uniform(0, math.pi)
        theta = random.uniform(0, math.pi * 2)
        r = radius * (random.uniform(0.88, 1.0))
        
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.cos(phi)
        z = r * math.sin(phi) * math.sin(theta)
        
        # 計算心形特徵區域 (Heart Region) 數學表達式近似
        norm_x = x / radius
        norm_y = y / radius
        norm_z = z / radius
        
        # 正面角度 (z > 0) 呈現心形暗斑
        lon = math.atan2(norm_x, norm_z)
        lat = norm_y
        
        # 簡單心形方程檢查
        heart_val = (lon**2 + lat**2 - 0.25)**3 - (lon**2)*(lat**3)
        is_heart = (heart_val < 0.05) and (norm_z > 0.2)
        
        if is_heart:
            color = "#FDF0D5"  # 心形區：淡金白色氮冰
        else:
            # 棕褐色、赤鐵礦色與冰灰層次
            rand_val = random.random()
            if lat < -0.3:
                color = "#664433"  # 南極深棕地表
            elif rand_val > 0.6:
                color = "#C38E70"  # 橘棕色
            elif rand_val > 0.3:
                color = "#8D5B4C"  # 暗赤紅
            else:
                color = "#4A3B32"  # 深岩石色
                
        particles.append(Particle3D(x, y, z, color, size=random.uniform(1.5, 2.5)))
        
    return particles


def create_diamond_particles(count=2800):
    """ 4. 鑽石 (Diamond) - 經典 57 面圓形明亮式切工 (Round Brilliant Cut) """
    particles = []
    
    # 切工關鍵幾何尺寸
    table_r = 35      # 頂部檯面半徑
    girdle_r = 75     # 腰部最寬半徑
    table_y = -35     # 檯面高度
    girdle_y = -5     # 腰部高度
    culet_y = 65      # 底尖高度
    
    for _ in range(count):
        # 決定粒子落點區域：檯面(10%), 冠部(35%), 腰部(15%), 亭部(40%)
        region = random.choices(["table", "crown", "girdle", "pavilion"], weights=[0.1, 0.35, 0.15, 0.4])[0]
        facet_angle = (random.randint(0, 15) / 16.0) * math.pi * 2  # 16 折面晶格
        
        if region == "table": # 頂面
            r = random.uniform(0, table_r)
            ang = random.uniform(0, math.pi * 2)
            x, y, z = r * math.cos(ang), table_y, r * math.sin(ang)
            color = "#FFFFFF"
            
        elif region == "crown": # 冠部 (檯面到腰部)
            t = random.uniform(0, 1)
            r = table_r + (girdle_r - table_r) * t
            y = table_y + (girdle_y - table_y) * t
            x = r * math.cos(facet_angle + random.uniform(-0.1, 0.1))
            z = r * math.sin(facet_angle + random.uniform(-0.1, 0.1))
            color = "#E0F7FA" if random.random() > 0.3 else "#80DEEA"
            
        elif region == "girdle": # 腰部薄層
            y = girdle_y + random.uniform(-3, 3)
            x = girdle_r * math.cos(facet_angle + random.uniform(-0.05, 0.05))
            z = girdle_r * math.sin(facet_angle + random.uniform(-0.05, 0.05))
            color = "#B2EBF2"
            
        else: # 亭部 (腰部收攏至底尖)
            t = random.uniform(0, 1)
            r = girdle_r * (1 - t)
            y = girdle_y + (culet_y - girdle_y) * t
            x = r * math.cos(facet_angle + random.uniform(-0.1, 0.1))
            z = r * math.sin(facet_angle + random.uniform(-0.1, 0.1))
            color = "#00E5FF" if t > 0.5 else "#E0F7FA"
            
        # 閃耀稜鏡感色調
        if random.random() < 0.08:
            color = "#FF80AB" if random.random() > 0.5 else "#EA80FC"  # 火彩折射閃光
            
        particles.append(Particle3D(x, y, z, color, size=random.uniform(1.2, 2.3)))
        
    return particles


def create_treasure_chest_particles(count=3200):
    """ 5. 寶箱 (Treasure Chest) - 含弧形蓋、金屬包角與滿溢金幣 """
    particles = []
    
    # 5.1 箱體下半部 (Cube Body)
    w, h, d = 90, 50, 60
    body_count = int(count * 0.45)
    for _ in range(body_count):
        # 選擇表面或內部金幣
        if random.random() < 0.7:  # 外殼 (木紋與金屬邊框)
            face = random.choice(["front", "back", "left", "right", "bottom"])
            if face == "front":
                x, y, z = random.uniform(-w/2, w/2), random.uniform(0, h), d/2
            elif face == "back":
                x, y, z = random.uniform(-w/2, w/2), random.uniform(0, h), -d/2
            elif face == "left":
                x, y, z = -w/2, random.uniform(0, h), random.uniform(-d/2, d/2)
            elif face == "right":
                x, y, z = w/2, random.uniform(0, h), random.uniform(-d/2, d/2)
            else:
                x, y, z = random.uniform(-w/2, w/2), h, random.uniform(-d/2, d/2)
                
            # 金屬包角鐵條 vs 木條顏色
            is_edge = (abs(x) > w/2 - 6) or (y < 6 or y > h - 6) or (abs(z) > d/2 - 6)
            color = "#D4AF37" if is_edge else "#5C3A21"  # 黃金邊框 / 深木色
        else:
            # 箱內金幣
            x = random.uniform(-w/2 + 5, w/2 - 5)
            y = random.uniform(5, 20)
            z = random.uniform(-d/2 + 5, d/2 - 5)
            color = "#FFD700"  # 純金光澤
            
        particles.append(Particle3D(x, y - 10, z, color, size=random.uniform(1.5, 2.5)))

    # 5.2 寶箱弧形蓋 (Arched Lid - 開啟狀態)
    lid_count = int(count * 0.4)
    lid_angle_open = math.radians(-35)  # 蓋子往後開啟的角度
    
    for _ in range(lid_count):
        theta = random.uniform(0, math.pi)  # 拱形半圓
        lx = random.uniform(-w/2, w/2)
        ly = - (d/2) * math.sin(theta)
        lz = - (d/2) * math.cos(theta)
        
        # 繞蓋子後軸旋轉 (開啟效果)
        z_pivot = -d/2
        lz_rot = (lz - z_pivot) * math.cos(lid_angle_open) - ly * math.sin(lid_angle_open) + z_pivot
        ly_rot = (lz - z_pivot) * math.sin(lid_angle_open) + ly * math.cos(lid_angle_open)
        
        is_edge = (abs(lx) > w/2 - 6) or (theta < 0.2 or theta > math.pi - 0.2)
        color = "#FFD700" if is_edge else "#7F4F24"
        
        particles.append(Particle3D(lx, ly_rot - 10, lz_rot, color, size=random.uniform(1.5, 2.5)))

    # 5.3 鎖扣與溢出的寶藏寶石 (Keyhole & Glowing Gems)
    extra_count = int(count * 0.15)
    for _ in range(extra_count):
        # 溢出到箱外的寶石
        x = random.uniform(-w/2 - 15, w/2 + 15)
        y = random.uniform(h - 15, h + 15) - 10
        z = random.uniform(d/2 - 10, d/2 + 20)
        color = random.choice(["#FF0054", "#00F5D4", "#7B2CBF", "#FFD700"])  # 紅寶石/翡翠/紫晶/金幣
        particles.append(Particle3D(x, y, z, color, size=random.uniform(2.0, 3.2)))

    return particles


# =========================================================================
# Tkinter 主視窗與 3D 繪圖引擎
# =========================================================================
class App3DParticleViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Particle Engine - Claude Modern Style")
        self.root.geometry("900 x 700")
        self.root.configure(bg="#121212")

        # 3D 視角控制變數
        self.angle_x = 15
        self.angle_y = 45
        self.angle_z = 0
        self.auto_rotate = True
        
        # 滑鼠拖曳控制
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # 鏡頭縮放控制 (滾輪)
        self.zoom = 1.0

        # UI 佈局
        self._setup_ui()
        
        # 預設載入模型
        self.models = {
            "羽球 (Shuttlecock)": create_shuttlecock_particles,
            "海王星 (Neptune)": create_neptune_particles,
            "冥王星 (Pluto)": create_pluto_particles,
            "鑽石 (Diamond)": create_diamond_particles,
            "寶箱 (Treasure Chest)": create_treasure_chest_particles
        }
        
        self.current_particles = self.models["羽球 (Shuttlecock)"]()
        
        # 啟動渲染迴圈
        self.render_loop()

    def _setup_ui(self):
        """ 建構黑深色科技感介面 """
        # 主 Canvas (繪製粒子)
        self.canvas = tk.Canvas(self.root, bg="#0A0A0C", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 控制面板 Frame (懸浮底部)
        control_frame = tk.Frame(self.root, bg="#1E1E24", bd=0)
        control_frame.pack(fill="x", side="bottom", ipady=8)

        # 選單標籤
        lbl = tk.Label(control_frame, text="切換 3D 粒子模型：", fg="#E0E0E0", bg="#1E1E24", font=("Segoe UI", 10))
        lbl.pack(side="left", padx=(20, 10))

        # 模型切換按鈕組
        btn_styles = {
            "bg": "#2B2B36", "fg": "#FFFFFF", "activebackground": "#D97757", 
            "activeforeground": "#FFFFFF", "bd": 0, "font": ("Segoe UI", 9, "bold"),
            "padx": 12, "pady": 5, "cursor": "hand2"
        }

        models_list = [
            ("羽球", "羽球 (Shuttlecock)"),
            ("海王星", "海王星 (Neptune)"),
            ("冥王星", "冥王星 (Pluto)"),
            ("鑽石", "鑽石 (Diamond)"),
            ("寶箱", "寶箱 (Treasure Chest)")
        ]

        for name, key in models_list:
            btn = tk.Button(control_frame, text=name, command=lambda k=key: self.switch_model(k), **btn_styles)
            btn.pack(side="left", padx=4)

        # 自動旋轉開關
        self.btn_auto = tk.Button(
            control_frame, text="自動旋轉: 開", command=self.toggle_auto_rotate,
            bg="#D97757", fg="#FFFFFF", bd=0, font=("Segoe UI", 9, "bold"), padx=10, pady=5, cursor="hand2"
        )
        self.btn_auto.pack(side="right", padx=20)

        # 滑鼠拖曳互動綁定
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)

        # 滑鼠滾輪縮放綁定 (Windows/Mac 用 <MouseWheel>，Linux 用 Button-4/5)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)

    def switch_model(self, model_key):
        """ 切換當前顯示的 3D 粒子模型 """
        self.current_particles = self.models[model_key]()

    def toggle_auto_rotate(self):
        self.auto_rotate = not self.auto_rotate
        self.btn_auto.config(
            text="自動旋轉: 開" if self.auto_rotate else "自動旋轉: 關",
            bg="#D97757" if self.auto_rotate else "#4A4A5A"
        )

    def _on_mouse_down(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def _on_mouse_drag(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        self.angle_y += dx * 0.5
        self.angle_x += dy * 0.5
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def _on_mouse_wheel(self, event):
        """ 滾輪縮放鏡頭 (往前滾=拉近, 往後滾=拉遠) """
        if event.num == 5 or getattr(event, "delta", 0) < 0:
            self.zoom = max(0.3, self.zoom - 0.05)
        elif event.num == 4 or getattr(event, "delta", 0) > 0:
            self.zoom = min(3.0, self.zoom + 0.05)

    def render_loop(self):
        """ 高效率 3D 粒子渲染迴圈 """
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 10:  # 視窗尚未初始化完成
            width, height = 900, 650

        # 自動旋轉角度更新
        if self.auto_rotate:
            self.angle_y += 1.2
            self.angle_x += 0.3

        # 1. 旋轉與投影運算
        for p in self.current_particles:
            p.rotate(self.angle_x, self.angle_y, self.angle_z)
            p.project(width, height, fov=400 * self.zoom)

        # 2. 深度排序 (Z-Sorting / Painter's Algorithm: 遠的粒子先畫，近的後畫)
        sorted_particles = sorted(self.current_particles, key=lambda p: p.rz, reverse=True)

        # 3. 在 Canvas 上繪製粒子
        for p in sorted_particles:
            # 根據 Z 軸距離調整縮放大小與透明度感
            r = max(0.5, p.size * p.scale * 0.8)
            x, y = p.proj_x, p.proj_y
            
            # 只繪製視窗範圍內的粒子 (裁剪優化)
            if 0 <= x <= width and 0 <= y <= height:
                self.canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    fill=p.color, outline=""
                )

        # 保持約 30~40 FPS 的渲染更新 Rate
        self.root.after(30, self.render_loop)
# =========================================================================
# 主程式入口
# =========================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = App3DParticleViewer(root)
    root.mainloop()