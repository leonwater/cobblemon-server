"""마을(회의장·상점가·체육관·경기장)·농장을 짓는 마인크래프트 함수(.mcfunction) 생성기.

마을(poke:town)은 허공 차원에 떨어진 섬 여러 개: 회의장·상점가·체육관은 서로 1000칸씩 떨어져 워프로만 오감.
섬 둘레는 투명 벽(barrier) + 매 틱 범위 검사(벗어나면 되돌림)라 걸어서 나가거나 떨어질 수 없음.
체육관 경기장·사천왕 방은 문 없는 닫힌 방이라 도전할 때 순간이동으로만 들어감.
크기·위치를 바꾸려면 아래 숫자를 고치고 실행 → 데이터팩의 build 버전(load.mcfunction) +1.
사용: python3 tools/build_world.py
"""
import json
import math
from pathlib import Path

FN = Path(__file__).resolve().parent.parent / 'pack/world/datapacks/pokeserver/data/poke/function'

# ── 마을 (poke:town, 허공. 땅 윗면 y=-60, 서는 높이 y=-59) ──
G = -60
HALL_AREA = (-40, 40, -48, 30)       # 회의장 섬 x1,x2,z1,z2
HALL = (-15, 15, -10, 12)            # 회의장 본관 (문은 북쪽, 앞에 기둥 현관)
SHOP_AREA = (960, 1040, -32, 32)     # 상점가 섬
MART = (970, 986, -8, 8)             # 프렌들리 숍 (문은 동쪽, 광장 쪽)
CENTER = (1012, 1028, -10, 10)       # 포켓몬센터 (문은 서쪽, 광장 쪽)
GYM_AREA = (1960, 2040, -36, 36)     # 체육관 섬
LOBBY = (1985, 2015, -14, 18)        # 포켓몬 체육관 건물 (문은 북쪽). 안내원에게 도전 신청
ARENA_X = 3000                       # n번 경기장: x ARENA_X+40(n-1) ~ +20, z -12~12 (닫힌 방)
E4 = (3400, 3440, -46, 12)           # 사천왕 본부 (닫힌 방 4개 + 명예의 전당)
# 워프 도착 (x, z, yaw): 0 남, 180 북
WARPS = {'hall': (0.5, -7.5, 0), 'street': (1000.5, 28.5, 180), 'gym': (2000.5, -11.5, 0)}
NPCS = [  # (NPC 종류, 차원, x, z, 태그, yaw)
    ('poke:nurse', 'poke:town', CENTER[1] - 3, (CENTER[2] + CENTER[3]) // 2, 'poke.nurse', 90),
    ('poke:merchant', 'poke:town', MART[1] - 3, MART[2] + 2, 'poke.merchant', 0),
    ('poke:gym_guide', 'poke:town', 2000, 12, 'poke.gymguide', 180),
]
# 체육관 테마 바닥 (번호 순): 바위·물·전기·풀·독·에스퍼·불꽃·땅 / 사천왕: 강철·드래곤·고스트·비행
GYM_THEME = ['cobblestone', 'prismarine', 'yellow_concrete', 'moss_block', 'purple_concrete', 'magenta_concrete',
             'red_nether_bricks', 'coarse_dirt']
GYM_ROOF = ['gray_terracotta', 'blue_terracotta', 'yellow_terracotta', 'lime_terracotta', 'purple_terracotta',
            'magenta_terracotta', 'red_terracotta', 'brown_terracotta']
BADGE_BLOCK = ['gray', 'blue', 'orange', 'lime', 'pink', 'yellow', 'red', 'green']
E4_THEME = ['iron_block', 'purpur_block', 'blackstone', 'light_blue_concrete']


def gym_geom(n):
    """n번 경기장(1~8): 도전자 자리(남쪽)·나가는 발판·관장 자리(북쪽)."""
    x0 = ARENA_X + 40 * (n - 1)
    xm = x0 + 10
    return dict(box=(x0, x0 + 20, -12, 12), inside=(xm + .5, -6.5, 0), exit=(xm - 1, -11, 3, 1), leader=(xm + .5, 9.5, 180))


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
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
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


def island(area, name):
    """섬 바닥(잔디 + 흙 3 + 기반암) + 가장자리 연석·돌담 + 높이 제한까지 투명 벽. 바깥은 허공."""
    x1, x2, z1, z2 = area
    L = [f'# ── {name} 섬 ──', fill(x1, G - 4, z1, x2, G - 4, z2, 'minecraft:bedrock'),
         fill(x1, G - 3, z1, x2, G - 1, z2, 'minecraft:dirt'), fill(x1, G, z1, x2, G, z2, 'minecraft:grass_block')]
    L += walls(x1, x2, z1, z2, G, G, 'minecraft:polished_andesite')
    L += walls(x1 + 1, x2 - 1, z1 + 1, z2 - 1, G + 1, G + 1, 'minecraft:stone_brick_wall')
    L += walls(x1, x2, z1, z2, G + 1, 319, 'minecraft:barrier')
    return L


def hall():
    """회의장: 신고전주의 (원작 포켓몬 리그 회관 느낌) — 기둥 6개 현관, 삼각 박공 + 몬스터볼, 초록 구리 돔."""
    x1, x2, z1, z2 = HALL
    top = G + 9
    cz, R = 1, 8                                 # 원형 홀(돔) 중심 z, 반지름 (x=0)
    L = ['# ── 회의장 ──', fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite')]
    for dx, dz in circle(R - 1):                 # 원형 홀 바닥: 흰·회 동심원
        L.append(sb(dx, G, cz + dz, 'minecraft:' + ('smooth_quartz' if round(math.hypot(dx, dz)) % 2 == 0 else 'polished_diorite')))
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:polished_diorite')
    L += walls(x1, x2, z1, z2, G + 2, top, 'minecraft:quartz_bricks')
    for x in range(x1, x2 + 1, 5):               # 벽기둥 + 사이 긴 창
        L += [fill(x, G + 1, z1, x, top, z1, 'minecraft:quartz_pillar'), fill(x, G + 1, z2, x, top, z2, 'minecraft:quartz_pillar')]
        if x + 3 < x2:
            L += [fill(x + 2, G + 3, z2, x + 3, G + 6, z2, 'minecraft:glass_pane'), sb(x + 2, G + 7, z2, 'minecraft:chiseled_quartz_block'),
                  sb(x + 3, G + 7, z2, 'minecraft:chiseled_quartz_block')]
            if abs(x + 2.5) > 4:
                L += [fill(x + 2, G + 3, z1, x + 3, G + 6, z1, 'minecraft:glass_pane')]
    for z in list(range(z1, z2 + 1, 5)) + [z2]:
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:quartz_pillar'), fill(x2, G + 1, z, x2, top, z, 'minecraft:quartz_pillar')]
        if z + 3 < z2:
            L += [fill(x1, G + 3, z + 2, x1, G + 6, z + 3, 'minecraft:glass_pane'), fill(x2, G + 3, z + 2, x2, G + 6, z + 3, 'minecraft:glass_pane')]
    # 정문 + 문틀
    L += [fill(-2, G + 1, z1, -2, G + 5, z1, 'minecraft:chiseled_quartz_block'), fill(2, G + 1, z1, 2, G + 5, z1, 'minecraft:chiseled_quartz_block'),
          fill(-2, G + 5, z1, 2, G + 5, z1, 'minecraft:chiseled_quartz_block'), fill(-1, G + 1, z1, 1, G + 4, z1, 'minecraft:air')]
    # 처마 + 난간 + 평지붕(천장 조명)
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:smooth_quartz')]
    L += walls(x1 - 1, x2 + 1, z1 - 1, z2 + 1, top + 2, top + 2, 'minecraft:smooth_quartz_slab')
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            if math.hypot(x, z - cz) > R + 1:
                L.append(sb(x, top + 1, z, 'minecraft:sea_lantern'))
    # 돔: 원통 받침(창) + 반구(녹청 구리) + 꼭대기 탑
    L += [sb(dx, top + 1, cz + dz, 'minecraft:air') for dx, dz in circle(R - 1)]
    for dx, dz in ring(R):
        for y in range(top + 1, top + 4):
            glass = y == top + 2 and (dx + dz) % 3 == 0
            L.append(sb(dx, y, cz + dz, 'minecraft:' + ('light_blue_stained_glass' if glass else 'smooth_quartz')))
    base = top + 3
    for dx in range(-R, R + 1):
        for dz in range(-R, R + 1):
            for dy in range(1, R + 1):
                d = math.sqrt(dx * dx + dy * dy + dz * dz)
                if R - 0.85 < d <= R + 0.25:
                    L.append(sb(dx, base + dy, cz + dz, 'minecraft:waxed_oxidized_cut_copper'))
    L += [fill(0, base + R + 1, cz, 0, base + R + 2, cz, 'minecraft:quartz_pillar'), sb(0, base + R + 3, cz, 'minecraft:gold_block'),
          sb(0, base + R + 4, cz, 'minecraft:lantern')]
    # 돔 아래 샹들리에
    L += [fill(0, top - 1, cz, 0, base + R - 1, cz, 'minecraft:chain'), sb(0, top - 2, cz, 'minecraft:sea_lantern')]
    for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        L += [sb(dx, top - 1, cz + dz, 'minecraft:chain'), sb(dx, top - 2, cz + dz, 'minecraft:lantern[hanging=true]')]
    L.append(fill(-2, top, cz, 2, top, cz, 'minecraft:chain[axis=x]'))
    L.append(fill(0, top, cz - 2, 0, top, cz + 2, 'minecraft:chain[axis=z]'))
    # 돔을 받치는 안쪽 기둥 (통로 자리는 비움)
    for dx, dz in ((R - 1, 0), (-R + 1, 0), (0, R - 1), (6, 5), (-6, 5), (5, -5), (-5, -5)):
        L.append(fill(dx, G + 1, cz + dz, dx, top, cz + dz, 'minecraft:quartz_pillar'))
    # 현관: 기둥 6개 + 들보 + 삼각 박공(몬스터볼)
    pz1, pz2 = z1 - 7, z1 - 1
    L += [fill(-13, G, pz1 - 1, 13, G, pz2, 'minecraft:smooth_quartz'),
          fill(-13, G, pz1 - 2, 13, G, pz1 - 2, 'minecraft:polished_diorite')]
    for x in (-10, -6, -2, 2, 6, 10):
        L += [sb(x, G + 1, pz1 + 1, 'minecraft:chiseled_quartz_block'), fill(x, G + 2, pz1 + 1, x, top - 1, pz1 + 1, 'minecraft:quartz_pillar'),
              sb(x, top, pz1 + 1, 'minecraft:chiseled_quartz_block')]
    L += [fill(-12, top + 1, pz1, 12, top + 1, pz2, 'minecraft:smooth_quartz'),
          fill(-12, top + 1, pz1, 12, top + 1, pz1, 'minecraft:chiseled_quartz_block')]
    for i in range(7):
        y, xa, xb = top + 2 + i, -12 + 2 * i, 12 - 2 * i
        if xa == xb:
            L.append(fill(xa, y, pz1, xa, y, pz2, 'minecraft:smooth_quartz'))
            break
        L += [fill(xa, y, pz1, xb, y, pz2, 'minecraft:smooth_quartz'),
              fill(xa, y, pz1, xa, y, pz2, 'minecraft:smooth_quartz_stairs[facing=east]'),
              fill(xb, y, pz1, xb, y, pz2, 'minecraft:smooth_quartz_stairs[facing=west]')]
    L += emblem_z(0, pz1 - 1, top + 4, r=3)
    L.append(label(0.5, top - 0.2, pz1 - 0.7, '포켓몬 리그 회의장', 'gold', 1.4, sub='POKéMON LEAGUE HALL'))
    # 안: 붉은 카펫 → 원탁·의자, 남쪽 단상·깃발, 양옆 책장
    L.append(fill(-1, G + 1, z1 + 1, 1, G + 1, cz - 5, 'minecraft:red_carpet'))
    L += [sb(dx, G + 1, cz + dz, 'minecraft:dark_oak_slab[type=top]') for dx, dz in circle(2)]
    L.append(sb(0, G + 2, cz, 'minecraft:lantern'))
    for dx, dz in ((0, 4), (0, -4), (4, 0), (-4, 0), (3, 3), (-3, 3), (3, -3), (-3, -3)):
        face = ('south' if dz > 0 else 'north') if abs(dz) >= abs(dx) else ('east' if dx > 0 else 'west')
        L.append(sb(dx, G + 1, cz + dz, f'minecraft:dark_oak_stairs[facing={face}]'))
    L += [fill(-4, G + 1, z2 - 2, 4, G + 1, z2 - 1, 'minecraft:smooth_quartz'), sb(0, G + 2, z2 - 2, 'minecraft:lectern[facing=north]')]
    for x in (-7, -4, 4, 7):
        L.append(sb(x, G + 5, z2 - 1, 'minecraft:red_wall_banner[facing=north]'))
    for xx in (x1 + 1, x2 - 1):
        L += [fill(xx, G + 1, z1 + 2, xx, G + 2, z1 + 5, 'minecraft:bookshelf'), fill(xx, G + 1, z2 - 5, xx, G + 2, z2 - 2, 'minecraft:bookshelf')]
    # 앞 광장: 분수, 꽃밭(나무 없음), 가로등, 몬스터볼 석상
    L += [fill(-24, G, -46, 24, G, pz1 - 3, 'minecraft:polished_andesite'),
          fill(-2, G, -46, 2, G, pz1 - 3, 'minecraft:smooth_stone')]
    L += walls(-24, 24, -46, pz1 - 3, G, G, 'minecraft:stone_bricks')
    fz = -33
    L += [sb(dx, G + 1, fz + dz, 'minecraft:quartz_slab') for dx, dz in ring(4)]
    L += [sb(dx, G + 1, fz + dz, 'minecraft:water') for dx, dz in circle(3)]
    L += [fill(0, G + 1, fz, 0, G + 3, fz, 'minecraft:quartz_pillar'), sb(0, G + 4, fz, 'minecraft:sea_lantern')]
    flowers = ['poppy', 'dandelion', 'cornflower', 'allium', 'oxeye_daisy', 'azure_bluet', 'lily_of_the_valley', 'red_tulip', 'pink_tulip']
    for k, (x, z) in enumerate(((-16, -41), (16, -41), (-16, -26), (16, -26))):
        L.append(fill(x - 2, G, z - 2, x + 2, G, z + 2, 'minecraft:grass_block'))
        L += [sb(x + dx, G + 1, z + dz, f'minecraft:{flowers[(k * 3 + dx * 2 + dz) % len(flowers)]}') for dx in range(-2, 3) for dz in range(-2, 3)]
    for x in (-8, 8, -22, 22):
        for z in (-44, -22):
            L += lamp(x, z)
    for sx in (-5, 5):
        L += [fill(sx, G + 1, pz1 - 3, sx, G + 2, pz1 - 3, 'minecraft:chiseled_stone_bricks'), sb(sx, G + 3, pz1 - 3, 'minecraft:red_concrete'),
              sb(sx, G + 4, pz1 - 3, 'minecraft:white_concrete')]
    return L


def shop_area():
    """상점가 광장: 서쪽 프렌들리 숍, 동쪽 포켓몬센터, 남쪽 아치 (나무 없음)."""
    zx1, zx2 = MART[1] + 1, CENTER[0] - 1
    L = ['# ── 상점가 광장 ──', fill(zx1, G, -14, zx2, G, 30, 'minecraft:polished_andesite'),
         fill(MART[1] + 1, G, -2, CENTER[0] - 1, G, 2, 'minecraft:smooth_stone')]
    L += walls(zx1, zx2, -14, 30, G, G, 'minecraft:stone_bricks')
    L += [fill(994, G + 1, 26, 994, G + 5, 26, 'minecraft:stone_bricks'), fill(1006, G + 1, 26, 1006, G + 5, 26, 'minecraft:stone_bricks'),
          fill(994, G + 6, 26, 1006, G + 6, 26, 'minecraft:dark_oak_planks'), fill(994, G + 7, 26, 1006, G + 7, 26, 'minecraft:dark_oak_slab'),
          label(1000.5, G + 8, 26.5, '상점가', 'gold', 2.0, sub='포켓몬센터 · 프렌들리 숍')]
    L += [sb(dx + 1000, G + 1, 12 + dz, 'minecraft:quartz_slab') for dx, dz in ring(3)]
    L += [sb(dx + 1000, G + 1, 12 + dz, 'minecraft:water') for dx, dz in circle(2)]
    for x in (990, 1010):
        for z in (-10, 8, 20):
            L += lamp(x, z)
        L += [sb(x, G + 1, 14, f'minecraft:spruce_stairs[facing={"west" if x < 1000 else "east"}]'),
              sb(x, G + 1, 15, f'minecraft:spruce_stairs[facing={"west" if x < 1000 else "east"}]')]
    for i, z in enumerate(range(-12, 29, 3)):
        for x in (zx1 + 1, zx2 - 1) if abs(z) > 3 else ():   # 가게 문 앞 길은 비움
            L.append(sb(x, G, z, 'minecraft:grass_block'))
            L.append(sb(x, G + 1, z, f'minecraft:{["poppy", "dandelion", "cornflower", "allium"][(i + x) % 4]}'))
    return L


def lobby():
    """포켓몬 체육관 (원작풍): 회색 벽 + 빨강·하양 띠와 계단식 지붕, 정면 몬스터볼 간판, 입구 석상.
    안: 장식 배틀 필드, 접수대 앞 안내원(우클릭 → 도전 목록), 뒤 벽에 배지 8색."""
    x1, x2, z1, z2 = LOBBY
    xm, top = (x1 + x2) // 2, G + 10
    L = ['# ── 포켓몬 체육관 ──', fill(x1 - 6, G, z1 - 14, x2 + 6, G, z1 - 1, 'minecraft:polished_andesite'),
         fill(xm - 2, G, z1 - 14, xm + 2, G, z1 - 1, 'minecraft:smooth_stone')]
    for z in range(z1, z2 + 1):                  # 바닥: 흰·회 체크무늬
        for x in range(x1, x2 + 1, 2):
            L.append(fill(x + (z % 2), G, z, min(x + (z % 2), x2), G, z, 'minecraft:light_gray_concrete'))
    L.insert(1, fill(x1, G, z1, x2, G, z2, 'minecraft:white_concrete'))
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:polished_deepslate')
    L += walls(x1, x2, z1, z2, G + 2, top - 2, 'minecraft:light_gray_concrete')
    L += walls(x1, x2, z1, z2, top - 1, top - 1, 'minecraft:red_concrete')
    L += walls(x1, x2, z1, z2, top, top, 'minecraft:white_concrete')
    for x in range(x1, x2 + 1, 5):
        L += [fill(x, G + 1, z1, x, top, z1, 'minecraft:quartz_pillar'), fill(x, G + 1, z2, x, top, z2, 'minecraft:quartz_pillar')]
    for z in list(range(z1, z2 + 1, 5)) + [z2]:
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:quartz_pillar'), fill(x2, G + 1, z, x2, top, z, 'minecraft:quartz_pillar')]
        if z + 3 < z2:
            L += [fill(x1, G + 3, z + 2, x1, G + 6, z + 3, 'minecraft:light_blue_stained_glass_pane'),
                  fill(x2, G + 3, z + 2, x2, G + 6, z + 3, 'minecraft:light_blue_stained_glass_pane')]
    # 계단식 지붕 (빨강·하양)
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:white_concrete'),
          fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:red_concrete'),
          fill(x1 + 3, top + 2, z1 + 3, x2 - 3, top + 2, z2 - 3, 'minecraft:red_concrete'),
          fill(x1 + 6, top + 3, z1 + 6, x2 - 6, top + 3, z2 - 6, 'minecraft:white_concrete'),
          fill(x1 + 9, top + 4, z1 + 9, x2 - 9, top + 4, z2 - 9, 'minecraft:red_concrete')]
    # 정면: 간판 벽 + 몬스터볼 + 이름, 유리 정문, 차양, 석상
    L += [fill(xm - 7, top + 1, z1, xm + 7, top + 8, z1, 'minecraft:white_concrete'),
          fill(xm - 7, top + 9, z1, xm + 7, top + 9, z1, 'minecraft:red_concrete')]
    L += emblem_z(xm, z1 - 1, top + 4, r=3)
    L += [label(xm + .5, top + 10.2, z1 - .6, '포켓몬 체육관', 'gold', 2.2, sub='POKéMON GYM'),
          fill(xm - 2, G + 1, z1, xm - 2, G + 5, z1, 'minecraft:quartz_pillar'), fill(xm + 2, G + 1, z1, xm + 2, G + 5, z1, 'minecraft:quartz_pillar'),
          fill(xm - 2, G + 5, z1, xm + 2, G + 5, z1, 'minecraft:chiseled_quartz_block'), fill(xm - 1, G + 1, z1, xm + 1, G + 4, z1, 'minecraft:air'),
          fill(xm - 3, G + 6, z1 - 1, xm + 3, G + 6, z1 - 1, 'minecraft:red_concrete'),
          fill(xm - 1, G + 1, z1 - 1, xm + 1, G + 1, z1 - 1, 'minecraft:air')]
    for sx in (xm - 6, xm + 6):
        L += [fill(sx, G + 1, z1 - 4, sx, G + 2, z1 - 4, 'minecraft:chiseled_stone_bricks'), sb(sx, G + 3, z1 - 4, 'minecraft:red_concrete'),
              sb(sx, G + 4, z1 - 4, 'minecraft:white_concrete')]
    for x in (xm - 10, xm + 10):
        for z in (z1 - 12, z1 - 4):
            L += lamp(x, z)
    # 안: 장식 배틀 필드
    fx1, fx2, fz1, fz2 = xm - 7, xm + 7, -6, 8
    L += [fill(fx1, G, fz1, fx2, G, fz2, 'minecraft:smooth_sandstone')]
    L += walls(fx1, fx2, fz1, fz2, G, G, 'minecraft:quartz_block')
    L += [fill(fx1, G, (fz1 + fz2) // 2, fx2, G, (fz1 + fz2) // 2, 'minecraft:quartz_block')]
    L += [sb(xm + dx, G, (fz1 + fz2) // 2 + dz, 'minecraft:quartz_block') for dx, dz in ring(2)]
    # 접수대 + 안내 표시 (안내원은 NPCS)
    L += [fill(xm - 5, G + 1, 14, xm + 5, G + 1, 14, 'minecraft:quartz_block'), fill(xm - 5, G + 2, 14, xm + 5, G + 2, 14, 'minecraft:smooth_quartz_slab'),
          label(xm + .5, G + 4.2, 14.5, '도전 접수', 'aqua', 1.2, sub='안내원을 우클릭해 도전할 체육관을 고르세요')]
    # 뒤 벽: 배지 8색
    for i, color in enumerate(BADGE_BLOCK):
        x = xm + 9 - 3 * i                       # 안에서 보면 왼쪽부터 1번
        L += [fill(x, G + 6, z2, x + 1, G + 7, z2, f'minecraft:{color}_concrete'), sb(x, G + 5, z2 - 1, 'minecraft:quartz_slab[type=top]'),
              sb(x + 1, G + 5, z2 - 1, 'minecraft:quartz_slab[type=top]')]
    L.append(label(xm + .5, G + 8.4, z2 - .6, '배지 8개를 모으면 사천왕에 도전!', 'gold', 1.0))
    # 벤치, 깃발, 조명
    for z in range(-8, 12, 4):
        L += [sb(x1 + 1, G + 1, z, 'minecraft:spruce_stairs[facing=west]'), sb(x2 - 1, G + 1, z, 'minecraft:spruce_stairs[facing=east]')]
    for z in (-10, 0, 10):
        L += [sb(x1 + 1, G + 6, z, 'minecraft:red_wall_banner[facing=east]'), sb(x2 - 1, G + 6, z, 'minecraft:red_wall_banner[facing=west]')]
    for x in range(x1 + 3, x2 - 1, 5):
        for z in range(z1 + 3, z2 - 1, 5):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
    return L


def arena(n):
    """n번 경기장 (닫힌 방): 타입 테마 바닥·지붕, 관장 단상(북쪽), 도전자 자리와 나가는 발판(남쪽)."""
    g = gym_geom(n)
    x1, x2, z1, z2 = g['box']
    xm, top = (x1 + x2) // 2, G + 8
    theme, roof = 'minecraft:' + GYM_THEME[n - 1], 'minecraft:' + GYM_ROOF[n - 1]
    L = [f'# ── {n}번 경기장 ──', fill(x1, G - 1, z1, x2, G - 1, z2, 'minecraft:bedrock'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:polished_andesite'), fill(x1 + 1, G, z1 + 1, x2 - 1, G, z2 - 1, theme)]
    L += walls(x1, x2, z1, z2, G + 1, G + 2, 'minecraft:polished_deepslate')
    L += walls(x1, x2, z1, z2, G + 3, top, 'minecraft:light_gray_concrete')
    for x in range(x1, x2 + 1, 5):
        L += [fill(x, G + 1, z1, x, top, z1, 'minecraft:quartz_pillar'), fill(x, G + 1, z2, x, top, z2, 'minecraft:quartz_pillar')]
    for z in range(z1, z2 + 1, 6):
        L += [fill(x1, G + 1, z, x1, top, z, 'minecraft:quartz_pillar'), fill(x2, G + 1, z, x2, top, z, 'minecraft:quartz_pillar')]
    L += [fill(x1, top + 1, z1, x2, top + 1, z2, roof),
          fill(x1 + 3, G, (z1 + z2) // 2, x2 - 3, G, (z1 + z2) // 2, 'minecraft:smooth_quartz')]
    L += [sb(xm + dx, G, (z1 + z2) // 2 + dz, 'minecraft:smooth_quartz') for dx, dz in ring(2)]
    lx, lz, _ = g['leader']
    px, pz, w, d = g['exit']
    L += [fill(int(lx) - 2, G, int(lz) - 1, int(lx) + 2, G, int(lz) + 1, 'minecraft:quartz_block'),
          fill(px, G, pz, px + w - 1, G, pz + d - 1, 'minecraft:orange_stained_glass'),
          label(px + 1.5, G + 2.5, pz + .5, '◀ 나가기', 'gold', 1.0),
          label(xm + .5, G + 6.5, z2 - 1.5, f'{n}번 체육관', 'gold', 1.6)]
    for x in range(x1 + 2, x2 - 1, 3):
        for z in range(z1 + 2, z2 - 1, 3):
            L.append(sb(x, top, z, 'minecraft:sea_lantern'))
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
    return L


def town():
    L = ['# 자동 생성: tools/build_world.py (직접 수정하지 말고 생성기를 고치세요)',
         'kill @e[type=minecraft:text_display,tag=poke.deco]',
         'kill @e[type=minecraft:item]']
    L += island(HALL_AREA, '회의장') + hall()
    L += island(SHOP_AREA, '상점가') + shop_area() + mart() + center()
    L += island(GYM_AREA, '체육관') + lobby()
    for n in range(1, 9):
        L += arena(n)
    L += e4_hall()
    return L


def town_mod():
    """Cobblemon 블록: 포켓몬센터 회복 장치·PC (모드 전용)."""
    x1, x2, z1, z2 = CENTER
    zm = (z1 + z2) // 2
    L = ['# 자동 생성: tools/build_world.py. Cobblemon 블록',
         'kill @e[type=cobblemon:pokemon]',   # 마을엔 포켓몬이 나오지 않음 (예전에 나온 것 정리)
         sb(x2 - 2, G + 1, zm - 2, 'cobblemon:healing_machine[facing=west,natural=false]'),
         sb(x2 - 2, G + 1, zm + 2, 'cobblemon:healing_machine[facing=west,natural=false]')]
    for z in (z1 + 2, z1 + 4):
        L += [sb(x1 + 3, G + 1, z, 'cobblemon:pc[facing=south,part=bottom]'), sb(x1 + 3, G + 2, z, 'cobblemon:pc[facing=south,part=top]')]
    return L


def spawn_npcs():
    L = ['# 자동 생성: tools/build_world.py. 기존 NPC 제거 후 다시 소환 (청크는 build/start에서 불러옴)',
         'execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s',
         'execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s',
         '# 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게',
         'execute in poke:hub run function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}',
         '# 간호사(회복), 점원(우클릭 → 상점), 체육관 안내원(우클릭 → 도전 목록; 모드가 태그로 처리)']
    for kind, dim, x, z, tag, yaw in NPCS:
        L.append(f'execute in {dim} run function poke:mod/spawn_npc {{id:"{kind}", x:{x}, y:{G + 1}, z:{z}, tag:"{tag}", yaw:{yaw}}}')
    return L


def chunks(box, pad=0):
    x1, x2, z1, z2 = box
    return f'{x1 - pad} {z1 - pad} {x2 + pad} {z2 + pad}'


def build_start():
    L = ['# 자동 생성: tools/build_world.py', 'execute in poke:hub run forceload add -16 -16 16 16',
         'execute in poke:hub run forceload add -40 112 40 236']
    for box in [HALL_AREA, SHOP_AREA, GYM_AREA, (ARENA_X, ARENA_X + 300, -12, 12), E4]:
        L.append(f'execute in poke:town run forceload add {chunks(box)}')
    L += ['# 청크가 다 불러와질 때까지 3초 기다렸다가 짓기', 'schedule function poke:build/run 60t']
    return L


def bounds(farm_box):
    """15. 범위 검사: 섬·경기장·농장 밖이나 바닥 아래로 가면 되돌림 (관리자 크리에이티브·관전 제외)."""
    def inside(box):
        x1, x2, z1, z2 = box
        return f'unless entity @s[x={x1},y={G - 3},z={z1},dx={x2 - x1},dy={400},dz={z2 - z1}]'
    who = 'execute as @a[gamemode=!creative,gamemode=!spectator] at @s'
    town_boxes = ' '.join(inside(b) for b in [HALL_AREA, SHOP_AREA, GYM_AREA] + arenas())
    fx1, fz1, fx2, fz2 = farm_box
    return ['# 자동 생성: tools/build_world.py. 마을·농장·튜토리얼 방 밖으로 나가거나 떨어지면 되돌림',
            f'{who} if dimension poke:town {town_boxes} run function poke:home',
            f'{who} if dimension poke:farm {inside((fx1, fx2, fz1, fz2))} run function poke:util/tp with storage poke:config farm',
            f'{who} if dimension poke:hub if entity @s[y=-100,dy=155] run function poke:util/tp with storage poke:config tutorial']


def config_warps():
    return [f'data modify storage poke:config {k} set value {{dim:"poke:town", x:{x}, y:{G + 1}, z:{z}, yaw:{yaw}}}'
            for k, (x, z, yaw) in WARPS.items()]


def clear_old_village():
    """예전 시작 마을(허공 공간 poke:hub, z 110~240)을 지움."""
    L = ['# 자동 생성: 예전 시작 마을 지우기', 'kill @e[type=minecraft:text_display,tag=poke.deco]']
    L += [fill(x, 60, 110, x, 90, 240, 'minecraft:air') for x in range(-40, 41)]
    return L


if __name__ == '__main__':
    f, box = farm()
    out = {'build/town.mcfunction': town(), 'mod/build_town.mcfunction': town_mod(),
           'build/clear_village.mcfunction': clear_old_village(), 'mod/spawn_npcs.mcfunction': spawn_npcs(),
           'build/start.mcfunction': build_start(), 'bounds.mcfunction': bounds(box), 'build/farm.mcfunction': f}
    for path, lines in out.items():
        (FN / path).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # 워프 위치는 config.mcfunction의 해당 줄만 바꿔 씀 (나머지는 손으로 고치는 설정)
    cfg = FN / 'config.mcfunction'
    keep = [l for l in cfg.read_text(encoding='utf-8').splitlines()
            if not any(l.startswith(f'data modify storage poke:config {k} ') for k in WARPS)]
    i = next(i for i, l in enumerate(keep) if 'poke:config tutorial' in l) + 1
    cfg.write_text('\n'.join(keep[:i] + config_warps() + keep[i:]) + '\n', encoding='utf-8')
    # 모드(땅 문서·보호)가 읽는 땅 목록
    farms = FN.parents[5] / 'config/pokeserver/farms.json'
    farms.write_text(json.dumps({'dimension': 'poke:farm', 'plots': [
        {'id': n, 'x1': x1, 'z1': z1, 'x2': x2, 'z2': z2} for n, x1, z1, x2, z2 in plots()]}, indent=2), encoding='utf-8')
    print({k: len(v) for k, v in out.items()}, 'farm box', box)
