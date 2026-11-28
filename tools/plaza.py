"""15·16. 광장 마을 (야생 첫 스폰 자리, 모드가 자리를 골라 땅을 고른 뒤 지음).

좌표는 광장 가운데 기준 상대값 (x 동쪽+, z 남쪽+, y=0이 땅 블록). build_world.py가 이 목록을 "~x ~y ~z"로 바꿔
poke:build/plaza/<n> 함수로 씀 → 마커(poke.plaza) 위치에서 실행.
건물 간격·방향을 일부러 고르지 않게 두고, 굽은 흙길·나무·연못·밭·바위·가로등으로 자연스러운 마을처럼 (참고 사진).
"""
import math
import random

import build_world as W

R = 72                       # 광장 반지름 (모드 Plaza.PROTECT 와 같아야 함)
CENTER_P = (16, 38, -11, 11)  # 포켓몬센터 (문 서쪽, 분수 쪽) — center()가 z 가운데를 0으로 씀
MART_P = (-40, -18, -4, 18)   # 프렌들리 숍 (문 동쪽)
ARRIVE = (0, 1, 16)           # 도착·리스폰 (Plaza.java 와 같게)
# 포켓몬 상식 건물: (키, 모양, x1, z1, 문 방향) — 키는 tips.py 의 분류
TIP_HOUSES = [('academy', 'diner', -33, -41, 's'), ('nature', 'house', -9, -53, 's'), ('types', 'mimikyu', 30, -44, 's'),
              ('catch', 'house2', -45, 29, 'n'), ('evolve', 'diner2', 6, 35, 'n'), ('dojo', 'gymlet', 27, 23, 'n')]
SIZE = {'diner': (13, 10), 'diner2': (13, 10), 'house': (11, 9), 'house2': (11, 9), 'gymlet': (13, 10), 'mimikyu': (15, 15)}

rng = random.Random(16)
OCC = set()                  # 건물·길·연못 자리 (나무·꽃이 피함)
MAIN = set()                 # 큰길 칸 (집으로 가는 샛길이 가장 가까운 큰길에서 갈라짐)


def occupy(x1, x2, z1, z2, pad=0):
    for x in range(x1 - pad, x2 + pad + 1):
        for z in range(z1 - pad, z2 + pad + 1):
            OCC.add((x, z))


def inside(x, z, r=R - 3):
    return x * x + z * z <= r * r


# ── 바탕: 비우고 잔디로 ──
def base():
    L = ['# 광장: 위를 비우고 땅을 잔디로 (지형은 모드가 이미 고름)',
         'kill @e[type=minecraft:text_display,tag=poke.plaza,distance=..100]',
         'kill @e[type=minecraft:item_display,tag=poke.plaza,distance=..100]',
         'kill @e[type=minecraft:text_display,tag=poke.deco,distance=..100]',
         'kill @e[type=minecraft:item_frame,tag=poke.deco,distance=..100]']
    for z in range(-R, R + 1):
        half = int(math.sqrt(R * R - z * z))
        L += [W.fill(-half, 1, z, half, 40, z, 'minecraft:air'), W.fill(-half, 0, z, half, 0, z, 'minecraft:grass_block'),
              W.fill(-half, -3, z, half, -1, z, 'minecraft:dirt')]
    return L


# ── 길: 웨이포인트를 잇는 굽은 흙길 ──
def path(points, width=1.4, main=True):
    cells = set()
    for (ax, az), (bx, bz) in zip(points, points[1:]):
        n = int(math.hypot(bx - ax, bz - az) * 2) + 1
        for i in range(n + 1):
            t = i / n
            # 살짝 휘게: 구간 가운데가 가장 많이 벗어남
            bend = math.sin(t * math.pi) * 1.5 * math.sin((ax + bz) * 0.7)
            px, pz = ax + (bx - ax) * t - (bz - az) / max(1, math.hypot(bx - ax, bz - az)) * bend, az + (bz - az) * t + (bx - ax) / max(1, math.hypot(bx - ax, bz - az)) * bend
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if math.hypot(dx, dz) <= width and inside(round(px) + dx, round(pz) + dz, R - 1):
                        cells.add((round(px) + dx, round(pz) + dz))
    L = []
    for x, z in sorted(cells):
        if (x, z) in OCC:
            continue
        k = rng.random()
        block = 'dirt_path' if main and k < 0.8 else ('coarse_dirt' if k < 0.93 else 'gravel')
        L.append(W.sb(x, 0, z, 'minecraft:' + block))
    for c in cells:
        OCC.add(c)
        if main:
            MAIN.add(c)
    return L


def paving():
    """분수 둘레 돌바닥 (둥글지만 가장자리를 들쭉날쭉하게)."""
    L = []
    for x in range(-16, 17):
        for z in range(-16, 17):
            r = 11.5 + 2.2 * math.sin(math.atan2(z, x) * 3 + 1.3) + rng.random() * 0.8
            if math.hypot(x, z) <= r:
                k = rng.random()
                b = 'polished_andesite' if k < 0.45 else 'stone_bricks' if k < 0.75 else 'smooth_stone' if k < 0.9 else 'mossy_stone_bricks'
                L.append(W.sb(x, 0, z, 'minecraft:' + b))
                OCC.add((x, z))
    return L


