"""마을(스폰 광장·회의장·상점가·체육관·경기장)·농장을 짓는 마인크래프트 함수(.mcfunction) 생성기.

마을(poke:town)은 허공 차원에 떨어진 섬 여러 개: 회의장·상점가·체육관은 서로 1000칸씩 떨어져 워프로만 오감.
섬 둘레는 투명 벽(barrier) + 매 틱 범위 검사(벗어나면 되돌림)라 걸어서 나가거나 떨어질 수 없음.
체육관 경기장·사천왕 방은 문 없는 닫힌 방이라 도전할 때 순간이동으로만 들어감.
크기·위치를 바꾸려면 아래 숫자를 고치고 실행 → 데이터팩의 build 버전(load.mcfunction) +1.
사용: python3 tools/build_world.py
"""
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terrain  # noqa: E402
import tips  # noqa: E402

FN = Path(__file__).resolve().parent.parent / 'pack/world/datapacks/pokeserver/data/poke/function'

# ── 마을 (poke:town, 허공. 땅 윗면 y=-60, 서는 높이 y=-59) ──
# 섬마다 걸어 다닐 수 있는 칸(PLAY) 둘레 40칸은 보기만 하는 판타지 지형(tools/terrain.py)
G = -60
# 15. 회의장·상점가 섬은 없앰 (광장은 야생으로: tools/plaza.py). 예전 섬 자리는 다시 지을 때 비움
OLD_ISLANDS = [('회의장', (-106, 106, -162, 74)), ('상점가', (904, 1096, -98, 98))]
CENTER = (16, 38, -11, 11)           # 포켓몬센터·숍 모양 (광장 기준 상대 좌표, tools/plaza.py가 씀)
MART = (-40, -18, -4, 18)
GYM_PLAY = (1944, 2056, -66, 48)     # 체육관 섬
LOBBY = (1985, 2015, -14, 18)        # 체육관 선택 건물 (문은 북쪽, 넓은 계단 위)
LOBBY_Y = G + 3                      # 체육관 선택 건물 바닥 높이 (계단 3칸 위)
ARENA_X, ARENA_STEP = 3000, 50       # n번 경기장: x ARENA_X+50(n-1) ~ +30, z -18~18 (닫힌 방)
E4 = (3500, 3540, -46, 12)           # 사천왕 본부 (닫힌 방 4개 + 명예의 전당)
# 워프 도착 (x, y, z, yaw): 0 남, 180 북
WARPS = {'gym': (2000.5, LOBBY_Y + 1, -11.5, 0)}   # 광장(hall)은 모드가 정함 (Plaza.java)
NPCS = [  # (NPC 종류, 차원, x, y, z, 태그, yaw). 광장 NPC는 tools/plaza.py
    ('poke:gym_guide', 'poke:town', 2000, LOBBY_Y + 1, 12, 'poke.gymguide', 180),
]


# 체육관 순서 (tools/build_league.py GYMS와 같은 순서: 같은 레벨 기준 약한 관장부터)
GYM_TYPES = ['바위', '전기', '불꽃', '독', '에스퍼', '땅', '풀', '물']
BADGE_BLOCK = ['gray', 'orange', 'red', 'pink', 'yellow', 'green', 'lime', 'blue']
E4_THEME = ['light_blue_concrete', 'iron_block', 'blackstone', 'purpur_block']   # 레드·성호·난천·단델
# 체육관 타입별 경기장 팔레트: 이름, 필드, 벽, 벽 아래 띠, 천장 색, 천장 조명, 관중석, 상징(주색, 보조색)
TYPES = [
    ('바위', 'smooth_sandstone', 'stone_bricks', 'chiseled_stone_bricks', 'brown_concrete', 'glowstone', 'sandstone', ('stone', 'cobblestone')),
    ('물', 'prismarine_bricks', 'light_blue_terracotta', 'dark_prismarine', 'blue_concrete', 'sea_lantern', 'warped_planks', ('blue_concrete', 'light_blue_concrete')),
    ('전기', 'cyan_concrete', 'yellow_terracotta', 'orange_concrete', 'cyan_concrete', 'ochre_froglight', 'cut_copper', ('yellow_concrete', 'orange_concrete')),
    ('풀', 'moss_block', 'green_terracotta', 'mossy_stone_bricks', 'lime_concrete', 'verdant_froglight', 'oak_planks', ('lime_concrete', 'green_concrete')),
    ('독', 'purple_terracotta', 'purpur_block', 'polished_blackstone_bricks', 'purple_concrete', 'pearlescent_froglight', 'crimson_planks', ('magenta_concrete', 'purple_concrete')),
    ('에스퍼', 'pink_terracotta', 'magenta_terracotta', 'purpur_pillar', 'pink_concrete', 'pearlescent_froglight', 'cherry_planks', ('magenta_concrete', 'white_concrete')),
    ('불꽃', 'red_nether_bricks', 'nether_bricks', 'magma_block', 'red_concrete', 'shroomlight', 'mangrove_planks', ('orange_concrete', 'yellow_concrete')),
    ('땅', 'coarse_dirt', 'terracotta', 'packed_mud', 'brown_terracotta', 'ochre_froglight', 'mud_bricks', ('brown_concrete', 'orange_terracotta')),
]


def gym_geom(n):
    """n번 경기장(1~8): 도전자 자리(남쪽)·나가는 발판·관장 자리(북쪽)."""
    x0 = ARENA_X + ARENA_STEP * (n - 1)
    xm = x0 + 15
    # battle: 배틀이 시작되면 도전자를 이 자리로 (관장과 몬스터볼 필드를 사이에 두고 마주 봄 → 포켓몬이 필드 위에 나옴)
    return dict(box=(x0, x0 + 30, -18, 18), inside=(xm + .5, -13.5, 0), exit=(xm - 1, -17, 3, 1), leader=(xm + .5, 14.5, 180),
                battle=(xm + .5, -9.5, 0))


def e4_geom():
    """사천왕 본부: 방 k(1~4) = z 구간, 도전자는 서쪽, 사천왕은 동쪽. 5번째는 명예의 전당."""
    x1, x2, z1, z2 = E4
    rooms = [(z1 + 1 + 11 * k, z1 + 11 + 11 * k) for k in range(5)]
    return dict(box=E4, rooms=rooms,
                inside=[(x1 + 16.5, (a + b) / 2 + .5, -90) for a, b in rooms],
                member=[(x2 - 6.5, (a + b) / 2 + .5, 90) for a, b in rooms[:4]],
                exit=(x1 + 2, rooms[4][0] + 4, 1, 3))

def arenas():
    """닫힌 방들의 (x1, x2, z1, z2) — 범위 검사·청크 불러오기에 씀."""
    return [gym_geom(n)['box'] for n in range(1, 9)] + [E4]


# ── 농장 (poke:farm, 평지 지면 y=-60) ──


# ── 농장 (poke:farm, 평지 지면 y=-60) ──
FY = -60
PLOT, GAP = 32, 3                   # 땅 한 칸 32x32, 땅 사이 길 3
COLS_X = [4, 4 + PLOT + GAP, -4 - PLOT + 1, -4 - 2 * PLOT - GAP + 1]  # 처음 4열의 x 시작 (1~16번, 4줄)
ROWS = 4
EAST_X = 4 + 2 * (PLOT + GAP)       # 7. 25칸으로 넓힘: 동쪽 5번째 열 + 남쪽 5번째 줄 (기존 1~16번 자리는 그대로 → 주인 있는 땅이 안 바뀜)
FARM_RETURN = (-1, 1, -8, -6)       # 광장으로 돌아가는 발판
OLD_FARM_BOX = (-73, -12, 73, 142)  # 16칸 시절 둘레 벽 (넓힐 때 지움)


def plots():
    """(번호, x1, z1, x2, z2) 목록. 모드에서도 같은 순서·번호를 씀. 1~16 예전 그대로, 17~25는 새 땅 (위→아래, 왼→오)."""
    out, n = [], 0
    z = lambda r: 3 + r * (PLOT + GAP)
    for r in range(ROWS):
        for x1 in sorted(COLS_X):
            n += 1
            out.append((n, x1, z(r), x1 + PLOT - 1, z(r) + PLOT - 1))
    new = [(z(r), EAST_X) for r in range(ROWS)] + [(z(ROWS), x1) for x1 in sorted(COLS_X + [EAST_X])]
    for z1, x1 in new:
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
            f'text:\'{{"text":"{text}","color":"{color}","bold":true,"font":"pokeserver:galmuri","extra":[{extra[1:]}]}}\'}}'.replace('"extra":[]', '"extra":[""]'))


def walls(x1, x2, z1, z2, y1, y2, block):
    return [fill(x1, y1, z1, x2, y2, z1, block), fill(x1, y1, z2, x2, y2, z2, block),
            fill(x1, y1, z1, x1, y2, z2, block), fill(x2, y1, z1, x2, y2, z2, block)]


