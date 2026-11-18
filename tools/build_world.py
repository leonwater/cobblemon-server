"""마을(회의장·상점가·체육관)·농장을 짓는 마인크래프트 함수(.mcfunction) 생성기.

크기·위치를 바꾸려면 아래 숫자를 고치고 실행 → 데이터팩의 build 버전(load.mcfunction) +1.
사용: python3 tools/build_world.py
"""
import json
import math
from pathlib import Path

FN = Path(__file__).resolve().parent.parent / 'pack/world/datapacks/pokeserver/data/poke/function'

# ── 마을 (poke:town, 평지. 땅 윗면 y=-60, 서는 높이 y=-59) ──
G = -60
HALL = (-14, 14, -9, 9)              # 회의장 x1,x2,z1,z2 (문은 북쪽)
PLAZA = (-20, 20, -24, -10)          # 회의장 앞 광장 (분수)
STREET = (-3, 3, -112, -25)          # 상점가 길 (남→북)
MART = (-24, -8, -71, -55)           # 프렌들리 숍 (문은 동쪽, 길 쪽)
CENTER_AT = (6, -68)                 # Cobblemon 포켓몬센터 구조물 놓는 곳 (10x14, 입구 서쪽)
GYM_ROAD = (21, 91, -19, -15)        # 광장 → 체육관 길
GYM = (92, 132, -40, 6)              # 체육관 (문은 서쪽)
BOUNDS = (-40, 140, -125, 20)        # 마을 둘레 벽

# ── 농장 (poke:farm, 평지 지면 y=-60) ──
FY = -60
PLOT, GAP = 32, 3                   # 땅 한 칸 32x32, 땅 사이 길 3
COLS_X = [4, 4 + PLOT + GAP, -4 - PLOT + 1, -4 - 2 * PLOT - GAP + 1]  # 각 열의 x 시작
ROWS = 4
FARM_RETURN = (-1, 1, -8, -6)       # 회의장으로 돌아가는 발판


def plots():
    """(번호, x1, z1, x2, z2) 목록. 모드에서도 같은 순서·번호를 씀."""
    out, n = [], 0
    for r in range(ROWS):
        z1 = 3 + r * (PLOT + GAP)
        for x1 in sorted(COLS_X):
            n += 1
            out.append((n, x1, z1, x1 + PLOT - 1, z1 + PLOT - 1))
    return out


def fill(x1, y1, z1, x2, y2, z2, block, mode=''):
    return f'fill {x1} {y1} {z1} {x2} {y2} {z2} {block}{" " + mode if mode else ""}'


def sb(x, y, z, block):
    return f'setblock {x} {y} {z} {block}'


def label(x, y, z, text, color='white', scale=1.0, tag='poke.deco', sub=None, bg=-1442840576):
    extra = f',{{"text":"\\\\n{sub}","color":"gray","bold":false}}' if sub else ''
    return (f'summon minecraft:text_display {x} {y} {z} {{Tags:["{tag}"],billboard:"center",shadow:1b,'
            f'background:{bg},transformation:{{scale:[{scale}f,{scale}f,{scale}f],translation:[0f,0f,0f],'
            f'left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}},'
            f'text:\'{{"text":"{text}","color":"{color}","bold":true,"extra":[{extra[1:]}]}}\'}}'.replace('"extra":[]', '"extra":[""]'))


def lamp(x, z):
    return [sb(x, G + 1, z, 'minecraft:stone_brick_wall'), sb(x, G + 2, z, 'minecraft:stone_brick_wall'),
            sb(x, G + 3, z, 'minecraft:lantern')]


def walls(x1, x2, z1, z2, y1, y2, block):
    return [fill(x1, y1, z1, x2, y2, z1, block), fill(x1, y1, z2, x2, y2, z2, block),
            fill(x1, y1, z1, x1, y2, z2, block), fill(x2, y1, z1, x2, y2, z2, block)]