def fountain():
    """가운데 분수 + 받침 위 몬스터볼 조형물 (참고 사진의 빨강·흰 공)."""
    L = []
    for dx, dz in W.circle(5):
        d = math.hypot(dx, dz)
        L.append(W.sb(dx, 0, dz, 'minecraft:water' if d < 4.6 else 'minecraft:smooth_quartz'))
        if d >= 4.6:
            L.append(W.sb(dx, 1, dz, 'minecraft:smooth_quartz_slab'))
    L += [W.sb(0, -1, 0, 'minecraft:sea_lantern'), W.fill(0, 0, 0, 0, 2, 0, 'minecraft:quartz_pillar'), W.sb(0, 3, 0, 'minecraft:chiseled_quartz_block')]
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dy * dy + dz * dz <= 5:
                    b = 'black_concrete' if dy == 0 else ('red_concrete' if dy > 0 else 'white_concrete')
                    L.append(W.sb(dx, 6 + dy, dz, 'minecraft:' + b))
    L += [W.sb(0, 6, 3, 'minecraft:white_concrete'), W.sb(0, 6, -3, 'minecraft:white_concrete')]
    L.append(W.label(0.5, 10.2, 0.5, '잡켓몬 서버', 'gold', 2.4, tag='poke.plaza'))
    occupy(-6, 6, -6, 6)
    return L