def emblem(plane_x, cz, cy, r=3, top='red_concrete'):
    """원작풍 몬스터볼 엠블럼 (x 고정 벽면에, 지름 2r+1): 얇은 검은 테두리, 위 색·아래 흰색, 가운데 검은 띠, 검은 테 두른 흰 단추."""
    L = []
    for dz in range(-r, r + 1):
        for dy in range(-r, r + 1):
            d = math.hypot(dz, dy)
            if d > r + 0.3:
                continue
            if d > r - 0.6:
                b = 'black_concrete'
            elif d <= (1.5 if r >= 5 else 0.5):
                b = 'white_concrete'
            elif d <= (2.5 if r >= 5 else 1.0):
                b = 'black_concrete'
            elif dy == 0:
                b = 'black_concrete'
            else:
                b = top if dy > 0 else 'white_concrete'
            L.append(sb(plane_x, cy + dy, cz + dz, 'minecraft:' + b))
    return L


def emblem_z(cx, plane_z, cy, r=3):
    """emblem()과 같은 몬스터볼을 z 고정 벽면(정면이 북쪽인 건물)에."""
    out = []
    for line in emblem(0, 0, cy, r):
        _, x, y, z, b = line.split(' ')
        out.append(sb(cx + int(z), int(y), plane_z, b))
    return out


def circle(r):
    """원 안의 (dx, dz) 칸."""
    return [(dx, dz) for dx in range(-r, r + 1) for dz in range(-r, r + 1) if dx * dx + dz * dz <= r * r + r]


def ring(r):
    inner = set(circle(r - 1))
    return [p for p in circle(r) if p not in inner]


def farm():
    L = ['# 자동 생성: tools/build_world.py. 주의: 다시 지으면 길·경계 위의 블록을 덮어씀',
         'kill @e[type=minecraft:text_display,tag=poke.farmdeco]']
    xs = [p[1] for p in plots()] + [p[3] for p in plots()]
    zs = [p[2] for p in plots()] + [p[4] for p in plots()]
    bx1, bx2, bz1, bz2 = min(xs) - 3, max(xs) + 3, -12, max(zs) + 3
    # 예전(16칸) 둘레 벽 지우기 → 넓어진 농장 안에 보이지 않는 벽이 남지 않게
    ox1, oz1, ox2, oz2 = OLD_FARM_BOX
    for a in range(ox1, ox2 + 1, 80):
        L.append(fill(a, FY + 1, oz2, min(a + 79, ox2), 319, oz2, 'minecraft:air replace minecraft:barrier'))
    for a in range(oz1, oz2 + 1, 80):
        L.append(fill(ox2, FY + 1, a, ox2, 319, min(a + 79, oz2), 'minecraft:air replace minecraft:barrier'))
    # 잔디만 길로 바꾸고 땅 안쪽은 길만 잔디로 되돌림 → 다시 지어도 플레이어가 깐 블록(경작지 등)은 그대로
    for a in range(bx1 + 1, bx2, 160):
        L.append(fill(a, FY, bz1 + 1, min(a + 159, bx2 - 1), FY, bz2 - 1, 'minecraft:dirt_path', 'replace minecraft:grass_block'))
    for n, x1, z1, x2, z2 in plots():
        # 땅 한가운데 이름표: 주인이 생기면 모드가 숨김 (배경 투명)
        L += [fill(x1, FY, z1, x2, FY, z1, 'minecraft:polished_andesite'), fill(x1, FY, z2, x2, FY, z2, 'minecraft:polished_andesite'),
              fill(x1, FY, z1, x1, FY, z2, 'minecraft:polished_andesite'), fill(x2, FY, z1, x2, FY, z2, 'minecraft:polished_andesite'),
              fill(x1 + 1, FY, z1 + 1, x2 - 1, FY, z2 - 1, 'minecraft:grass_block', 'replace minecraft:dirt_path'),
              label(x1 + PLOT / 2, FY + 2.5, z1 + PLOT / 2, f'농장 {n}', 'yellow', 2.0, tag='poke.farmdeco",'
                    f'"poke.plot{n}', sub='빈 땅 · 땅 문서로 등록', bg=0)]
    x1, x2, z1, z2 = FARM_RETURN
    L += [fill(x1, FY, z1, x2, FY, z2, 'minecraft:light_blue_stained_glass'),
          label(0.5, FY + 3, (z1 + z2) / 2 + 0.5, '◀ 광장으로', 'aqua', 1.5, tag='poke.farmdeco')]
    # 둘레 벽 (지면~높이 제한, fill 한 번 최대 32768칸이라 나눠서)
    for a in range(bx1, bx2 + 1, 80):
        b = min(a + 79, bx2)
        L += [fill(a, FY + 1, bz1, b, 319, bz1, 'minecraft:barrier'), fill(a, FY + 1, bz2, b, 319, bz2, 'minecraft:barrier')]
    for a in range(bz1, bz2 + 1, 80):
        b = min(a + 79, bz2)
        L += [fill(bx1, FY + 1, a, bx1, 319, b, 'minecraft:barrier'), fill(bx2, FY + 1, a, bx2, 319, b, 'minecraft:barrier')]
    return L, (bx1, bz1, bx2, bz2)


def island_walls(play, name):
    """걸어 다닐 수 있는 칸 둘레의 높이 제한까지 투명 벽 (언덕 블록은 그대로 두고 빈칸만). 한 번에 32768칸이라 나눠서."""
    x1, x2, z1, z2 = play
    L = [f'# ── {name} 섬 투명 벽 ──']
    for a in range(x1, x2 + 1, 80):
        b = min(a + 79, x2)
        L += [fill(a, G + 1, z1, b, 319, z1, 'minecraft:barrier', 'replace minecraft:air'),
              fill(a, G + 1, z2, b, 319, z2, 'minecraft:barrier', 'replace minecraft:air')]
    for a in range(z1, z2 + 1, 80):
        b = min(a + 79, z2)
        L += [fill(x1, G + 1, a, x1, 319, b, 'minecraft:barrier', 'replace minecraft:air'),
              fill(x2, G + 1, a, x2, 319, b, 'minecraft:barrier', 'replace minecraft:air')]
    return L


def glow(x1, x2, z1, z2, y, step=4):
    """실내를 밝게: 보이지 않는 빛 블록(밝기 15)을 격자로. 모험 모드라 부수거나 바꿀 수 없음."""
    return [sb(x, y, z, 'minecraft:light[level=15]') for x in range(x1 + 2, x2 - 1, step) for z in range(z1 + 2, z2 - 1, step)]


def stone_lantern(x, z, y=None):
    """동양풍 석등: 받침 기둥 + 등불 + 넓은 지붕."""
    y = G + 1 if y is None else y
    return [sb(x, y, z, 'minecraft:stone_bricks'), sb(x, y + 1, z, 'minecraft:stone_brick_wall'), sb(x, y + 2, z, 'minecraft:lantern'),
            fill(x - 1, y + 3, z - 1, x + 1, y + 3, z + 1, 'minecraft:stone_brick_slab'), sb(x, y + 3, z, 'minecraft:stone_bricks'),
            sb(x, y + 4, z, 'minecraft:stone_button[face=floor]')]


def big_windows(x1, x2, z1, z2, y1, y2, skip_x=None):
    """큰 유리창 (벽 기둥 사이 3칸)."""
    L = []
    for x in range(x1 + 2, x2 - 2, 4):
        L += [fill(x, y1, z1, x + 1, y2, z1, 'minecraft:glass_pane'), fill(x, y1, z2, x + 1, y2, z2, 'minecraft:glass_pane')]
    for z in range(z1 + 2, z2 - 2, 4):
        for x in (x1, x2):
            if x != skip_x:
                L.append(fill(x, y1, z, x, y2, z + 1, 'minecraft:glass_pane'))
    return L


def hip_roof(x1, x2, z1, z2, y, block, stairs):
    """모임지붕 (가로 2칸에 1칸씩 올라감)."""
    L = []
    for i in range(20):
        a, b, c, d = x1 - 1 + 2 * i, x2 + 1 - 2 * i, z1 - 1 + 2 * i, z2 + 1 - 2 * i
        if a > b or c > d:
            break
        L += [fill(a, y + i, c, b, y + i, d, block),
              fill(a, y + i, c, b, y + i, c, f'{stairs}[facing=south]'), fill(a, y + i, d, b, y + i, d, f'{stairs}[facing=north]'),
              fill(a, y + i, c + 1, a, y + i, d - 1, f'{stairs}[facing=east]'), fill(b, y + i, c + 1, b, y + i, d - 1, f'{stairs}[facing=west]')]
    return L, y + i


ROOF_STEPS = [0, 1, 2, 3, 5, 7, 9, 11]   # 층마다 안으로 들어가는 칸 → 둥근 빵 모양 계단 지붕 (원작 센터·숍 지붕)


