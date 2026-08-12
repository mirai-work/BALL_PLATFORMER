import pyxel
import math
import random

# --- 定数 ---
WIDTH = 256
HEIGHT = 144
FOV = math.pi / 2.5
MOVE_SPEED = 0.08
ROT_SPEED = 0.06
MAX_WAVES = 5

# 各面（Wave 1〜5）ごとの異なるマップ定義
MAPS = [
    # Wave 1
    [
        "111111111111111111111111",
        "100000000001000001111111",
        "100000000001000001111111",
        "100110011001000001111111",
        "100110011000000000000001",
        "100000000001000001111111",
        "111100111111111111111111",
        "100000000000000000000001",
        "101111011110000000000001",
        "101111011110011111100001",
        "101111011110010000100001",
        "101111011110010000100001",
        "100000000000010110100001",
        "100000000000010000100001",
        "111100001111111001111111",
        "100000000000000000000001",
        "101010010100111100011111",
        "100000000000100000000001",
        "101010010100100111000001",
        "100000000000100111000001",
        "111111111100100111000001",
        "100000000000000111000001",
        "100000000000000000000001",
        "111111111111111111111111",
    ],
    # Wave 2
    [
        "111111111111111111111111",
        "100000011100001110000001",
        "101110011101101110111001",
        "101010000001010000010101",
        "101011111101011111010101",
        "100000000000000000000001",
        "111101111111111111101111",
        "100001000000000000100001",
        "101101011110011110101101",
        "101100011110011110001101",
        "100000000000000000000001",
        "111111011111111110111111",
        "100000010000000010000001",
        "101110010111110100111001",
        "101010000001100000010101",
        "101011100001100001110101",
        "100000100000000001000001",
        "111100000111110000001111",
        "100000001000001000000001",
        "100111110000000111111001",
        "100100000011100000001001",
        "100100000011100000001001",
        "100000000000000000000001",
        "111111111111111111111111",
    ],
    # Wave 3
    [
        "111111111111111111111111",
        "100000000000000000000001",
        "101111111011110111111101",
        "101000001010010100000101",
        "101011101010010101110101",
        "101011101000000101110101",
        "101000001110011100000101",
        "101111111000000111111101",
        "100000000011110000000001",
        "111101111111111111101111",
        "100001000000000000100001",
        "101101011111111110101101",
        "101100011111111110001101",
        "100001000000000000100001",
        "111101111111111111101111",
        "100000000001000000000001",
        "101111100101010011111101",
        "100000100100010010000001",
        "111000100111110010001111",
        "100001100000000011000001",
        "101101111101011111011001",
        "101000000001000000000101",
        "100000000000000000000001",
        "111111111111111111111111",
    ],
    # Wave 4
    [
        "111111111111111111111111",
        "100000001111111100000001",
        "101110001111111100011101",
        "101010000000000000010101",
        "1010111110111011111010101",
        "1010000010101010000010101",
        "1011110010101010011110101",
        "100001000000000000100001",
        "111101011110011110101111",
        "111100011110011110001111",
        "100001000000000000100001",
        "111101111110011111101111",
        "100000000010010000000001",
        "101111110010010011111101",
        "100000010000000100000001",
        "111100010111110100011111",
        "100000000100010000000001",
        "101111100100010011111101",
        "101000100000000001000101",
        "101000111011101111000101",
        "101000000011100000000101",
        "100000000011100000000001",
        "100000000000000000000001",
        "111111111111111111111111",
    ],
    # Wave 5
    [
        "111111111111111111111111",
        "100000000000000000000001",
        "101111111110011111111101",
        "101000000010010000000101",
        "101011111010010111110101",
        "101011111000000111110101",
        "101000000011110000000101",
        "101111111011110111111101",
        "100000000011110000000001",
        "111101111111111111101111",
        "100001000000000000100001",
        "101101011110033330101101",
        "101100011110033330001101",
        "100001000000000000100001",
        "111101111111111111101111",
        "100000000000000000000001",
        "101111111101101111111101",
        "100000000010010000000001",
        "111111100010010001111111",
        "100000100000000001000001",
        "101101111100011111011001",
        "101000000000000000000101",
        "100000000000000000000001",
        "111111111111111111111111",
    ]
]

