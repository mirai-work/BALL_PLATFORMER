import math
import sys
import pyxel

TILE = 16
GRAVITY = 0.35
MOVE_SPEED = 2.2
JUMP_POWER = -6
SPRING_POWER = -9.5

levels = [
    [
        "##########################################",
        "#........................................#",
        "#........................................#",
        "#........................................#",
        "#........................................#",
        "#.P.............##########...............#",
        "#...B....#######################.......G.#",
        "##########################################",
        "##########################################",
    ],
    [
        "################################################",
        "#..........................333.....#...........#",
        "#..................................#.........G.#",
        "#.....33...........................#...........#",
        "#...............C...4..........4...####...##111#",
        "#.........##########4.........#4...#...........#",
        "#...................4.........#4...#...........#",
        "#.P.................4.........#4...............#",
        "#...B...............4.........#4...C...........#",
        "#######1####.......###.....111#4..###..111######",
        "############.......#############################",
    ],
    [
        "##############################################",
        "#3333...........#......#.....................#",
        "#3333...........#......#................C....#",
        "#3333...........#......#...............###...#",
        "#...............#......#######111#11111#     #",
        "#...............#............#44.#.....#     #",
        "#....########...C...####     #44.#     #..####",
        "#1111###################     #44##     #     #",
        "#    #     222         #     #44.#     #     #",
        "#    #     222         #     #44.#     ##### #",
        "#    #     222         #     #44.#11111#   22#",
        "#1111...########...#111#     #44.#     #     #",
        "####################111#     #44.#     #.#   #",
        "#          #       #   #     #44.S     #.##11#",
        "#.P        #       #   #      44.S     #     #",
        "#...B         C        #      44.S     #   G.#",
        "##################..111##.C.######11111#     #",
        "###########################################1##",
        "##############################################",
    ],
    [
        "##########################################",
        "#P...B........................#       S22#",
        "#####4###.....................#       S  #",
        "#....4..#..33..2       2    33#3     2#  #",
        "#    4  #         #####    ######     #.G#",
        "#    4            #   #      C.#3     #  #",
        "#    4     S  S   #   #      C..3     #  #",
        "##########1####1###   #1###1######1111#11#",
        "###################   ####################",
    ],
    [
        "##########################################",
        "#     3       33       33  #3334.44444444#",
        "#.B                        #  #4#444444G4#",
        "###  4                     #  #4#44444444#",
        "####141#######11#######11#.#11#4#44444444#",
        "#    4                     #  #4#44444444#",
        "#    4              3      #  #4#44444444#",
        "#    4              3      #  #4#44444444#",
        "#    4   3       22.S3     #  #4#444######",
        "#    4       3      S3  2    S#4#44444444#",
        "#..P.4     ###    B.S3    2   #4#44444444#",
        "#    4    #      #  S3         4#44444444#",
        "#########1#      #  ####S.C.##############",
        "###########       11   ###################",
    ],
]


class Player:

  def __init__(s, x, y):
    s.x = x
    s.y = y
    s.vx = s.vy = 0
    s.on_ground = 0
    s.dir = 1
    s.walk_frame = 0
    s.spring_timer = 0
    s.is_climbing = False

  def rect(s):
    return s.x + 2, s.y + 2, 12, 12


class Ball:

  def __init__(s, x, y):
    s.x = x
    s.y = y
    s.vx = s.vy = 0
    s.radius = 5
    s.on_ground = 0
    s.spring_timer = 0

  def rect(s):
    return s.x - s.radius, s.y - s.radius, s.radius * 2, s.radius * 2