def hall():
    x1, x2, z1, z2 = HALL
    top = G + 6
    L = ['# ── 회의장: 흰 벽 + 짙은 나무 기둥 + 슬레이트 박공지붕 ──',
         fill(x1 - 1, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:stone_bricks'),
         fill(x1 + 1, G, z1 + 1, x2 - 1, G, z2 - 1, 'minecraft:dark_oak_planks')]
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:stone_bricks')
    L += walls(x1, x2, z1, z2, G + 2, top, 'minecraft:white_concrete')
    for x in range(x1, x2 + 1, 4):                      # 긴 벽 기둥 + 사이 창문
        L += [fill(x, G + 1, z1, x, top, z1, 'minecraft:stripped_dark_oak_log'),
              fill(x, G + 1, z2, x, top, z2, 'minecraft:stripped_dark_oak_log')]
        if x + 2 < x2:
            L += [fill(x + 1, G + 2, z1, x + 3, G + 4, z1, 'minecraft:glass_pane'),
                  fill(x + 1, G + 2, z2, x + 3, G + 4, z2, 'minecraft:glass_pane')]
    for z in (z1, z2):
        L.append(fill(x1, top, z, x2, top, z, 'minecraft:stripped_dark_oak_log[axis=x]'))
    for x in (x1, x2):
        L += [fill(x, G + 1, z1, x, top, z2, 'minecraft:stripped_dark_oak_log'),
              fill(x, G + 2, z1 + 2, x, G + 4, z2 - 2, 'minecraft:glass_pane')]
    # 박공지붕: 용마루는 x 방향, 양쪽으로 한 칸씩 처마
    w = (z2 - z1 + 2) // 2
    for i in range(w + 1):
        y = top + 1 + i
        za, zb = z1 - 1 + i, z2 + 1 - i
        if za > zb:
            break
        if za == zb:
            L.append(fill(x1 - 1, y, za, x2 + 1, y, za, 'minecraft:deepslate_tiles'))
            break
        L += [fill(x1 - 1, y, za, x2 + 1, y, za, 'minecraft:deepslate_tile_stairs[facing=south]'),
              fill(x1 - 1, y, zb, x2 + 1, y, zb, 'minecraft:deepslate_tile_stairs[facing=north]')]
        if za + 1 <= zb - 1:                             # 박공 벽 (양 끝 삼각형)
            L += [fill(x1, y, za + 1, x1, y, zb - 1, 'minecraft:dark_oak_planks'),
                  fill(x2, y, za + 1, x2, y, zb - 1, 'minecraft:dark_oak_planks'),
                  fill(x1 + 1, y, za + 1, x2 - 1, y, zb - 1, 'minecraft:air')]
    # 입구 (북쪽) + 간판
    L += [fill(-1, G + 1, z1, 1, G + 4, z1, 'minecraft:air'),
          fill(-2, G + 5, z1 - 1, 2, G + 5, z1 - 1, 'minecraft:dark_oak_slab[type=top]'),
          label(0.5, G + 7.2, z1 - 0.6, '회의장', 'gold', 2.0)]
    # 안: 긴 탁자, 의자, 단상, 샹들리에, 책장, 붉은 카펫 통로
    L += [fill(-1, G + 1, z1 + 1, 1, G + 1, z2 - 1, 'minecraft:red_carpet'),
          fill(-7, G + 1, -1, 7, G + 1, 1, 'minecraft:dark_oak_slab[type=top]')]
    for x in range(-7, 8, 2):
        L += [sb(x, G + 1, -2, 'minecraft:dark_oak_stairs[facing=north]'),
              sb(x, G + 1, 2, 'minecraft:dark_oak_stairs[facing=south]')]
    L += [fill(x1 + 1, G + 1, -3, x1 + 3, G + 1, 3, 'minecraft:smooth_quartz'),
          sb(x1 + 2, G + 2, 0, 'minecraft:lectern[facing=east]'),
          fill(x2 - 1, G + 1, z1 + 1, x2 - 1, G + 3, z1 + 3, 'minecraft:bookshelf'),
          fill(x2 - 1, G + 1, z2 - 3, x2 - 1, G + 3, z2 - 1, 'minecraft:bookshelf')]
    for x in (-6, 0, 6):
        L += [fill(x, G + 5, 0, x, top + 2, 0, 'minecraft:chain'), sb(x, G + 4, 0, 'minecraft:lantern[hanging=true]')]
    for x in (x1 + 3, x2 - 3):
        for z in (z1 + 2, z2 - 2):
            L += [sb(x, G + 1, z, 'minecraft:potted_azalea_bush'), sb(x, top, z, 'minecraft:sea_lantern')]
    return L


def plaza():
    x1, x2, z1, z2 = PLAZA
    L = ['# ── 회의장 앞 광장 + 분수 ──',
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z1, 'minecraft:stone_bricks'), fill(x1, G, z2, x2, G, z2, 'minecraft:stone_bricks'),
         fill(x1, G, z1, x1, G, z2, 'minecraft:stone_bricks'), fill(x2, G, z1, x2, G, z2, 'minecraft:stone_bricks'),
         fill(-3, G + 1, -20, 3, G + 1, -14, 'minecraft:stone_bricks'),
         fill(-2, G, -19, 2, G, -15, 'minecraft:stone_bricks'),
         fill(-2, G + 1, -19, 2, G + 1, -15, 'minecraft:water'),
         fill(0, G + 1, -17, 0, G + 2, -17, 'minecraft:stone_brick_wall'), sb(0, G + 3, -17, 'minecraft:sea_lantern')]
    for x, z in ((x1 + 2, z1 + 2), (x2 - 2, z1 + 2), (x1 + 2, z2 - 2), (x2 - 2, z2 - 2)):
        L += lamp(x, z)
    for x in (x1 + 5, x2 - 5):                           # 벤치
        L += [sb(x, G + 1, -17, f'minecraft:spruce_stairs[facing={"west" if x < 0 else "east"}]'),
              sb(x, G + 1, -18, f'minecraft:spruce_stairs[facing={"west" if x < 0 else "east"}]')]
    return L


