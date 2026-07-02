import random
import math
import uuid

ROLES = {
    'square': {'color': '#e74c3c', 'speed': 3, 'hp': 150, 'size': 25, 'attack': 1},
    'triangle': {'color': '#3498db', 'speed': 4, 'hp': 150, 'size': 28, 'attack': 1.2},
    'circle': {'color': '#2ecc71', 'speed': 2.5, 'hp': 150, 'size': 22, 'attack': 0.8},
    'rectangle': {'color': '#9b59b6', 'speed': 2, 'hp': 150, 'size': {'w': 35, 'h': 22}, 'attack': 1.5}
}

SPAWN_INTERVALS = {
    'square': 72,
    'triangle': 60,
    'circle': 90,
    'rectangle': 48
}

class Player:
    def __init__(self, role_id, config):
        self.x = 400.0
        self.y = 300.0
        self.role = role_id
        self.color = config['color']
        self.speed = config['speed']
        self.hp = config['hp']
        self.max_hp = config['hp']
        self.size = config['size']
        self.attack_dmg = config['attack']
        self.invincible = False
        self.invincible_timer = 0
        self.last_dx = 0.0
        self.last_dy = 1.0
        self.attack_timer = 0
        self.slash_timer = 0

class Monster:
    def __init__(self, x, y, px, py):
        types = ['circle', 'triangle', 'square']
        colors = ['#c0392b', '#8e44ad', '#d35400', '#16a085', '#2c3e50', '#7f8c8d']
        self.x = x
        self.y = y
        self.type = random.choice(types)
        self.color = random.choice(colors)
        self.max_hp = 2 + random.randint(0, 2)
        self.hp = self.max_hp
        self.speed = 0.8 + random.random() * 0.8
        self.target_x = px
        self.target_y = py