def poke_building(box, door, top, roof, roof_dark, band, inner, inner_band):
    """8. 원작풍 포켓몬센터·프렌들리 숍 공통 외관 (참고 사진: 흰 벽, 층층이 쌓인 둥근 지붕, 정면 몬스터볼 간판, 파란 창 격자).
    벽은 2겹(바깥 흰색, 안쪽 실내색은 각 건물이 칠함). door: 문이 있는 쪽 'w'(x1) / 'e'(x2). 지붕 꼭대기 y를 함께 돌려줌."""
    x1, x2, z1, z2 = box
    zm = (z1 + z2) // 2
    fx = x1 if door == 'w' else x2            # 정면 벽
    out = -1 if door == 'w' else 1            # 바깥쪽 방향
    L = [fill(x1 - 2, G, z1 - 2, x2 + 2, G, z2 + 2, 'minecraft:smooth_stone'),                      # 받침
         fill(x1, G, z1, x2, G, z2, 'minecraft:smooth_quartz')]
    L += walls(x1, x2, z1, z2, G + 1, top, 'minecraft:white_concrete')
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:light_gray_concrete')                       # 밑동
    L += walls(x1, x2, z1, z2, G + 6, G + 6, f'minecraft:{band}')                                   # 창 사이 색 띠
    L += walls(x1, x2, z1, z2, top, top, 'minecraft:smooth_quartz')                                 # 처마 밑
    L += walls(x1 + 1, x2 - 1, z1 + 1, z2 - 1, G + 1, top - 1, f'minecraft:{inner}')                 # 안쪽 벽
    L += walls(x1 + 1, x2 - 1, z1 + 1, z2 - 1, G + 5, G + 5, f'minecraft:{inner_band}')
    L.append(fill(x1 + 1, top, z1 + 1, x2 - 1, top, z2 - 1, 'minecraft:smooth_quartz'))             # 천장
    # 파란 창 격자 (3칸 유리 + 흰 창살), 아래·위 두 줄. 벽 두 겹을 함께 뚫음
    for y1, y2 in ((G + 2, G + 4), (G + 7, G + 8)):
        for x in range(x1 + 2, x2 - 2, 4):
            L += [fill(x, y1, z1, x + 2, y2, z1 + 1, 'minecraft:light_blue_stained_glass'),
                  fill(x, y1, z2 - 1, x + 2, y2, z2, 'minecraft:light_blue_stained_glass')]
        for z in range(z1 + 2, z2 - 2, 4):
            for x in (x1, x2):
                if x == fx and abs(z + 1 - zm) <= 6 or x != fx:
                    continue                                                                          # 정면 현관 자리·뒷벽(벽화·진열)
                L.append(fill(min(x, x - out), y1, z, max(x, x - out), y2, z + 2, 'minecraft:light_blue_stained_glass'))
    # 지붕: 처마는 벽 밖으로 1칸, 위로 갈수록 둥글게 들어감. 2번째 층은 흰 줄무늬, 가장자리는 짙은 색
    y = top + 1
    for i, d in enumerate(ROOF_STEPS):
        a1, a2, c1, c2 = x1 - 1 + d, x2 + 1 - d, z1 - 1 + d, z2 + 1 - d
        if a1 > a2 or c1 > c2:
            break
        blk = 'minecraft:white_concrete' if i == 2 else f'minecraft:{roof}'
        L.append(fill(a1, y, c1, a2, y, c2, blk))
        if i != 2:
            L += walls(a1, a2, c1, c2, y, y, f'minecraft:{roof_dark}') if i == 0 else []
        y += 1
    roof_top = y - 1
    # 정면 현관: 벽에서 2칸 튀어나온 흰 탑 + 둥근 윗모서리 + 몬스터볼 간판 + 유리문
    px1, px2 = sorted((fx + out, fx + 2 * out))
    ptop = top + 8
    L += [fill(px1, G, zm - 6, px2, G, zm + 6, 'minecraft:smooth_stone'),
          fill(px1, G + 1, zm - 6, px2, ptop, zm + 6, 'minecraft:white_concrete'),
          fill(px1, ptop, zm - 6, px2, ptop, zm - 6, 'minecraft:air'), fill(px1, ptop, zm + 6, px2, ptop, zm + 6, 'minecraft:air'),
          fill(px1, ptop - 1, zm - 6, px2, ptop - 1, zm - 6, 'minecraft:smooth_quartz_stairs[facing=south]'),
          fill(px1, ptop - 1, zm + 6, px2, ptop - 1, zm + 6, 'minecraft:smooth_quartz_stairs[facing=north]'),
          fill(px1, ptop, zm - 5, px2, ptop, zm + 5, 'minecraft:smooth_quartz'),
          fill(px1, G + 1, zm - 6, px2, G + 1, zm + 6, 'minecraft:light_gray_concrete'),
          fill(px1, G + 6, zm - 6, px2, G + 6, zm + 6, f'minecraft:{band}')]
    # 문 (3칸 폭, 4칸 높이) + 양옆 유리 + 문 위 유리
    ix1, ix2 = sorted((fx - out, fx + 2 * out))
    L += [fill(ix1, G + 1, zm - 1, ix2, G + 4, zm + 1, 'minecraft:air'),
          fill(px1, G + 1, zm - 3, px2, G + 4, zm - 2, 'minecraft:light_blue_stained_glass'),
          fill(px1, G + 1, zm + 2, px2, G + 4, zm + 3, 'minecraft:light_blue_stained_glass'),
          fill(fx + 2 * out, G + 5, zm - 1, fx + 2 * out, G + 5, zm + 1, 'minecraft:light_blue_stained_glass'),
          fill(fx + 3 * out, G, zm - 2, fx + 6 * out, G, zm + 2, 'minecraft:smooth_quartz')]                # 문 앞 흰 발판
    L += [sb(fx + 3 * out, top + 2 + dy, zm + dz, 'minecraft:yellow_concrete')                            # 노란 테두리
          for dz in range(-6, 7) for dy in range(-6, 7) if 5.3 < math.hypot(dz, dy) <= 6.4]
    L += emblem(fx + 3 * out, zm, top + 2, 5, top=roof)                                                   # 정면 몬스터볼 간판 (튀어나옴)
    # 화단 (참고 사진의 초록 덤불): 현관 양옆
    for z in (zm - 8, zm + 8):
        L += [fill(fx + out, G + 1, z - 1, fx + 2 * out, G + 1, z + 1, 'minecraft:moss_block'),
              fill(fx + out, G + 2, z - 1, fx + 2 * out, G + 2, z + 1, 'minecraft:azalea_leaves[persistent=true]'),
              sb(fx + out, G + 3, z, 'minecraft:flowering_azalea_leaves[persistent=true]')]
    return L, roof_top