def street():
    x1, x2, z1, z2 = STREET
    L = ['# ── 상점가: 아치 + 길 + 가로등 + 나무·꽃 ──',
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x1, G, z2, 'minecraft:stone_bricks'), fill(x2, G, z1, x2, G, z2, 'minecraft:stone_bricks'),
         fill(x1 - 1, G + 1, z2 - 1, x1 - 1, G + 5, z2 - 1, 'minecraft:stone_bricks'),
         fill(x2 + 1, G + 1, z2 - 1, x2 + 1, G + 5, z2 - 1, 'minecraft:stone_bricks'),
         fill(x1 - 1, G + 6, z2 - 1, x2 + 1, G + 6, z2 - 1, 'minecraft:dark_oak_planks'),
         fill(x1 - 1, G + 7, z2 - 1, x2 + 1, G + 7, z2 - 1, 'minecraft:dark_oak_slab'),
         label(0.5, G + 8, z2 - 0.5, '상점가', 'gold', 2.0, sub='포켓몬센터 · 프렌들리 숍'),
         fill(-6, G, z1, 6, G, z1 + 6, 'minecraft:polished_andesite'),   # 북쪽 끝 작은 광장
         fill(-1, G + 1, z1 + 3, 1, G + 1, z1 + 3, 'minecraft:stone_brick_wall')]
    for z in range(z2 - 6, z1 + 6, -10):
        L += lamp(x1 - 2, z) + lamp(x2 + 2, z)
        L += [f'place feature minecraft:birch {x1 - 6} {G + 1} {z - 5}', f'place feature minecraft:birch {x2 + 6} {G + 1} {z - 5}']
    flowers = ['poppy', 'dandelion', 'cornflower', 'allium', 'oxeye_daisy', 'azure_bluet']
    for i, z in enumerate(range(z2 - 2, z1 + 2, -3)):
        L += [sb(x1 - 1, G + 1, z, f'minecraft:{flowers[i % 6]}'), sb(x2 + 1, G + 1, z, f'minecraft:{flowers[(i + 3) % 6]}')]
    # 포켓몬센터·숍 앞 진입로
    cx, cz = CENTER_AT
    L += [fill(x2 + 1, G, cz + 6, cx + 2, G, cz + 7, 'minecraft:polished_andesite'),
          fill(MART[1] + 1, G, -64, x1 - 1, G, -62, 'minecraft:polished_andesite'),
          label(cx + 5.5, G + 13, cz + 7, '포켓몬센터', 'red', 2.0)]
    return L