class Energy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class GameState:
    def __init__(self, role_id):
        config = ROLES[role_id]
        self.id = str(uuid.uuid4())
        self.player = Player(role_id, config)
        self.monsters = []
        self.energies = []
        self.score = 0
        self.running = True
        self.spell_active = False
        self.current_word = ''
        self.tick = 0
        self.last_spawn_tick = 0
        self.last_energy_tick = 0
        self.spawn_interval = SPAWN_INTERVALS.get(role_id, 60)
        self.energy_interval = 300
        self.words = []

    def set_words(self, words):
        self.words = words

    def update(self, keys):
        if not self.running or self.spell_active:
            return
        self.tick += 1

        if self.player.invincible:
            self.player.invincible_timer -= 1
            if self.player.invincible_timer <= 0:
                self.player.invincible = False

        if self.player.attack_timer > 0:
            self.player.attack_timer -= 1
        if self.player.slash_timer > 0:
            self.player.slash_timer -= 1

        dx, dy = 0.0, 0.0
        if keys.get('w'): dy = -1
        if keys.get('s'): dy = 1
        if keys.get('a'): dx = -1
        if keys.get('d'): dx = 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        if dx != 0 or dy != 0:
            self.player.last_dx = dx
            self.player.last_dy = dy

        self.player.x += dx * self.player.speed
        self.player.y += dy * self.player.speed
        self.player.x = max(25, min(775, self.player.x))
        self.player.y = max(25, min(575, self.player.y))

        for m in self.monsters:
            angle = math.atan2(self.player.y - m.y, self.player.x - m.x)
            m.target_x = self.player.x
            m.target_y = self.player.y
            m.x += math.cos(angle) * m.speed
            m.y += math.sin(angle) * m.speed

        self.monsters = [m for m in self.monsters if self._check_monster_collision(m)]
        self.energies = [e for e in self.energies if self._check_energy_collection(e)]

        if self.tick - self.last_spawn_tick >= self.spawn_interval:
            self._spawn_monster()
            self.last_spawn_tick = self.tick

        if self.tick - self.last_energy_tick >= self.energy_interval:
            self._spawn_energy()
            self.last_energy_tick = self.tick

    def _check_monster_collision(self, m):
        dist = math.hypot(self.player.x - m.x, self.player.y - m.y)
        if dist < 30 and not self.player.invincible:
            self.player.hp -= 0.5
            if self.player.hp <= 0:
                self.running = False
                return False
            if self.player.hp <= 20 and not self.spell_active:
                self.trigger_spell()
        return m.hp > 0

    def _check_energy_collection(self, e):
        dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
        if dist < 30 and not self.spell_active:
            self.trigger_spell()
            return False
        return True

    def _spawn_monster(self):
        side = random.randint(0, 3)
        if side == 0:
            x = random.random() * 800
            y = -30
        elif side == 1:
            x = 830
            y = random.random() * 600
        elif side == 2:
            x = random.random() * 800
            y = 630
        else:
            x = -30
            y = random.random() * 600
        self.monsters.append(Monster(x, y, self.player.x, self.player.y))

    def _spawn_energy(self):
        x = 30 + random.random() * 740
        y = 30 + random.random() * 540
        self.energies.append(Energy(x, y))

    def attack(self, mouse_x=None, mouse_y=None):
        if self.player.attack_timer > 0 or not self.running or self.spell_active:
            return
        self.player.attack_timer = 15
        self.player.slash_timer = 10

        if mouse_x is not None and mouse_y is not None:
            dir_x = mouse_x - self.player.x
            dir_y = mouse_y - self.player.y
            d = math.hypot(dir_x, dir_y)
            if d > 0:
                dir_x /= d
                dir_y /= d
                self.player.last_dx = dir_x
                self.player.last_dy = dir_y
        else:
            dir_x = self.player.last_dx
            dir_y = self.player.last_dy

        atk_range = 100
        atk_width = 35

        for m in self.monsters[:]:
            dx = m.x - self.player.x
            dy = m.y - self.player.y
            dist = math.hypot(dx, dy)
            if dist > atk_range + 15:
                continue

            if dist > 0:
                dot = (dx * dir_x + dy * dir_y) / dist
                if dot < 0.3:
                    continue

            perp = abs(-dx * dir_y + dy * dir_x) / dist if dist > 0 else 0
            if perp > atk_width:
                continue

            m.hp -= self.player.attack_dmg
            if m.hp <= 0:
                self.score += 10

    def activate_super(self):
        if not self.running or self.spell_active:
            return
        for m in self.monsters:
            self.score += 5
        self.monsters.clear()
        self.player.invincible = True
        self.player.invincible_timer = 180

    def trigger_spell(self):
        if not self.words:
            return
        self.spell_active = True
        self.current_word = random.choice(self.words)

    def check_spell(self, given):
        correct = given.strip().lower() == self.current_word.lower()
        if correct:
            if self.player.hp < 50:
                self.monsters = [m for m in self.monsters if math.hypot(self.player.x - m.x, self.player.y - m.y) > 30]
            self.player.hp = min(self.player.max_hp, self.player.hp + 50)
        self.spell_active = False
        self.current_word = ''
        return correct

    def to_dict(self):
        size = self.player.size
        if isinstance(size, dict):
            size = dict(size)
        return {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'role': self.player.role,
                'color': self.player.color,
                'hp': self.player.hp,
                'maxHp': self.player.max_hp,
                'size': size,
                'invincible': self.player.invincible,
                'lastDx': self.player.last_dx,
                'lastDy': self.player.last_dy,
                'slashTimer': self.player.slash_timer
            },
            'monsters': [{
                'x': m.x, 'y': m.y, 'type': m.type,
                'color': m.color, 'hp': m.hp, 'maxHp': m.max_hp
            } for m in self.monsters],
            'energies': [{'x': e.x, 'y': e.y} for e in self.energies],
            'score': self.score,
            'running': self.running,
            'spellActive': self.spell_active,
            'currentWord': self.current_word
        }


class GameManager:
    def __init__(self):
        self.games = {}

    def create_game(self, role_id):
        gs = GameState(role_id)
        gs.set_words(WORDS)
        self.games[gs.id] = gs
        return gs.id

    def get_game(self, game_id):
        return self.games.get(game_id)

    def remove_game(self, game_id):
        self.games.pop(game_id, None)


WORDS = [
    "apple", "brave", "crane", "dance", "eagle", "flame", "grape", "heart",
    "image", "jolly", "knife", "lemon", "mango", "noble", "ocean", "piano",
    "queen", "river", "snake", "tiger", "umbra", "vivid", "whale", "xenon",
    "yacht", "zebra", "arrow", "bloom", "coral", "drift", "elite", "frost",
    "ghost", "honey", "ivory", "jewel", "koala", "lunar", "magic", "north",
    "olive", "pearl", "quest", "raven", "solar", "trace", "ultra", "vigor",
    "wheat", "amber", "basil", "cedar", "daisy", "ember", "fairy", "golem",
    "hazel", "indie", "jumbo", "kayak", "lilac", "mimic", "neon", "oxide",
    "pixel", "radar", "sable", "topaz", "uncle", "vista", "wispy", "yogic",
    "bliss", "chill", "dwarf", "eager", "flair", "grasp", "hover", "irate",
    "joker", "kneel", "lodge", "moist", "niece", "opera", "prank", "quilt",
    "rinse", "shift", "thorn", "usher", "vouch", "wince", "yearn", "zesty"
]