# ── 집: 청록·초록 박공지붕 목조 (참고 사진 House, 마을 사진) ──
def house(x1, z1, door, roof='prismarine_brick', roof_dark='dark_prismarine', wall='oak_planks', post='stripped_spruce_log'):
    w, d = SIZE['house']
    x2, z2 = x1 + w - 1, z1 + d - 1
    fz = z2 if door == 's' else z1
    out = 1 if door == 's' else -1
    xm = (x1 + x2) // 2
    top = 4
    L = [W.fill(x1, 0, z1, x2, 0, z2, 'minecraft:spruce_planks'), W.fill(x1, 1, z1, x2, 1, z2, 'minecraft:cobblestone')]
    L += W.walls(x1, x2, z1, z2, 2, top, f'minecraft:{wall}')
    L += W.walls(x1, x2, z1, z2, 1, 1, 'minecraft:cobblestone')
    for x in (x1, xm, x2):
        for z in (z1, z2):
            L.append(W.fill(x, 1, z, x, top, z, f'minecraft:{post}'))
    L += [W.fill(x1, top + 1, z1, x2, top + 1, z2, f'minecraft:{post}[axis=x]')]
    # 창 (덧문·꽃 상자)
    for x in (x1 + 2, x2 - 2):
        for z in (z1, z2):
            if z == fz and abs(x - xm) < 2:
                continue
            L += [W.sb(x, 3, z, 'minecraft:glass_pane'), W.sb(x - 1 if x < xm else x + 1, 3, z, 'minecraft:glass_pane')]
        zf = fz + out
        L += [W.sb(x, 2, zf, f'minecraft:spruce_trapdoor[facing={"south" if out > 0 else "north"},half=top,open=false]'),
              W.sb(x, 3, zf, 'minecraft:potted_red_tulip' if rng.random() < .5 else 'minecraft:potted_allium')]
    for z in (z1 + 3, z2 - 3):
        L += [W.sb(x1, 3, z, 'minecraft:glass_pane'), W.sb(x2, 3, z, 'minecraft:glass_pane')]
    # 박공지붕: 마루는 x 방향, 한 층마다 안쪽으로 1칸
    half = (d + 1) // 2
    for i in range(half + 1):
        y = top + 1 + i
        za, zb = z1 - 1 + i, z2 + 1 - i
        if za > zb:
            break
        if za == zb:
            L.append(W.fill(x1 - 1, y, za, x2 + 1, y, za, f'minecraft:{roof}s'))
            break
        L += [W.fill(x1 - 1, y, za, x2 + 1, y, za, f'minecraft:{roof}_stairs[facing=south]'),
              W.fill(x1 - 1, y, zb, x2 + 1, y, zb, f'minecraft:{roof}_stairs[facing=north]')]
        if zb - za > 1:
            L += [W.fill(x1, y, za + 1, x1, y, zb - 1, f'minecraft:{wall}'), W.fill(x2, y, za + 1, x2, y, zb - 1, f'minecraft:{wall}')]
    L += [W.fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z1 - 1, f'minecraft:{roof_dark}_stairs[facing=south]'),
          W.fill(x1 - 1, top + 1, z2 + 1, x2 + 1, top + 1, z2 + 1, f'minecraft:{roof_dark}_stairs[facing=north]')]
    # 굴뚝 + 연기
    cx = x2 - 2
    L += [W.fill(cx, top + 1, z1 + 2, cx, top + half + 2, z1 + 2, 'minecraft:bricks'), W.sb(cx, top + half + 3, z1 + 2, 'minecraft:campfire[lit=true,signal_fire=false]')]
    # 문 + 작은 현관
    L += [W.fill(xm, 2, fz, xm, 3, fz, 'minecraft:air'), W.sb(xm, 1, fz, 'minecraft:spruce_planks'),
          W.sb(xm, 2, fz, f'minecraft:spruce_door[facing={"south" if out > 0 else "north"},half=lower]'),
          W.sb(xm, 3, fz, f'minecraft:spruce_door[facing={"south" if out > 0 else "north"},half=upper]'),
          W.sb(xm, 1, fz + out, f'minecraft:spruce_stairs[facing={"north" if out > 0 else "south"}]'),
          W.fill(xm - 1, 4, fz + out, xm + 1, 4, fz + out, 'minecraft:spruce_slab[type=top]'),
          W.sb(xm - 1, 2, fz + out, 'minecraft:spruce_fence'), W.sb(xm + 1, 2, fz + out, 'minecraft:spruce_fence'),
          W.sb(xm - 1, 3, fz + out, 'minecraft:spruce_fence'), W.sb(xm + 1, 3, fz + out, 'minecraft:spruce_fence'),
          W.sb(xm + 1, 4, fz + out, 'minecraft:lantern[hanging=true]')]
    # 안: 마루·탁자·책장·조명
    L += [W.fill(x1 + 1, 1, z1 + 1, x2 - 1, 1, z2 - 1, 'minecraft:oak_planks'),
          W.fill(x1 + 1, 2, fz - out * (d - 2), x2 - 1, 3, fz - out * (d - 2), 'minecraft:bookshelf'),
          W.sb(x1 + 2, 2, (z1 + z2) // 2, 'minecraft:crafting_table'), W.sb(x2 - 2, 2, (z1 + z2) // 2, 'minecraft:barrel[facing=up]')]
    L += W.glow(x1, x2, z1, z2, 4, step=3)
    occupy(x1, x2, z1, z2, 1)
    occupy(xm - 1, xm + 1, min(fz, fz + out * 2), max(fz, fz + out * 2))
    return L, door_spot(x1, x2, z1, z2, door, 2)   # 마루(y=1) 위에 서게


# ── 식당풍: 나무 정면 + 높은 가운데 박공 + 초록 차양 (참고 사진 1) ──
def diner(x1, z1, door, accent='green'):
    w, d = SIZE['diner']
    x2, z2 = x1 + w - 1, z1 + d - 1
    fz = z2 if door == 's' else z1
    out = 1 if door == 's' else -1
    xm = (x1 + x2) // 2
    top = 8
    L = [W.fill(x1, 0, z1, x2, 0, z2, 'minecraft:stone_bricks'), W.fill(x1 + 1, 1, z1 + 1, x2 - 1, 1, z2 - 1, 'minecraft:spruce_planks')]
    L += W.walls(x1, x2, z1, z2, 1, top, 'minecraft:spruce_planks')
    L += W.walls(x1, x2, z1, z2, 1, 1, 'minecraft:red_terracotta')
    L += W.walls(x1, x2, z1, z2, 5, 5, 'minecraft:dark_oak_planks')
    for x in (x1, xm - 3, xm + 3, x2):
        for z in (z1, z2):
            L.append(W.fill(x, 1, z, x, top, z, 'minecraft:stripped_dark_oak_log'))
    # 옥상 난간 (초록 띠 + 흰 점)
    L += [W.fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:spruce_slab'), *W.walls(x1, x2, z1, z2, top + 1, top + 1, f'minecraft:{accent}_terracotta')]
    L += [W.sb(x, top + 2, z, 'minecraft:birch_fence') for x in range(x1, x2 + 1, 2) for z in (z1, z2)]
    # 정면 가운데: 높은 박공 (빨강 테두리), 위에 몬스터볼
    for k in range(5):
        L += [W.fill(xm - 3 + k, top + 1 + k, fz, xm + 3 - k, top + 1 + k, fz, 'minecraft:spruce_planks'),
              W.sb(xm - 3 + k, top + 1 + k, fz, 'minecraft:red_terracotta'), W.sb(xm + 3 - k, top + 1 + k, fz, 'minecraft:red_terracotta')]
    L += W.emblem_z(xm, fz + out, top + 1, 1)
    # 1층 큰 창 (따뜻한 불빛) + 초록·흰 줄 차양, 2층 창
    for xa in (x1 + 1, xm + 4):
        L += [W.fill(xa, 2, fz, xa + 1, 4, fz, 'minecraft:glass_pane'), W.fill(xa, 2, fz - out, xa + 1, 2, fz - out, 'minecraft:shroomlight')]
        for x in range(xa - 1, xa + 3):
            L.append(W.sb(x, 5, fz + out, f'minecraft:{accent if x % 2 else "white"}_wool'))
        L += [W.fill(xa, 6, fz, xa + 1, 7, fz, 'minecraft:glass_pane')]
    # 문 (가운데 두 짝) + 빨간 계단. 경첩은 바깥쪽 (남향이면 left/right가 뒤집힘 → 손잡이가 가운데로)
    hl, hr = ('right', 'left') if out > 0 else ('left', 'right')
    L += [W.fill(xm - 1, 1, fz, xm, 4, fz, 'minecraft:air'),
          W.sb(xm - 1, 2, fz, f'minecraft:spruce_door[facing={"south" if out > 0 else "north"},half=lower,hinge={hl}]'),
          W.sb(xm - 1, 3, fz, f'minecraft:spruce_door[facing={"south" if out > 0 else "north"},half=upper,hinge={hl}]'),
          W.sb(xm, 2, fz, f'minecraft:spruce_door[facing={"south" if out > 0 else "north"},half=lower,hinge={hr}]'),
          W.sb(xm, 3, fz, f'minecraft:spruce_door[facing={"south" if out > 0 else "north"},half=upper,hinge={hr}]'),
          W.fill(xm - 1, 1, fz, xm, 1, fz, 'minecraft:spruce_planks'), W.fill(xm + 1, 1, fz, xm + 1, 4, fz, 'minecraft:spruce_planks'),
          W.fill(xm - 1, 4, fz, xm, 4, fz, 'minecraft:spruce_planks'),   # 문 위 (위에서 4칸 높이까지 비워 문 위가 뚫려 있었음)
          W.fill(xm - 1, 1, fz + out, xm, 1, fz + out, f'minecraft:red_nether_brick_stairs[facing={"north" if out > 0 else "south"}]'),
          W.fill(xm - 2, 1, fz + out * 2, xm + 1, 1, fz + out * 2, 'minecraft:moss_carpet')]
    # 화단 (창 아래)
    L += [W.fill(x1 + 1, 1, fz + out, x1 + 2, 1, fz + out, 'minecraft:azalea_leaves[persistent=true]'),
          W.fill(x2 - 2, 1, fz + out, x2 - 1, 1, fz + out, 'minecraft:flowering_azalea_leaves[persistent=true]')]
    # 안: 2층 바닥, 탁자, 의자
    L += [W.fill(x1 + 1, 5, z1 + 1, x2 - 1, 5, z2 - 1, 'minecraft:spruce_slab[type=top]'),
          W.fill(xm - 1, 5, fz - out, xm, 5, fz - out * 2, 'minecraft:air')]
    for x in (x1 + 3, x2 - 3):
        L += [W.sb(x, 2, (z1 + z2) // 2, 'minecraft:spruce_fence'), W.sb(x, 3, (z1 + z2) // 2, 'minecraft:spruce_pressure_plate'),
              W.sb(x - 1, 2, (z1 + z2) // 2, 'minecraft:spruce_stairs[facing=east]'), W.sb(x + 1, 2, (z1 + z2) // 2, 'minecraft:spruce_stairs[facing=west]')]
    L += W.glow(x1, x2, z1, z2, 4, step=3) + W.glow(x1, x2, z1, z2, 7, step=4)
    occupy(x1, x2, z1, z2, 1)
    occupy(xm - 2, xm + 1, min(fz, fz + out * 2), max(fz, fz + out * 2))
    return L, door_spot(x1, x2, z1, z2, door, 2)


# ── 따라큐 모양 건물 (참고 사진 3): 원을 층층이 쌓아 몸·머리, 귀 하나는 꺾임 ──
def mimikyu(x1, z1, door):
    w, _ = SIZE['mimikyu']
    cx, cz = x1 + w // 2, z1 + w // 2
    out = 1 if door == 's' else -1
    body, black, cheek = 'minecraft:smooth_sandstone', 'minecraft:black_concrete', 'minecraft:orange_terracotta'
    prof = {1: 7, 2: 6.6, 3: 6, 4: 5.8, 5: 5.6, 6: 5.4, 7: 5, 8: 4.6, 9: 5, 10: 5.6, 11: 6, 12: 6, 13: 5.8, 14: 5.4, 15: 4.8, 16: 4, 17: 3}
    L = [W.fill(cx - 7, 0, cz - 7, cx + 7, 0, cz + 7, 'minecraft:smooth_sandstone')]
    for y, r in prof.items():
        for dz in range(-7, 8):
            span = [dx for dx in range(-7, 8) if dx * dx + dz * dz <= r * r]
            if span:
                L.append(W.fill(cx + span[0], y, cz + dz, cx + span[-1], y, cz + dz, body))
                inner = [dx for dx in span if dx * dx + dz * dz <= (r - 1.2) ** 2]
                if inner and 1 <= y <= 15:
                    L.append(W.fill(cx + inner[0], y, cz + dz, cx + inner[-1], y, cz + dz, 'minecraft:air'))
    # 아래 검은 발톱 (자락 끝)
    for a in range(0, 360, 60):
        dx, dz = round(math.cos(math.radians(a)) * 7.5), round(math.sin(math.radians(a)) * 7.5)
        L += [W.sb(cx + dx, 1, cz + dz, black), W.sb(cx + dx + (1 if dx > 0 else -1 if dx < 0 else 0), 1, cz + dz + (1 if dz > 0 else -1 if dz < 0 else 0), black)]
    # 서 있는 귀 (가운데, 끝 검정) + 꺾인 귀 (옆으로)
    for k, y in enumerate(range(18, 25)):
        rr = 1.6 - k * 0.15
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz <= rr * rr:
                    L.append(W.sb(cx + dx, y, cz + dz, black if y >= 22 else body))
    for k in range(6):
        L.append(W.fill(cx - 3 - k, 17 - (k // 3), cz - 1, cx - 3 - k, 18 - (k // 3), cz + 1, black if k >= 4 else body))
    # 얼굴 (머리 앞): 눈·볼·지그재그 입, 몸통의 가짜 눈 구멍
    fz = cz + out * 6
    L += [W.fill(cx - 3, 13, fz, cx - 2, 14, fz, black), W.fill(cx + 2, 13, fz, cx + 3, 14, fz, black),
          W.fill(cx - 4, 11, fz, cx - 3, 11, fz, cheek), W.fill(cx + 3, 11, fz, cx + 4, 11, fz, cheek)]
    L += [W.sb(cx + dx, 11 + (dx % 2), fz, black) for dx in range(-2, 3)]
    L += [W.fill(cx - 2, 5, cz + out * 6, cx - 1, 6, cz + out * 6, black), W.fill(cx + 1, 5, cz + out * 6, cx + 2, 6, cz + out * 6, black)]
    # 문 + 계단
    door_z = cz + out * 7
    L += [W.fill(cx - 1, 1, cz + out * 5, cx + 1, 3, door_z, 'minecraft:air'),
          W.fill(cx - 1, 0, door_z + out, cx + 1, 0, door_z + out * 2, 'minecraft:smooth_sandstone'),
          W.fill(cx - 1, 1, door_z + out, cx + 1, 1, door_z + out, f'minecraft:sandstone_stairs[facing={"north" if out > 0 else "south"}]')]
    L += [W.fill(cx - 4, 1, cz - 4, cx + 4, 1, cz + 4, 'minecraft:yellow_carpet', 'replace minecraft:air')]
    L += W.glow(cx - 6, cx + 6, cz - 6, cz + 6, 4, step=3) + W.glow(cx - 5, cx + 5, cz - 5, cz + 5, 12, step=3)
    occupy(cx - 8, cx + 8, cz - 8, cz + 8, 1)
    occupy(cx - 1, cx + 1, min(door_z, door_z + out * 2), max(door_z, door_z + out * 2))
    spots = [(cx - 2, 1, cz - out * 3, 0 if out > 0 else 180), (cx + 2, 1, cz - out * 3, 0 if out > 0 else 180)]
    return L, (spots, (cx, door_z + out * 2))


# ── 체육관풍 작은 건물 (참고 사진 2 Gym): 흰 벽·파란 창 띠·빨강 흰 기둥·겹친 황토색 지붕·노란 차양 ──
def gymlet(x1, z1, door):
    w, d = SIZE['gymlet']
    x2, z2 = x1 + w - 1, z1 + d - 1
    fz = z2 if door == 's' else z1
    out = 1 if door == 's' else -1
    xm = (x1 + x2) // 2
    top = 5
    L = [W.fill(x1, 0, z1, x2, 0, z2, 'minecraft:smooth_stone'), W.fill(x1 + 1, 1, z1 + 1, x2 - 1, 1, z2 - 1, 'minecraft:birch_planks')]
    L += W.walls(x1, x2, z1, z2, 1, top, 'minecraft:white_concrete')
    L += W.walls(x1, x2, z1, z2, 1, 1, 'minecraft:light_gray_concrete')
    L += W.walls(x1, x2, z1, z2, 3, 3, 'minecraft:light_blue_stained_glass')
    for x in (x1, x2):
        for z in (z1, z2):
            L += [W.sb(x, y, z, 'minecraft:red_concrete' if y % 2 else 'minecraft:white_concrete') for y in range(1, top + 1)]
    # 겹친 지붕: 넓은 층 → 좁은 층, 위에 줄무늬
    L += [W.fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:smooth_sandstone'),
          W.fill(x1, top + 2, z1, x2, top + 2, z2, 'minecraft:cut_sandstone'),
          W.fill(x1 + 1, top + 3, z1 + 1, x2 - 1, top + 3, z2 - 1, 'minecraft:smooth_sandstone')]
    L += [W.fill(x, top + 3, z1 + 2, x, top + 3, z2 - 2, 'minecraft:sandstone') for x in range(x1 + 2, x2 - 1, 2)]
    # 노란 차양 + 흰 구름 장식, 유리문
    L += [W.fill(xm - 3, 4, fz + out, xm + 3, 4, fz + out * 2, 'minecraft:yellow_concrete'),
          W.fill(xm - 2, 5, fz + out, xm + 2, 5, fz + out, 'minecraft:white_concrete'),
          W.sb(xm - 3, 1, fz + out * 2, 'minecraft:red_concrete'), W.sb(xm + 3, 1, fz + out * 2, 'minecraft:red_concrete'),
          W.fill(xm - 3, 2, fz + out * 2, xm - 3, 3, fz + out * 2, 'minecraft:white_concrete'), W.fill(xm + 3, 2, fz + out * 2, xm + 3, 3, fz + out * 2, 'minecraft:white_concrete'),
          W.fill(xm - 1, 1, fz, xm + 1, 3, fz, 'minecraft:air'), W.fill(xm - 2, 1, fz, xm - 2, 3, fz, 'minecraft:light_blue_stained_glass'),
          W.fill(xm + 2, 1, fz, xm + 2, 3, fz, 'minecraft:light_blue_stained_glass')]
    L += W.glow(x1, x2, z1, z2, 4, step=3)
    occupy(x1 - 1, x2 + 1, z1 - 1, z2 + 1, 1)
    occupy(xm - 3, xm + 3, min(fz, fz + out * 2), max(fz, fz + out * 2))
    return L, door_spot(x1, x2, z1, z2, door, 2)   # 마루(y=1) 위에 서게


def door_spot(x1, x2, z1, z2, door, y):
    """상식 NPC 2명 자리(안쪽 벽 앞, 문을 바라봄)와 문 앞 칸."""
    xm = (x1 + x2) // 2
    back = z1 + 2 if door == 's' else z2 - 2
    yaw = 0 if door == 's' else 180
    front = (xm, z2 + 2 if door == 's' else z1 - 2)
    return [(xm - 2, y, back, yaw), (xm + 2, y, back, yaw)], front


# ── 조경 ──
def tree(x, z, kind='oak', h=None):
    h = h or rng.randint(4, 6)
    log, leaf = (f'minecraft:{kind}_log', f'minecraft:{kind}_leaves[persistent=true]')
    L = [W.fill(x, 1, z, x, h, z, log)]
    r = 2.6 if h < 6 else 3.1
    for dx in range(-3, 4):
        for dy in range(-2, 3):
            for dz in range(-3, 4):
                if dx * dx + (dy * 1.4) ** 2 + dz * dz <= r * r and not (dx == 0 and dz == 0 and dy < 1) and rng.random() > 0.08:
                    L.append(W.sb(x + dx, h + dy, z + dz, leaf))
    return L


def boulder(x, z, r):
    L = []
    for dx in range(-3, 4):
        for dy in range(0, 3):
            for dz in range(-3, 4):
                if dx * dx + (dy * 1.5) ** 2 + dz * dz <= r * r + rng.random():
                    L.append(W.sb(x + dx, 1 + dy, z + dz, 'minecraft:' + rng.choice(['stone', 'andesite', 'cobblestone', 'mossy_cobblestone', 'tuff'])))
    occupy(x - 3, x + 3, z - 3, z + 3)
    return L


def pond(cx, cz):
    L, cells = [], []
    for dx in range(-9, 10):
        for dz in range(-7, 8):
            if (dx / 8) ** 2 + (dz / 5.5) ** 2 + 0.25 * math.sin(dx * 0.9 + dz) <= 1:
                cells.append((cx + dx, cz + dz))
    for x, z in cells:
        L += [W.sb(x, 0, z, 'minecraft:water'), W.sb(x, -1, z, 'minecraft:water' if rng.random() < .6 else 'minecraft:clay')]
        if rng.random() < 0.12:
            L.append(W.sb(x, 1, z, 'minecraft:lily_pad'))
    edge = {(x + a, z + b) for x, z in cells for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)
    for x, z in edge:
        if rng.random() < 0.3:
            L.append(W.fill(x, 1, z, x, 2, z, 'minecraft:sugar_cane'))
        elif rng.random() < 0.3:
            L.append(W.sb(x, 0, z, 'minecraft:sand'))
    for c in cells + list(edge):
        OCC.add(c)
    return L


def farm_patch(x1, z1, w=9, d=7):
    x2, z2 = x1 + w - 1, z1 + d - 1
    L = [W.fill(x1, 0, z1, x2, 0, z2, 'minecraft:farmland[moisture=7]'), W.fill(x1, 0, (z1 + z2) // 2, x2, 0, (z1 + z2) // 2, 'minecraft:water')]
    for z in range(z1, z2 + 1):
        if z == (z1 + z2) // 2:
            continue
        crop = 'wheat[age=7]' if z < (z1 + z2) // 2 else 'carrots[age=7]'
        L.append(W.fill(x1, 1, z, x2, 1, z, 'minecraft:' + crop))
    L += [W.fill(x1 - 1, 1, z1 - 1, x2 + 1, 1, z1 - 1, 'minecraft:oak_fence'), W.fill(x1 - 1, 1, z2 + 1, x2 + 1, 1, z2 + 1, 'minecraft:oak_fence'),
          W.fill(x1 - 1, 1, z1, x1 - 1, 1, z2, 'minecraft:oak_fence'), W.fill(x2 + 1, 1, z1, x2 + 1, 1, z2, 'minecraft:oak_fence'),
          W.sb(x2 + 1, 1, (z1 + z2) // 2, 'minecraft:oak_fence_gate[facing=east]'), W.sb(x1 - 1, 2, z1 - 1, 'minecraft:carved_pumpkin'),
          W.fill(x1 - 1, 0, z1 - 1, x1 - 1, 0, z1 - 1, 'minecraft:grass_block')]
    occupy(x1 - 1, x2 + 1, z1 - 1, z2 + 1, 1)
    return L


def lamp_post(x, z):
    return [W.fill(x, 1, z, x, 3, z, 'minecraft:spruce_fence'), W.sb(x, 4, z, 'minecraft:lantern')]


def bench(x, z, facing):
    return [W.sb(x, 1, z, f'minecraft:spruce_stairs[facing={facing}]'), W.sb(x + (1 if facing in ('north', 'south') else 0), 1,
                                                                                   z + (1 if facing in ('east', 'west') else 0), f'minecraft:spruce_stairs[facing={facing}]')]


def scatter(n, min_gap, place, rmin=8, rmax=R - 5, tries=4000):
    """빈 자리에 n개를 서로 min_gap 넘게 떨어지게 무작위로."""
    out, L = [], []
    for _ in range(tries):
        if len(out) >= n:
            break
        a, r = rng.random() * math.tau, rmin + (rmax - rmin) * math.sqrt(rng.random())
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if any((x + dx, z + dz) in OCC for dx in (-2, 0, 2) for dz in (-2, 0, 2)) or any(math.hypot(x - p, z - q) < min_gap for p, q in out):
            continue
        out.append((x, z))
        L += place(x, z)
    return L


# ── 전부 ──
def plaza():
    """(명령 목록, NPC 목록). NPC: (종류, x, y, z, 태그, yaw) — 광장 기준 상대."""
    import tips
    OCC.clear()
    MAIN.clear()
    G0, C0, M0 = W.G, W.CENTER, W.MART
    W.G, W.CENTER, W.MART = 0, CENTER_P, MART_P            # 센터·숍 모양은 build_world 것을 광장 좌표로
    try:
        L = base() + paving() + fountain()
        occupy(CENTER_P[0] - 4, CENTER_P[1] + 1, CENTER_P[2] - 2, CENTER_P[3] + 2)
        occupy(MART_P[0] - 2, MART_P[1] + 5, MART_P[2] - 2, MART_P[3] + 2)
        L += W.center() + W.mart()
        npcs = [('poke:nurse', CENTER_P[1] - 3, 1, 0, 'poke.nurse', 90),
                ('poke:merchant', MART_P[0] + 5, 1, (MART_P[2] + MART_P[3]) // 2 - 3, 'poke.merchant_poke', -90),   # 코블몬 물품 (W.mart 진열 위치와 같음)
                ('poke:merchant', MART_P[0] + 5, 1, (MART_P[2] + MART_P[3]) // 2 + 3, 'poke.merchant_mc', -90)]     # 마인크래프트 물품
        fronts = []
        makers = {'house': lambda x, z, d: house(x, z, d), 'house2': lambda x, z, d: house(x, z, d, 'mossy_stone_brick', 'mossy_cobblestone', 'birch_planks', 'stripped_dark_oak_log'),
                  'diner': lambda x, z, d: diner(x, z, d), 'diner2': lambda x, z, d: diner(x, z, d, 'lime'),
                  'mimikyu': mimikyu, 'gymlet': gymlet}
        for key, kind, x1, z1, door in TIP_HOUSES:
            cmds, (spots, front) = makers[kind](x1, z1, door)
            L += cmds
            fronts.append(front)
            for (tid, *_rest), (x, y, z, yaw) in zip([t for t in tips.TIPS if t[1] == key], spots):
                npcs.append((f'poke:tip_{tid}', x, y, z, f'poke.tip_{tid}', yaw))
        # 길: 출구 4곳 + 센터·숍 문 + 집마다 (굽게)
        L += path([(0, 6), (2, 30), (-3, 52), (1, R)])
        L += path([(-1, -6), (4, -24), (-2, -46), (2, -R)])
        L += path([(6, -2), (CENTER_P[0] - 2, 0)], 1.2)
        L += path([(12, -15), (30, -20), (50, -14), (R, -6)])
        L += path([(-6, 3), (MART_P[1] + 3, (MART_P[2] + MART_P[3]) // 2)], 1.2)
        L += path([(-8, -9), (-28, -20), (-50, -16), (-R, -24)])
        # 19. 센터·숍 문 앞 흰 발판 다시 깔기 (길이 비스듬히 들어오며 한쪽을 덮어 좌우가 안 맞았음): 문 가운데 기준 좌우 2칸씩 같게
        for (bx1, bx2, bz1, bz2), door in ((CENTER_P, 'w'), (MART_P, 'e')):
            fx, out, zm = (bx1, -1, (bz1 + bz2) // 2) if door == 'w' else (bx2, 1, (bz1 + bz2) // 2)
            L.append(W.fill(min(fx + 3 * out, fx + 6 * out), 0, zm - 2, max(fx + 3 * out, fx + 6 * out), 0, zm + 2, 'minecraft:smooth_quartz'))
        for fx, fz in fronts:                               # 샛길: 가장 가까운 큰길 칸에서 문 앞까지, 가운데를 살짝 비틀어
            sx, sz = min(MAIN, key=lambda c: (c[0] - fx) ** 2 + (c[1] - fz) ** 2)
            mx, mz = (sx + fx) / 2 + rng.uniform(-3, 3), (sz + fz) / 2 + rng.uniform(-3, 3)
            L += path([(sx, sz), (mx, mz), (fx, fz)], 1.0, main=False)
        # 연못·밭·바위
        L += pond(-55, 2) + farm_patch(-30, 46) + boulder(52, 40, 2.6) + boulder(-60, -40, 2.2) + boulder(58, -46, 2.8) + boulder(-20, 62, 2.0)
        # 가로등 (길가), 벤치 (분수 둘레)
        for x, z in ((4, -20), (-5, -38), (5, 24), (-4, 44), (26, -16), (46, -15), (-20, -14), (-44, -17), (-14, 10), (10, 2)):
            if (x, z) not in OCC:
                L += lamp_post(x, z)
                OCC.add((x, z))
        L += bench(-9, -9, 'south') + bench(8, 9, 'north') + bench(9, -10, 'west')
        # 나무 (참나무·자작나무·벚나무 섞어서), 덤불, 꽃
        L += scatter(26, 7, lambda x, z: tree(x, z, rng.choice(['oak', 'oak', 'birch', 'cherry'])), rmin=16)
        L += scatter(30, 3, lambda x, z: [W.sb(x, 1, z, 'minecraft:' + rng.choice(['azalea_leaves[persistent=true]', 'flowering_azalea_leaves[persistent=true]', 'oak_leaves[persistent=true]']))], rmin=10)
        flowers = ['poppy', 'dandelion', 'cornflower', 'allium', 'azure_bluet', 'oxeye_daisy', 'lily_of_the_valley', 'pink_tulip', 'short_grass', 'short_grass']
        L += scatter(160, 1.5, lambda x, z: [W.sb(x, 1, z, 'minecraft:' + rng.choice(flowers))], rmin=7, tries=20000)
        L += [W.label(ARRIVE[0] + 0.5, 3.2, ARRIVE[2] + 0.5, '포켓몬 마을 광장', 'aqua', 0.9, tag='poke.plaza')]
    finally:
        W.G, W.CENTER, W.MART = G0, C0, M0
    return L, npcs


def plaza_mod():
    """Cobblemon 블록: 센터 회복 장치·PC (모드 전용)."""
    x1, x2, z1, z2 = CENTER_P
    L = []
    for z in (-3, 3):
        L += [W.sb(x2 - 5, 2, z, 'minecraft:air'), W.sb(x2 - 5, 1, z, 'cobblemon:healing_machine[facing=west,natural=false]')]
    for x in (x1 + 15, x1 + 17):
        L += [W.sb(x, 1, z1 + 2, 'cobblemon:pc[facing=north,part=bottom]'), W.sb(x, 2, z1 + 2, 'cobblemon:pc[facing=north,part=top]')]
    L.append(W.label(x1 + 16.5, 3.6, z1 + 2.8, 'PC 박스', 'aqua', 0.9, tag='poke.plaza'))
    return L


def relative(cmd):
    """절대 좌표 명령 → ~상대 좌표 (fill·setblock·summon)."""
    if cmd.startswith('fill '):
        p = cmd.split(' ', 7)
        return ' '.join([p[0]] + [f'~{v}' for v in p[1:7]] + p[7:])
    if cmd.startswith('setblock '):
        p = cmd.split(' ', 4)
        return ' '.join([p[0]] + [f'~{v}' for v in p[1:4]] + p[4:])
    if cmd.startswith('summon '):
        p = cmd.split(' ', 5)
        return ' '.join(p[:2] + [f'~{v}' for v in p[2:5]] + p[5:])
    return cmd


if __name__ == '__main__':
    cmds, npcs = plaza()
    print(len(cmds), 'commands', len(npcs), 'npcs')
    assert all(relative(c).count('~') >= 3 or not c.startswith(('fill', 'setblock', 'summon')) for c in cmds)