class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Pyxel FPS: Wave & Flee (AI Mode)", fps=60)
        self.init_sounds()
        
        self.is_mobile = False
        try:
            import js
            ua = js.navigator.userAgent.lower()
            if any(k in ua for k in ["iphone", "ipad", "ipod", "android", "mobile"]):
                self.is_mobile = True
        except ImportError:
            pass
            
        # スマホ環境の場合はタッチ操作（マウス操作）を有効にする
        if self.is_mobile:
            pyxel.mouse(True)

        self.state = "TITLE"
        self.max_wave = MAX_WAVES 
        self.wave = 1
        self.ai_mode = False 
        
        self.invincible = False
        self.cheat_sequence = [pyxel.KEY_UP, pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_DOWN]
        self.cheat_index = 0
        
        self.px, self.py, self.pa = 2.5, 2.5, 0
        self.hp = 100
        
        self.flash_timer = 0
        self.damage_flash = 0
        self.shake = 0
        self.wave_announce_timer = 0
        self.particles = []
        self.projectiles = []
        self.explosions = []
        self.health_items = []
        self.clear_timer = 0
        
        pyxel.run(self.update, self.draw)

    def init_sounds(self):
        pyxel.sounds[0].set("c2e2g2b2 c3g2e2c2 a2c3e3g3 f2a2c3e3", "p", "6666 6666 7777 5555", "s", 25)
        pyxel.sounds[1].set("a2g2c1", "n", "7", "f", 4)
        pyxel.sounds[2].set("c1c0", "s", "7", "v", 6)
        pyxel.sounds[3].set("c3e3g3c4", "t", "7", "v", 6)
        pyxel.sounds[4].set("g1f1e1d1c1", "n", "7", "f", 8)
        pyxel.sounds[5].set("c3e3g3c4g3c4", "t", "7", "v", 8)

    def load_map(self):
        m_data = MAPS[min(self.wave - 1, len(MAPS) - 1)]
        self.map = [[int(c) for c in row] for row in m_data]
        self.map_w = len(self.map[0])
        self.map_h = len(self.map)

    def is_open_space(self, x, y):
        ix, iy = int(x), int(y)
        if self.wall(ix, iy) > 0: return False
        open_count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= ix + dx < self.map_w and 0 <= iy + dy < self.map_h:
                    if self.map[iy + dy][ix + dx] == 0:
                        open_count += 1
        return open_count >= 5

    def init_wave(self):
        self.load_map()
        self.px, self.py, self.pa = 2.5, 2.5, math.pi/4
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = int(self.px) + dx, int(self.py) + dy
                if 0 <= nx < self.map_w and 0 <= ny < self.map_h:
                    self.map[ny][nx] = 0

        self.hp = 100
        self.flash_timer = 0
        self.wave_announce_timer = 120
        self.particles = []
        self.projectiles = []
        self.explosions = []
        self.enemies = []
        self.health_items = []
        
        pyxel.play(0, 5)
        
        for _ in range(2):
            while True:
                rx, ry = random.uniform(2, self.map_w-2), random.uniform(2, self.map_h-2)
                if self.is_open_space(rx, ry) and math.sqrt((rx-self.px)**2 + (ry-self.py)**2) > 4:
                    self.health_items.append({"x": rx, "y": ry, "alive": True})
                    break

        boss_hp = 15 + (self.wave * 5)
        while True:
            rx, ry = random.uniform(2, self.map_w-2), random.uniform(2, self.map_h-2)
            if self.is_open_space(rx, ry) and math.sqrt((rx-self.px)**2 + (ry-self.py)**2) > 8:
                self.enemies.append({"x": rx, "y": ry, "alive": True, "type": "boss", "hp": boss_hp, "max_hp": boss_hp, "timer": 0})
                break

        num_enemies = self.wave * 2 + 1
        for _ in range(num_enemies):
            while True:
                rx, ry = random.uniform(2, self.map_w-2), random.uniform(2, self.map_h-2)
                if self.is_open_space(rx, ry) and math.sqrt((rx-self.px)**2 + (ry-self.py)**2) > 6:
                    r = random.random()
                    if r < 0.3 + (self.wave * 0.05): etype = "brute"
                    elif r < 0.7: etype = "soldier"
                    else: etype = "drone"
                    
                    hp = 8 if etype == "brute" else (4 if etype == "soldier" else 2)
                    self.enemies.append({"x": rx, "y": ry, "alive": True, "type": etype, "hp": hp, "max_hp": hp, "timer": random.randint(0,100)})
                    break

    def wall(self, x, y):
        if x < 0 or y < 0 or x >= self.map_w or y >= self.map_h: return 1
        return self.map[int(y)][int(x)]

    def add_particles(self, x, y, count, col_choices, is_blood=False):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.05, 0.25)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            vz = random.uniform(-0.15, 0.2) if not is_blood else random.uniform(0, 0.2)
            life = random.randint(12, 25)
            col = random.choice(col_choices)
            self.particles.append([x, y, 0.5, vx, vy, vz, life, col])
        if len(self.particles) > 60:
            self.particles = self.particles[-60:]

    def add_explosion(self, x, y, colors=None, power=1.0):
        if colors is None:
            colors = [7, 10, 12, 9]
        self.explosions.append({
            "x": x, "y": y, "life": 14, "max_life": 14, "power": power,
            "colors": colors, "seed": random.randint(0, 9999)
        })
        if len(self.explosions) > 12:
            self.explosions.pop(0)
        self.add_particles(x, y, int(8 + 8 * power), colors)
        pyxel.play(0, 4)

    def update(self):
        if self.shake > 0: self.shake -= 1
        if self.damage_flash > 0: self.damage_flash -= 1
        if self.wave_announce_timer > 0: self.wave_announce_timer -= 1

        if self.state == "TITLE":
            if pyxel.play_pos(1) is None:
                pyxel.play(1, 0, loop=True)
                
            for key in [pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT]:
                if pyxel.btnp(key):
                    if key == self.cheat_sequence[self.cheat_index]:
                        self.cheat_index += 1
                        if self.cheat_index == len(self.cheat_sequence):
                            self.invincible = True
                            self.cheat_index = 0
                    else:
                        self.cheat_index = 1 if key == self.cheat_sequence[0] else 0

            # モバイル時のタップでも開始できるように追加
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or (self.is_mobile and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
                self.state = "PLAY"
                self.wave = 1
                self.init_wave()
                
        elif self.state == "PLAY":
            if pyxel.play_pos(1) is None:
                pyxel.play(1, 0, loop=True)
                
            if pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.KEY_CTRL) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                self.ai_mode = not self.ai_mode
                
            # モバイルのAUTOボタン判定
            if self.is_mobile and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                if WIDTH - 45 <= mx <= WIDTH - 5 and 5 <= my <= 20:
                    self.ai_mode = not self.ai_mode
                    
            self.update_play()
            
        elif self.state == "GAMEOVER":
            pyxel.stop()
            # モバイル時のタップでもリトライできるように追加
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or (self.is_mobile and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
                self.state = "TITLE"
                self.invincible = False
                
        elif self.state == "CLEAR":
            self.clear_timer += 1
            self.pa += 0.005
            dx, dy = math.cos(self.pa) * 0.02, math.sin(self.pa) * 0.02
            if not self.wall(self.px + dx, self.py): self.px += dx
            if not self.wall(self.px, self.py + dy): self.py += dy
            
            if self.clear_timer > 1800:
                self.state = "TITLE"
                self.invincible = False

    def update_play(self):
        move_forward, move_backward, turn_left, turn_right, shoot_trigger = False, False, False, False, False

        if self.ai_mode:
            nearest_enemy, min_dist = None, 999.0
            for en in self.enemies:
                if en["alive"]:
                    dist = math.sqrt((en["x"] - self.px)**2 + (en["y"] - self.py)**2)
                    if dist < min_dist:
                        min_dist, nearest_enemy = dist, en
            
            if nearest_enemy:
                target_angle = math.atan2(nearest_enemy["y"] - self.py, nearest_enemy["x"] - self.px)
                angle_diff = (target_angle - self.pa + math.pi) % (math.pi * 2) - math.pi
                
                ai_turn_speed = ROT_SPEED * 2.5
                if abs(angle_diff) > ai_turn_speed:
                    if angle_diff > 0: self.pa += ai_turn_speed
                    else: self.pa -= ai_turn_speed
                else:
                    self.pa = target_angle
                
                check_dx, check_dy = math.cos(self.pa) * 1.5, math.sin(self.pa) * 1.5
                if self.wall(self.px + check_dx, self.py + check_dy):
                    self.pa += 0.3
                    
                if min_dist > 4.0: move_forward = True
                elif min_dist < 3.0: move_backward = True
                
                if min_dist < 15.0 and abs(angle_diff) < 1.2 and self.flash_timer == 0:
                    shoot_trigger = True
            else:
                self.pa += ROT_SPEED * 2.0
        else:
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) < -30: turn_left = True
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) > 30: turn_right = True
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) < -30: move_forward = True
            if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) > 30: move_backward = True
            
            if pyxel.btn(pyxel.KEY_C) or pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER): 
                shoot_trigger = True
                
            # モバイル環境時の仮想コントローラ入力判定
            if self.is_mobile and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                
                # 仮想D-Pad（少し広めに当たり判定を設定）
                if 20 <= mx <= 50 and HEIGHT - 70 <= my <= HEIGHT - 40: move_forward = True
                if 20 <= mx <= 50 and HEIGHT - 30 <= my <= HEIGHT: move_backward = True
                if 0 <= mx <= 30 and HEIGHT - 50 <= my <= HEIGHT - 20: turn_left = True
                if 40 <= mx <= 70 and HEIGHT - 50 <= my <= HEIGHT - 20: turn_right = True
                
                # 仮想SHOOTボタン
                if math.hypot(mx - (WIDTH - 30), my - (HEIGHT - 35)) <= 30:
                    shoot_trigger = True

        if turn_left: self.pa -= ROT_SPEED
        if turn_right: self.pa += ROT_SPEED
        
        dx, dy = math.cos(self.pa) * MOVE_SPEED, math.sin(self.pa) * MOVE_SPEED
        if move_forward:
            if not self.wall(self.px + dx, self.py): self.px += dx
            if not self.wall(self.px, self.py + dy): self.py += dy
        if move_backward:
            if not self.wall(self.px - dx, self.py): self.px -= dx
            if not self.wall(self.px, self.py - dy): self.py -= dy

        self.is_moving = move_forward or move_backward

        for item in self.health_items:
            if item["alive"]:
                dist = math.hypot(item["x"] - self.px, item["y"] - self.py)
                if dist < 0.6:
                    self.hp = min(100, self.hp + 25)
                    item["alive"] = False
                    pyxel.play(0, 3)
                    self.add_particles(self.px, self.py, 15, [11, 7, 10], is_blood=False)

        if shoot_trigger and self.flash_timer == 0:
            self.flash_timer = 10
            self.shake = 3
            pyxel.play(0, 1)
            vx = math.cos(self.pa) * 0.45
            vy = math.sin(self.pa) * 0.45
            self.projectiles.append({"x": self.px, "y": self.py, "vx": vx, "vy": vy, "type": "player"})
            if len(self.projectiles) > 40:
                self.projectiles.pop(0)

        if self.flash_timer > 0: self.flash_timer -= 1

        for en in self.enemies:
            if not en["alive"]: continue
            en["timer"] += 1
            dist = math.sqrt((en["x"]-self.px)**2 + (en["y"]-self.py)**2)
            
            edx, edy = 0, 0
            if en["type"] == "brute":
                speed = 0.02
                edx = speed if self.px > en["x"] else -speed
                edy = speed if self.py > en["y"] else -speed
                if dist < 0.8 and pyxel.frame_count % 30 == 0:
                    if not self.invincible:
                        self.hp -= 20
                        self.damage_flash = 10
                        self.shake = 5
                        pyxel.play(0, 2)
                    
            elif en["type"] == "soldier":
                speed = 0.03
                if dist > 5:
                    edx = speed if self.px > en["x"] else -speed
                    edy = speed if self.py > en["y"] else -speed
                elif dist < 3:
                    edx = -speed if self.px > en["x"] else speed
                    edy = -speed if self.py > en["y"] else speed
                    
                if dist < 8 and en["timer"] % 60 == 0:
                    ex, ey = (self.px - en["x"])/max(0.001, dist), (self.py - en["y"])/max(0.001, dist)
                    self.projectiles.append({"x": en["x"], "y": en["y"], "vx": ex*0.15, "vy": ey*0.15, "type": "enemy"})
                    if len(self.projectiles) > 40:
                        self.projectiles.pop(0)

            elif en["type"] == "boss":
                speed = 0.012
                edx = speed if self.px > en["x"] else -speed
                edy = speed if self.py > en["y"] else -speed
                if dist < 12 and en["timer"] % 40 == 0:
                    ex, ey = (self.px - en["x"])/max(0.001, dist), (self.py - en["y"])/max(0.001, dist)
                    self.projectiles.append({"x": en["x"], "y": en["y"], "vx": ex*0.2, "vy": ey*0.2, "type": "enemy"})
                    if len(self.projectiles) > 40:
                        self.projectiles.pop(0)
                    
            elif en["type"] == "drone":
                speed = 0.05
                base_dx = speed if self.px > en["x"] else -speed
                base_dy = speed if self.py > en["y"] else -speed
                zig = math.sin(en["timer"] * 0.1) * 0.05
                edx = base_dx + zig * (-base_dy)
                edy = base_dy + zig * base_dx
                if dist < 0.6 and pyxel.frame_count % 15 == 0:
                    if not self.invincible:
                        self.hp -= 5
                        self.damage_flash = 5
                        pyxel.play(0, 2)

            if not self.wall(en["x"] + edx, en["y"]): en["x"] += edx
            if not self.wall(en["x"], en["y"] + edy): en["y"] += edy

        for proj in self.projectiles[:]:
            proj["x"] += proj["vx"]
            proj["y"] += proj["vy"]
            
            if self.wall(proj["x"], proj["y"]):
                self.projectiles.remove(proj)
                cols = [8, 9, 10, 7] if proj["type"] == "enemy" else [6, 12, 7, 10]
                self.add_explosion(proj["x"], proj["y"], cols, 0.9)
                continue
            
            if proj["type"] == "enemy":
                p_dist = math.sqrt((proj["x"]-self.px)**2 + (proj["y"]-self.py)**2)
                if p_dist < 0.5:
                    if not self.invincible:
                        self.hp -= 15
                        self.damage_flash = 10
                        self.shake = 5
                        pyxel.play(0, 2)
                    self.projectiles.remove(proj)
                    self.add_explosion(self.px, self.py, [8, 10, 7, 2], 1.0)
            else:
                hit_enemy = False
                for en in self.enemies:
                    if not en["alive"]: continue
                    e_dist = math.sqrt((proj["x"]-en["x"])**2 + (proj["y"]-en["y"])**2)
                    if e_dist < 0.6:
                        en["hp"] -= 4
                        self.add_explosion(en["x"], en["y"], [7, 8, 10, 12], 1.0)
                        self.add_particles(en["x"], en["y"], 8, [7, 9, 10, 12], is_blood=True)
                        if en["hp"] <= 0:
                            en["alive"] = False
                            self.add_explosion(en["x"], en["y"], [7, 8, 9, 10, 12], 1.8)
                            self.add_particles(en["x"], en["y"], 25, [7, 8, 9, 10, 12])
                        hit_enemy = True
                        break
                if hit_enemy:
                    self.projectiles.remove(proj)

        for ex in self.explosions[:]:
            ex["life"] -= 1
            if ex["life"] <= 0:
                self.explosions.remove(ex)

        for p in self.particles[:]:
            p[0] += p[3]; p[1] += p[4]; p[2] += p[5]
            p[5] -= 0.005
            if p[2] < 0: p[2] = 0; p[5] *= -0.5
            p[6] -= 1
            if p[6] <= 0: self.particles.remove(p)

        if self.hp <= 0:
            self.state = "GAMEOVER"
            return
            
        if not any(en["alive"] for en in self.enemies):
            self.wave += 1
            if self.wave > self.max_wave:
                self.state = "CLEAR"
                self.clear_timer = 0
                pyxel.play(0, 5)
            else:
                self.init_wave()

    def draw(self):
        cx = random.randint(-self.shake, self.shake) if self.shake else 0
        cy = random.randint(-self.shake, self.shake) if self.shake else 0
        pyxel.camera(cx, cy)

        if self.state == "TITLE": self.draw_title()
        elif self.state == "PLAY": self.draw_play()
        elif self.state == "GAMEOVER": self.draw_gameover()
        elif self.state == "CLEAR": self.draw_clear()

        pyxel.camera(0, 0)

    def _panel(self, x, y, w, h, fill=0, border=5, accent=12):
        pyxel.rect(x, y, w, h, fill)
        pyxel.rectb(x, y, w, h, border)
        if w > 8 and h > 8:
            pyxel.line(x + 2, y + 2, x + w - 3, y + 2, accent)

    def _draw_shadow_text(self, x, y, s, color):
        pyxel.text(x + 1, y + 1, s, 0)
        pyxel.text(x, y, s, color)

    def draw_title(self):
        pyxel.cls(0)
        t = pyxel.frame_count

        for y in range(HEIGHT):
            c = 1 if y < HEIGHT * 0.42 else (5 if y < HEIGHT * 0.7 else 0)
            pyxel.line(0, y, WIDTH - 1, y, c)

        for i in range(42):
            sx = (i * 47 + 17) % WIDTH
            sy = (i * 29 + 11) % 78
            tw = 7 if (t // 8 + i) % 7 == 0 else 1
            pyxel.pset(sx, sy, tw)

        horizon = HEIGHT // 2 + 17
        pyxel.line(0, horizon, WIDTH - 1, horizon, 8)
        pyxel.line(0, horizon + 1, WIDTH - 1, horizon + 1, 2)

        for i in range(14):
            yy = horizon + int((i + (t % 20) / 20) ** 1.65 * 3)
            if yy < HEIGHT: pyxel.line(0, yy, WIDTH - 1, yy, 1 if i % 3 else 5)
        for i in range(-12, 13):
            bx = WIDTH // 2 + i * 13
            pyxel.line(WIDTH // 2, horizon, bx, HEIGHT, 1)

        title = "T.K PRESENTS"
        sub = "Pyxel FPS: Wave & Flee (AI Mode)"
        tx = WIDTH // 2 - len(title) * 2
        sx = WIDTH // 2 - len(sub) * 2
        pyxel.text(tx + 2, 30 + 2, title, 1)
        pyxel.text(tx, 30, title, 10)
        pyxel.text(tx - 1, 29, title, 7)
        pyxel.text(sx, 43, sub, 12)

        if self.invincible:
            pyxel.text(WIDTH // 2 - 28, 55, "- INVINCIBLE MODE -", 10)

        self._panel(49, 67, 158, 35, 0, 5, 12)
        pyxel.text(67, 75, "TACTICAL SIMULATION", 6)
        if t % 60 < 42:
            # モバイル環境の表示切替
            if self.is_mobile:
                pyxel.text(80, 88, "> TAP TO START <", 10)
            else:
                pyxel.text(72, 88, "> PRESS C/B OR SPACE <", 10)
        pyxel.text(65, 117, "[ A / X ]  AUTO PILOT", 7)
        pyxel.text(91, 132, "(C) 2026 MIRAI WORK", 5)

    def draw_gameover(self):
        pyxel.cls(0)
        t = pyxel.frame_count

        for y in range(HEIGHT):
            c = 8 if ((y + t // 3) % 13 == 0) else (2 if y % 5 == 0 else 0)
            pyxel.line(0, y, WIDTH - 1, y, c)

        for i in range(70):
            y = (i * 31 + t * (i % 3 + 1)) % HEIGHT
            x = (i * 53 + t) % WIDTH
            ln = 4 + (i * 7) % 35
            pyxel.line(x, y, min(WIDTH - 1, x + ln), y, random.choice([2, 8, 10]))

        self._panel(38, 42, 180, 61, 0, 8, 8)
        msg = "SIGNAL LOST"
        x = WIDTH // 2 - len(msg) * 2
        pyxel.text(x + 2, 56 + 2, msg, 2)
        pyxel.text(x, 56, msg, 8)
        pyxel.text(72, 72, "COMBAT SYSTEM OFFLINE", 7)

        if t % 60 < 40:
            if self.is_mobile:
                pyxel.text(72, 90, "- TAP TO RETRY -", 10)
            else:
                pyxel.text(62, 90, "- PRESS C/B TO RETRY -", 10)

    def draw_clear(self):
        self.flash_timer = 0
        self.draw_play()

        t = self.clear_timer
        
        if t < 500:
            index = (t // 100) % 5
            
            intros = [
                ("PLAYER AGENT", "SURVIVOR", "Brave human combatant who survived."),
                ("DRONE", "RECON DRONE", "Fast flying tracking unit."),
                ("SOLDIER", "ASSAULT", "Human-type rogue with blasters."),
                ("BRUTE", "HEAVY ARMOR", "Heavy armor & powerful melee."),
                ("BOSS", "OMEGA COMMANDER", "Supreme leader of hostile forces.")
            ]
            name, role, desc = intros[index]

            pw, ph = 240, 68
            px_pos = WIDTH // 2 - pw // 2
            py_pos = HEIGHT // 2 - ph // 2
            
            pyxel.rect(px_pos, py_pos, pw, ph, 0)
            pyxel.rectb(px_pos, py_pos, pw, ph, 5)
            pyxel.rectb(px_pos + 2, py_pos + 2, pw - 4, ph - 4, 12)

            cx_icon = px_pos + 42
            cy_icon = py_pos + ph // 2
            self.draw_intro_graphic(index, cx_icon, cy_icon)

            tx = px_pos + 82
            pyxel.text(tx, py_pos + 12, "THE ENEMY & YOU FILE", 6)
            self._draw_shadow_text(tx, py_pos + 23, name, 10)
            pyxel.text(tx, py_pos + 33, f"[{role}]", 7)
            pyxel.text(tx, py_pos + 47, desc, 13)

        else:
            panel_w, panel_h = 220, 120
            panel_x = WIDTH // 2 - panel_w // 2
            panel_y = HEIGHT // 2 - panel_h // 2
            pyxel.rect(panel_x, panel_y, panel_w, panel_h, 0)
            pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 5)
            pyxel.rectb(panel_x + 2, panel_y + 2, panel_w - 4, panel_h - 4, 12)

            roll_progress = t - 500
            cy = HEIGHT - roll_progress * 0.4
            
            credits_data = [
                ("MISSION CLEAR", 10),
                ("CONGRATULATIONS!", 7),
                ("", 0),
                ("CREDITS", 12),
                ("", 0),
                ("DIRECTOR & PROGRAMMER", 11),
                ("T. K.", 7),
                ("", 0),
                ("COOPERATE", 11),
                ("TEAM T.D", 7),
                ("", 0),
                ("SOUND & ARRANGEMENT", 11),
                ("M. T.", 7),
                ("", 0),
                ("SPECIAL THANKS", 11),
                ("YOU & ALL PLAYERS!", 10),
                ("PRESENTED BY", 13),
                ("(C)MIRAI WORK 2026", 13)
            ]

            for i, (s, c) in enumerate(credits_data):
                yy = int(cy + i * 20)
                if panel_y + 8 < yy < panel_y + panel_h - 12 and s:
                    x = WIDTH // 2 - len(s) * 2
                    self._draw_shadow_text(x, yy, s, c)

    def draw_intro_graphic(self, index, x, y):
        if index == 0:  # Player
            pyxel.rect(x - 8, y - 12, 16, 20, 1)
            pyxel.rect(x - 6, y - 10, 12, 10, 6)
            pyxel.rect(x - 2, y - 2, 4, 10, 12)
            pyxel.rect(x - 3, y - 14, 6, 4, 7)
        elif index == 1:  # Drone
            pyxel.circ(x, y, 10, 13)
            pyxel.circb(x, y, 10, 12)
            pyxel.circ(x, y, 4, 10)
            pyxel.line(x - 12, y - 8, x + 12, y + 8, 7)
        elif index == 2:  # Soldier
            pyxel.rect(x - 8, y - 12, 16, 22, 3)
            pyxel.rect(x - 4, y - 8, 8, 8, 4)
            pyxel.line(x - 8, y + 2, x + 8, y + 2, 11)
        elif index == 3:  # Brute
            pyxel.rect(x - 12, y - 14, 24, 26, 2)
            pyxel.rectb(x - 12, y - 14, 24, 26, 4)
            pyxel.rect(x - 6, y - 8, 12, 8, 3)
            pyxel.rect(x - 4, y - 4, 8, 4, 10)
        elif index == 4:  # Boss
            pyxel.rect(x - 16, y - 16, 32, 28, 8)
            pyxel.rectb(x - 16, y - 16, 32, 28, 2)
            pyxel.circ(x, y - 2, 6, 10)
            pyxel.circ(x, y - 2, 2, 7)
            pyxel.rect(x - 12, y - 12, 4, 4, 1)
            pyxel.rect(x + 8, y - 12, 4, 4, 1)

    def draw_play(self):
        half = HEIGHT // 2
        flash = self.flash_timer > 0

        sky_cols = [1, 1, 5, 5, 13, 13]
        for y in range(half):
            idx = min(len(sky_cols) - 1, int(y / half * len(sky_cols)))
            pyxel.line(0, y, WIDTH - 1, y, sky_cols[idx])

        for y in range(max(0, half - 10), half):
            if y % 3 == 0: pyxel.line(0, y, WIDTH - 1, y, 13)

        for i in range(32):
            sx = (i * 71 + 19) % WIDTH
            sy = (i * 23 + 7) % max(1, half - 14)
            if (i + pyxel.frame_count // 20) % 9 != 0:
                pyxel.pset(sx, sy, 7 if i % 5 == 0 else 1)

        for y in range(half, HEIGHT):
            d = (y - half + 1) / (HEIGHT - half)
            col = 0 if d < 0.18 else (1 if d < 0.45 else 5)
            pyxel.line(0, y, WIDTH - 1, y, col)

        for i in range(12):
            yy = half + int((i / 12) ** 2.0 * (HEIGHT - half))
            if yy < HEIGHT: pyxel.line(0, yy, WIDTH - 1, yy, 1 if i % 3 else 5)
        
        angle_offset = (self.pa * 18) % 24
        for i in range(-14, 15):
            bx = WIDTH // 2 + int(i * 12 - angle_offset)
            pyxel.line(WIDTH // 2, half, bx, HEIGHT, 1)

        if flash: pyxel.rect(0, 0, WIDTH, HEIGHT, 7)
        z_buffer = [999.0] * WIDTH

        wave_wall_colors = {
            1: 6,   # Wave 1: ブルー系
            2: 11,  # Wave 2: グリーン系
            3: 8,   # Wave 3: レッド系
            4: 2,   # Wave 4: パープル系
            5: 9,   # Wave 5: イエロー系
        }
        wall_col = wave_wall_colors.get(self.wave, 6)
        if flash: wall_col = 7

        for x in range(WIDTH):
            ray_angle = self.pa - FOV / 2 + FOV * x / WIDTH
            vx, vy = math.cos(ray_angle), math.sin(ray_angle)
            mx, my = int(self.px), int(self.py)

            delta_x = abs(1 / vx) if vx != 0 else 1e30
            delta_y = abs(1 / vy) if vy != 0 else 1e30

            if vx < 0: sx, side_x = -1, (self.px - mx) * delta_x
            else: sx, side_x = 1, (mx + 1 - self.px) * delta_x
            if vy < 0: sy, side_y = -1, (self.py - my) * delta_y
            else: sy, side_y = 1, (my + 1 - self.py) * delta_y

            side = 0
            for _ in range(64):
                if side_x < side_y:
                    side_x += delta_x; mx += sx; side = 0
                else:
                    side_y += delta_y; my += sy; side = 1
                if self.wall(mx, my) > 0: break

            if side == 0: dist = (mx - self.px + (1 - sx) / 2) / vx
            else: dist = (my - self.py + (1 - sy) / 2) / vy

            dist = max(0.05, dist * math.cos(ray_angle - self.pa))
            z_buffer[x] = dist
            h = int(HEIGHT / dist)

            if dist > 12: col = 0
            elif dist > 9: col = max(0, wall_col - 2)
            else:
                col = wall_col if side == 1 else max(0, wall_col - 1)

            top = max(0, half - h // 2)
            bottom = min(HEIGHT - 1, half + h // 2)
            pyxel.line(x, top, x, bottom, col)

        self.draw_sprites(z_buffer)
        if self.state != "CLEAR":
            self.draw_ui()

        if self.wave_announce_timer > 0:
            ann_w = 140
            ann_h = 28
            ax = WIDTH // 2 - ann_w // 2
            ay = HEIGHT // 2 - ann_h // 2
            pyxel.rect(ax, ay, ann_w, ann_h, 0)
            pyxel.rectb(ax, ay, ann_w, ann_h, 10)
            pyxel.text(ax + 34, ay + 6, f"- WAVE {self.wave} -", 7)
            pyxel.text(ax + 26, ay + 16, "MISSION START", 10)

        if self.damage_flash > 0:
            intensity = 8 if self.damage_flash % 3 else 2
            pyxel.rectb(0, 0, WIDTH - 1, HEIGHT - 1, intensity)
            pyxel.rectb(2, 2, WIDTH - 5, HEIGHT - 5, intensity)

    def draw_sprites(self, z_buffer):
        sprites = []
        for en in self.enemies:
            if en["alive"]:
                dist = math.hypot(en["x"] - self.px, en["y"] - self.py)
                sprites.append((dist, en["x"], en["y"], en["type"], en))
        for item in self.health_items:
            if item["alive"]:
                dist = math.hypot(item["x"] - self.px, item["y"] - self.py)
                sprites.append((dist, item["x"], item["y"], "health", item))
        for ex in self.explosions:
            dist = math.hypot(ex["x"] - self.px, ex["y"] - self.py)
            sprites.append((dist, ex["x"], ex["y"], "explosion", ex))
        for p in self.particles:
            dist = math.hypot(p[0] - self.px, p[1] - self.py)
            sprites.append((dist, p[0], p[1], "particle", p))
        for pr in self.projectiles:
            dist = math.hypot(pr["x"] - self.px, pr["y"] - self.py)
            sprites.append((dist, pr["x"], pr["y"], "projectile", pr))

        sprites.sort(key=lambda s: s[0], reverse=True)
        for sp in sprites:
            self.draw_at_3d(sp[1], sp[2], sp[3], sp[0], z_buffer, sp[4])

    def draw_at_3d(self, x, y, sp_type, dist, z_buffer, obj_data):
        if dist < 0.01: return

        angle = math.atan2(y - self.py, x - self.px)
        rel_angle = (angle - self.pa + math.pi) % (math.pi * 2) - math.pi

        if abs(rel_angle) >= FOV / 2 + 0.25: return
        sx = int((rel_angle / FOV + 0.5) * WIDTH)
        if not (0 <= sx < WIDTH): return
        
        if dist > 0.8 and (z_buffer[sx] + 0.3 < dist): return

        size = max(2, int(HEIGHT / dist))
        t = pyxel.frame_count

        if sp_type == "health":
            bob = int(math.sin(t * 0.15) * max(1, size // 10))
            yy = HEIGHT // 2 + bob
            r = max(2, size // 6)
            pyxel.rect(sx - r // 2, yy - r, r, r * 2, 7)
            pyxel.rectb(sx - r // 2, yy - r, r, r * 2, 3)
            pyxel.rect(sx - r // 4, yy - r // 2, r // 2, r, 11)
            pyxel.rect(sx - r // 2, yy - r // 4, r, r // 2, 11)
            return

        if sp_type == "explosion":
            life = obj_data["life"]
            max_life = obj_data["max_life"]
            progress = 1.0 - life / max_life
            power = obj_data["power"]

            yy = HEIGHT // 2
            if progress < 0.55:
                grow = progress / 0.55
                radius = max(1, int(size * 0.05 + size * 0.42 * grow * power))
            else:
                shrink = (progress - 0.55) / 0.45
                radius = max(1, int(size * 0.47 * (1.0 - shrink) * power))

            cols = obj_data["colors"]
            pulse = 1 if (pyxel.frame_count + obj_data["seed"]) % 3 else 0

            pyxel.circ(sx, yy, radius + 2, 0)
            pyxel.circ(sx, yy, radius, cols[1 if pulse else 0])
            if radius > 3:
                pyxel.circb(sx, yy, radius, cols[-1])
                pyxel.circ(sx, yy, max(2, radius // 2), 7)

            ray_count = 8
            for i in range(ray_count):
                ang = i * math.pi * 2 / ray_count + obj_data["seed"] * 0.001
                ray_len = int(radius * (1.2 + ((i * 7) % 5) * 0.15))
                x2 = sx + int(math.cos(ang) * ray_len)
                y2 = yy + int(math.sin(ang) * ray_len)
                pyxel.line(sx, yy, x2, y2, cols[(i + 2) % len(cols)])

            return

        if sp_type == "particle":
            pz = obj_data[2]
            yy = HEIGHT // 2 + int(size * (0.55 - pz))
            r = max(1, size // 16)
            pyxel.circ(sx, yy, r + 1, 0)
            pyxel.pset(sx, yy, obj_data[7])
            return

        if sp_type == "projectile":
            yy = HEIGHT // 2

            r = max(2, size // 13)
            color = 12 if obj_data.get("type") == "player" else 10

            pyxel.line(sx, yy + r + 2, sx, yy + r + 6, 7)
            if r >= 3:
                pyxel.pset(sx - 1, yy + r + 5, 9)
                pyxel.pset(sx + 1, yy + r + 5, 9)

            pyxel.line(sx - r, yy + r - 1, sx - r - 2, yy + r + 3, color)
            pyxel.line(sx + r, yy + r - 1, sx + r + 2, yy + r + 3, color)

            body_h = max(4, r * 3)
            pyxel.rect(sx - max(1, r // 2), yy - r, max(2, r), body_h, color)

            pyxel.tri(
                sx, yy - r - 4,
                sx - max(1, r // 2), yy - r,
                sx + max(1, r // 2), yy - r,
                7
            )

            pyxel.line(sx, yy - r + 1, sx, yy + r, 7)
            return

        bob = int(math.sin(t * 0.18 + dist) * max(1, size // 12))

        if sp_type == "boss":
            w, h = max(12, int(size * 1.5)), max(16, int(size * 1.8))
            yy = HEIGHT // 2 - h // 4 + bob
            pyxel.rect(sx - w // 2 - 1, yy - h // 2 - 1, w + 2, h + 2, 0)
            pyxel.rect(sx - w // 2, yy + h // 2 - 4, w, 4, 0)
            pyxel.rect(sx - w // 2, yy - h // 2, w, h, 8)
            pyxel.rectb(sx - w // 2, yy - h // 2, w, h, 2)
            pyxel.rect(sx - w // 4, yy - h // 4, w // 2, h // 2, 0)
            eye = 10 if t % 10 < 5 else 7
            pyxel.circ(sx, yy, max(2, w // 6), eye)
            
            hp_ratio = max(0, obj_data["hp"]) / obj_data["max_hp"]
            pyxel.rect(sx - w // 2, yy - h // 2 - 6, w, 3, 1)
            pyxel.rect(sx - w // 2, yy - h // 2 - 6, max(1, int(w * hp_ratio)), 3, 8)

        elif sp_type == "brute":
            w, h = max(6, size), max(8, int(size * 1.18))
            yy = HEIGHT // 2 - h // 4 + bob
            pyxel.rect(sx - w // 2 - 1, yy - h // 2 - 1, w + 2, h + 2, 0)
            pyxel.rect(sx - w // 2, yy + h // 2 - 3, w, 3, 0)
            pyxel.rect(sx - w // 2, yy - h // 2, w, h, 2)
            pyxel.rectb(sx - w // 2, yy - h // 2, w, h, 4)
            pyxel.rect(sx - w // 3, yy - h // 2 + 2, max(2, w * 2 // 3), max(3, h // 3), 3)
            pyxel.line(sx - w // 2 + 2, yy, sx + w // 2 - 2, yy, 1)
            pyxel.line(sx - w // 3, yy + h // 4, sx + w // 3, yy + h // 4, 4)
            eye = 8 if t % 12 < 8 else 10
            pyxel.rect(sx - w // 4, yy - h // 4, max(2, w // 7), max(2, h // 10), eye)
            pyxel.rect(sx + w // 4 - max(2, w // 7), yy - h // 4, max(2, w // 7), max(2, h // 10), eye)
            hp_ratio = max(0, obj_data["hp"]) / obj_data["max_hp"]
            pyxel.rect(sx - w // 2, yy - h // 2 - 5, w, 2, 1)
            pyxel.rect(sx - w // 2, yy - h // 2 - 5, max(1, int(w * hp_ratio)), 2, 8)

        elif sp_type == "soldier":
            w, h = max(5, size // 2), max(8, size)
            yy = HEIGHT // 2 + bob
            pyxel.rect(sx - w // 2 - 1, yy - h // 2 - 1, w + 2, h + 2, 0)
            pyxel.rect(sx - w // 2, yy - h // 2, w, h, 3)
            pyxel.rect(sx - w // 3, yy - h // 5, max(2, w * 2 // 3), max(3, h // 3), 4)
            pyxel.rectb(sx - w // 3, yy - h // 5, max(2, w * 2 // 3), max(3, h // 3), 5)
            pyxel.rect(sx - w // 2 + 1, yy - h // 3, max(2, w - 2), max(2, h // 8), 0)
            pyxel.line(sx - w // 3, yy - h // 3, sx + w // 3, yy - h // 3, 11)
            pyxel.rect(sx + w // 3, yy - 1, max(3, w // 2), max(2, h // 7), 1)
            pyxel.rect(sx + w // 3, yy - 2, max(2, w // 3), 1, 7)
            pyxel.line(sx - w // 4, yy + h // 3, sx - w // 4, yy + h // 2, 5)
            pyxel.line(sx + w // 4, yy + h // 3, sx + w // 4, yy + h // 2, 5)

        elif sp_type == "drone":
            w = max(6, int(size * 0.62))
            yy = HEIGHT // 2 - size // 2 + bob
            if t % 8 < 4:
                pyxel.line(sx - w // 2, yy + w // 2, sx - w // 2 - 2, yy + w // 2 + 4, 7)
                pyxel.line(sx + w // 2, yy + w // 2, sx + w // 2 + 2, yy + w // 2 + 4, 7)
            pyxel.circ(sx, yy, w // 2 + 3, 0)
            pyxel.circ(sx, yy, w // 2, 13)
            pyxel.circb(sx, yy, w // 2, 12)
            pyxel.line(sx - w // 2, yy, sx + w // 2, yy, 12)
            pyxel.line(sx, yy - w // 2, sx, yy + w // 2, 12)
            core = 7 if t % 10 < 5 else 10
            pyxel.circ(sx, yy, max(2, w // 4), 1)
            pyxel.circ(sx, yy, max(1, w // 5), core)
            hp_ratio = max(0, obj_data["hp"]) / obj_data["max_hp"]
            pyxel.rect(sx - w // 2, yy - w // 2 - 5, w, 2, 1)
            pyxel.rect(sx - w // 2, yy - w // 2 - 5, max(1, int(w * hp_ratio)), 2, 10)

    def draw_ui(self):
        t = pyxel.frame_count

        pyxel.rect(0, 0, WIDTH, 39, 0)
        pyxel.line(0, 38, WIDTH - 1, 38, 5)
        pyxel.line(0, 39, WIDTH - 1, 39, 1)

        hp_col = 8 if self.hp < 30 else (10 if self.hp < 60 else 11)
        pyxel.text(7, 5, "VITAL", 7)
        pyxel.rect(7, 14, 78, 7, 1)
        pyxel.rectb(7, 14, 78, 7, 5)
        hpw = int(74 * max(0, min(100, self.hp)) / 100)
        if hpw: pyxel.rect(9, 16, hpw, 3, hp_col)
        pyxel.text(89, 14, f"{max(0, self.hp):03d}", hp_col)

        pyxel.text(7, 27, f"WAVE {self.wave:02d}/{self.max_wave:02d}", 10)
        alive = sum(1 for en in self.enemies if en["alive"])
        pyxel.text(90, 27, f"HOSTILES {alive:02d}", 8 if alive else 11)

        if self.ai_mode:
            pyxel.rect(174, 5, 73, 15, 2)
            pyxel.rectb(174, 5, 73, 15, 10)
            pyxel.text(181, 10, "AUTO PILOT", 10)

        if self.invincible:
            pyxel.rect(174, 22, 73, 15, 3)
            pyxel.rectb(174, 22, 73, 15, 7)
            pyxel.text(180, 27, "INVINCIBLE", 7)

        s = 2
        mw, mh = self.map_w * s, self.map_h * s
        mox, moy = WIDTH - mw - 5, 44
        pyxel.rect(mox - 3, moy - 3, mw + 6, mh + 6, 0)
        pyxel.rectb(mox - 3, moy - 3, mw + 6, mh + 6, 5)

        for y, row in enumerate(self.map):
            for x, v in enumerate(row):
                if v > 0: pyxel.rect(mox + x * s, moy + y * s, s, s, 5)

        for item in self.health_items:
            if item["alive"]:
                ix, iy = int(mox + item["x"] * s), int(moy + item["y"] * s)
                pyxel.pset(ix, iy, 7)
                pyxel.pset(ix - 1, iy, 11)
                pyxel.pset(ix + 1, iy, 11)
                pyxel.pset(ix, iy - 1, 11)
                pyxel.pset(ix, iy + 1, 11)

        for en in self.enemies:
            if en["alive"]:
                if en["type"] == "boss": c = 8
                elif en["type"] == "brute": c = 9
                elif en["type"] == "soldier": c = 11
                else: c = 10
                ex, ey = int(mox + en["x"] * s), int(moy + en["y"] * s)
                pyxel.rect(ex - 1, ey - 1, 3, 3, c)

        pxm, pym = mox + self.px * s, moy + self.py * s
        pyxel.circ(int(pxm), int(pym), 2, 9)
        pyxel.line(int(pxm), int(pym),
                   int(pxm + math.cos(self.pa) * 6),
                   int(pym + math.sin(self.pa) * 6), 7)

        cx, cy = WIDTH // 2, HEIGHT // 2
        cross = 10 if self.flash_timer else 7
        gap = 5 if self.flash_timer else 4
        pyxel.rect(cx - 1, cy - 1, 3, 3, cross)
        pyxel.line(cx - 12, cy, cx - gap, cy, cross)
        pyxel.line(cx + gap, cy, cx + 12, cy, cross)
        pyxel.line(cx, cy - 12, cx, cy - gap, cross)
        pyxel.line(cx, cy + gap, cx, cy + 12, cross)

        moving = hasattr(self, "is_moving") and self.is_moving
        bob_x = math.sin(t * 0.15) * 4 if moving else 0
        bob_y = abs(math.cos(t * 0.15)) * 3 if moving else 0
        recoil = 13 if self.flash_timer else 0
        
        gx = int(WIDTH // 2 + bob_x)
        gy = int(HEIGHT - 18 + bob_y + recoil)

        pyxel.rect(gx - 27, gy + 2, 18, 14, 3)
        pyxel.rect(gx + 8, gy + 2, 18, 14, 3)
        pyxel.line(gx - 26, gy + 3, gx - 10, gy + 3, 5)
        pyxel.line(gx + 10, gy + 3, gx + 25, gy + 3, 5)

        pyxel.rect(gx - 12, gy - 4, 24, 27, 0)
        pyxel.rectb(gx - 12, gy - 4, 24, 27, 5)
        pyxel.rect(gx - 8, gy - 18, 16, 15, 1)
        pyxel.rect(gx - 4, gy - 27, 8, 10, 5)
        pyxel.rect(gx - 2, gy - 33, 4, 8, 6)
        pyxel.rect(gx - 8, gy + 3, 16, 5, 12 if not self.flash_timer else 7)
        pyxel.line(gx - 7, gy + 4, gx + 7, gy + 4, 7)
        pyxel.rect(gx - 5, gy + 9, 10, 7, 4)

        if self.flash_timer:
            r = 8 + (self.flash_timer % 3) * 3
            pyxel.circ(gx, gy - 34, r + 4, 0)
            pyxel.circ(gx, gy - 34, r, 12)
            pyxel.circ(gx, gy - 34, max(2, r // 2), 7)
            for i in range(10):
                ang = (i / 10) * math.pi * 2 + t * 0.08
                ln = random.randint(7, 17)
                pyxel.line(gx, gy - 34,
                           gx + int(math.cos(ang) * ln),
                           gy - 34 + int(math.sin(ang) * ln),
                           random.choice([7, 12, 10]))

        # --- モバイル時のみ仮想コントローラを描画 ---
        if getattr(self, "is_mobile", False):
            pad_col, pad_border = 1, 5
            
            # 仮想D-Pad
            pyxel.rect(25, HEIGHT - 65, 20, 20, pad_col)
            pyxel.rectb(25, HEIGHT - 65, 20, 20, pad_border)
            pyxel.tri(35, HEIGHT - 61, 29, HEIGHT - 51, 41, HEIGHT - 51, 7)
            
            pyxel.rect(25, HEIGHT - 25, 20, 20, pad_col)
            pyxel.rectb(25, HEIGHT - 25, 20, 20, pad_border)
            pyxel.tri(35, HEIGHT - 9, 29, HEIGHT - 19, 41, HEIGHT - 19, 7)
            
            pyxel.rect(5, HEIGHT - 45, 20, 20, pad_col)
            pyxel.rectb(5, HEIGHT - 45, 20, 20, pad_border)
            pyxel.tri(9, HEIGHT - 35, 19, HEIGHT - 41, 19, HEIGHT - 29, 7)
            
            pyxel.rect(45, HEIGHT - 45, 20, 20, pad_col)
            pyxel.rectb(45, HEIGHT - 45, 20, 20, pad_border)
            pyxel.tri(61, HEIGHT - 35, 51, HEIGHT - 41, 51, HEIGHT - 29, 7)
            
            # 仮想SHOOTボタン
            pyxel.circ(WIDTH - 30, HEIGHT - 35, 20, pad_col)
            pyxel.circb(WIDTH - 30, HEIGHT - 35, 20, 8)
            pyxel.circb(WIDTH - 30, HEIGHT - 35, 18, 8)
            pyxel.text(WIDTH - 42, HEIGHT - 37, "SHOOT", 7)
            
            # 仮想AUTO切り替えボタン
            auto_bg = 12 if self.ai_mode else pad_col
            auto_fg = 0 if self.ai_mode else 7
            pyxel.rect(WIDTH - 45, 5, 40, 15, auto_bg)
            pyxel.rectb(WIDTH - 45, 5, 40, 15, 12)
            pyxel.text(WIDTH - 33, 10, "AUTO", auto_fg)

App()
