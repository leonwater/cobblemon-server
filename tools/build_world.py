"""마을(스폰 광장·회의장·상점가·체육관·경기장)·농장을 짓는 마인크래프트 함수(.mcfunction) 생성기.

마을(poke:town)은 허공 차원에 떨어진 섬 여러 개: 회의장·상점가·체육관은 서로 1000칸씩 떨어져 워프로만 오감.
섬 둘레는 투명 벽(barrier) + 매 틱 범위 검사(벗어나면 되돌림)라 걸어서 나가거나 떨어질 수 없음.
체육관 경기장·사천왕 방은 문 없는 닫힌 방이라 도전할 때 순간이동으로만 들어감.
크기·위치를 바꾸려면 아래 숫자를 고치고 실행 → 데이터팩의 build 버전(load.mcfunction) +1.
사용: python3 tools/build_world.py
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terrain  # noqa: E402
import tips  # noqa: E402

FN = Path(__file__).resolve().parent.parent / 'pack/world/datapacks/pokeserver/data/poke/function'

# ── 마을 (poke:town, 허공. 땅 윗면 y=-60, 서는 높이 y=-59) ──
# 섬마다 걸어 다닐 수 있는 칸(PLAY) 둘레 40칸은 보기만 하는 판타지 지형(tools/terrain.py)
G = -60
HALL_PLAY = (-66, 66, -122, 34)      # 스폰 광장 + 회의장 섬
HALL = (-15, 15, -10, 12)            # 회의장 본관 (문은 북쪽, 앞에 기둥 현관)
PLAZA_C, PLAZA_R = (0, -54), 26      # 서버 스폰 광장 (원형)
CITY_SHOPS = [(-46, -34, -72, -60, 'e'), (-46, -34, -48, -36, 'e'), (34, 46, -72, -60, 'w'), (34, 46, -48, -36, 'w')]   # 광장 둘레 상가 (문 방향)
PAGODAS = [(-30, -18, -98, -88), (18, 30, -98, -88)]                  # 북쪽 동양풍 건물 (문은 남쪽)
SHOP_PLAY = (944, 1056, -58, 58)     # 상점가 섬
MART = (962, 984, -10, 10)           # 프렌들리 숍 (문은 동쪽, 광장 쪽)
CENTER = (1012, 1034, -11, 11)       # 포켓몬센터 (문은 서쪽, 광장 쪽, 2층 발코니)
GYM_PLAY = (1944, 2056, -66, 48)     # 체육관 섬
LOBBY = (1985, 2015, -14, 18)        # 체육관 선택 건물 (문은 북쪽, 넓은 계단 위)
LOBBY_Y = G + 3                      # 체육관 선택 건물 바닥 높이 (계단 3칸 위)
ARENA_X, ARENA_STEP = 3000, 50       # n번 경기장: x ARENA_X+50(n-1) ~ +30, z -18~18 (닫힌 방)
E4 = (3500, 3540, -46, 12)           # 사천왕 본부 (닫힌 방 4개 + 명예의 전당)
# 워프 도착 (x, y, z, yaw): 0 남, 180 북
WARPS = {'hall': (0.5, G + 2, PLAZA_C[1] + 0.5, 0), 'street': (1000.5, G + 1, 30.5, 180), 'gym': (2000.5, LOBBY_Y + 1, -11.5, 0)}
NPCS = [  # (NPC 종류, 차원, x, y, z, 태그, yaw, 이름표)
    ('poke:nurse', 'poke:town', CENTER[1] - 3, G + 1, 0, 'poke.nurse', 90, ('간호사', '우클릭 → 포켓몬 회복')),
    ('poke:merchant', 'poke:town', MART[0] + 4, G + 1, -3, 'poke.merchant', -90, ('점원', '우클릭 → 상점')),   # 숍 안쪽(뒤편) 계산대
    ('poke:merchant', 'poke:town', MART[0] + 4, G + 1, 3, 'poke.merchant', -90, ('점원', '우클릭 → 상점')),
    ('poke:gym_guide', 'poke:town', 2000, LOBBY_Y + 1, 12, 'poke.gymguide', 180, ('체육관 안내원', '우클릭 → 도전 신청')),
]


def tip_npcs():
    """광장 건물 안 포켓몬 상식 NPC 자리: 상가는 안쪽 벽 앞에서 문을 바라보고, 동양풍 건물은 남쪽 문을 바라봄."""
    out = []
    homes = dict(zip(('academy', 'nature', 'types', 'catch'), CITY_SHOPS))
    homes.update(zip(('evolve', 'dojo'), PAGODAS))
    for key, home in homes.items():
        mine = [t for t in tips.TIPS if t[1] == key]
        for k, (tid, _b, name, role, _skin, _pages) in enumerate(mine):
            if len(home) == 5:
                x1, x2, z1, z2, door = home
                zm = (z1 + z2) // 2
                x, y, z, yaw = (x1 + 3 if door == 'e' else x2 - 3), G + 1, zm + (-2 if k == 0 else 2), (-90 if door == 'e' else 90)
            else:
                x1, x2, z1, z2 = home
                x, y, z, yaw = (x1 + x2) // 2 + (-2 if k == 0 else 2), G + 2, z1 + 3, 0
            out.append((f'poke:tip_{tid}', 'poke:town', x, y, z, f'poke.tip_{tid}', yaw, (name, f'{role} · 우클릭')))
    return out


NPCS += tip_npcs()
BADGE_BLOCK = ['gray', 'blue', 'orange', 'lime', 'pink', 'yellow', 'red', 'green']
E4_THEME = ['iron_block', 'purpur_block', 'blackstone', 'light_blue_concrete']
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
# 바닥 타입 상징 (11x11, '#' 주색, '+' 보조색)
SYMBOLS = {
    '바위': ['...#####...', '..##+++##..', '.##++++#+#.', '##+++++####', '#+++#+++++#', '#++###++++#', '#+++#+++#+#', '##++++++###', '.##+++++##.', '..#######..', '...........'],
    '물': ['.....#.....', '....###....', '....#+#....', '...##+##...', '..##+++##..', '.##+++++##.', '.#+++++++#.', '.#++#++++#.', '.##++#++##.', '..##+++##..', '...#####...'],
    '전기': ['......####.', '.....####..', '....####...', '...####....', '..########.', '.#########.', '......####.', '.....####..', '....###....', '...##......', '..#........'],
    '풀': ['.......###.', '.....##++#.', '...##+++##.', '..#+++++#..', '.#+++#++#..', '.#++#++#...', '.#+#++##...', '.##++##....', '.#.##......', '#..........', '...........'],
    '독': ['...#####...', '..#######..', '.##+###+##.', '.#+++#+++#.', '.##+###+##.', '..#######..', '...#.#.#...', '...........', '.+.......+.', '+++.....+++', '.+.......+.'],
    '에스퍼': ['...........', '...#####...', '.##.....##.', '#...###...#', '#..#+++#..#', '#..#+#+#..#', '#..#+++#..#', '#...###...#', '.##.....##.', '...#####...', '...........'],
    '불꽃': ['.....#.....', '....##.....', '....###..#.', '...####.##.', '..##+####..', '.##++###...', '.#+++##+##.', '.#+++++++#.', '.##+++++##.', '..##+++##..', '...#####...'],
    '땅': ['...........', '.....#.....', '....###....', '...##+##...', '..##+++##..', '.##+#+++##.', '##+###+++##', '#+++++#+++#', '###########', '+.+.+.+.+.+', '.+.+.+.+.+.'],
}

def gym_geom(n):
    """n번 경기장(1~8): 도전자 자리(남쪽)·나가는 발판·관장 자리(북쪽)."""
    x0 = ARENA_X + ARENA_STEP * (n - 1)
    xm = x0 + 15
    return dict(box=(x0, x0 + 30, -18, 18), inside=(xm + .5, -13.5, 0), exit=(xm - 1, -17, 3, 1), leader=(xm + .5, 14.5, 180))


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
            f'text:\'{{"text":"{text}","color":"{color}","bold":true,"font":"pokeserver:galmuri","extra":[{extra[1:]}]}}\'}}'.replace('"extra":[]', '"extra":[""]'))


def lamp(x, z):
    return [sb(x, G + 1, z, 'minecraft:stone_brick_wall'), sb(x, G + 2, z, 'minecraft:stone_brick_wall'),
            sb(x, G + 3, z, 'minecraft:lantern')]


def walls(x1, x2, z1, z2, y1, y2, block):
    return [fill(x1, y1, z1, x2, y2, z1, block), fill(x1, y1, z2, x2, y2, z2, block),
            fill(x1, y1, z1, x1, y2, z2, block), fill(x2, y1, z1, x2, y2, z2, block)]


def emblem(plane_x, cz, cy, r=3, top='red_concrete'):
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
    L += glow(x1, x2, z1, z2, G + 4)
    return L


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


def city_shop(x1, x2, z1, z2, door, name):
    """포켓몬 도시풍 상가: 흰 벽, 붉은 계단식 지붕, 청색 포인트(문틀·차양·창). door = 문이 있는 쪽 ('e'/'w')."""
    top = G + 7
    L = [fill(x1, G, z1, x2, G, z2, 'minecraft:smooth_quartz')]
    L += walls(x1, x2, z1, z2, G + 1, G + 1, 'minecraft:light_blue_concrete')
    L += walls(x1, x2, z1, z2, G + 2, top, 'minecraft:white_concrete')
    for x in (x1, x2):
        for z in (z1, z2):
            L.append(fill(x, G + 1, z, x, top, z, 'minecraft:quartz_pillar'))
    fx = x2 if door == 'e' else x1
    out = 1 if door == 'e' else -1
    zm = (z1 + z2) // 2
    L += [fill(fx, G + 3, z1 + 2, fx, G + 5, z2 - 2, 'minecraft:light_blue_stained_glass_pane'),
          fill(fx, G + 1, zm - 1, fx, G + 3, zm + 1, 'minecraft:air'),                                   # 열린 문
          fill(fx + out, G + 4, zm - 3, fx + out, G + 4, zm + 3, 'minecraft:blue_concrete'),           # 차양
          fill(fx, G + 6, z1 + 1, fx, G + 6, z2 - 1, 'minecraft:blue_concrete'),
          label(fx + out * 0.6, G + 6.6, zm + .5, name, 'white', 1.0)]
    for x in range(x1 + 2, x2 - 1, 4):
        L += [fill(x, G + 3, z1, x + 1, G + 5, z1, 'minecraft:light_blue_stained_glass_pane'),
              fill(x, G + 3, z2, x + 1, G + 5, z2, 'minecraft:light_blue_stained_glass_pane')]
    L += [fill(x1 - 1, top + 1, z1 - 1, x2 + 1, top + 1, z2 + 1, 'minecraft:white_concrete'),
          fill(x1, top + 1, z1, x2, top + 1, z2, 'minecraft:red_concrete'),
          fill(x1 + 2, top + 2, z1 + 2, x2 - 2, top + 2, z2 - 2, 'minecraft:red_concrete'),
          fill(x1 + 4, top + 3, z1 + 4, x2 - 4, top + 3, z2 - 4, 'minecraft:red_concrete')]
    # 안: 책장·탁자·화분, 천장 등 + 밝은 빛 (팁 NPC는 NPCS)
    back = x1 + 1 if door == 'e' else x2 - 1
    L += [fill(back, G + 1, z1 + 1, back, G + 3, z2 - 1, 'minecraft:bookshelf'),
          fill(x1 + 1, G + 1, zm - 1, x2 - 1, G + 1, zm + 1, 'minecraft:red_carpet'),
          sb(x1 + 1 if door == 'w' else x2 - 1, G + 1, z1 + 1, 'minecraft:potted_azure_bluet'),
          sb(x1 + 1 if door == 'w' else x2 - 1, G + 1, z2 - 1, 'minecraft:potted_oxeye_daisy')]
    for x in range(x1 + 3, x2 - 1, 4):
        L.append(sb(x, top, zm, 'minecraft:lantern[hanging=true]'))
    L += glow(x1, x2, z1, z2, G + 4, 3)
    return L


def pagoda(x1, x2, z1, z2):
    """동양풍 붉은 건물: 돌 기단, 붉은 기둥, 짙은 나무 벽·창살, 끝이 들린 2층 기와지붕."""
    L = [fill(x1 - 1, G + 1, z1 - 1, x2 + 1, G + 1, z2 + 1, 'minecraft:stone_bricks')]
    b = G + 2
    L += walls(x1, x2, z1, z2, b, b + 4, 'minecraft:dark_oak_planks')
    for x in range(x1, x2 + 1, 3):
        for z in (z1, z2):
            L.append(fill(x, b, z, x, b + 4, z, 'minecraft:red_concrete'))
    for z in range(z1, z2 + 1, 3):
        for x in (x1, x2):
            L.append(fill(x, b, z, x, b + 4, z, 'minecraft:red_concrete'))
    for x in range(x1 + 1, x2, 3):
        L += [fill(x, b + 1, z1, x + 1, b + 3, z1, 'minecraft:spruce_trapdoor[facing=north,half=top,open=true]'),
              fill(x, b + 1, z2, x + 1, b + 3, z2, 'minecraft:spruce_trapdoor[facing=south,half=top,open=true]')]

    def roof(a1, a2, c1, c2, y):
        R = [fill(a1 - 1, y, c1 - 1, a2 + 1, y, c2 + 1, 'minecraft:deepslate_tiles'),
             fill(a1 - 2, y, c1 - 2, a2 + 2, y, c1 - 2, 'minecraft:deepslate_tile_stairs[facing=south]'),
             fill(a1 - 2, y, c2 + 2, a2 + 2, y, c2 + 2, 'minecraft:deepslate_tile_stairs[facing=north]'),
             fill(a1 - 2, y, c1 - 1, a1 - 2, y, c2 + 1, 'minecraft:deepslate_tile_stairs[facing=east]'),
             fill(a2 + 2, y, c1 - 1, a2 + 2, y, c2 + 1, 'minecraft:deepslate_tile_stairs[facing=west]')]
        for x, z in ((a1 - 2, c1 - 2), (a2 + 2, c1 - 2), (a1 - 2, c2 + 2), (a2 + 2, c2 + 2)):
            R.append(sb(x, y + 1, z, 'minecraft:deepslate_tile_slab'))                     # 들린 처마 끝
        R.append(fill(a1, y + 1, c1, a2, y + 1, c2, 'minecraft:deepslate_tile_slab'))
        return R
    L += roof(x1, x2, z1, z2, b + 5)
    L += walls(x1 + 2, x2 - 2, z1 + 2, z2 - 2, b + 6, b + 8, 'minecraft:red_concrete')
    L += roof(x1 + 2, x2 - 2, z1 + 2, z2 - 2, b + 9)
    L.append(sb((x1 + x2) // 2, b + 11, (z1 + z2) // 2, 'minecraft:gold_block'))
    xm = (x1 + x2) // 2                                                   # 광장 쪽 문 + 안: 붉은 깔개·등불·빛
    L += [fill(xm - 1, b, z2, xm + 1, b + 2, z2, 'minecraft:air'), fill(xm - 1, G + 1, z2 + 1, xm + 1, G + 1, z2 + 1, 'minecraft:stone_brick_stairs[facing=north]'),
          fill(x1 + 1, b, z1 + 1, x2 - 1, b, z2 - 1, 'minecraft:red_carpet'), sb(xm, b + 3, z1 + 2, 'minecraft:lantern[hanging=true]')]
    L += glow(x1, x2, z1, z2, b + 3, 3)
    return L


def torii(x, z, half=4):
    """붉은 도리이 문."""
    L = [fill(x - half, G + 1, z, x - half, G + 6, z, 'minecraft:red_concrete'), fill(x + half, G + 1, z, x + half, G + 6, z, 'minecraft:red_concrete'),
         fill(x - half - 1, G + 5, z, x + half + 1, G + 5, z, 'minecraft:red_concrete'),
         fill(x - half - 2, G + 7, z, x + half + 2, G + 7, z, 'minecraft:red_concrete'),
         fill(x - half - 2, G + 8, z, x + half + 2, G + 8, z, 'minecraft:blackstone_slab'),
         sb(x, G + 6, z, 'minecraft:red_concrete')]
    return L


def spawn_plaza():
    """서버 스폰 광장: 심층암 바닥 + 붉은 카펫 동심원·십자 길, 가운데 흰 단상, 둘레 상가(흰 벽·붉은 지붕·청색 포인트,
    안에 포켓몬 상식 NPC), 동양풍 붉은 건물·도리이·석등."""
    cx, cz = PLAZA_C
    R = PLAZA_R
    L = ['# ── 서버 스폰 광장 ──']
    for dx in range(-R, R + 1):                                       # 원형 심층암 바닥
        w = int(math.sqrt(max(0, R * R + R - dx * dx)))
        L.append(fill(cx + dx, G, cz - w, cx + dx, G, cz + w, 'minecraft:deepslate_tiles'))
    for r in (R, 18, 10):
        L += [sb(cx + dx, G, cz + dz, 'minecraft:polished_deepslate') for dx, dz in ring(r)]
    for r in (19, 11):                                                # 붉은 카펫 고리
        L += [sb(cx + dx, G + 1, cz + dz, 'minecraft:red_carpet') for dx, dz in ring(r)]
    L += [fill(cx - 1, G + 1, cz - R, cx + 1, G + 1, cz + R, 'minecraft:red_carpet'),   # 십자 카펫 길
          fill(cx - R, G + 1, cz - 1, cx + R, G + 1, cz + 1, 'minecraft:red_carpet')]
    L += [sb(cx + dx, G + 1, cz + dz, 'minecraft:smooth_quartz') for dx, dz in circle(4)]   # 흰 단상
    L += [sb(cx + dx, G + 1, cz + dz, 'minecraft:quartz_slab') for dx, dz in ring(5)]
    L += [sb(cx + dx, G + 1, cz + dz, 'minecraft:quartz_block') for dx, dz in ring(2)]
    L.append(label(cx + .5, G + 4.5, cz + .5, '포켓서버', 'gold', 2.4, sub='G 키: 메인 메뉴 · 워프'))
    # 광장 → 회의장 현관 길
    L += [fill(-3, G, cz + R, 3, G, HALL[2] - 9, 'minecraft:polished_deepslate'),
          fill(-1, G + 1, cz + R, 1, G + 1, HALL[2] - 9, 'minecraft:red_carpet')]
    # 둘레 상가 (광장을 향해 문)
    for (x1, x2, z1, z2, door), key in zip(CITY_SHOPS, ('academy', 'nature', 'types', 'catch')):
        L += city_shop(x1, x2, z1, z2, door, tips.BUILDINGS[key].split(' · ')[0])
    # 동양풍: 북쪽 도리이 + 양옆 붉은 건물, 길가 석등
    L += torii(cx, cz - R - 6)
    for (x1, x2, z1, z2), key in zip(PAGODAS, ('evolve', 'dojo')):
        L += pagoda(x1, x2, z1, z2) + [label((x1 + x2) / 2 + .5, G + 6.5, z2 + 1.6, tips.BUILDINGS[key].split(' · ')[0], 'gold', 1.0)]
    L += [fill(cx - 1, G, cz - R - 16, cx + 1, G, cz - R, 'minecraft:polished_deepslate')]
    for z in range(cz - R - 14, cz - R, 4):
        L += stone_lantern(cx - 3, z) + stone_lantern(cx + 3, z)
    for k in range(12):                                               # 광장 둘레 석등
        t = math.radians(15 + k * 30)
        x, z = cx + round((R + 3) * math.cos(t)), cz + round((R + 3) * math.sin(t))
        if abs(x - cx) > 4 and abs(z - cz) > 4:
            L += stone_lantern(x, z)
    return L


def brick_wood_walls(x1, x2, z1, z2, f1, f2, top):
    """1층 붉은 벽돌(f1~f2-1), 2층 짙은 목재(f2~top) + 기둥."""
    L = walls(x1, x2, z1, z2, f1, f2 - 1, 'minecraft:bricks')
    L += walls(x1, x2, z1, z2, f2, top, 'minecraft:dark_oak_planks')
    L += walls(x1, x2, z1, z2, f2 - 1, f2 - 1, 'minecraft:stripped_dark_oak_log[axis=x]')
    for x in range(x1, x2 + 1, 4):
        for z in (z1, z2):
            L.append(fill(x, f2, z, x, top, z, 'minecraft:stripped_dark_oak_log'))
    for z in range(z1, z2 + 1, 4):
        for x in (x1, x2):
            L.append(fill(x, f2, z, x, top, z, 'minecraft:stripped_dark_oak_log'))
    for x in (x1, x2):
        for z in (z1, z2):
            L.append(fill(x, f1, z, x, top, z, 'minecraft:stripped_dark_oak_log'))
    return L


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


def pokeball(cx, cy, cz, r=3, front='w'):
    """지붕 위 입체 몬스터볼."""
    L = []
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dy * dy + dz * dz <= r * r + 1:
                    b = 'black_concrete' if dy == 0 else ('red_concrete' if dy > 0 else 'white_concrete')
                    L.append(sb(cx + dx, cy + dy, cz + dz, 'minecraft:' + b))
    fx = cx - r - 1 if front == 'w' else cx + r + 1
    L += [sb(fx, cy, cz, 'minecraft:white_concrete'), sb(fx + (1 if front == 'w' else -1), cy, cz, 'minecraft:black_concrete')]
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


def center():
    """포켓몬센터: 붉은 벽돌·짙은 목재 벽, 큰 유리창, 2층 발코니, 흰 지붕 위 몬스터볼. 안: 카운터·회복기·간호사 자리·따뜻한 조명."""
    x1, x2, z1, z2 = CENTER
    zm = 0
    f2, top = G + 7, G + 12
    L = ['# ── 포켓몬센터 ──', fill(x1 - 4, G, z1 - 1, x2 + 1, G, z2 + 1, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:smooth_quartz'), fill(x1 + 1, f2, z1 + 1, x2 - 1, f2, z2 - 1, 'minecraft:spruce_planks')]
    L += brick_wood_walls(x1, x2, z1, z2, G + 1, f2, top)
    L += big_windows(x1, x2, z1, z2, G + 2, G + 4, skip_x=None) + big_windows(x1, x2, z1, z2, f2 + 1, f2 + 3)
    # 정면(서쪽): 유리 자동문, 간판, 2층 발코니
    L += [fill(x1, G + 1, zm - 1, x1, G + 4, zm + 1, 'minecraft:air'),
          fill(x1, G + 1, zm - 3, x1, G + 4, zm - 2, 'minecraft:glass_pane'), fill(x1, G + 1, zm + 2, x1, G + 4, zm + 3, 'minecraft:glass_pane'),
          fill(x1 - 3, f2, z1 + 3, x1 - 1, f2, z2 - 3, 'minecraft:dark_oak_slab[type=top]'),
          fill(x1 - 3, f2 + 1, z1 + 3, x1 - 3, f2 + 1, z2 - 3, 'minecraft:dark_oak_fence'),
          fill(x1 - 3, f2 + 1, z1 + 3, x1 - 1, f2 + 1, z1 + 3, 'minecraft:dark_oak_fence'),
          fill(x1 - 3, f2 + 1, z2 - 3, x1 - 1, f2 + 1, z2 - 3, 'minecraft:dark_oak_fence'),
          fill(x1 - 3, G + 1, z1 + 3, x1 - 3, f2 - 1, z1 + 3, 'minecraft:dark_oak_log'), fill(x1 - 3, G + 1, z2 - 3, x1 - 3, f2 - 1, z2 - 3, 'minecraft:dark_oak_log'),
          fill(x1, f2 + 1, zm - 1, x1, f2 + 2, zm + 1, 'minecraft:air'),                       # 발코니로 나가는 문
          sb(x1 - 3, f2 + 2, z1 + 3, 'minecraft:lantern'), sb(x1 - 3, f2 + 2, z2 - 3, 'minecraft:lantern'),
          label(x1 - 0.6, G + 5.4, zm + .5, '포켓몬센터', 'red', 1.5, sub='POKéMON CENTER'),
          label(x1 - 3.6, f2 + 4.2, zm + .5, 'POKéMON CENTER', 'white', 2.2, bg=0x80A01020)]
    roof, ry = hip_roof(x1, x2, z1, z2, top + 1, 'minecraft:smooth_quartz', 'minecraft:smooth_quartz_stairs')
    L += roof + pokeball((x1 + x2) // 2, ry + 4, zm, 3)
    # 안 1층: 붉은 카펫, 카운터(목재 + 흰 상판), 간호사 자리, 회복기(모드), PC(모드), 벤치, 따뜻한 조명
    L += [fill(x1 + 1, G + 1, zm - 1, x2 - 6, G + 1, zm + 1, 'minecraft:red_carpet'),
          fill(x2 - 5, G + 1, zm - 6, x2 - 5, G + 1, zm + 6, 'minecraft:dark_oak_planks'),
          fill(x2 - 5, G + 2, zm - 6, x2 - 5, G + 2, zm + 6, 'minecraft:smooth_quartz_slab'),
          fill(x2 - 4, G + 1, zm - 6, x2 - 1, G + 1, zm - 6, 'minecraft:dark_oak_planks'),
          fill(x2 - 4, G + 1, zm + 6, x2 - 1, G + 1, zm + 6, 'minecraft:dark_oak_planks'),
          fill(x2 - 1, G + 1, zm - 2, x2 - 1, G + 3, zm + 2, 'minecraft:red_wool')]
    for x in range(x1 + 2, x1 + 9, 2):
        L += [sb(x, G + 1, z2 - 1, 'minecraft:spruce_stairs[facing=south]')]
    for x in range(x1 + 3, x2 - 1, 4):
        for z in range(z1 + 3, z2 - 1, 4):
            L += [sb(x, f2, z, 'minecraft:shroomlight'), sb(x, f2 - 1, z, 'minecraft:lantern[hanging=true]')]
    # 2층으로 가는 계단 (남쪽 벽) + 2층 휴게실
    for k in range(6):
        L.append(fill(x1 + 15 - k, G + 1 + k, z2 - 2, x1 + 15 - k, G + 1 + k, z2 - 1, 'minecraft:dark_oak_stairs[facing=west]'))
    L.append(fill(x1 + 9, f2, z2 - 2, x1 + 16, f2, z2 - 1, 'minecraft:air'))
    L += [fill(x1 + 3, f2 + 1, z1 + 3, x1 + 5, f2 + 1, z1 + 5, 'minecraft:dark_oak_slab[type=top]'),
          sb(x1 + 4, f2 + 2, z1 + 4, 'minecraft:potted_red_tulip'),
          fill(x2 - 1, f2 + 1, z1 + 1, x2 - 1, f2 + 3, z1 + 6, 'minecraft:bookshelf')]
    for x in range(x1 + 3, x2 - 1, 5):
        L.append(sb(x, top - 1, zm, 'minecraft:lantern[hanging=true]'))
    L += glow(x1, x2, z1, z2, G + 4) + [c for c in glow(x1, x2, z1, z2, f2 + 4) if not (x1 + 8 <= int(c.split()[1]) <= x1 + 16 and int(c.split()[3]) >= z2 - 2)]
    return L


def mart():
    """프렌들리 숍: 포켓몬센터와 같은 붉은 벽돌·짙은 목재 양식 + 파란 간판·몬스터볼 아이콘. 안: 진열대, 계산대."""
    x1, x2, z1, z2 = MART
    zm = (z1 + z2) // 2
    f2, top = G + 6, G + 10
    L = ['# ── 프렌들리 숍 ──', fill(x1 - 1, G, z1 - 1, x2 + 4, G, z2 + 1, 'minecraft:polished_andesite'),
         fill(x1, G, z1, x2, G, z2, 'minecraft:smooth_quartz')]
    L += brick_wood_walls(x1, x2, z1, z2, G + 1, f2, top)
    L += big_windows(x1, x2, z1, z2, G + 2, G + 4, skip_x=x2) + big_windows(x1, x2, z1, z2, f2 + 1, f2 + 2)
    L += [fill(x2, G + 1, zm - 1, x2, G + 4, zm + 1, 'minecraft:air'),
          fill(x2, G + 2, z1 + 2, x2, G + 4, zm - 3, 'minecraft:glass_pane'), fill(x2, G + 2, zm + 3, x2, G + 4, z2 - 2, 'minecraft:glass_pane'),
          fill(x2 + 1, G + 5, zm - 4, x2 + 1, G + 5, zm + 4, 'minecraft:blue_concrete'),                 # 차양
          fill(x2 + 1, top + 2, zm - 5, x2 + 1, top + 10, zm + 5, 'minecraft:blue_concrete'),            # 지붕 위 파란 간판판
          fill(x2 + 1, top + 2, zm - 5, x2 + 1, top + 2, zm + 5, 'minecraft:light_blue_concrete'),
          label(x2 + 1.7, f2 + 1.4, zm + .5, 'POKé MART', 'white', 2.0, bg=0x80104090),
          label(x2 + 1.7, G + 5.6, zm + .5, '프렌들리 숍', 'aqua', 1.0)]
    L += emblem(x2 + 2, zm, top + 6, top='light_blue_concrete')
    roof, _ = hip_roof(x1, x2, z1, z2, top + 1, 'minecraft:smooth_quartz', 'minecraft:smooth_quartz_stairs')
    L += roof
    # 안: 진열대 두 줄, 계산대(점원 자리 앞), 따뜻한 조명
    for z in (zm - 6, zm + 6):
        L += [fill(x1 + 3, G + 1, z, x2 - 8, G + 1, z, 'minecraft:barrel[facing=up]'),
              fill(x1 + 3, G + 2, z, x2 - 8, G + 2, z, 'minecraft:spruce_trapdoor[half=bottom,open=false]')]
    for a, b in ((zm - 4, zm - 2), (zm + 2, zm + 4)):                    # 점원(숍 안쪽, 진열대 끝) 앞 계산대: 1칸 높이라 점원 상반신이 보임
        L += [fill(x1 + 6, G + 1, a, x1 + 6, G + 1, b, 'minecraft:stripped_dark_oak_wood'),
              fill(x1 + 6, G + 2, a, x1 + 6, G + 2, b, 'minecraft:air')]
    L += [fill(x1 + 1, G + 1, z1 + 1, x1 + 1, G + 3, z2 - 1, 'minecraft:bookshelf')]
    L += glow(x1, x2, z1, z2, G + 4)
    for x in range(x1 + 3, x2 - 1, 4):
        for z in range(z1 + 3, z2 - 1, 4):
            L += [sb(x, f2, z, 'minecraft:shroomlight'), sb(x, f2 - 1, z, 'minecraft:lantern[hanging=true]')]
    return L


def shop_area():
    """상점가 광장: 서쪽 프렌들리 숍, 동쪽 포켓몬센터, 남쪽 아치 (나무 없음)."""
    zx1, zx2 = MART[1] + 4, CENTER[0] - 5
    L = ['# ── 상점가 광장 ──', fill(zx1, G, -20, zx2, G, 36, 'minecraft:polished_andesite'),
         fill(MART[1] + 1, G, -2, CENTER[0] - 1, G, 2, 'minecraft:smooth_stone')]
    L += walls(zx1, zx2, -20, 36, G, G, 'minecraft:stone_bricks')
    L += [fill(994, G + 1, 34, 994, G + 5, 34, 'minecraft:bricks'), fill(1006, G + 1, 34, 1006, G + 5, 34, 'minecraft:bricks'),
          fill(994, G + 6, 34, 1006, G + 6, 34, 'minecraft:dark_oak_planks'), fill(994, G + 7, 34, 1006, G + 7, 34, 'minecraft:dark_oak_slab'),
          label(1000.5, G + 8, 34.5, '상점가', 'gold', 2.0, sub='포켓몬센터 · 프렌들리 숍')]
    L += [sb(dx + 1000, G + 1, 14 + dz, 'minecraft:smooth_quartz') for dx, dz in ring(3)]
    L += [sb(dx + 1000, G + 1, 14 + dz, 'minecraft:water') for dx, dz in circle(2)]
    for x in (zx1 + 2, zx2 - 2):
        for z in (-14, 8, 24):
            L += stone_lantern(x, z)
        L += [sb(x, G + 1, 16, f'minecraft:spruce_stairs[facing={"west" if x < 1000 else "east"}]'),
              sb(x, G + 1, 17, f'minecraft:spruce_stairs[facing={"west" if x < 1000 else "east"}]')]
    return L


GYM_LETTERS = ['.###.  #...#  #...#', '#...#  #...#  ##.##', '#....  .#.#.  #.#.#', '#.###  ..#..  #.#.#',
               '#...#  ..#..  #...#', '#...#  ..#..  #...#', '.###.  ..#..  #...#']   # 금색 "GYM" (5x7 글자 3개)


def lobby():
    """체육관 선택 건물: 넓은 입구 계단 위, 높은 정면 파사드 상단에 큰 "GYM" 간판과 몬스터볼 엠블럼.
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
    L += walls(x1, x2, z1, z2, B + 2, top - 1, 'minecraft:smooth_sandstone')
    L += walls(x1, x2, z1, z2, top, top, 'minecraft:cut_sandstone')
    for x in range(x1, x2 + 1, 5):
        L += [fill(x, B + 1, z1, x, top, z1, 'minecraft:chiseled_sandstone'), fill(x, B + 1, z2, x, top, z2, 'minecraft:chiseled_sandstone')]
    for z in list(range(z1, z2 + 1, 5)) + [z2]:
        L += [fill(x1, B + 1, z, x1, top, z, 'minecraft:chiseled_sandstone'), fill(x2, B + 1, z, x2, top, z, 'minecraft:chiseled_sandstone')]
        if z + 3 < z2:
            L += [fill(x1, B + 3, z + 2, x1, B + 6, z + 3, 'minecraft:glass_pane'), fill(x2, B + 3, z + 2, x2, B + 6, z + 3, 'minecraft:glass_pane')]
    roof, _ = hip_roof(x1, x2, z1, z2, top + 1, 'minecraft:dark_prismarine', 'minecraft:dark_prismarine_stairs')
    L += roof
    # 높은 정면 파사드: 금 테두리 + 검은 판의 GYM 글자 + 위에 몬스터볼 엠블럼
    fy1, fy2 = top + 1, top + 22
    L += [fill(xm - 13, B + 1, z1 - 1, xm + 13, fy2, z1 - 1, 'minecraft:smooth_sandstone'),
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
    L += [label(xm + .5, B + 7.4, z1 - 2.6, '포켓몬 체육관', 'gold', 1.6, sub='POKéMON GYM · 안내원에게 도전 신청'),
          fill(xm - 3, B + 1, z1 - 1, xm + 3, B + 5, z1, 'minecraft:air'),
          fill(xm - 4, B + 1, z1 - 1, xm - 4, B + 6, z1 - 1, 'minecraft:polished_blackstone'),
          fill(xm + 4, B + 1, z1 - 1, xm + 4, B + 6, z1 - 1, 'minecraft:polished_blackstone'),
          fill(xm - 4, B + 6, z1 - 1, xm + 4, B + 6, z1 - 1, 'minecraft:gold_block')]
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
    """n번 경기장 (닫힌 방): 직사각형 배틀 필드 + 바닥 타입 상징, 타입 색 줄무늬 천장 조명, 북쪽 관장 자리, 양옆 관중석."""
    g = gym_geom(n)
    x1, x2, z1, z2 = g['box']
    xm, top = (x1 + x2) // 2, G + 12
    name, field, wall, base, ceil, light, seat, (c1, c2) = TYPES[n - 1]
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
    # 배틀 필드 (흰 선) + 가운데 타입 상징
    fx1, fx2, fz1, fz2 = xm - 7, xm + 7, -12, 12
    L += [fill(fx1, G, fz1, fx2, G, fz2, m(field))]
    L += walls(fx1, fx2, fz1, fz2, G, G, m('quartz_block'))
    L.append(fill(fx1, G, 0, fx2, G, 0, m('quartz_block')))
    for r, row in enumerate(SYMBOLS[name]):
        for c, ch in enumerate(row):
            if ch != '.':
                L.append(sb(xm - 5 + c, G, -5 + r, m(c1 if ch == '#' else c2)))
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
    return [terrain.Island('회의장', HALL_PLAY, G, 11, keep=[(-50, 50, -100, 16)]),
            terrain.Island('상점가', SHOP_PLAY, G, 22, keep=[(956, 1040, -24, 40)]),
            terrain.Island('체육관', GYM_PLAY, G, 33, keep=[(1972, 2028, -40, 22)])]


def town():
    L = ['# 자동 생성: tools/build_world.py (직접 수정하지 말고 생성기를 고치세요). 지형(build/terrain)을 먼저 짓고 실행됨',
         'kill @e[type=minecraft:text_display,tag=poke.deco]', 'kill @e[type=minecraft:item_display,tag=poke.deco]',
         'kill @e[type=minecraft:item]']
    L += hall() + spawn_plaza() + island_walls(HALL_PLAY, '회의장')
    L += shop_area() + mart() + center() + island_walls(SHOP_PLAY, '상점가')
    L += lobby() + island_walls(GYM_PLAY, '체육관')
    for n in range(1, 9):
        L += arena(n)
    L += e4_hall()
    for _kind, _dim, x, y, z, _tag, _yaw, (name, sub) in NPCS:      # NPC 머리 위 이름표 (홀로그램)
        L.append(label(x + .5, y + 2.6, z + .5, name, 'aqua', 0.9, sub=sub))
    return L


def town_mod():
    """Cobblemon 블록: 포켓몬센터 회복 장치(카운터 위)·PC(북쪽 벽, 화면이 방 안을 보게) (모드 전용)."""
    x1, x2, z1, z2 = CENTER
    L = ['# 자동 생성: tools/build_world.py. Cobblemon 블록',
         'kill @e[type=cobblemon:pokemon]',   # 마을엔 포켓몬이 나오지 않음 (예전에 나온 것 정리)
         'kill @e[type=minecraft:interaction,tag=poke.trade]']
    for z in (-3, 3):
        L += [sb(x2 - 5, G + 2, z, 'minecraft:air'), sb(x2 - 5, G + 1, z, 'cobblemon:healing_machine[facing=west,natural=false]')]
    # PC: Cobblemon PC는 화면이 facing의 반대쪽
    for x in (x1 + 4, x1 + 6):
        L += [sb(x, G + 1, z1 + 1, 'cobblemon:pc[facing=north,part=bottom]'), sb(x, G + 2, z1 + 1, 'cobblemon:pc[facing=north,part=top]')]
    L.append(label(x1 + 5.5, G + 3.6, z1 + 1.8, 'PC 박스', 'aqua', 0.9))
    return L


def spawn_npcs():
    L = ['# 자동 생성: tools/build_world.py. 기존 NPC 제거 후 다시 소환 (청크는 build/start에서 불러옴)',
         'execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s',
         'execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s',
         '# 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게',
         'execute in poke:hub run function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}',
         '# 간호사(회복), 점원(우클릭 → 상점), 체육관 안내원(우클릭 → 도전 목록; 모드가 태그로 처리)']
    for kind, dim, x, y, z, tag, yaw, _ in NPCS:
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
    """지형 명령을 여러 틱에 나눠 실행할 조각들 (한 조각 최대 12000개)."""
    cmds = []
    for I in islands():
        x1, x2, z1, z2 = I.outer
        cmds += [f'# ── {I.name} 섬 지형 ──'] + clear_box(x1, x2, z1, z2, G - 4, G + 64)
        I.plan('nsew')
        cmds += I.biomes() + I.commands()
    a1, a2, c1, c2 = ARENA_REGION
    cmds += ['# ── 경기장 자리 비우기 ──'] + clear_box(a1, a2, c1, c2, G - 2, G + 16)
    return [cmds[i:i + 12000] for i in range(0, len(cmds), 12000)]


def bounds(farm_box):
    """15. 범위 검사: 섬·경기장·농장 밖이나 바닥 아래로 가면 되돌림 (관리자 크리에이티브·관전 제외)."""
    def inside(box):
        x1, x2, z1, z2 = box
        return f'unless entity @s[x={x1},y={G - 3},z={z1},dx={x2 - x1},dy={400},dz={z2 - z1}]'
    who = 'execute as @a[gamemode=!creative,gamemode=!spectator] at @s'
    town_boxes = ' '.join(inside(b) for b in [HALL_PLAY, SHOP_PLAY, GYM_PLAY] + arenas())
    fx1, fz1, fx2, fz2 = farm_box
    return ['# 자동 생성: tools/build_world.py. 마을·농장·튜토리얼 방 밖으로 나가거나 떨어지면 되돌림',
            f'{who} if dimension poke:town {town_boxes} run function poke:home',
            f'{who} if dimension poke:farm {inside((fx1, fx2, fz1, fz2))} run function poke:util/tp with storage poke:config farm',
            f'{who} if dimension poke:hub if entity @s[y=-100,dy=155] run function poke:util/tp with storage poke:config tutorial']


LAB = (-8, 8, -11, 7)                  # 튜토리얼: 오박사 연구소 (poke:hub, 바닥 y=64). 스폰 (0,65,3) → 3칸 앞 (0,65,0)에 오박사


def lab():
    """튜토리얼 방 = 오박사 연구소. 원작 연구소처럼 흰 벽(석영)·밝은 회색 타일 바닥·흰 천장 조명, 책장 줄, 연구 기계, 몬스터볼 3개 놓인 탁자.
    밖은 울타리 친 잔디 마당(창밖이 허공이 아니게). 문은 철문이라 나갈 수 없음."""
    x1, x2, z1, z2 = LAB
    F, top = 64, 72
    L = ['# 자동 생성: tools/build_world.py. 튜토리얼 방 = 오박사 연구소',
         'kill @e[type=minecraft:text_display,tag=poke.lab]',
         fill(-16, 63, -16, 16, 90, 16, 'minecraft:air'),
         fill(-16, 62, -16, 16, 62, 16, 'minecraft:dirt'), fill(-16, 63, -16, 16, 63, 16, 'minecraft:dirt'),
         fill(-16, 64, -16, 16, 64, 16, 'minecraft:grass_block'),
         *walls(-16, 16, -16, 16, 65, 65, 'minecraft:oak_fence'),
         fill(-1, 64, z2 + 1, 1, 64, 16, 'minecraft:dirt_path'),                     # 문 앞 길
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
    # 문(남쪽): 닫힌 철문 + 양옆 창, 위 간판
    L += [fill(-1, F + 1, z2, 1, F + 4, z2, 'minecraft:smooth_quartz'),
          sb(0, F + 1, z2, 'minecraft:iron_door[facing=north,half=lower]'), sb(0, F + 2, z2, 'minecraft:iron_door[facing=north,half=upper]'),
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
    out = {'build/town.mcfunction': town(), 'mod/build_town.mcfunction': town_mod() + lab_mod(), 'build/tutorial.mcfunction': lab(), 'mod/spawn_npcs.mcfunction': spawn_npcs(),
           'build/start.mcfunction': build_start(), 'bounds.mcfunction': bounds(box), 'build/farm.mcfunction': f}
    tdir = FN / 'build/terrain'
    tdir.mkdir(parents=True, exist_ok=True)
    for old in tdir.glob('*.mcfunction'):
        old.unlink()
    parts = terrain_parts()
    for k, part in enumerate(parts):
        out[f'build/terrain/{k}.mcfunction'] = ['# 자동 생성: tools/terrain.py (판타지 지형)'] + part
        nxt = f'poke:build/terrain/run_{k + 1}' if k + 1 < len(parts) else 'poke:build/finish'
        out[f'build/terrain/run_{k}.mcfunction'] = [f'execute in poke:town run function poke:build/terrain/{k}', f'schedule function {nxt} 2t']
    out['build/run.mcfunction'] = ['# 자동 생성: tools/build_world.py. 지형을 여러 틱에 나눠 지은 뒤 build/finish',
                                   'function poke:build/terrain/run_0']
    out['build/finish.mcfunction'] = [
        '# 자동 생성: tools/build_world.py',
        'execute in poke:hub run function poke:build/tutorial', 'execute in poke:town run function poke:build/town',
        'execute in poke:town run function poke:mod/build_town', 'execute in poke:hub run function poke:mod/spawn_npcs',
        'execute in poke:town run forceload remove all', 'data modify storage poke:state build set value 10',
        '# 관장·사천왕은 플레이어가 접속하면 소환 (RCT 명령이 플레이어를 요구)', 'data modify storage poke:state leaders set value 0',
        'say [pokeserver] 튜토리얼 방·마을(스폰 광장·상점가·체육관)과 지형을 지었습니다.']
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
