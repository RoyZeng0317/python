import pygame as pg, random as ra, math

pg.init()
pg.display.set_caption("新年煙火")
winInfo = pg.display.Info()
screenWidth = winInfo.current_w
screenHeight = winInfo.current_h
win = pg.display.set_mode((screenWidth, screenHeight))
clock = pg.time.Clock()
vector = pg.math.Vector2
trail_colors = [(45, 45, 45), (60, 60, 60), (75, 75, 75),
                (125, 125, 125), (150, 150, 150)]

# 粒子類 (火花 / 上升的煙火本體)
class Particle:
    def __init__(self, x, y, firework, colour):
        self.x = x
        self.y = y
        self.firework = firework
        self.colour = colour
        self.radius = 5 if firework else 2
        self.trail = []
        if firework:
            self.vel = vector(ra.uniform(-1, 1), ra.uniform(-17, -9))
        else:
            angle = ra.uniform(0, math.tau)
            speed = ra.uniform(2, 8)
            self.vel = vector(math.cos(angle) * speed, math.sin(angle) * speed)

    def apply_gravity(self, g):
        self.vel += g
        self.trail.insert(0, (self.x, self.y))
        self.trail = self.trail[:5]
        self.x += self.vel.x
        self.y += self.vel.y

    def draw(self, win):
        for i, pos in enumerate(self.trail):
            colour = trail_colors[min(i, len(trail_colors) - 1)]
            pg.draw.circle(win, colour, (int(pos[0]), int(pos[1])), max(self.radius - 1, 1))
        pg.draw.circle(win, self.colour, (int(self.x), int(self.y)), self.radius)

# 煙火類
class Firework:
    def __init__(self):
        # 隨機產生一個 RGB 顏色
        self.colour = (ra.randint(50, 255), ra.randint(50, 255), ra.randint(50, 255))
        # 從畫面底部隨機 x 位置發射出的火花粒子
        self.firework = Particle(ra.randint(0, screenWidth), screenHeight, True, self.colour)
        # 是否已經爆炸
        self.exploded = False
        self.particles = []
        # 爆炸後產生的粒子數量範圍
        self.min_max_particles = vector(30, 60)

    def update(self, win):
        g = vector(0, ra.uniform(0.15, 0.4))
        if not self.exploded:
            self.firework.apply_gravity(g)
            self.firework.draw(win)
            if self.firework.vel.y >= 0:
                self.exploded = True
                self.explode()
        else:
            for particle in self.particles:
                particle.apply_gravity(g)
                particle.draw(win)

    def explode(self):
        amount = ra.randint(int(self.min_max_particles.x), int(self.min_max_particles.y))
        for _ in range(amount):
            self.particles.append(
                Particle(self.firework.x, self.firework.y, False, self.colour)
            )

    def remove(self):
        # 所有粒子都掉出畫面外時才移除這個煙火
        return all(
            particle.y >= screenHeight or particle.x <= 0 or particle.x >= screenWidth
            for particle in self.particles
        )

def main():
    fireworks = []
    running = True
    while running:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        win.fill((0, 0, 0))

        if ra.randint(1, 20) == 1:
            fireworks.append(Firework())

        for firework in fireworks[:]:
            firework.update(win)
            if firework.exploded and firework.remove():
                fireworks.remove(firework)

        pg.display.update()

    pg.quit()

if __name__ == "__main__":
    main()
