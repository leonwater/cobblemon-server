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
CENTER = (8, 24, -72, -52)           # 포켓몬센터 x1,x2,z1,z2 (문은 서쪽, 길 쪽)
GYM_ROAD = (21, 199, -19, -15)       # 광장 → 체육관 거리 → 사천왕 본부
GYM_X = (40, 80, 120, 160)           # 배지 체육관 x 시작 (길 북쪽·남쪽에 하나씩, 21x25)
E4 = (200, 240, -46, 12)             # 사천왕 본부 (문은 서쪽): 방 4개 + 명예의 전당
BOUNDS = (-40, 250, -125, 20)        # 마을 둘레 벽
# 체육관 테마 바닥 (번호 순): 바위·물·전기·풀·독·에스퍼·불꽃·땅 / 사천왕: 얼음·격투·고스트·드래곤
GYM_THEME = ['cobblestone', 'prismarine', 'yellow_concrete', 'moss_block', 'purple_concrete', 'magenta_concrete',
             'red_nether_bricks', 'coarse_dirt']
GYM_ROOF = ['gray_terracotta', 'blue_terracotta', 'yellow_terracotta', 'lime_terracotta', 'purple_terracotta',
            'magenta_terracotta', 'red_terracotta', 'brown_terracotta']
E4_THEME = ['packed_ice', 'smooth_stone', 'blackstone', 'purpur_block']