class Game:

  def __init__(s):
    pyxel.init(256, 160, title="BALL PLATFORMER NORMAL EDITION", display_scale=4)
    
    # スマホ環境の判定（Pyxel Web Launcher等を使用した場合）
    s.is_smartphone = False
    if sys.platform == "emscripten":
      try:
        import js
        ua = js.navigator.userAgent.lower()
        # ユーザーエージェントにスマホ系の文字列が含まれているかチェック
        if "iphone" in ua or "ipad" in ua or "ipod" in ua or "android" in ua:
          s.is_smartphone = True
      except ImportError:
        pass

 
    s.build_textures()
    s.init_audio()
    s.current_stage = 0
    s.all_cleared = 0
    s.game_state = "title"
    s.cp_active = False
    s.cp_x = s.cp_y = 0
    s.score = 0
    s.high_score = 0
    s.total_time = 0
    s.summary_timer = 0
    s.time_limit = 1800
    s.credit_y = 110
    s.clear_timer = 0
    s.load_level()
    s.cam_x = s.cam_y = 0
    pyxel.play(2, 17, loop=True)
    pyxel.run(s.update, s.draw)

  def build_textures(s):
    pyxel.images[0].rect(0, 0, 256, 256, 13)
    ART = {
        "BLOCK": [
            "0000000000000000",
            "0333333333333333",
            "0344444444444443",
            "0349944499444443",
            "0349944499444443",
            "0344444444444443",
            "0344499444449943",
            "0344499444449943",
            "0344444444444443",
            "0349944499444443",
            "0349944499444443",
            "0344444444444443",
            "0344499444449943",
            "0344499444449943",
            "0333333333333333",
            "0000000000000000",
        ],
        "BALL": [
            "......0000......",
            "....001CC100....",
            "...01CCDDCC10...",
            "..01CDDDDDDDC1..",
            ".01CDD7777DDDC1.",
            ".01CD777777DDC1.",
            "01CDD77777DDDC10",
            "01CDDD7777DDDDC0",
            "01CDDDDDDDDDDDDC0",
            "01CDDDDDDDDDDDDC0",
            ".01CDDDDDDDDDC1.",
            ".01CDDDDDDDDDC1.",
            "..01CCDDDDDCC1..",
            "...011CCDDCC11..",
            "....001111100...",
            "......0000......",
        ],
        "GOAL": [
            "....00000000....",
            "...08A8A888880..",
            "..08A8A88888880.",
            "..08A8A88888880.",
            "...08A8A888880..",
            "....000000000...",
            ".....0660.......",
            ".....0660.......",
            ".....0660.......",
            ".....0660.......",
            ".....0660.......",
            ".....0660.......",
            ".....0660.......",
            "....055550......",
            "...055555550....",
            "..05555555550...",
        ],
        "SPIKE": [
            "................",
            "................",
            "................",
            "....00....00....",
            "...0660..0660...",
            "...0660..0660...",
            "..067700067700..",
            "..067700067700..",
            ".06677000066770.",
            ".06677000066770.",
            "0666770000667700",
            "0666770000667700",
            "0555555555555550",
            "0555555555555550",
            "0000000000000000",
            "................",
        ],
        "SPRING_N": [
            "................",
            "................",
            "................",
            "................",
            "................",
            "................",
            "................",
            "................",
            "................",
            "................",
            "0000000000000000",
            "0666666666666660",
            "0888888888888880",
            "0888888888888880",
            "0555555555555550",
            "0000000000000000",
        ],
        "SPRING_B": [
            "................",
            "................",
            "................",
            "0000000000000000",
            "0666666666666660",
            "0000000000000000",
            "0888888888888880",
            "0000000000000000",
            "0888888888888880",
            "0000000000000000",
            "0888888888888880",
            "0000000000000000",
            "0888888888888880",
            "0000000000000000",
            "0555555555555550",
            "0000000000000000",
        ],
        "POLE": [
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
        ],
        "CP_OFF": [
            "......060.......",
            "......068880....",
            "......06888880..",
            "......06888880..",
            "......068880....",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
        ],
        "CP_ON": [
            "......060.......",
            "......0611110...",
            "......061111110.",
            "......061111110.",
            "......0611110...",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
            "......060.......",
        ],
        "PLAYER_IDLE": [
            "................",
            ".....0000.......",
            "....0FFFF0......",
            "...0F7777F0.....",
            "...0F0FF0F0.....",
            "...0FFFFF0......",
            "....0FFF0.......",
            "...0888880......",
            "..08D88D80......",
            "..08D88D80......",
            "...0888880......",
            "....0DD0........",
            "...05..50.......",
            "..000..000......",
            ".000....000.....",
            "000......000....",
        ],
        "PLAYER_RIGHT1": [
            "................",
            ".....0000.......",
            "....0FFFF0......",
            "...0F7777F0.....",
            "...0F0FF0F0.....",
            "...0FFFFF0......",
            "....0FFF00......",
            "...0888880......",
            "..08D88D80......",
            "..08D88D80......",
            "...0888880......",
            "....0DD50.......",
            "...50...........",
            "..000....000....",
            ".000......000...",
            "000........000..",
        ],
        "PLAYER_RIGHT2": [
            "................",
            ".....0000.......",
            "....0FFFF0......",
            "...0F7777F0.....",
            "...0F0FF0F0.....",
            "...0FFFFF0......",
            "....0FFF00......",
            "...0888880......",
            "..08D88D80......",
            "..08D88D80......",
            "...0888880......",
            "...50DD0........",
            "..000....05.....",
            "........000.....",
            ".......000......",
            "......000.......",
        ],
        "PLAYER_LEFT1": [
            "................",
            ".......0000.....",
            "......0FFFF0....",
            ".....0F7777F0...",
            ".....0F0FF0F0...",
            "......0FFFFF0...",
            ".....00FFF0.....",
            "....0888880.....",
            "...08D88D80.....",
            "...08D88D80.....",
            "....0888880.....",
            ".....05DD0......",
            "..........50....",
            "....000....000..",
            "...000......000.",
            "..000........000",
        ],
        "PLAYER_LEFT2": [
            "................",
            ".......0000.....",
            "......0FFFF0....",
            ".....0F7777F0...",
            ".....0F0FF0F0...",
            "......0FFFFF0...",
            ".....00FFF0.....",
            "....0888880.....",
            "...08D88D80.....",
            "...08D88D80.....",
            "....0888880.....",
            "......0DD05.....",
            ".....50....000..",
            ".....000........",
            "    000.........",
            "...000..........",
        ],
        "PLAYER_JUMP": [
            "................",
            ".....0000.......",
            "....0FFFF0......",
            "...0F7777F0.....",
            "...0F0FF0F0.....",
            "...0FFFFF0......",
            "....0FFF0.......",
            "...0888880......",
            "..08D88D80......",
            "..08D88D80......",
            "...0888880......",
            "...05....50.....",
            "..000....000....",
            ".000......000...",
            "................",
            "................",
        ],
        "PLAYER_CLIMB1": [
            "................",
            ".....0000.......",
            "....0FFFF0......",
            "...0F7777F0.....",
            "...0F0FF0F0.....",
            "...0FFFFF0......",
            "....0FFF0.......",
            "...0888880......",
            "..08D88D80......",
            "..08D88D80......",
            "...0888880......",
            "...050050.......",
            "...005500.......",
            "...00..00.......",
            "..000..000......",
            "................",
        ],
        "PLAYER_CLIMB2": [
            "................",
            ".....0000.......",
            "....0FFFF0......",
            "...0F7777F0.....",
            "...0F0FF0F0.....",
            "...0FFFFF0......",
            "....0FFF0.......",
            "...0888880......",
            "..08D88D80......",
            "..08D88D80......",
            "...0888880......",
            "...005500.......",
            "...050050.......",
            "...00..00.......",
            "..000..000......",
            "................",
        ],
    }
    pos = {
        "BLOCK": (0, 0),
        "BALL": (16, 0),
        "GOAL": (32, 0),
        "PLAYER_IDLE": (48, 0),
        "PLAYER_RIGHT1": (64, 0),
        "PLAYER_RIGHT2": (80, 0),
        "PLAYER_JUMP": (96, 0),
        "PLAYER_CLIMB1": (112, 0),
        "PLAYER_CLIMB2": (128, 0),
        "PLAYER_LEFT1": (144, 0),
        "PLAYER_LEFT2": (160, 0),
        "SPIKE": (0, 16),
        "SPRING_N": (16, 16),
        "SPRING_B": (32, 16),
        "POLE": (48, 16),
        "CP_OFF": (64, 16),
        "CP_ON": (80, 16),
    }

    def rot(k, a):
      res = []
      for y in range(16):
        r = ""
        for x in range(16):
          r += ART[k][x][15 - y] if a == 90 else ART[k][15 - x][y]
        res.append(r)
      return res

    ART["SPRING_L_N"] = rot("SPRING_N", 90)
    ART["SPRING_L_B"] = rot("SPRING_B", 90)
    ART["SPRING_R_N"] = rot("SPRING_N", 270)
    ART["SPRING_R_B"] = rot("SPRING_B", 270)
    pos.update({
        "SPRING_L_N": (96, 16),
        "SPRING_L_B": (112, 16),
        "SPRING_R_N": (128, 16),
        "SPRING_R_B": (144, 16),
    })

    for k, (ox, oy) in pos.items():
      for y, row in enumerate(ART[k]):
        for x, c in enumerate(row):
          if c not in [".", " "]:
            pyxel.images[0].pset(ox + x, oy + y, int(c, 16))

  def init_audio(s):
    pyxel.sounds[0].set("a3a2", "p", "7", "s", 10)
    pyxel.sounds[1].set("c2c1", "n", "7", "f", 4)
    pyxel.sounds[2].set("c3e3g3c4", "p", "4", "v", 20)
    pyxel.sounds[3].set("g3e3c3", "n", "7", "f", 30)
    pyxel.sounds[4].set(
        "e2e2e2e2 a1a1a1a1 c2c2c2c2 g1g1g1g1", "t", "3", "n", 30
    )
    pyxel.sounds[5].set(
        "c3c3c3c3 e2e2e2e2 g2g2g2g2 c2c2c2c2", "t", "2", "n", 30
    )
    pyxel.sounds[6].set("c3e3", "s", "5", "s", 8)
    pyxel.sounds[7].set("c4e4g4c4", "p", "7", "v", 6)
    pyxel.sounds[8].set("c4g4c4e4g4", "p", "7", "v", 10)

    pyxel.sounds[9].set(
        "f2f2f2f2 d1d1d1d1 f2f2f2f2 c1c1c1c1", "t", "3", "n", 30
    )
    pyxel.sounds[10].set(
        "a3a3a3a3 f2f2f2f2 c3c3c3c3 f2f2f2f2", "t", "2", "n", 30
    )
    pyxel.sounds[11].set(
        "g2g2g2g2 e1e1e1e1 g2g2g2g2 d1d1d1d1", "t", "3", "n", 30
    )
    pyxel.sounds[12].set(
        "b3b3b3b3 g2g2g2g2 d3d3d3d3 g2g2g2g2", "t", "2", "n", 30
    )
    pyxel.sounds[13].set(
        "a2a2a2a2 f1f1f1f1 a2a2a2a2 e1e1e1e1", "t", "3", "n", 30
    )
    pyxel.sounds[14].set(
        "c4c4c4c4 a3a3a3a3 e3e3e3e3 a3a3a3a3", "t", "2", "n", 30
    )

    pyxel.sounds[17].set(
        "c3e3g3b3 c4g3e3c3 g3b3d4f4 e4c4g3e3", "p", "5", "v", 12
    )
    pyxel.sounds[18].set(
        "c4e4g4c4 g4e4c4g3 e4g4b4c4 b4g4e4d4", "p", "6", "v", 16
    )
    pyxel.sounds[19].set("g3f3e3d3 c3", "p", "5", "f", 20)

  def play_stage_bgm(s):
    pyxel.stop(2)
    pyxel.stop(3)
    if s.current_stage == 0:
      pyxel.play(2, 4, loop=True)
      pyxel.play(3, 5, loop=True)
    elif s.current_stage == 1:
      pyxel.play(2, 9, loop=True)
      pyxel.play(3, 10, loop=True)
    elif s.current_stage == 2:
      pyxel.play(2, 11, loop=True)
      pyxel.play(3, 12, loop=True)
    elif s.current_stage == 3:
      pyxel.play(2, 13, loop=True)
      pyxel.play(3, 14, loop=True)
    else:
      pyxel.play(2, 4, loop=True)
      pyxel.play(3, 5, loop=True)

  def text_s(s, x, y, t, c):
    pyxel.text(x + 1, y + 1, t, 0)
    pyxel.text(x, y, t, c)

  def draw_trans_rect(s, x, y, w, h, col):
    for py in range(y, y + h):
      start_x = x + (1 if py % 2 == 1 else 0)
      for px in range(start_x, x + w, 2):
        pyxel.pset(px, py, col)

  def draw_window_box(s, x, y, w, h, border_col1=5, border_col2=6, border_col3=7):
    pyxel.rectb(x, y, w, h, border_col1)
    pyxel.rectb(x + 1, y + 1, w - 2, h - 2, border_col2)
    pyxel.rectb(x + 2, y + 2, w - 4, h - 4, border_col3)
    s.draw_trans_rect(x + 3, y + 3, w - 6, h - 6, 0)

  def btn(s, k, g, t_x, t_y, t_w, t_h, p=False):
    t = False
    if s.is_smartphone:
      if p:
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
          t = (
              t_x <= pyxel.mouse_x <= t_x + t_w
              and t_y <= pyxel.mouse_y <= t_y + t_h
          )
        return pyxel.btnp(k) or pyxel.btnp(g) or t
      else:
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
          t = (
              t_x <= pyxel.mouse_x <= t_x + t_w
              and t_y <= pyxel.mouse_y <= t_y + t_h
          )
        return pyxel.btn(k) or pyxel.btn(g) or t
    else:
      if p:
        return pyxel.btnp(k) or pyxel.btnp(g)
      else:
        return pyxel.btn(k) or pyxel.btn(g)

  def b_L(s):
    return (
        (pyxel.frame_count % 120 < 60)
        if s.game_state == "title"
        else s.btn(
            pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, 5, 130, 30, 25
        )
    )

  def b_R(s):
    return (
        (60 <= pyxel.frame_count % 120 < 120)
        if s.game_state == "title"
        else s.btn(
            pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, 45, 130, 30, 25
        )
    )

  def b_U(s):
    return s.btn(pyxel.KEY_UP, pyxel.GAMEPAD1_BUTTON_DPAD_UP, 0, 0, 0, 0)

  def b_D(s):
    return (
        False
        if s.game_state == "title"
        else s.btn(
            pyxel.KEY_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, 45, 140, 30, 20
        )
    )

  def b_J(s, p):
    return (
        (pyxel.frame_count % 45 == 0)
        if s.game_state == "title"
        else s.btn(
            pyxel.KEY_SPACE, pyxel.GAMEPAD1_BUTTON_A, 210, 125, 40, 25, p
        )
    )

  def b_A(s):
    return (
        s.btn(pyxel.KEY_SPACE, pyxel.GAMEPAD1_BUTTON_A, 0, 0, 256, 160, True)
        or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)
    )

  def b_Rt(s):
    return s.btn(pyxel.KEY_R, pyxel.GAMEPAD1_BUTTON_Y, 220, 3, 30, 14, True)

  def load_level(s, from_checkpoint=False):
    s.tiles = []
    s.spikes = []
    s.springs = []
    s.springs_l = []
    s.springs_r = []
    s.is_cleared = s.is_gameover = 0
    s.clear_timer = 0
    s.balls = []
    s.goal_x = s.goal_y = 0
    s.poles = []
    s.checkpoints = []
    s.particles = []
    s.time_limit = 1800
    p_start_x = p_start_y = 0
    b_starts = []
    for y, row in enumerate(levels[s.current_stage]):
      line = []
      for x, c in enumerate(row):
        if c == "P":
          p_start_x = x * TILE
          p_start_y = y * TILE
          c = "."
        elif c == "G":
          s.goal_x = x * TILE
          s.goal_y = y * TILE
          c = "."
        elif c == "B":
          b_starts.append((x * TILE + 8, y * TILE + 8))
          c = "."
        elif c == "S":
          s.spikes.append((x * TILE, y * TILE))
          c = "."
        elif c == "1":
          s.springs.append((x * TILE, y * TILE))
          c = "."
        elif c == "2":
          s.springs_l.append((x * TILE, y * TILE))
          c = "."
        elif c == "3":
          s.springs_r.append((x * TILE, y * TILE))
          c = "."
        elif c == "4":
          s.poles.append((x * TILE, y * TILE))
          c = "."
        elif c == "C":
          s.checkpoints.append((x * TILE, y * TILE))
          c = "."
        line.append(c)
      s.tiles.append(line)

    if from_checkpoint and s.cp_active:
      s.player = Player(s.cp_x, s.cp_y)
      r_x, r_y, t_x, t_y, l_x, l_y = (
          s.cp_x + TILE,
          s.cp_y,
          s.cp_x,
          s.cp_y - TILE,
          s.cp_x - TILE,
          s.cp_y,
      )
      if s.tile(r_x, r_y) != "#":
        bx, by = r_x + 8, r_y + 8
      elif s.tile(t_x, t_y) != "#":
        bx, by = t_x + 8, t_y + 8
      else:
        bx, by = l_x + 8, l_y + 8
      s.balls.append(Ball(bx, by))
    else:
      s.player = Player(p_start_x, p_start_y)
      if b_starts:
        bx, by = b_starts[0]
        s.balls.append(Ball(bx, by))
      else:
        s.balls.append(Ball(p_start_x + 16, p_start_y + 8))

  def tile(s, x, y):
    tx = int(x // TILE)
    ty = int(y // TILE)
    if ty < 0 or ty >= len(s.tiles) or tx < 0 or tx >= len(s.tiles[ty]):
      return "."
    return s.tiles[ty][tx]

  def is_wall(s, x, y):
    return s.tile(x, y) == "#"

  def check_collision(s, nx, ny, rw, rh):
    return any(
        s.is_wall(x, y)
        for x, y in (
            (nx, ny),
            (nx + rw, ny),
            (nx + rw, ny + rh),
            (nx, ny + rh),
        )
    )

  def trigger_gameover(s):
    if not s.is_gameover:
      s.is_gameover = 1
      pyxel.stop(2)
      pyxel.stop(3)
      pyxel.play(1, 19)

  def trigger_clear(s):
    if not s.is_cleared and not s.all_cleared:
      s.is_cleared = 1
      s.clear_timer = 150
      s.score += 1000
      pyxel.stop(2)
      pyxel.stop(3)
      pyxel.play(1, 8)
      for _ in range(60):
        col = pyxel.rndi(8, 14)
        s.particles.append([
            s.goal_x + 8,
            s.goal_y + 8,
            pyxel.rndf(-4, 4),
            pyxel.rndf(-6, -1),
            col,
            pyxel.rndi(30, 80),
        ])

  def update_player(s):
    if s.is_gameover or s.is_cleared or s.all_cleared:
      return
    p = s.player
    pcx, pcy = p.x + 8, p.y + 8
    if p.spring_timer > 0:
      p.spring_timer -= 1
    on_pole = any(
        sx <= pcx < sx + TILE and sy <= pcy < sy + TILE for sx, sy in s.poles
    )

    if on_pole:
      if (
          s.b_J(False) or s.b_U() or s.b_D() or pyxel.btn(pyxel.KEY_SPACE)
      ) and not p.is_climbing:
        p.is_climbing = True
        p.spring_timer = 0
        p.vx = 0
    else:
      p.is_climbing = False

    if p.is_climbing and (s.b_L() or s.b_R()):
      p.is_climbing = False

    if p.is_climbing:
      p.vx = 0
      climb_moved = False
      if s.b_J(False) or s.b_U() or pyxel.btn(pyxel.KEY_SPACE):
        p.vy = -1.5
        p.walk_frame += 1
        climb_moved = True
      elif s.b_D():
        p.vy = 1.5
        p.walk_frame += 1
        climb_moved = True
      else:
        p.vy = 0
      if climb_moved and pyxel.frame_count % 10 == 0:
        pyxel.play(0, 6)
    else:
      if p.spring_timer > 0:
        pass
      elif s.b_L():
        p.vx = -MOVE_SPEED
        p.dir = -1
        p.walk_frame += 1
      elif s.b_R():
        p.vx = MOVE_SPEED
        p.dir = 1
        p.walk_frame += 1
      else:
        p.vx = 0
        p.walk_frame = 0

      if s.b_J(True) and p.on_ground:
        p.vy = JUMP_POWER
        p.spring_timer = 0
        if s.game_state != "title":
          pyxel.play(0, 0)
      p.vy += GRAVITY

    px, py, pw, ph = p.rect()
    for sx, sy in s.springs:
      if (
          px < sx + TILE
          and px + pw > sx
          and py + ph >= sy
          and py + ph <= sy + 6
          and p.vy >= 0
      ):
        p.vy = SPRING_POWER
        p.on_ground = 0
        p.spring_timer = 0
        p.is_climbing = False
        break
    for sx, sy in s.springs_l:
      if (
          py < sy + TILE
          and py + ph > sy
          and px <= sx + TILE
          and px + pw >= sx + 10
          and p.vx <= 0
      ):
        p.vx = SPRING_POWER
        p.spring_timer = 15
        p.is_climbing = False
        break
    for sx, sy in s.springs_r:
      if (
          py < sy + TILE
          and py + ph > sy
          and px + pw >= sx
          and px <= sx + 6
          and p.vx >= 0
      ):
        p.vx = -SPRING_POWER
        p.spring_timer = 15
        p.is_climbing = False
        break

    nx = p.x + p.vx
    if s.check_collision(nx + 2, p.y + 2, 12, 12):
      p.vx = 0
      p.spring_timer = 0
    else:
      p.x = nx
    ny = p.y + p.vy
    if not s.check_collision(p.x + 2, ny + 2, 12, 12):
      p.y = ny
      p.on_ground = 0
    else:
      p.on_ground = p.vy > 0
      p.vy = 0
      if p.on_ground:
        p.spring_timer = 0
        p.is_climbing = False
    if p.y > len(s.tiles) * TILE:
      s.trigger_gameover()

  def update_balls(s):
    if s.is_gameover or (s.is_cleared and not s.all_cleared):
      return
    p = s.player
    pcx, pcy = p.x + 8, p.y + 8
    for b in s.balls:
      if b.spring_timer > 0:
        b.spring_timer -= 1
      b.vy += GRAVITY * 0.85
      if b.spring_timer == 0:
        b.vx *= 0.98
      bx, by, bw, bh = b.rect()
      for sx, sy in s.springs:
        if (
            bx < sx + TILE
            and bx + bw > sx
            and by + bh >= sy
            and by + bh <= sy + 6
            and b.vy >= 0
        ):
          b.vy = SPRING_POWER * 0.9
          b.y = sy - b.radius
          b.spring_timer = 0
          break
      for sx, sy in s.springs_l:
        if (
            by < sy + TILE
            and by + bh > sy
            and bx <= sx + TILE
            and bx + bw >= sx + 10
            and b.vx <= 0
        ):
          b.vx = SPRING_POWER
          b.spring_timer = 15
          break
      for sx, sy in s.springs_r:
        if (
            by < sy + TILE
            and by + bh > sy
            and bx + bw >= sx
            and bx <= sx + 6
            and b.vx >= 0
        ):
          b.vx = -SPRING_POWER
          b.spring_timer = 15
          break

      speed = math.hypot(b.vx, b.vy)
      sub_steps = max(1, int(speed / (b.radius * 0.5)))
      dx_step = b.vx / sub_steps
      dy_step = b.vy / sub_steps
      for _ in range(sub_steps):
        b.x += dx_step
        b.y += dy_step
        for cx, cy in s.checkpoints:
          if (
              cx - b.radius <= b.x <= cx + TILE + b.radius
              and cy - b.radius <= b.y <= cy + TILE + b.radius
          ):
            if not s.cp_active or s.cp_x != cx or s.cp_y != cy:
              s.cp_active = True
              s.cp_x = cx
              s.cp_y = cy
              s.score += 200
              pyxel.play(1, 7)
        x_start = int((b.x - b.radius) // TILE)
        x_end = int((b.x + b.radius) // TILE)
        y_start = int((b.y - b.radius) // TILE)
        y_end = int((b.y + b.radius) // TILE)
        for ty in range(y_start, y_end + 1):
          for tx in range(x_start, x_end + 1):
            if (
                0 <= ty < len(s.tiles)
                and 0 <= tx < len(s.tiles[ty])
                and s.tiles[ty][tx] == "#"
            ):
              tw_left, tw_top = tx * TILE, ty * TILE
              tw_right, tw_bottom = tw_left + TILE, ty * TILE + TILE
              closest_x = max(tw_left, min(b.x, tw_right))
              closest_y = max(tw_top, min(b.y, tw_bottom))
              dx = b.x - closest_x
              dy = b.y - closest_y
              dist = math.hypot(dx, dy)
              if dist < b.radius:
                if dist == 0:
                  nx, ny, overlap = 0, -1, b.radius
                else:
                  nx, ny = dx / dist, dy / dist
                  overlap = b.radius - dist
                b.x += nx * overlap
                b.y += ny * overlap
                v_dot_n = b.vx * nx + b.vy * ny
                if v_dot_n < 0:
                  if abs(v_dot_n) > 1.5 and s.game_state != "title":
                    pyxel.play(0, 1)
                  restitution = 0.5 if ny < -0.7 else 0.6
                  b.vx -= (1 + restitution) * v_dot_n * nx
                  b.vy -= (1 + restitution) * v_dot_n * ny
                  dx_step = b.vx / sub_steps
                  dy_step = b.vy / sub_steps
                  if ny < -0.7:
                    b.on_ground = 1
                    b.vx *= 0.95
                    if abs(b.vy) < 0.3:
                      b.vy = 0
      if b.y > len(s.tiles) * TILE:
        s.trigger_gameover()
        return
      d = math.hypot(pcx - b.x, pcy - b.y)
      if d < 8 + b.radius:
        a = math.atan2(b.y - pcy, b.x - pcx)
        sp = math.hypot(p.vx, p.vy) + 2.2
        b.vx = math.cos(a) * sp + p.vx * 0.4
        b.vy = math.sin(a) * sp - 1.5

  def update_spike(s):
    if s.is_cleared or s.is_gameover or s.all_cleared:
      return
    px, py, _, _ = s.player.rect()
    for sx, sy in s.spikes:
      if abs(px - sx) < 12 and abs(py - sy) < 12:
        s.trigger_gameover()
        return

  def update_goal(s):
    if s.is_cleared or s.is_gameover or s.all_cleared:
      return
    gx, gy = s.goal_x + 8, s.goal_y + 8
    for b in s.balls:
      if abs(b.x - gx) < 14 and abs(b.y - gy) < 14:
        s.trigger_clear()
        break

  def update_camera(s):
    if s.is_gameover or (s.is_cleared and not s.all_cleared):
      return
    p = s.player
    s.cam_x = max(0, min(int(p.x - 120), 1000))
    s.cam_y = max(0, int(p.y - 90))

  def update(s):
    if s.game_state == "title":
      if s.player.y > len(s.tiles) * TILE or any(
          b.y > len(s.tiles) * TILE for b in s.balls
      ):
        s.load_level(False)
      s.update_player()
      s.update_balls()
      s.update_camera()
      if s.b_A():
        s.game_state = "play"
        s.current_stage = 0
        s.score = 0
        s.total_time = 0
        s.load_level(False)
        s.play_stage_bgm()
      return

    if s.all_cleared or s.is_cleared:
      for p in s.particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[3] += 0.05
        p[5] -= 1
        if p[5] <= 0:
          s.particles.remove(p)
      if pyxel.frame_count % 20 == 0:
        hx, hy = s.cam_x + pyxel.rndi(20, 236), s.cam_y + pyxel.rndi(30, 100)
        col = pyxel.rndi(8, 14)
        for _ in range(25):
          s.particles.append([
              hx,
              hy,
              pyxel.rndf(-3, 3),
              pyxel.rndf(-3, 3),
              col if pyxel.rndi(0, 1) else 7,
              pyxel.rndf(20, 50),
          ])

      pl = s.player
      pl.vy += GRAVITY
      pl.y += pl.vy
      if s.check_collision(pl.x + 2, pl.y + 2, 12, 12):
        pl.y -= pl.vy
        pl.vy = -3.5

      if s.all_cleared == 1:
        s.credit_y -= 0.5
        if s.credit_y < -320:
          s.all_cleared = 2
          s.summary_timer = 150
        s.update_balls()
        s.update_camera()
      elif s.all_cleared == 2:
        s.summary_timer -= 1
        if s.summary_timer <= 0:
          s.game_state = "title"
          s.all_cleared = 0
          s.is_cleared = 0
          s.cp_active = False
          s.load_level(False)
          pyxel.play(2, 17, loop=True)
          pyxel.stop(3)
      else:
        s.clear_timer -= 1
        if s.clear_timer <= 0:
          s.cp_active = False
          if s.current_stage + 1 >= len(levels):
            s.all_cleared = 1
            s.is_cleared = 0
            s.credit_y = 110
            if s.score > s.high_score:
              s.high_score = s.score
            pyxel.stop(2)
            pyxel.stop(3)
            pyxel.play(2, 18, loop=True)
          else:
            s.current_stage += 1
            s.load_level()
            s.play_stage_bgm()
        elif s.b_Rt():
          s.cp_active = False
          s.load_level(False)
          s.play_stage_bgm()
      return

    if s.is_gameover:
      if s.b_Rt() or s.b_A():
        s.load_level(True)
        s.play_stage_bgm()
      return

    if s.b_Rt():
      s.load_level(True)
      s.play_stage_bgm()
      return

    if s.game_state == "play" and not s.is_cleared and not s.is_gameover:
      s.time_limit -= 1
      s.total_time += 1
      if s.time_limit <= 0:
        s.trigger_gameover()

    s.update_player()
    s.update_balls()
    s.update_spike()
    s.update_goal()
    s.update_camera()

  def draw_bg(s):
    stage = s.current_stage
    if stage == 0:
      pyxel.cls(13)
      pyxel.circ(200, 30, 12, 10)
      pyxel.circ(200, 30, 8, 7)
      mx = s.cam_x * 0.1
      for i in range(10):
        bx = i * 60 - (mx % 60) - 20
        pyxel.tri(bx, 160, bx + 30, 80, bx + 60, 160, 12)
        pyxel.tri(bx + 10, 160, bx + 30, 80, bx + 30, 160, 1)
      mx2 = s.cam_x * 0.3
      for i in range(10):
        bx = i * 80 - (mx2 % 80) - 30
        pyxel.tri(bx, 160, bx + 40, 100, bx + 80, 160, 3)
        pyxel.tri(bx + 20, 160, bx + 40, 100, bx + 40, 160, 11)
      cx = s.cam_x * 0.5
      for i in range(5):
        x = (i * 90 - cx) % 300 - 20
        y = 20 + (i % 3) * 15
        pyxel.circ(x, y, 10, 7)
        pyxel.circ(x + 10, y - 5, 12, 7)
        pyxel.circ(x + 20, y, 10, 7)
        pyxel.rect(x, y, 20, 11, 7)

    elif stage == 1:
      pyxel.cls(9)
      pyxel.circ(60, 40, 14, 10)
      pyxel.circ(60, 40, 10, 7)
      mx = s.cam_x * 0.15
      for i in range(10):
        bx = i * 70 - (mx % 70) - 20
        pyxel.tri(bx, 160, bx + 35, 90, bx + 70, 160, 2)
      mx2 = s.cam_x * 0.4
      for i in range(10):
        bx = i * 90 - (mx2 % 90) - 30
        pyxel.tri(bx, 160, bx + 45, 115, bx + 90, 160, 4)

    elif stage == 2:
      pyxel.cls(1)
      pyxel.circ(220, 25, 10, 7)
      for i in range(20):
        hx = (i * 37 + int(s.cam_x * 0.05)) % 256
        hy = (i * 19) % 100
        pyxel.pset(hx, hy, 7 if i % 3 == 0 else 6)
      mx = s.cam_x * 0.2
      for i in range(10):
        bx = i * 65 - (mx % 65) - 20
        pyxel.tri(bx, 160, bx + 32, 85, bx + 64, 160, 5)

    elif stage == 3:
      pyxel.cls(5)
      mx = s.cam_x * 0.3
      for i in range(12):
        bx = i * 50 - (mx % 50) - 25
        pyxel.tri(bx, 0, bx + 25, 30 + (i * 7) % 25, bx + 50, 0, 1)
        pyxel.tri(bx, 160, bx + 25, 130 - (i * 11) % 20, bx + 50, 160, 1)

    else:
      pyxel.cls(0)
      for i in range(30):
        hx = (i * 29 + int(s.cam_x * 0.1)) % 256
        hy = (i * 13) % 140
        pyxel.pset(hx, hy, 10 if i % 2 == 0 else 11)
      cx = s.cam_x * 0.5
      for i in range(8):
        lx = i * 40 - (cx % 40)
        pyxel.line(lx, 140, lx - 20, 160, 8)
        pyxel.line(lx, 140, lx + 20, 160, 8)
      pyxel.line(0, 140, 256, 140, 8)

  def draw_map(s):
    for y, row in enumerate(s.tiles):
      for x, c in enumerate(row):
        if c == "#":
          pyxel.blt(x * TILE - s.cam_x, y * TILE - s.cam_y, 0, 0, 0, 16, 16, 13)

  def draw_poles(s):
    for x, y in s.poles:
      pyxel.blt(x - s.cam_x, y - s.cam_y, 0, 48, 16, 16, 16, 13)

  def draw_spikes(s):
    for x, y in s.spikes:
      pyxel.blt(x - s.cam_x, y - s.cam_y, 0, 0, 16, 16, 16, 13)

  def draw_springs(s):
    p = s.player
    for x, y in s.springs:
      is_b = (
          p.vy < 0
          and p.spring_timer > 0
          and abs(p.x - x) < 24
          and abs(p.y - y) < 24
      )
      pyxel.blt(x - s.cam_x, y - s.cam_y, 0, 32 if is_b else 16, 16, 16, 16, 13)
    for x, y in s.springs_l:
      is_b = (
          p.vx > 0
          and p.spring_timer > 0
          and abs(p.x - x) < 24
          and abs(p.y - y) < 24
      )
      pyxel.blt(x - s.cam_x, y - s.cam_y, 0, 112 if is_b else 96, 16, 16, 16, 13)
    for x, y in s.springs_r:
      is_b = (
          p.vx < 0
          and p.spring_timer > 0
          and abs(p.x - x) < 24
          and abs(p.y - y) < 24
      )
      pyxel.blt(
          x - s.cam_x, y - s.cam_y, 0, 144 if is_b else 128, 16, 16, 16, 13
      )

  def draw_checkpoints(s):
    for x, y in s.checkpoints:
      u = 80 if (s.cp_active and s.cp_x == x and s.cp_y == y) else 64
      pyxel.blt(x - s.cam_x, y - s.cam_y, 0, u, 16, 16, 16, 13)

  def draw_goal(s):
    pyxel.blt(s.goal_x - s.cam_x, s.goal_y - s.cam_y, 0, 32, 0, 16, 16, 13)

  def draw_balls(s):
    for b in s.balls:
      if b.y <= len(s.tiles) * TILE:
        pyxel.blt(b.x - 8 - s.cam_x, b.y - 8 - s.cam_y, 0, 16, 0, 16, 16, 13)

  def draw_player(s):
    p = s.player
    if p.is_climbing:
      u = 112 if (p.walk_frame // 8) % 2 == 0 else 128
      w = 16
    elif not p.on_ground:
      u = 96
      w = 16 if p.dir == 1 else -16
    elif p.vx != 0:
      if p.dir == 1:
        u = 64 if (p.walk_frame // 6) % 2 == 0 else 80
        w = 16
      else:
        u = 144 if (p.walk_frame // 6) % 2 == 0 else 160
        w = 16
    else:
      u = 48
      w = 16 if p.dir == 1 else -16
    pyxel.blt(p.x - 2 - s.cam_x, p.y - 2 - s.cam_y, 0, u, 0, w, 16, 13)

  def draw_ui(s):
    pyxel.rectb(5, 130, 30, 25, 5)
    s.text_s(17, 138, "<", 7)
    pyxel.rectb(45, 130, 30, 25, 5)
    s.text_s(57, 138, ">", 7)
    pyxel.rectb(210, 125, 40, 25, 5)
    s.text_s(220, 133, "JUMP", 7)
    pyxel.rectb(220, 3, 30, 14, 5)
    s.text_s(231, 6, "RET", 7)

  def draw(s):
    s.draw_bg()
    s.draw_poles()
    s.draw_map()
    s.draw_checkpoints()
    s.draw_springs()
    s.draw_spikes()
    s.draw_goal()
    s.draw_balls()

    for p in s.particles:
      pyxel.rect(p[0] - s.cam_x, p[1] - s.cam_y, 2, 2, p[4])
      pyxel.pset((p[0] - p[2]) - s.cam_x, (p[1] - p[3]) - s.cam_y, p[4])

    if s.player.y <= len(s.tiles) * TILE:
      s.draw_player()

    if s.game_state == "title":
      pyxel.rect(20, 18, 216, 124, 0)
      pyxel.rectb(20, 18, 216, 124, 5)
      pyxel.rectb(22, 20, 212, 120, 6)
      pyxel.rectb(24, 22, 208, 116, 7)

      s.text_s(92, 34, "T.K PRESENTS", 6)
      s.text_s(88, 48, "BALL PLATFORMER", 10)
      s.text_s(90, 49, "BALL PLATFORMER", 7)

      s.text_s(75, 75, "PUSH BALLS TO THE GOAL!", 9)
      s.text_s(92, 92, "NORMAL EDITION", 3)

      c = 11 if pyxel.frame_count % 30 < 15 else 7
      s.text_s(65, 116, "- PUSH SPACE(START) BUTTON! -", c)
      s.text_s(85, 130, "(C) 2026 MIRAI WORK", 13)
      return

    pyxel.rect(0, 0, 256, 18, 0)
    pyxel.rectb(0, 0, 256, 18, 6)
    s.text_s(6, 5, f"SCORE:{s.score:05d}", 7)
    s.text_s(96, 5, f"STAGE {s.current_stage + 1}", 10)
    time_sec = max(0, int(s.time_limit // 30))
    s.text_s(184, 5, f"TIME LIMIT:{time_sec:03d}", 9)

    if (
        s.game_state == "play"
        and not s.is_cleared
        and not s.is_gameover
        and not s.all_cleared
    ):
      # スマホ環境のときのみUIを描画する
      if s.is_smartphone:
        s.draw_ui()

    if s.is_gameover:
      s.draw_window_box(38, 50, 180, 62, 2, 8, 1)
      c = 8 if pyxel.frame_count % 30 < 15 else 7
      s.text_s(90, 64, "GAME OVER", c)
      s.text_s(60, 82, "CONTINUE OR RETRY?", 7)
      s.text_s(52, 96, "PRESS R/Y OR SPACE KEY", 6)

    if s.is_cleared and not s.all_cleared:
      s.draw_window_box(38, 55, 180, 48, 11, 12, 3)
      c = 10 if pyxel.frame_count % 30 < 15 else 7
      dy = int(math.sin(pyxel.frame_count * 0.15) * 2)
      s.text_s(86, 67 + dy, "STAGE CLEAR!", c)
      s.text_s(64, 83 + dy, f"STAGE {s.current_stage+1} COMPLETED", 7)

    if s.all_cleared == 1:
      s.draw_window_box(24, 26, 208, 112, 9, 10, 8)

      pyxel.clip(28, 30, 200, 104)
      credits_list = [
          "CONGRATULATIONS!",
          "",
          "BALL PLATFORMER",
          "",
          "- CREDITS -",
          "",
          "SUPER VISION",
          "TEAM T.D",
          "",
          "GAME DESIGN & DIRECTION",
          "T.K",
          "",
          "ARRANGEMENT",
          "M.T",
          "",
          "PRODUCED BY",
          "(c)MIRAI WORK ",
          "",
          "T.K/M.T 2026",
      ]
      for i, text in enumerate(credits_list):
        cy = s.credit_y + i * 16
        if -16 < cy < 120:
          col = 11 if i == 0 or i == 2 else 7
          tx = 128 - (len(text) * 2)
          s.text_s(tx, cy, text, col)
      pyxel.clip()

      c = 11 if pyxel.frame_count % 30 < 15 else 7
      s.text_s(76, 120, "THANK YOU FOR PLAYING!", c)

    elif s.all_cleared == 2:
      s.draw_window_box(24, 26, 208, 112, 9, 10, 8)

      c = 11 if pyxel.frame_count % 30 < 15 else 7
      s.text_s(104, 46, "RESULT", c)

      s.text_s(64, 70, f"HIGH SCORE : {s.high_score:05d}", 7)
      total_sec = s.total_time // 30
      m = total_sec // 60
      sec = total_sec % 60
      s.text_s(64, 90, f"TOTAL TIME : {m:02d}:{sec:02d}", 7)

      s.text_s(72, 116, "RETURNING TO TITLE...", c)


Game()