def checker_floor(x1, x2, z1, z2, a, b, mark):
    """원작 센터 바닥: 4칸 타일 체크 + 줄 교차점 분홍 표시 (참고 사진 1)."""
    L = []
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if (x - x1) % 4 == 0 and (z - z1) % 4 == 0:
                L.append(sb(x, G, z, f'minecraft:{mark}'))
            elif ((x - x1) // 4 + (z - z1) // 4) % 2:
                L.append(sb(x, G, z, f'minecraft:{b}'))
    return [fill(x1, G, z1, x2, G, z2, f'minecraft:{a}')] + L


def center():
    """포켓몬센터 (문은 서쪽): 흰 벽·빨간 계단 지붕·몬스터볼 간판. 안: 빨간 벽, 뒷벽 대형 몬스터볼 벽화, 체크 바닥, 흰·청록 카운터, 벤치·화분."""
    x1, x2, z1, z2 = CENTER
    zm = 0
    top = G + 10
    L = ['# ── 포켓몬센터 ──']
    body, rtop = poke_building(CENTER, 'w', top, 'red_concrete', 'red_terracotta', 'red_concrete', 'red_concrete', 'red_terracotta')
    L += body
    L += checker_floor(x1 + 2, x2 - 2, z1 + 2, z2 - 2, 'smooth_sandstone', 'birch_planks', 'pink_terracotta')
    for x in range(x1 + 4, x2 - 2, 4):                                                                     # 천장 조명 격자 + 흰 들보
        L.append(fill(x, top, z1 + 2, x, top, z2 - 2, 'minecraft:quartz_pillar[axis=z]'))
        for z in range(z1 + 4, z2 - 2, 4):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    # 뒷벽 대형 몬스터볼 벽화 (노란 테두리)
    L += emblem(x2 - 1, zm, G + 5, 5)
    # 카운터 (청록 몸통 + 석영 상판), 간호사는 카운터 뒤 (x2-3)
    L += [fill(x2 - 5, G + 1, zm - 6, x2 - 5, G + 1, zm + 6, 'minecraft:cyan_concrete'),           # 1칸 깊이: 회복 장치·간호사에 손이 닿게
          fill(x2 - 5, G + 2, zm - 6, x2 - 5, G + 2, zm + 6, 'minecraft:smooth_quartz_slab'),
          fill(x2 - 4, G + 1, zm - 6, x2 - 2, G + 1, zm - 6, 'minecraft:white_concrete'),
          fill(x2 - 4, G + 1, zm + 6, x2 - 2, G + 1, zm + 6, 'minecraft:white_concrete'),
          fill(x2 - 4, G, zm - 5, x2 - 2, G, zm + 5, 'minecraft:light_gray_concrete')]
    # 입구 빨간 카펫 길, 벤치 (빨간 방석 + 유리 칸막이 + 화분)
    L.append(fill(x1 + 2, G + 1, zm - 1, x2 - 7, G + 1, zm + 1, 'minecraft:red_carpet'))
    for z in (z1 + 3, z2 - 3):
        for x in range(x1 + 4, x1 + 13, 4):
            L += [sb(x, G + 1, z, 'minecraft:dark_oak_slab'), sb(x + 1, G + 1, z, 'minecraft:dark_oak_slab'),
                  sb(x, G + 2, z, 'minecraft:red_carpet'), sb(x + 1, G + 2, z, 'minecraft:red_carpet'),
                  sb(x + 2, G + 1, z, 'minecraft:glass_pane'), sb(x + 2, G + 2, z, 'minecraft:glass_pane')]
        L += [sb(x1 + 3, G + 1, z, 'minecraft:spruce_planks'), sb(x1 + 3, G + 2, z, 'minecraft:potted_azalea_bush')]
    L += glow(x1 + 1, x2 - 1, z1 + 1, z2 - 1, G + 4)
    L += [label(x1 - 3.6, G + 5.4, zm + .5, '포켓몬센터', 'white', 1.2, bg=0xC0B01020),
          label(x1 - 3.6, top + 9.6, zm + .5, 'POKéMON CENTER', 'white', 1.6, bg=0x80A01020)]
    return L


def mart():
    """프렌들리 숍 (문은 동쪽): 센터와 같은 흰 몸통 + 파란 계단 지붕·파란 몬스터볼 간판. 안: 흰·하늘색 벽, 진열대, 계산대(점원은 숍 안쪽)."""
    x1, x2, z1, z2 = MART
    zm = (z1 + z2) // 2
    top = G + 9
    L = ['# ── 프렌들리 숍 ──']
    body, rtop = poke_building(MART, 'e', top, 'blue_concrete', 'blue_terracotta', 'blue_concrete', 'white_concrete', 'light_blue_concrete')
    L += body
    L += checker_floor(x1 + 2, x2 - 2, z1 + 2, z2 - 2, 'smooth_quartz', 'light_gray_concrete', 'light_blue_concrete')
    for x in range(x1 + 4, x2 - 2, 4):
        for z in range(z1 + 4, z2 - 2, 4):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    # 진열대 두 줄 (파란 받침 + 통 + 다락문 선반), 뒷벽 파란 몬스터볼
    for z in (zm - 6, zm + 6):
        L += [fill(x1 + 9, G + 1, z, x2 - 5, G + 1, z, 'minecraft:blue_concrete'),
              fill(x1 + 9, G + 2, z, x2 - 5, G + 2, z, 'minecraft:barrel[facing=up]'),
              fill(x1 + 9, G + 3, z, x2 - 5, G + 3, z, 'minecraft:birch_trapdoor[half=bottom,open=false]')]
    L += emblem(x1 + 1, zm, G + 5, 5, top='blue_concrete')
    # 점원(숍 안쪽, x1+5) 앞 계산대: 1칸 높이라 상반신이 보임. 입구 쪽 카펫
    for a, b in ((zm - 4, zm - 2), (zm + 2, zm + 4)):
        L.append(fill(x1 + 6, G + 1, a, x1 + 6, G + 1, b, 'minecraft:light_blue_concrete'))
    L.append(fill(x1 + 8, G + 1, zm - 1, x2 - 2, G + 1, zm + 1, 'minecraft:light_blue_carpet'))
    # 상인 둘 (숍 안쪽 x1+5, zm∓3): 뒤 벽에 진열판(3x3) + 대표 물품 액자 3개 + 머리 위 이름표
    for dz, (top_row, board, items, name, color) in ((-3, ('red_concrete', 'white_concrete', ('cobblemon:poke_ball', 'cobblemon:potion', 'cobblemon:rare_candy'), '포켓몬 상점', 'red')),
                                                       (3, ('grass_block', 'oak_planks', ('minecraft:iron_pickaxe', 'minecraft:wheat', 'minecraft:bricks'), '생활 상점', 'green'))):
        z = zm + dz
        L += [fill(x1 + 1, G + 2, z - 1, x1 + 1, G + 3, z + 1, 'minecraft:' + board), fill(x1 + 1, G + 4, z - 1, x1 + 1, G + 4, z + 1, 'minecraft:' + top_row)]
        L += [f'summon minecraft:item_frame {x1 + 2} {G + 3} {z + k} {{Facing:5b,Fixed:1b,Invulnerable:1b,Tags:["poke.deco"],Item:{{id:"{it}",count:1}}}}'
              for k, it in zip((-1, 0, 1), items)]
        L.append(label(x1 + 5.5, G + 4.0, z + .5, name, color, 0.8))
    L += glow(x1 + 1, x2 - 1, z1 + 1, z2 - 1, G + 4)
    L += [label(x2 + 3.6, G + 5.4, zm + .5, '프렌들리 숍', 'white', 1.2, bg=0xC0104090),
          label(x2 + 3.6, top + 9.6, zm + .5, 'POKé MART', 'white', 1.6, bg=0x80104090)]
    return L


GYM_LETTERS = ['.###.  #...#  #...#', '#...#  #...#  ##.##', '#....  .#.#.  #.#.#', '#.###  ..#..  #.#.#',
               '#...#  ..#..  #...#', '#...#  ..#..  #...#', '.###.  ..#..  #...#']   # 금색 "GYM" (5x7 글자 3개)


def lobby():
    """체육관 선택 건물 (14. 참고 사진 Gym 풍): 흰 벽·파란 창 띠·빨강 흰 줄무늬 기둥·겹친 황토색 지붕·노란 차양.
    넓은 입구 계단 위, 높은 정면 파사드 상단에 큰 "GYM" 간판과 몬스터볼 엠블럼.
    안: 장식 배틀 필드, 접수대 앞 안내원(우클릭 → 도전 목록), 뒤 벽에 배지 전시."""
    x1, x2, z1, z2 = LOBBY
    xm, B = (x1 + x2) // 2, LOBBY_Y            # B = 바닥 블록 높이
    top = B + 10
    L = ['# ── 체육관 선택 건물 ──', fill(x1 - 8, G, z1 - 20, x2 + 8, G, z1 - 1, 'minecraft:polished_andesite'),
         fill(xm - 3, G, z1 - 20, xm + 3, G, z1 - 8, 'minecraft:smooth_stone'),
         fill(x1, G, z1, x2, B, z2, 'minecraft:stone_bricks'), fill(x1, B, z1, x2, B, z2, 'minecraft:white_concrete')]
    for z in range(z1, z2 + 1):                  # 바닥: 흰·회 체크무늬
        for x in range(x1 + (z % 2), x2 + 1, 2):
            L.append(sb(x, B, z, 'minecraft:light_gray_concrete'))
    # 넓은 입구 계단 (3칸)
    for k in range(3):
        zb = z1 - 7 + 2 * k
        L += [fill(x1 + 3, G + 1, zb, x2 - 3, G + 1 + k, zb + 1, 'minecraft:polished_andesite'),
              fill(x1 + 3, G + 1 + k, zb, x2 - 3, G + 1 + k, zb, 'minecraft:polished_andesite_stairs[facing=south]')]
    L += walls(x1, x2, z1, z2, B + 1, B + 1, 'minecraft:stone_bricks')
    L += walls(x1, x2, z1, z2, B + 2, top - 1, 'minecraft:white_concrete')
    L += walls(x1, x2, z1, z2, top, top, 'minecraft:light_gray_concrete')
    L += walls(x1, x2, z1, z2, B + 7, B + 7, 'minecraft:light_blue_concrete')                      # 파란 띠
    stripe = lambda x, z: [sb(x, y, z, 'minecraft:red_concrete' if y % 2 else 'minecraft:white_concrete') for y in range(B + 1, top + 1)]
    for x in range(x1, x2 + 1, 5):
        L += stripe(x, z1) + stripe(x, z2)
    for z in list(range(z1, z2 + 1, 5)) + [z2]:
        L += stripe(x1, z) + stripe(x2, z)
        if z + 3 < z2:
            L += [fill(x1, B + 3, z + 2, x1, B + 6, z + 3, 'minecraft:light_blue_stained_glass'), fill(x2, B + 3, z + 2, x2, B + 6, z + 3, 'minecraft:light_blue_stained_glass')]
    # 겹친 황토색 지붕: 넓은 층(처마) → 안쪽 층 → 줄무늬 꼭대기
    L += [fill(x1 - 2, top + 1, z1 - 2, x2 + 2, top + 1, z2 + 2, 'minecraft:smooth_sandstone'),
          fill(x1 - 1, top + 2, z1 - 1, x2 + 1, top + 2, z2 + 1, 'minecraft:cut_sandstone'),
          fill(x1 + 1, top + 3, z1 + 1, x2 - 1, top + 3, z2 - 1, 'minecraft:smooth_sandstone')]
    L += [fill(x1 + 3, top + 3, z, x2 - 3, top + 3, z, 'minecraft:sandstone') for z in range(z1 + 3, z2 - 2, 2)]
    # 높은 정면 파사드: 금 테두리 + 검은 판의 GYM 글자 + 위에 몬스터볼 엠블럼
    fy1, fy2 = top + 1, top + 22
    L += [fill(xm - 13, B + 1, z1 - 1, xm + 13, fy2, z1 - 1, 'minecraft:white_concrete'),
          fill(xm - 13, B + 7, z1 - 1, xm + 13, B + 7, z1 - 1, 'minecraft:light_blue_concrete'),
          fill(xm - 13, B + 1, z1 - 1, xm - 13, fy2, z1 - 1, 'minecraft:chiseled_quartz_block'),
          fill(xm + 13, B + 1, z1 - 1, xm + 13, fy2, z1 - 1, 'minecraft:chiseled_quartz_block'),
          fill(xm - 13, fy2 + 1, z1 - 1, xm + 13, fy2 + 1, z1 - 1, 'minecraft:gold_block'),
          fill(xm - 10, fy1, z1 - 2, xm + 10, fy1 + 8, z1 - 2, 'minecraft:gold_block'),
          fill(xm - 9, fy1 + 1, z1 - 2, xm + 9, fy1 + 7, z1 - 2, 'minecraft:polished_blackstone')]
    for r, row in enumerate(GYM_LETTERS):
        for c, ch in enumerate(row):
            if ch == '#':
                L.append(sb(xm + 9 - c, fy1 + 7 - r, z1 - 3, 'minecraft:gold_block'))   # 앞(북쪽)에서 보면 x가 오른쪽→왼쪽
    L += emblem_z(xm, z1 - 2, fy1 + 14, r=4)
    L += [label(xm + .5, B + 9.8, z1 - 4.6, '포켓몬 체육관', 'gold', 1.6, sub='POKéMON GYM · 안내원에게 도전 신청'),
          fill(xm - 3, B + 1, z1 - 1, xm + 3, B + 5, z1, 'minecraft:air'),
          fill(xm - 4, B + 1, z1 - 1, xm - 4, B + 6, z1 - 1, 'minecraft:polished_blackstone'),
          fill(xm + 4, B + 1, z1 - 1, xm + 4, B + 6, z1 - 1, 'minecraft:polished_blackstone'),
          fill(xm - 4, B + 6, z1 - 1, xm + 4, B + 6, z1 - 1, 'minecraft:gold_block'),
          # 노란 차양 + 흰 구름 장식 (참고 사진 Gym 입구)
          fill(xm - 6, B + 6, z1 - 4, xm + 6, B + 6, z1 - 2, 'minecraft:yellow_concrete'),
          fill(xm - 5, B + 7, z1 - 4, xm + 5, B + 7, z1 - 4, 'minecraft:white_concrete'),
          sb(xm - 3, B + 8, z1 - 4, 'minecraft:white_concrete'), sb(xm, B + 8, z1 - 4, 'minecraft:white_concrete'), sb(xm + 3, B + 8, z1 - 4, 'minecraft:white_concrete'),
          fill(xm - 6, B + 1, z1 - 4, xm - 6, B + 5, z1 - 4, 'minecraft:red_concrete'), fill(xm + 6, B + 1, z1 - 4, xm + 6, B + 5, z1 - 4, 'minecraft:red_concrete'),
          fill(xm - 6, B + 2, z1 - 4, xm - 6, B + 2, z1 - 4, 'minecraft:white_concrete'), fill(xm + 6, B + 2, z1 - 4, xm + 6, B + 2, z1 - 4, 'minecraft:white_concrete'),
          fill(xm - 6, B + 4, z1 - 4, xm - 6, B + 4, z1 - 4, 'minecraft:white_concrete'), fill(xm + 6, B + 4, z1 - 4, xm + 6, B + 4, z1 - 4, 'minecraft:white_concrete')]
    for sx in (xm - 8, xm + 8):                  # 체육관 석상
        L += [fill(sx - 1, B + 1, z1 - 4, sx + 1, B + 1, z1 - 2, 'minecraft:polished_andesite'),
              sb(sx, B + 2, z1 - 3, 'minecraft:chiseled_stone_bricks'), sb(sx, B + 3, z1 - 3, 'minecraft:andesite_wall'),
              sb(sx, B + 4, z1 - 3, 'minecraft:stone_bricks'), sb(sx, B + 5, z1 - 3, 'minecraft:stone_brick_stairs[facing=north]'),
              sb(sx, B + 2, z1 - 4, 'minecraft:gold_block')]
    for x in (xm - 14, xm + 14):
        for z in (z1 - 18, z1 - 10):
            L += stone_lantern(x, z)
    # 안: 장식 배틀 필드
    fx1, fx2, fz1, fz2 = xm - 7, xm + 7, -6, 8
    L += [fill(fx1, B, fz1, fx2, B, fz2, 'minecraft:smooth_sandstone')]
    L += walls(fx1, fx2, fz1, fz2, B, B, 'minecraft:quartz_block')
    L += [fill(fx1, B, (fz1 + fz2) // 2, fx2, B, (fz1 + fz2) // 2, 'minecraft:quartz_block')]
    L += [sb(xm + dx, B, (fz1 + fz2) // 2 + dz, 'minecraft:quartz_block') for dx, dz in ring(2)]
    L += [fill(xm - 5, B + 1, 14, xm + 5, B + 1, 14, 'minecraft:quartz_block'), fill(xm - 5, B + 2, 14, xm + 5, B + 2, 14, 'minecraft:smooth_quartz_slab')]
    for i, color in enumerate(BADGE_BLOCK):     # 뒤 벽: 배지 전시
        x = xm + 9 - 3 * i
        L += [fill(x, B + 6, z2, x + 1, B + 7, z2, f'minecraft:{color}_concrete'), sb(x, B + 5, z2 - 1, 'minecraft:quartz_slab[type=top]'),
              sb(x + 1, B + 5, z2 - 1, 'minecraft:quartz_slab[type=top]'),
              f'summon minecraft:item_display {x + 1.0} {B + 7.0} {z2 - 0.06} {{Tags:["poke.deco"],item:{{id:"minecraft:gold_nugget",count:1,'
              f'components:{{"minecraft:custom_model_data":{1001 + i}}}}},transformation:{{scale:[1.4f,1.4f,1.4f],translation:[0f,0f,0f],'
              f'left_rotation:[0f,1f,0f,0f],right_rotation:[0f,0f,0f,1f]}}}}']
    L.append(label(xm + .5, B + 8.4, z2 - .6, '배지 8개를 모으면 사천왕에 도전!', 'gold', 1.0, sub='체육관을 이기면 이 배지를 받아요'))
    for z in range(-8, 12, 4):
        L += [sb(x1 + 1, B + 1, z, 'minecraft:spruce_stairs[facing=west]'), sb(x2 - 1, B + 1, z, 'minecraft:spruce_stairs[facing=east]')]
    for z in (-10, 0, 10):
        L += [sb(x1 + 1, B + 6, z, 'minecraft:red_wall_banner[facing=east]'), sb(x2 - 1, B + 6, z, 'minecraft:red_wall_banner[facing=west]')]
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    L += glow(x1, x2, z1, z2, B + 4)
    return L


def arena(n):
    """n번 경기장 (닫힌 방): 팔각형 배틀 필드 + 가운데 몬스터볼, 타입 색 줄무늬 천장 조명, 북쪽 관장 자리, 양옆 관중석."""
    g = gym_geom(n)
    x1, x2, z1, z2 = g['box']
    xm, top = (x1 + x2) // 2, G + 12
    name, field, wall, base, ceil, light, seat, (c1, c2) = next(t for t in TYPES if t[0] == GYM_TYPES[n - 1])
    m = lambda b: 'minecraft:' + b
    L = [f'# ── {n}번 경기장 ({name}) ──', fill(x1, G - 1, z1, x2, G - 1, z2, m('bedrock')),
         fill(x1, G, z1, x2, G, z2, m(wall)), fill(x1 + 1, G, z1 + 1, x2 - 1, G, z2 - 1, m('polished_andesite'))]
    L += walls(x1, x2, z1, z2, G + 1, G + 2, m(base))
    L += walls(x1, x2, z1, z2, G + 3, top, m(wall))
    for x in range(x1, x2 + 1, 5):
        L += [fill(x, G + 1, z1, x, top, z1, m('quartz_pillar')), fill(x, G + 1, z2, x, top, z2, m('quartz_pillar'))]
    for z in range(z1, z2 + 1, 6):
        L += [fill(x1, G + 1, z, x1, top, z, m('quartz_pillar')), fill(x2, G + 1, z, x2, top, z, m('quartz_pillar'))]
    # 천장: 타입 색 + 줄무늬 조명
    L.append(fill(x1, top + 1, z1, x2, top + 1, z2, m(ceil)))
    for z in range(z1 + 1, z2, 2):
        L.append(fill(x1 + 1, top + 1, z, x2 - 1, top + 1, z, m(light)))
    for z in range(z1 + 3, z2 - 2, 6):                                    # 벽 등불
        L += [sb(x1 + 1, G + 6, z, m('lantern')), sb(x2 - 1, G + 6, z, m('lantern'))]
    # 배틀 필드 (참고 사진 풍): 타입 콘셉트 색 바닥, 모서리를 자른 팔각형, 흰 테두리·가로선, 가운데 큰 몬스터볼, 테두리 안쪽 포인트 색 점
    fx1, fx2, fz1, fz2 = xm - 8, xm + 8, -12, 12
    L += [fill(fx1, G, fz1, fx2, G, fz2, m(field))]
    L += walls(fx1, fx2, fz1, fz2, G, G, m('quartz_block'))
    for dz in (-6, 6):                                                    # 가로선 (진영 구분)
        L.append(fill(fx1, G, dz, fx2, G, dz, m('quartz_block')))
    for cx, cz in ((fx1, fz1), (fx2, fz1), (fx1, fz2), (fx2, fz2)):      # 모서리 자르기 → 팔각형
        sx, sz = (1 if cx == fx1 else -1), (1 if cz == fz1 else -1)
        L += [sb(cx, G, cz, m('polished_andesite')), sb(cx + sx, G, cz, m('polished_andesite')), sb(cx, G, cz + sz, m('polished_andesite')),
              sb(cx + sx, G, cz + sz, m('quartz_block'))]
    for dx in (-5, -1, 1, 5):                                             # 포인트 색 점 (양 끝줄)
        L += [sb(xm + dx, G, fz1 + 2, m(c1)), sb(xm + dx, G, fz2 - 2, m(c1))]
    for dz in (-9, -3, 3, 9):                                             # 포인트 색 점 (양옆)
        L += [sb(fx1 + 2, G, dz, m(c2)), sb(fx2 - 2, G, dz, m(c2))]
    R = 5.6                                                               # 몬스터볼: 왼쪽 흰색·오른쪽 빨강, 검은 테두리·가운데 줄·단추
    for dx in range(-6, 7):
        for dz in range(-6, 7):
            d = (dx * dx + dz * dz) ** .5
            if d > R + .5:
                continue
            b = ('black_concrete' if d > R - .5 or (abs(dx) == 0 and d > 2.4) or 1.5 < d <= 2.4
                 else 'white_concrete' if d <= 1.5 or dx < 0 else 'red_concrete')
            L.append(sb(xm + dx, G, dz, m(b)))
    # 관중석 (양옆 3단, 계단 블록 의자는 필드를 바라봄)
    stairs = seat[:-7] + '_stairs' if seat.endswith('_planks') else {'mud_bricks': 'mud_brick_stairs'}.get(seat, seat + '_stairs')
    for k in range(3):
        for front, back, face in ((x1 + 5 - 2 * k, max(x1 + 1, x1 + 4 - 2 * k), 'west'), (x2 - 5 + 2 * k, min(x2 - 1, x2 - 4 + 2 * k), 'east')):
            if k:
                L.append(fill(min(front, back), G + 1, -14, max(front, back), G + k, 14, m(seat)))
            L += [fill(back, G + 1 + k, -14, back, G + 1 + k, 14, m(seat)) if back != front else 'say',
                  fill(front, G + 1 + k, -14, front, G + 1 + k, 14, m(f'{stairs}[facing={face}]'))]
    L = [c for c in L if c != 'say']
    # 관장 자리 (북쪽) + 도전자 자리·나가는 발판 (남쪽)
    lx, lz, _ = g['leader']
    px, pz, w, d = g['exit']
    L += [fill(int(lx) - 3, G, int(lz) - 1, int(lx) + 3, G, int(lz) + 2, m('quartz_block')),
          fill(int(lx) - 3, G + 1, int(lz) + 2, int(lx) + 3, G + 1, int(lz) + 2, m(f'{c1}')),
          fill(px, G, pz, px + w - 1, G, pz + d - 1, m('orange_stained_glass')),
          label(px + 1.5, G + 2.5, pz + .5, '◀ 나가기', 'gold', 1.0),
          label(xm + .5, G + 8, z2 - 1.5, f'{n}번 체육관 · {name} 타입', 'gold', 1.6)]
    L += glow(x1, x2, z1, z2, G + 5) + glow(x1, x2, z1, z2, G + 10, 6)
    return L


def e4_hall():
    """사천왕 본부 (닫힌 방 4개, 서로 막힘) + 명예의 전당. 순간이동으로만 드나듦."""
    g = e4_geom()
    x1, x2, z1, z2 = g['box']
    top = G + 9
    L = ['# ── 사천왕 본부 ──', fill(x1, G - 1, z1, x2, G - 1, z2, 'minecraft:bedrock'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite')]
    L += walls(x1, x2, z1, z2, G + 1, top, 'minecraft:quartz_bricks')
    for z in range(z1, z2 + 1, 5):
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:quartz_pillar'), fill(x2, G + 1, z, x2, top, z, 'minecraft:quartz_pillar')]
    for k, (a, b) in enumerate(g['rooms']):
        floor = 'minecraft:' + (E4_THEME[k] if k < 4 else 'gold_block')
        L += [fill(x1 + 1, G, a, x2 - 1, G, b, floor), fill(x1 + 1, top, a, x2 - 1, top, b, 'minecraft:quartz_block')]
        if k < 4:
            L.append(fill(x1 + 1, G + 1, b + 1, x2 - 1, top, b + 1, 'minecraft:quartz_bricks'))   # 방 사이 벽
        for x in range(x1 + 3, x2 - 1, 3):
            L += [sb(x, top, a + 2, 'minecraft:sea_lantern'), sb(x, top, b - 2, 'minecraft:sea_lantern')]
        if k < 4:
            L.append(label(x2 - 6.5, G + 4.2, (a + b) / 2 + .5, f'사천왕 {k + 1}번째 방', 'light_purple', 1.2, sub='역대 최강 챔피언'))
    fa, fb = g['rooms'][4]
    L += [fill(x2 - 4, G + 1, fa + 2, x2 - 2, G + 3, fb - 2, 'minecraft:gold_block'),
          label(x2 - 6.5, G + 4, (fa + fb) / 2 + .5, '명예의 전당', 'gold', 2.0, sub='사천왕을 모두 이긴 트레이너')]
    px, pz, w, d = g['exit']
    L += [fill(px, G, pz, px + w - 1, G, pz + d - 1, 'minecraft:orange_stained_glass'),
          label(px + .5, G + 2.5, pz + 1.5, '◀ 나가기', 'gold', 1.0),
          fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:purple_terracotta')]
    L += glow(x1, x2, z1, z2, G + 4)
    return L


def islands():
    """판타지 지형을 두를 섬들: (이름, 걸어 다닐 칸, 평평하게 둘 칸, 흙길 방향, 씨앗)."""
    return [terrain.Island('체육관', GYM_PLAY, G, 33, keep=[(1972, 2028, -40, 22)])]


def town():
    L = ['# 자동 생성: tools/build_world.py (직접 수정하지 말고 생성기를 고치세요). 지형(build/terrain)을 먼저 짓고 실행됨',
         'kill @e[type=minecraft:text_display,tag=poke.deco]', 'kill @e[type=minecraft:item_display,tag=poke.deco]',
         'kill @e[type=minecraft:item]']
    L += lobby() + island_walls(GYM_PLAY, '체육관')
    for n in range(1, 9):
        L += arena(n)
    L += e4_hall()
    return L


def spawn_npcs():
    L = ['# 자동 생성: tools/build_world.py. 기존 NPC 제거 후 다시 소환 (청크는 build/start에서 불러옴)',
         # 3. @e는 모든 차원을 고르므로 튜토리얼 방·마을 것만 지움 (예전엔 광장(야생) NPC까지 지웠음)
         'execute as @e[type=cobblemon:npc,tag=poke.npc] at @s unless dimension poke:wild run npcdelete @s',
         'execute as @e[type=cobblemon:npc,tag=poke.tutor] at @s unless dimension poke:wild run npcdelete @s',
         '# 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게',
         'execute in poke:hub run function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}',
         '# 간호사(회복), 점원(우클릭 → 상점), 체육관 안내원(우클릭 → 도전 목록; 모드가 태그로 처리)']
    for kind, dim, x, y, z, tag, yaw in NPCS:
        L.append(f'execute in {dim} run function poke:mod/spawn_npc {{id:"{kind}", x:{x}, y:{y}, z:{z}, tag:"{tag}", yaw:{yaw}}}')
    return L


def chunks(box, pad=0):
    x1, x2, z1, z2 = box
    return f'{x1 - pad} {z1 - pad} {x2 + pad} {z2 + pad}'


ARENA_REGION = (ARENA_X - 10, E4[1] + 10, E4[2] - 4, 22)


def build_start():
    L = ['# 자동 생성: tools/build_world.py', 'execute in poke:hub run forceload add -16 -16 16 16']
    for I in islands():
        L.append(f'execute in poke:town run forceload add {chunks(I.outer)}')
    L.append(f'execute in poke:town run forceload add {chunks(ARENA_REGION)}')
    for _, box in OLD_ISLANDS:
        L.append(f'execute in poke:town run forceload add {chunks(box)}')
    L += ['# 청크가 다 불러와질 때까지 3초 기다렸다가 짓기', 'schedule function poke:build/run 60t']
    return L


def clear_box(x1, x2, z1, z2, y1, y2):
    """예전 건물 지우기: 16x16 기둥씩 (fill 한 번 32768칸)."""
    out = []
    for x in range(x1, x2 + 1, 16):
        for z in range(z1, z2 + 1, 16):
            for y in range(y1, y2 + 1, 128):
                out.append(fill(x, y, z, min(x + 15, x2), min(y + 127, y2), min(z + 15, z2), 'minecraft:air'))
    return out


def terrain_parts():
    """지형 명령을 여러 틱에 나눠 실행할 조각들 (한 조각 최대 3000개: 한 틱이 1초를 넘지 않게)."""
    cmds = []
    for I in islands():
        x1, x2, z1, z2 = I.outer
        cmds += [f'# ── {I.name} 섬 지형 ──'] + clear_box(x1, x2, z1, z2, G - 4, G + 64)
        I.plan('nsew')
        cmds += I.biomes() + I.commands()
    a1, a2, c1, c2 = ARENA_REGION
    cmds += ['# ── 경기장 자리 비우기 ──'] + clear_box(a1, a2, c1, c2, G - 2, G + 16)
    for name, (x1, x2, z1, z2) in OLD_ISLANDS:                      # 15. 없앤 회의장·상점가 섬 지우기
        cmds += [f'# ── 예전 {name} 섬 지우기 ──'] + clear_box(x1, x2, z1, z2, G - 4, G + 64)
    return [cmds[i:i + 3000] for i in range(0, len(cmds), 3000)]


def bounds(farm_box):
    """15. 범위 검사: 섬·경기장·농장 밖이나 바닥 아래로 가면 되돌림 (관리자 크리에이티브·관전 제외)."""
    def inside(box):
        x1, x2, z1, z2 = box
        return f'unless entity @s[x={x1},y={G - 3},z={z1},dx={x2 - x1},dy={400},dz={z2 - z1}]'
    who = 'execute as @a[gamemode=!creative,gamemode=!spectator] at @s'
    town_boxes = ' '.join(inside(b) for b in [GYM_PLAY] + arenas())
    fx1, fz1, fx2, fz2 = farm_box
    return ['# 자동 생성: tools/build_world.py. 마을·농장·튜토리얼 방 밖으로 나가거나 떨어지면 되돌림',
            f'{who} if dimension poke:town {town_boxes} run function poke:home',
            f'{who} if dimension poke:farm {inside((fx1, fx2, fz1, fz2))} run function poke:util/tp with storage poke:config farm',
            f'{who} if dimension poke:hub if entity @s[y=-100,dy=155] run function poke:util/tp with storage poke:config tutorial']


LAB = (-8, 8, -11, 7)                  # 튜토리얼: 오박사 연구소 (poke:hub, 바닥 y=64). 스폰 (0,65,3) → 3칸 앞 (0,65,0)에 오박사


def lab():
    """튜토리얼 방 = 오박사 연구소. 원작 연구소처럼 흰 벽(석영)·밝은 회색 타일 바닥·흰 천장 조명, 책장 줄, 연구 기계, 몬스터볼 3개 놓인 탁자.
    밖은 울타리 친 잔디 마당(창밖이 허공이 아니게). 출입문 없음: 튜토리얼을 끝내면 바로 광장으로 옮겨 줌."""
    x1, x2, z1, z2 = LAB
    F, top = 64, 72
    L = ['# 자동 생성: tools/build_world.py. 튜토리얼 방 = 오박사 연구소',
         'kill @e[type=minecraft:text_display,tag=poke.lab]',
         fill(-16, 63, -16, 16, 90, 16, 'minecraft:air'),
         fill(-16, 62, -16, 16, 62, 16, 'minecraft:dirt'), fill(-16, 63, -16, 16, 63, 16, 'minecraft:dirt'),
         fill(-16, 64, -16, 16, 64, 16, 'minecraft:grass_block'),
         *walls(-16, 16, -16, 16, 65, 65, 'minecraft:oak_fence'),
         fill(x1, F, z1, x2, F, z2, 'minecraft:smooth_quartz')]
    L += [fill(x, F, z1 + 1, x, F, z2 - 1, 'minecraft:light_gray_concrete') for x in range(x1 + 1, x2, 4)]      # 타일 줄눈
    L += [fill(x1 + 1, F, z, x2 - 1, F, z, 'minecraft:light_gray_concrete') for z in range(z1 + 1, z2, 4)]
    for x, z, b in ((-12, -12, 'oak'), (12, -12, 'birch'), (-12, 12, 'oak'), (12, 12, 'birch')):   # 마당 나무
        L += [fill(x, 65, z, x, 69, z, f'minecraft:{b}_log'), fill(x - 2, 68, z - 2, x + 2, 69, z + 2, f'minecraft:{b}_leaves[persistent=true]', 'keep'),
              fill(x - 1, 70, z - 1, x + 1, 71, z + 1, f'minecraft:{b}_leaves[persistent=true]', 'keep')]
    for x, z in ((-4, 11), (4, 11), (-11, 0), (11, 0), (-6, -14), (6, -14)):
        L += [sb(x, 65, z, 'minecraft:poppy'), sb(x + 1, 65, z, 'minecraft:dandelion'), sb(x - 1, 65, z, 'minecraft:cornflower')]
    L += walls(x1, x2, z1, z2, F + 1, top, 'minecraft:smooth_quartz')
    for x in range(x1, x2 + 1, 4):                                                     # 흰 석영 기둥
        L += [fill(x, F + 1, z, x, top, z, 'minecraft:quartz_pillar') for z in (z1, z2)]
    for z in range(z1, z2 + 1, 4):
        L += [fill(x, F + 1, z, x, top, z, 'minecraft:quartz_pillar') for x in (x1, x2)]
    L += walls(x1, x2, z1, z2, F + 1, F + 1, 'minecraft:light_gray_concrete')         # 벽 아래 띠
    L += big_windows(x1, x2, z1, z2, F + 2, F + 4)
    L += [fill(x1 + 1, top, z1 + 1, x2 - 1, top, z2 - 1, 'minecraft:smooth_quartz')]    # 흰 천장 + 천장 조명
    L += [sb(x, top, z, 'minecraft:sea_lantern') for x in range(x1 + 2, x2 - 1, 4) for z in range(z1 + 2, z2 - 1, 4)]
    L += [fill(-1, F + 1, z2, 1, F + 4, z2, 'minecraft:smooth_quartz'),   # 남쪽 벽 (예전 철문 자리도 막음)
          label(0.5, F + 4.4, z2 + 0.6, '오박사 연구소', 'gold', 1.2, tag='poke.lab')]
    roof, _ = hip_roof(x1, x2, z1, z2, top + 1, 'minecraft:polished_andesite', 'minecraft:polished_andesite_stairs')
    L += roof
    # 안: 붉은 카펫(입구 → 오박사), 북쪽 벽 책장 + 간판, 가운데 책장 두 줄, 양옆 연구 기계, 몬스터볼 탁자
    L += [fill(0, F + 1, 1, 0, F + 1, z2 - 1, 'minecraft:red_carpet'),
          fill(x1 + 1, F + 1, z1 + 1, x2 - 1, F + 4, z1 + 1, 'minecraft:bookshelf'),
          fill(-1, F + 2, z1 + 1, 1, F + 3, z1 + 1, 'minecraft:white_concrete'),        # 연구 칠판
          label(0.5, F + 5.2, z1 + 2.0, '오박사 포켓몬 연구소', 'gold', 1.0, tag='poke.lab', sub='POKéMON LAB'),
          fill(x1 + 1, F + 1, -6, -3, F + 2, -6, 'minecraft:bookshelf'), fill(3, F + 1, -6, x2 - 1, F + 2, -6, 'minecraft:bookshelf'),
          fill(-1, F + 1, -2, 1, F + 1, -2, 'minecraft:stripped_dark_oak_wood')]          # 몬스터볼 탁자 (볼은 모드 파일)
    for z in (-4, -3, -2):                                                             # 동쪽: 컴퓨터 (콘솔 + 화면)
        L += [sb(x2 - 1, F + 1, z, 'minecraft:polished_deepslate'), sb(x2 - 1, F + 2, z, 'minecraft:daylight_detector'),
              sb(x2 - 1, F + 3, z, 'minecraft:verdant_froglight' if z == -3 else 'minecraft:black_stained_glass')]
    for z in (-4, -2):                                                                 # 서쪽: 분석 기계
        L += [sb(x1 + 1, F + 1, z, 'minecraft:iron_block'), sb(x1 + 1, F + 2, z, 'minecraft:observer[facing=up]'),
              sb(x1 + 1, F + 3, z, 'minecraft:lightning_rod')]
    L += [sb(x1 + 2, F + 1, 2, 'minecraft:lectern[facing=east]'), sb(x2 - 2, F + 1, 2, 'minecraft:cartography_table'),
          sb(x2 - 2, F + 2, 2, 'minecraft:brewing_stand'),
          sb(x1 + 1, F + 1, z2 - 1, 'minecraft:potted_fern'), sb(x2 - 1, F + 1, z2 - 1, 'minecraft:potted_azalea_bush'),
          sb(x1 + 1, F + 1, -8, 'minecraft:potted_bamboo'), sb(x2 - 1, F + 1, -8, 'minecraft:potted_cactus')]
    L += glow(x1, x2, z1, z2, F + 5)
    return L


def lab_mod():
    """연구소의 Cobblemon 물건: 탁자 위 몬스터볼 3개, 회복 장치 (모드 전용, poke:hub)."""
    L = ['execute in poke:hub run kill @e[type=minecraft:item_display,tag=poke.lab]',
         'execute in poke:hub run setblock -6 65 -8 cobblemon:healing_machine[facing=east,natural=false]']
    for x in (-1, 0, 1):
        L.append(f'execute in poke:hub run summon minecraft:item_display {x + 0.5} 66.2 -1.5 {{Tags:["poke.lab"],'
                 f'item:{{id:"cobblemon:poke_ball",count:1}},transformation:{{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],'
                 f'left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}}}')
    return L


def config_warps():
    return [f'data modify storage poke:config {k} set value {{dim:"poke:town", x:{x}, y:{y}, z:{z}, yaw:{yaw}}}'
            for k, (x, y, z, yaw) in WARPS.items()]


if __name__ == '__main__':
    f, box = farm()
    import plaza as P
    pl, pl_npcs = P.plaza()
    old_npcs = [f'execute in poke:town as @e[type=cobblemon:npc,tag=poke.npc,x={x1},y={G - 10},z={z1},dx={x2 - x1},dy=80,dz={z2 - z1}] run npcdelete @s'
                for _, (x1, x2, z1, z2) in OLD_ISLANDS]           # 없앤 섬에 있던 NPC
    out = {'mod/build_town.mcfunction': ['# 자동 생성: tools/build_world.py. Cobblemon 물건', 'execute as @e[type=cobblemon:pokemon] at @s if dimension poke:town run kill @s'] + old_npcs + lab_mod(), 'build/tutorial.mcfunction': lab(), 'mod/spawn_npcs.mcfunction': spawn_npcs(),
           'build/start.mcfunction': build_start(), 'bounds.mcfunction': bounds(box), 'build/farm.mcfunction': f}
    tdir = FN / 'build/terrain'
    tdir.mkdir(parents=True, exist_ok=True)
    for old in tdir.glob('*.mcfunction'):
        old.unlink()
    # 지형 조각들 뒤에 마을 건물(6천여 줄)도 2,000줄씩 이어서 지음 → 한 틱이 길어지지 않게 (예전엔 build/town 한 번에)
    t = town()
    parts = terrain_parts() + [t[i:i + 2000] for i in range(0, len(t), 2000)]
    old_town = FN / 'build/town.mcfunction'
    if old_town.exists():
        old_town.unlink()
    for k, part in enumerate(parts):
        out[f'build/terrain/{k}.mcfunction'] = ['# 자동 생성: tools/build_world.py (지형 → 마을 건물 순서)'] + part
        nxt = f'poke:build/terrain/run_{k + 1}' if k + 1 < len(parts) else 'poke:build/finish'
        out[f'build/terrain/run_{k}.mcfunction'] = [f'execute in poke:town run function poke:build/terrain/{k}', f'schedule function {nxt} 2t']
    # 짓는 도중 서버가 꺼지면 남은 예약이 저장됨 → 새로 짓기 전에 지워 두 번 짓지 않게
    out['build/start.mcfunction'][1:1] = ['schedule clear poke:build/run', 'schedule clear poke:build/finish'] + [
        f'schedule clear poke:build/terrain/run_{k}' for k in range(len(parts))]
    out['build/run.mcfunction'] = ['# 자동 생성: tools/build_world.py. 지형을 여러 틱에 나눠 지은 뒤 build/finish',
                                   'function poke:build/terrain/run_0']
    # 건물 번호는 load.mcfunction 한 곳에서만 정함 (둘이 다르면 서버를 켤 때마다 다시 지음)
    BUILD = int(re.search(r'\{build:(\d+)\}', (FN / 'load.mcfunction').read_text()).group(1))
    out['build/finish.mcfunction'] = [
        '# 자동 생성: tools/build_world.py',
        'execute in poke:hub run function poke:build/tutorial',
        'execute in poke:town run function poke:mod/build_town', 'execute in poke:hub run function poke:mod/spawn_npcs',
        'execute in poke:town run forceload remove all', f'data modify storage poke:state build set value {BUILD}',
        '# 관장·사천왕은 플레이어가 접속하면 소환 (RCT 명령이 플레이어를 요구)', 'data modify storage poke:state leaders set value 0',
        'say [pokeserver] 튜토리얼 방·체육관과 지형을 지었습니다.']
    # 15. 광장 마을 (야생): 모드가 자리·지형을 정한 뒤 그 자리에서 build/plaza/start 실행 → 마커 기준 상대 좌표로 2,000줄씩
    pdir = FN / 'build/plaza'
    pdir.mkdir(parents=True, exist_ok=True)
    for old in pdir.glob('*.mcfunction'):
        old.unlink()
    pparts = [pl[i:i + 2000] for i in range(0, len(pl), 2000)]
    out['build/plaza/start.mcfunction'] = [
        '# 자동 생성: tools/build_world.py. 모드(Plaza.java)가 광장 가운데에서 실행',
        *[f'schedule clear poke:build/plaza/run_{k}' for k in range(len(pparts))],
        f'forceload add ~-{P.R + 8} ~-{P.R + 8} ~{P.R + 8} ~{P.R + 8}',
        'kill @e[type=minecraft:marker,tag=poke.plaza]', 'summon minecraft:marker ~ ~ ~ {Tags:["poke.plaza"]}',
        'schedule function poke:build/plaza/run_0 60t']
    for k, part in enumerate(pparts):
        out[f'build/plaza/{k}.mcfunction'] = ['# 자동 생성: tools/plaza.py (광장 기준 상대 좌표)'] + [P.relative(c) for c in part]
        nxt = f'poke:build/plaza/run_{k + 1}' if k + 1 < len(pparts) else 'poke:build/plaza/finish'
        out[f'build/plaza/run_{k}.mcfunction'] = [f'execute in poke:wild at @e[type=minecraft:marker,tag=poke.plaza,limit=1] run function poke:build/plaza/{k}',
                                                  f'schedule function {nxt} 2t']
    out['build/plaza/finish.mcfunction'] = [
        '# 자동 생성: tools/build_world.py',
        'execute in poke:wild at @e[type=minecraft:marker,tag=poke.plaza,limit=1] run function poke:mod/plaza',
        # 청크를 한 번에 풀면 조명 계산이 몰려 한 틱이 길어짐 → 16칸 줄씩 1초 간격으로 풂
        *[f'schedule function poke:build/plaza/unload_{k} {20 * (i + 1)}t' for i, k in enumerate([0, 1, 2, 3, 4, 6, 7, 8, 9, 5])],   # 마커가 있는 줄(5)은 마지막
        'say [pokeserver] 광장 마을을 지었습니다.']
    for k in range(10):
        x = -80 + 16 * k
        out[f'build/plaza/unload_{k}.mcfunction'] = [
            f'execute in poke:wild at @e[type=minecraft:marker,tag=poke.plaza,limit=1] run forceload remove ~{x} ~-80 ~{x + 15} ~80']
    out['mod/plaza.mcfunction'] = ['# 자동 생성: tools/build_world.py. 광장의 Cobblemon 물건·NPC (마커 위치에서 실행)',
                                   'execute as @e[type=cobblemon:npc,tag=poke.npc,distance=..90] run npcdelete @s',
                                   *[P.relative(c) for c in P.plaza_mod()],
                                   *[f'function poke:mod/spawn_npc {{id:"{k}", x:"~{x}", y:"~{y}", z:"~{z}", tag:"{t}", yaw:{yaw}}}' for k, x, y, z, t, yaw in pl_npcs]]
    for path, lines in out.items():
        (FN / path).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # 워프 위치는 config.mcfunction의 해당 줄만 바꿔 씀 (나머지는 손으로 고치는 설정)
    cfg = FN / 'config.mcfunction'
    keep = [l for l in cfg.read_text(encoding='utf-8').splitlines()
            if not any(l.startswith(f'data modify storage poke:config {k} ') for k in WARPS)]
    i = next(i for i, l in enumerate(keep) if 'poke:config tutorial' in l) + 2
    cfg.write_text('\n'.join(keep[:i] + config_warps() + keep[i:]) + '\n', encoding='utf-8')
    # 모드(땅 문서·보호)가 읽는 땅 목록
    farms = FN.parents[5] / 'config/pokeserver/farms.json'
    farms.write_text(json.dumps({'dimension': 'poke:farm', 'plots': [
        {'id': n, 'x1': x1, 'z1': z1, 'x2': x2, 'z2': z2} for n, x1, z1, x2, z2 in plots()]}, indent=2), encoding='utf-8')
    print({k: len(v) for k, v in out.items() if not k.startswith('build/terrain/run')}, 'farm box', box)


def refresh_pack():
    """생성한 파일이 바뀌면 모드팩 목록(index.toml)의 지문도 갱신해야 함. 안 하면 설치 프로그램이 "Hash invalid"로 멈춤."""
    import os
    import shutil
    import subprocess
    exe = shutil.which('packwiz') or os.path.expanduser('~/go/bin/packwiz')
    if os.path.exists(exe):
        subprocess.run([exe, 'refresh'], cwd=Path(__file__).resolve().parent.parent / 'pack', check=True, capture_output=True)
    else:
        print('경고: packwiz가 없어 pack/index.toml을 갱신하지 못함 → 올리기 전에 packwiz refresh 실행 필요')


if __name__ == '__main__':
    refresh_pack()