def mart():
    x1, x2, z1, z2 = MART
    zm = (z1 + z2) // 2
    L = ['# ── 프렌들리 숍: 흰 벽 + 파란 계단식 지붕 + 유리 가게 앞 (문은 동쪽) ──',
         fill(x1 - 1, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:smooth_quartz')]
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:light_blue_concrete')
    L += walls(x1, x2, z1, z2, G + 2, G + 5, 'minecraft:white_concrete')
    for x in (x1, x2):
        for z in (z1, z2):
            L.append(fill(x, G + 1, z, x, G + 5, z, 'minecraft:quartz_pillar'))
    L += [fill(x2, G + 2, z1 + 2, x2, G + 4, z2 - 2, 'minecraft:light_blue_stained_glass_pane'),   # 가게 앞 유리
          fill(x2, G + 1, zm - 1, x2, G + 3, zm + 1, 'minecraft:air'),                                  # 입구
          fill(x2, G + 5, z1, x2, G + 5, z2, 'minecraft:blue_concrete'),                                # 간판 띠
          fill(x2 + 1, G + 4, zm - 3, x2 + 1, G + 4, zm + 3, 'minecraft:blue_concrete'),                # 차양
          label(x2 + 1.6, G + 6.6, zm + 0.5, '프렌들리 숍', 'white', 1.8, sub='POKé MART')]
    for z in range(z1 + 3, z2 - 2, 4):                   # 옆 창문
        L += [fill(x1, G + 2, z, x1, G + 4, z + 1, 'minecraft:light_blue_stained_glass_pane')]
    for x in range(x1 + 3, x2 - 2, 4):
        L += [fill(x, G + 2, z1, x + 1, G + 4, z1, 'minecraft:light_blue_stained_glass_pane'),
              fill(x, G + 2, z2, x + 1, G + 4, z2, 'minecraft:light_blue_stained_glass_pane')]
    # 파란 계단식 지붕
    L += [fill(x1 - 1, G + 6, z1 - 1, x2 + 1, G + 6, z2 + 1, 'minecraft:light_blue_concrete'),
          fill(x1, G + 6, z1, x2, G + 6, z2, 'minecraft:blue_concrete'),
          fill(x1 + 2, G + 7, z1 + 2, x2 - 2, G + 7, z2 - 2, 'minecraft:blue_concrete'),
          fill(x1 + 5, G + 8, z1 + 5, x2 - 5, G + 8, z2 - 5, 'minecraft:blue_concrete')]
    # 안: 진열대 두 줄, 계산대, 조명
    for z in (zm - 4, zm + 4):
        L += [fill(x1 + 3, G + 1, z, x2 - 6, G + 1, z, 'minecraft:barrel[facing=up]'),
              fill(x1 + 3, G + 2, z, x2 - 6, G + 2, z, 'minecraft:spruce_trapdoor[half=bottom,open=false]')]
    L += [fill(x1 + 1, G + 1, z1 + 1, x1 + 1, G + 3, z2 - 1, 'minecraft:bookshelf'),
          fill(x2 - 4, G + 1, z1 + 1, x2 - 4, G + 1, z1 + 4, 'minecraft:smooth_quartz'),
          fill(x2 - 4, G + 1, z1 + 4, x2 - 2, G + 1, z1 + 4, 'minecraft:smooth_quartz')]
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            L.append(sb(x, G + 5, z, 'minecraft:sea_lantern'))
    return L


def gym():
    x1, x2, z1, z2 = GYM
    zm = (z1 + z2) // 2
    top = G + 8
    L = ['# ── 체육관: 진회색 아래벽 + 밝은 위벽 + 석영 기둥 + 붉은 계단식 지붕 (문은 서쪽) ──',
         fill(x1 - 1, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite')]
    L += walls(x1, x2, z1, z2, G + 1, G + 2, 'minecraft:polished_deepslate')
    L += walls(x1, x2, z1, z2, G + 3, top, 'minecraft:light_gray_concrete')
    for x in range(x1, x2 + 1, 6):
        L += [fill(x, G + 1, z1, x, top, z1, 'minecraft:quartz_pillar'), fill(x, G + 1, z2, x, top, z2, 'minecraft:quartz_pillar')]
        if x + 3 < x2:
            L += [fill(x + 2, G + 5, z1, x + 4, G + 7, z1, 'minecraft:glass_pane'), fill(x + 2, G + 5, z2, x + 4, G + 7, z2, 'minecraft:glass_pane')]
    for z in range(z1, z2 + 1, 6):
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:quartz_pillar'), fill(x2, G + 1, z, x2, top, z, 'minecraft:quartz_pillar')]
    L += [fill(x1, G + 1, zm - 2, x1, G + 5, zm + 2, 'minecraft:air'),                         # 입구
          fill(x1 - 1, G + 6, zm - 3, x1 - 1, G + 6, zm + 3, 'minecraft:red_terracotta'),
          label(x1 - 1.6, top + 3, zm + 0.5, '체육관', 'red', 3.0, sub='POKéMON GYM')]
    # 붉은 계단식 지붕
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:red_nether_bricks'),
          fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:red_terracotta'),
          fill(x1 + 3, top + 2, z1 + 3, x2 - 3, top + 2, z2 - 3, 'minecraft:red_terracotta'),
          fill(x1 + 7, top + 3, z1 + 7, x2 - 7, top + 3, z2 - 7, 'minecraft:red_terracotta')]
    # 안: 배틀 필드(잔디 + 흰 선 + 가운데 원), 관중석, 관장 단상
    ax1, ax2, az1, az2 = x1 + 8, x2 - 8, z1 + 9, z2 - 9
    L += [fill(ax1, G, az1, ax2, G, az2, 'minecraft:moss_block'),
          fill(ax1, G, az1, ax2, G, az1, 'minecraft:smooth_quartz'), fill(ax1, G, az2, ax2, G, az2, 'minecraft:smooth_quartz'),
          fill(ax1, G, az1, ax1, G, az2, 'minecraft:smooth_quartz'), fill(ax2, G, az1, ax2, G, az2, 'minecraft:smooth_quartz'),
          fill((ax1 + ax2) // 2, G, az1, (ax1 + ax2) // 2, G, az2, 'minecraft:smooth_quartz')]
    cxm = (ax1 + ax2) // 2
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            if 3.5 <= math.hypot(dx, dz) < 4.5:
                L.append(sb(cxm + dx, G, zm + dz, 'minecraft:smooth_quartz'))
    for i in range(3):                                   # 양옆 관중석
        L += [fill(ax1, G + 1 + i, z1 + 1 + i, ax2, G + 1 + i, z1 + 1 + i, 'minecraft:stone_brick_stairs[facing=north]'),
              fill(ax1, G + 1 + i, z2 - 1 - i, ax2, G + 1 + i, z2 - 1 - i, 'minecraft:stone_brick_stairs[facing=south]')]
        L += [fill(ax1, G + 1, z1 + 1, ax2, G + i, z1 + 1 + i, 'minecraft:stone_bricks')] if i else []
        L += [fill(ax1, G + 1, z2 - 1 - i, ax2, G + i, z2 - 1, 'minecraft:stone_bricks')] if i else []
    L += [fill(x2 - 5, G + 1, zm - 4, x2 - 1, G + 1, zm + 4, 'minecraft:quartz_block'),
          fill(x2 - 3, G + 2, zm - 2, x2 - 1, G + 2, zm + 2, 'minecraft:quartz_block'),
          fill(x2 - 6, G + 1, zm - 4, x2 - 6, G + 1, zm + 4, 'minecraft:quartz_stairs[facing=east]')]
    for x in range(x1 + 4, x2 - 1, 6):
        for z in range(z1 + 4, z2 - 1, 6):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    return L


def town():
    x1, x2, z1, z2 = GYM_ROAD
    L = ['# 자동 생성: tools/build_world.py (직접 수정하지 말고 생성기를 고치세요)',
         'kill @e[type=minecraft:text_display,tag=poke.deco]',
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z1, 'minecraft:stone_bricks'), fill(x1, G, z2, x2, G, z2, 'minecraft:stone_bricks'),
         label(x1 + 2.5, G + 4, z2 + 1.5, '▶ 체육관', 'red', 1.5)]
    for x in range(x1 + 6, x2, 12):
        L += lamp(x, z1 - 1) + lamp(x, z2 + 1)
    L += hall() + plaza() + street() + mart() + gym()
    # 둘레 벽: 모험 모드라 못 올라가지만 높이 제한까지 막음 (fill 한 번 최대 32768칸)
    bx1, bx2, bz1, bz2 = BOUNDS
    for a in range(bx1, bx2 + 1, 80):
        b = min(a + 79, bx2)
        L += [fill(a, G + 1, bz1, b, 319, bz1, 'minecraft:barrier'), fill(a, G + 1, bz2, b, 319, bz2, 'minecraft:barrier')]
    for a in range(bz1, bz2 + 1, 80):
        b = min(a + 79, bz2)
        L += [fill(bx1, G + 1, a, bx1, 319, b, 'minecraft:barrier'), fill(bx2, G + 1, a, bx2, 319, b, 'minecraft:barrier')]
    return L


def town_mod():
    """Cobblemon 구조물·블록 (모드 전용)."""
    cx, cz = CENTER_AT
    L = ['# 자동 생성: tools/build_world.py. Cobblemon 공식 포켓몬센터·나무열매 정원',
         f'place template cobblemon:village_plains/village_plains_pokecenter {cx} {G} {cz}',
         fill(cx, G, cz, cx + 9, G + 10, cz + 13, 'minecraft:oak_planks', 'replace minecraft:jigsaw')]
    for i, (x, z) in enumerate(((-12, -45), (6, -45), (-12, -90), (8, -90))):
        L += [f'place template cobblemon:village_plains/plains_berry_{"large" if i % 2 else "small"} {x} {G} {z}',
              fill(x, G, z, x + 6, G + 7, z + 6, 'minecraft:grass_block', 'replace minecraft:jigsaw')]
    return L


def clear_old_village():
    """예전 시작 마을(허공 공간 poke:hub, z 110~240)을 지움."""
    L = ['# 자동 생성: 예전 시작 마을 지우기', 'kill @e[type=minecraft:text_display,tag=poke.deco]']
    L += [fill(x, 60, 110, x, 90, 240, 'minecraft:air') for x in range(-40, 41)]
    return L


def farm():
    L = ['# 자동 생성: tools/build_world.py. 주의: 다시 지으면 길·경계 위의 블록을 덮어씀',
         'kill @e[type=minecraft:text_display,tag=poke.farmdeco]']
    xs = [p[1] for p in plots()] + [p[3] for p in plots()]
    zs = [p[2] for p in plots()] + [p[4] for p in plots()]
    bx1, bx2, bz1, bz2 = min(xs) - 3, max(xs) + 3, -12, max(zs) + 3
    L.append(fill(bx1 + 1, FY, bz1 + 1, bx2 - 1, FY, bz2 - 1, 'minecraft:dirt_path'))   # 전체를 길로 깔고
    for n, x1, z1, x2, z2 in plots():                                                  # 땅만 잔디로
        # 땅 한가운데 이름표: 주인이 생기면 모드가 숨김 (배경 투명)
        L += [fill(x1, FY, z1, x2, FY, z2, 'minecraft:polished_andesite'),
              fill(x1 + 1, FY, z1 + 1, x2 - 1, FY, z2 - 1, 'minecraft:grass_block'),
              label(x1 + PLOT / 2, FY + 2.5, z1 + PLOT / 2, f'농장 {n}', 'yellow', 2.0, tag='poke.farmdeco",'
                    f'"poke.plot{n}', sub='빈 땅 · 땅 문서로 등록', bg=0)]
    x1, x2, z1, z2 = FARM_RETURN
    L += [fill(x1, FY, z1, x2, FY, z2, 'minecraft:light_blue_stained_glass'),
          label(0.5, FY + 3, (z1 + z2) / 2 + 0.5, '◀ 회의장으로', 'aqua', 1.5, tag='poke.farmdeco')]
    # 둘레 벽 (지면~높이 제한, fill 한 번 최대 32768칸이라 나눠서)
    for a in range(bx1, bx2 + 1, 80):
        b = min(a + 79, bx2)
        L += [fill(a, FY + 1, bz1, b, 319, bz1, 'minecraft:barrier'), fill(a, FY + 1, bz2, b, 319, bz2, 'minecraft:barrier')]
    for a in range(bz1, bz2 + 1, 80):
        b = min(a + 79, bz2)
        L += [fill(bx1, FY + 1, a, bx1, 319, b, 'minecraft:barrier'), fill(bx2, FY + 1, a, bx2, 319, b, 'minecraft:barrier')]
    return L, (bx1, bz1, bx2, bz2)


if __name__ == '__main__':
    out = {'build/town.mcfunction': town(), 'mod/build_town.mcfunction': town_mod(),
           'build/clear_village.mcfunction': clear_old_village()}
    f, box = farm()
    out['build/farm.mcfunction'] = f
    for path, lines in out.items():
        (FN / path).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    for old in ('build/village.mcfunction', 'mod/build_center.mcfunction'):
        (FN / old).unlink(missing_ok=True)
    # 모드(땅 문서·보호)가 읽는 땅 목록
    cfg = FN.parents[5] / 'config/pokeserver/farms.json'
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(json.dumps({'dimension': 'poke:farm', 'plots': [
        {'id': n, 'x1': x1, 'z1': z1, 'x2': x2, 'z2': z2} for n, x1, z1, x2, z2 in plots()]}, indent=2), encoding='utf-8')
    print({k: len(v) for k, v in out.items()}, 'farm box', box)
