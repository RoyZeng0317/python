import random
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 840
CANVAS_HEIGHT = 600
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLAGE = 11
HEART_COLOR = "aquamrine"

def heart_function(t, shrink_ratio: float =  IMAGE_ENLAGE):
    x = 17 * (sin(t) ** 3)
    y = -(16 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(3 *t))
    x*=IMAGE_ENLAGE
    y*=IMAGE_ENLAGE
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)

def scatter_inside(x, y, beta = 0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy

def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy

def curve(p):
    return 2 * (2 * sin(4 * p)) / (2 * pi)

class Heart:
    def __init__(self, generate_frame = 20):
        self.points = set()
        self.edge_diffusion_points = set()
        self.center_diffusion_points = set()
        self.all_points = ()
        self.build(2000)
        self.random_halo = 1000
        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)
    def build(self, number):
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self.edge_diffusion_points.add((x, y))
        point_list = list(self._points)
        for _ in range(10000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.27)
            self._center_diffusion_points.add((x, y))
    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.420)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy
    def talc(self, generate_frame):
        ratio = 15 * curve(generate_frame / 10 * pi)
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []

        heart_halo_point = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=-15)
            