def gym_geom(n):
    """n번 체육관(1~8) 위치: 입장 발판·도전자 자리·나가는 발판·관장 자리·밖으로 나올 자리."""
    x0 = GYM_X[(n - 1) // 2]
    xm = x0 + 10
    if n % 2:   # 북쪽 (문은 남쪽 벽 z=-22)
        return dict(box=(x0, x0 + 20, -46, -22), door_z=-22, pad=(xm - 1, -21, 3, 1), inside=(xm + .5, -27.5, 180),
                    exit=(xm - 1, -23, 3, 1), leader=(xm + .5, -42.5, 0), out=(xm + .5, -17.5, 180))
    return dict(box=(x0, x0 + 20, -12, 12), door_z=-12, pad=(xm - 1, -14, 3, 1), inside=(xm + .5, -6.5, 0),
                exit=(xm - 1, -11, 3, 1), leader=(xm + .5, 9.5, 180), out=(xm + .5, -16.5, 0))


def e4_geom():
    """사천왕 본부: 방 k(1~4) = z 구간, 도전자는 서쪽, 사천왕은 동쪽. 5번째는 명예의 전당."""
    x1, x2, z1, z2 = E4
    rooms = [(z1 + 1 + 11 * k, z1 + 11 + 11 * k) for k in range(5)]
    return dict(box=E4, pad=(x1 - 2, -18, 1, 3), out=(x1 - 4.5, -16.5, 90), rooms=rooms,
                inside=[(x1 + 6.5, (a + b) / 2 + .5, -90) for a, b in rooms],
                member=[(x2 - 6.5, (a + b) / 2 + .5, 90) for a, b in rooms[:4]],
                exit=(x1 + 2, rooms[4][0] + 4, 1, 3))


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


def emblem(plane_x, cz, cy, r=3):
    """원작풍 몬스터볼 엠블럼 (x 고정 벽면에, 지름 2r+1): 위 빨강, 가운데 검은 띠, 아래 흰색, 가운데 단추."""
    L = []
    for dz in range(-r, r + 1):
        for dy in range(-r, r + 1):
            d = math.hypot(dz, dy)
            if d > r + 0.3:
                continue
            if d > r - 0.7:
                b = 'black_concrete'
            elif abs(dy) <= 0 or (abs(dy) <= 1 and abs(dz) <= 1):
                b = 'white_concrete' if dz == 0 and dy == 0 else 'black_concrete'
            else:
                b = 'red_concrete' if dy > 0 else 'white_concrete'
            L.append(sb(plane_x, cy + dy, cz + dz, 'minecraft:' + b))
    return L


def center():
    x1, x2, z1, z2 = CENTER
    zm = (z1 + z2) // 2
    top = G + 7
    L = ['# ── 포켓몬센터 (원작풍): 흰 벽 + 빨간 지붕 + 몬스터볼 엠블럼 + 유리 자동문 (문은 서쪽) ──',
         fill(x1 - 1, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:smooth_quartz')]
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:red_concrete')
    L += walls(x1, x2, z1, z2, G + 2, top, 'minecraft:white_concrete')
    for z in (z1, z2):
        for x in (x1, x2):
            L.append(fill(x, G + 1, z, x, top, z, 'minecraft:quartz_pillar'))
    for z in range(z1 + 3, z2 - 2, 4):                   # 옆·뒤 창문
        L += [fill(x2, G + 3, z, x2, G + 5, z + 1, 'minecraft:light_blue_stained_glass_pane')]
    for x in range(x1 + 3, x2 - 2, 4):
        L += [fill(x, G + 3, z1, x + 1, G + 5, z1, 'minecraft:light_blue_stained_glass_pane'),
              fill(x, G + 3, z2, x + 1, G + 5, z2, 'minecraft:light_blue_stained_glass_pane')]
    # 정면: 유리 자동문 + 빨간 차양 + 간판 벽 + 몬스터볼 엠블럼
    L += [fill(x1, G + 1, zm - 1, x1, G + 3, zm + 1, 'minecraft:air'),
          fill(x1, G + 1, zm - 3, x1, G + 4, zm - 2, 'minecraft:light_blue_stained_glass_pane'),
          fill(x1, G + 1, zm + 2, x1, G + 4, zm + 3, 'minecraft:light_blue_stained_glass_pane'),
          fill(x1 - 1, G + 5, zm - 4, x1 - 1, G + 5, zm + 4, 'minecraft:red_concrete'),
          fill(x1, top + 1, zm - 5, x1, top + 7, zm + 5, 'minecraft:white_concrete'),
          fill(x1, top + 8, zm - 5, x1, top + 8, zm + 5, 'minecraft:red_concrete')]
    L += emblem(x1 - 1, zm, top + 4)
    L.append(label(x1 - 1.6, G + 6.6, zm + 0.5, '포켓몬센터', 'red', 1.6, sub='POKéMON CENTER'))
    # 빨간 계단식 지붕 (흰 테두리)
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:white_concrete'),
          fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:red_concrete'),
          fill(x1 + 2, top + 2, z1 + 2, x2 - 1, top + 2, z2 - 2, 'minecraft:red_concrete'),
          fill(x1 + 5, top + 3, z1 + 5, x2 - 3, top + 3, z2 - 5, 'minecraft:red_concrete')]
    # 안: 붉은 카펫 통로, 접수대(간호사·회복 장치는 mod/build_town), 대기 의자, 화분, 조명
    L += [fill(x1 + 1, G + 1, zm - 1, x2 - 6, G + 1, zm + 1, 'minecraft:red_carpet'),
          fill(x2 - 5, G + 1, zm - 4, x2 - 5, G + 1, zm + 4, 'minecraft:quartz_block'),
          fill(x2 - 4, G + 1, zm - 4, x2 - 2, G + 1, zm - 4, 'minecraft:quartz_block'),
          fill(x2 - 4, G + 1, zm + 4, x2 - 2, G + 1, zm + 4, 'minecraft:quartz_block')]
    for x in range(x1 + 3, x2 - 7, 2):
        L += [sb(x, G + 1, z2 - 2, 'minecraft:red_terracotta'), sb(x, G + 1, z2 - 1, 'minecraft:white_carpet')]
    L += [sb(x1 + 1, G + 1, z1 + 1, 'minecraft:potted_flowering_azalea_bush'), sb(x1 + 1, G + 1, z2 - 1, 'minecraft:potted_flowering_azalea_bush')]
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    return L


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
    cz = (CENTER[2] + CENTER[3]) // 2
    L += [fill(x2 + 1, G, cz - 1, CENTER[0] - 1, G, cz + 1, 'minecraft:polished_andesite'),
          fill(MART[1] + 1, G, -64, x1 - 1, G, -62, 'minecraft:polished_andesite')]
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
          fill(x2, G + 6, zm - 4, x2, G + 9, zm + 4, 'minecraft:blue_concrete'),                         # 원작풍 MART 간판 벽
          fill(x2, G + 10, zm - 4, x2, G + 10, zm + 4, 'minecraft:light_blue_concrete'),
          label(x2 + 0.6, G + 6.9, zm + 0.5, 'POKé MART', 'white', 2.2, bg=0),
          label(x2 + 1.6, G + 4.4, zm + 0.5, '프렌들리 숍', 'aqua', 1.0)]
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


def gym(n):
    """배지 체육관 (원작풍): 석상 + 몬스터볼 엠블럼 + 타입색 계단식 지붕. 문은 장식(유리), 드나들기는 발판으로."""
    g = gym_geom(n)
    x1, x2, z1, z2 = g['box']
    xm, dz = (x1 + x2) // 2, g['door_z']
    face = -1 if dz == z2 else 1          # 바깥쪽 방향 (북쪽 체육관은 +z 쪽이 바깥)
    out_z = dz + (1 if dz == z2 else -1)
    top = G + 7
    theme, roof = 'minecraft:' + GYM_THEME[n - 1], 'minecraft:' + GYM_ROOF[n - 1]
    L = [f'# ── {n}번 체육관 ──', fill(x1 - 1, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:polished_andesite'),
         fill(x1 + 1, G, z1 + 1, x2 - 1, G, z2 - 1, theme)]
    L += walls(x1, x2, z1, z2, G + 1, G + 2, 'minecraft:polished_deepslate')
    L += walls(x1, x2, z1, z2, G + 3, top, 'minecraft:light_gray_concrete')
    for x in range(x1, x2 + 1, 5):
        L += [fill(x, G + 1, z1, x, top, z1, 'minecraft:quartz_pillar'), fill(x, G + 1, z2, x, top, z2, 'minecraft:quartz_pillar')]
    for z in range(z1, z2 + 1, 6):
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:quartz_pillar'), fill(x2, G + 1, z, x2, top, z, 'minecraft:quartz_pillar')]
    # 정면: 유리문(장식), 차양, 엠블럼 대신 문 위 몬스터볼 무늬 띠
    L += [fill(xm - 1, G + 1, dz, xm + 1, G + 3, dz, 'minecraft:light_blue_stained_glass'),
          fill(xm - 3, G + 4, out_z, xm + 3, G + 4, out_z, roof),
          fill(xm - 3, G + 5, dz, xm + 3, G + 5, dz, 'minecraft:red_concrete'),
          fill(xm - 3, G + 6, dz, xm + 3, G + 6, dz, 'minecraft:black_concrete'),
          fill(xm - 3, G + 7, dz, xm + 3, G + 7, dz, 'minecraft:white_concrete'),
          label(xm + .5, G + 9, out_z + .5 * (1 if dz == z2 else -1) + .5, f'{n}번 체육관', 'gold', 1.6)]
    for sx in (xm - 5, xm + 5):                          # 입구 석상
        L += [fill(sx, G + 1, out_z, sx, G + 2, out_z, 'minecraft:chiseled_stone_bricks'),
              sb(sx, G + 3, out_z, 'minecraft:red_concrete')]
    # 지붕
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:white_concrete'),
          fill(x1, top + 1, z1, x2, top + 1, z2, roof),
          fill(x1 + 3, top + 2, z1 + 3, x2 - 3, top + 2, z2 - 3, roof),
          fill(x1 + 6, top + 3, z1 + 6, x2 - 6, top + 3, z2 - 6, roof)]
    # 안: 경기장 흰 선, 관장 단상, 발판(입장: 바깥, 나가기: 안쪽), 조명
    lx, lz, _ = g['leader']
    L += [fill(x1 + 3, G, (z1 + z2) // 2, x2 - 3, G, (z1 + z2) // 2, 'minecraft:smooth_quartz'),
          fill(int(lx) - 2, G, int(lz) - 1, int(lx) + 2, G, int(lz) + 1, 'minecraft:quartz_block')]
    for key, glass in (('pad', 'minecraft:lime_stained_glass'), ('exit', 'minecraft:orange_stained_glass')):
        px, pz, w, d = g[key]
        L.append(fill(px, G, pz, px + w - 1, G, pz + d - 1, glass))
    px, pz, _, _ = g['exit']
    L.append(label(px + 1.5, G + 2.5, pz + .5, '◀ 나가기', 'gold', 1.0))
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    return L


def e4_hall():
    """사천왕 본부: 큰 건물 안에 방 4개(서로 막힘) + 명예의 전당."""
    g = e4_geom()
    x1, x2, z1, z2 = g['box']
    top = G + 9
    L = ['# ── 사천왕 본부 ──', fill(x1 - 1, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:polished_andesite')]
    L += walls(x1, x2, z1, z2, G + 1, top, 'minecraft:quartz_bricks')
    for z in range(z1, z2 + 1, 5):
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:gold_block' if z == -17 else 'minecraft:quartz_pillar')]
    for k, (a, b) in enumerate(g['rooms']):
        floor = 'minecraft:' + (E4_THEME[k] if k < 4 else 'gold_block')
        L += [fill(x1 + 1, G, a, x2 - 1, G, b, floor), fill(x1 + 1, top, a, x2 - 1, top, b, 'minecraft:quartz_block')]
        if k < 4:
            L.append(fill(x1 + 1, G + 1, b + 1, x2 - 1, top, b + 1, 'minecraft:quartz_bricks'))   # 방 사이 벽
        for x in range(x1 + 4, x2 - 1, 6):
            L.append(sb(x, top, (a + b) // 2, 'minecraft:sea_lantern'))
    fa, fb = g['rooms'][4]
    L += [fill(x2 - 4, G + 1, fa + 2, x2 - 2, G + 3, fb - 2, 'minecraft:gold_block'),
          label(x2 - 6.5, G + 4, (fa + fb) / 2 + .5, '명예의 전당', 'gold', 2.0, sub='사천왕을 모두 이긴 트레이너')]
    px, pz, w, d = g['pad']
    L += [fill(px, G, pz, px + w - 1, G, pz + d - 1, 'minecraft:lime_stained_glass'),
          fill(x1, G + 1, -18, x1, G + 4, -16, 'minecraft:light_blue_stained_glass'),
          label(x1 - 1.5, top + 3, -16.5, '사천왕', 'gold', 3.0, sub='POKéMON LEAGUE · 배지 8개 필요')]
    L += emblem(x1 - 1, -17, top - 2, r=3)
    px, pz, w, d = g['exit']
    L += [fill(px, G, pz, px + w - 1, G, pz + d - 1, 'minecraft:orange_stained_glass'),
          label(px + .5, G + 2.5, pz + 1.5, '◀ 나가기', 'gold', 1.0)]
    # 지붕
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:white_concrete'),
          fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:purple_terracotta'),
          fill(x1 + 4, top + 2, z1 + 4, x2 - 4, top + 2, z2 - 4, 'minecraft:purple_terracotta')]
    return L


def town():
    x1, x2, z1, z2 = GYM_ROAD
    L = ['# 자동 생성: tools/build_world.py (직접 수정하지 말고 생성기를 고치세요)',
         'kill @e[type=minecraft:text_display,tag=poke.deco]',
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z1, 'minecraft:stone_bricks'), fill(x1, G, z2, x2, G, z2, 'minecraft:stone_bricks'),
         label(x1 + 2.5, G + 4, z2 + 1.5, '▶ 체육관 거리 · 사천왕', 'red', 1.5)]
    for x in (30, 70, 110, 150, 190):                    # 체육관 사이에만 (입장 발판과 안 겹치게)
        L += lamp(x, z1 - 1) + lamp(x, z2 + 1)
    L += hall() + plaza() + street() + mart() + center()
    for n in range(1, 9):
        L += gym(n)
    L += e4_hall()
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
    """Cobblemon 블록: 포켓몬센터 회복 장치·PC, 나무열매 정원 (모드 전용)."""
    x1, x2, z1, z2 = CENTER
    zm = (z1 + z2) // 2
    L = ['# 자동 생성: tools/build_world.py. Cobblemon 블록·나무열매 정원',
         sb(x2 - 2, G + 1, zm - 2, 'cobblemon:healing_machine[facing=west,natural=false]'),
         sb(x2 - 2, G + 1, zm + 2, 'cobblemon:healing_machine[facing=west,natural=false]')]
    for z in (z1 + 2, z1 + 4):
        L += [sb(x1 + 3, G + 1, z, 'cobblemon:pc[facing=south,part=bottom]'), sb(x1 + 3, G + 2, z, 'cobblemon:pc[facing=south,part=top]')]
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
