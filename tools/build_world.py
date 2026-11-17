"""시작 마을·건물·농장을 짓는 마인크래프트 함수(.mcfunction) 생성기.

크기·위치를 바꾸려면 아래 숫자를 고치고 실행 → 데이터팩의 build 버전(load.mcfunction) +1.
사용: python3 tools/build_world.py
"""
import math
from pathlib import Path

FN = Path(__file__).resolve().parent.parent / 'pack/world/datapacks/pokeserver/data/poke/function'

# ── 시작 마을 (poke:hub, 바닥 y=64) ──
CX, CZ, Y = 0, 200, 64
R = 14.5 * 1.5                      # 원 반지름 (지름 1.5배)
ROAD = (-2, 2, 151, 178)            # 북쪽 길 x1,x2,z1,z2
PLAZA = (-30, 30, 143, 150)         # 길 끝 광장
SHOP = (-28, -8, 127, 142)          # 상점 건물 x1,x2,z1,z2 (문은 남쪽)
CENTER = (8, 28, 127, 142)          # 포켓몬센터
PADS = {'farm': (18, 20, 199, 201), 'wild': (-20, -18, 199, 201)}  # 동쪽 농장, 서쪽 채집맵 워프 발판

# ── 농장 (poke:farm, 평지 지면 y=-60) ──
FY = -60
PLOT, GAP = 32, 3                   # 땅 한 칸 32x32, 땅 사이 길 3
COLS_X = [4, 4 + PLOT + GAP, -4 - PLOT + 1, -4 - 2 * PLOT - GAP + 1]  # 각 열의 x 시작
ROWS = 4
FARM_RETURN = (-1, 1, -8, -6)       # 마을로 돌아가는 발판


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


def disc(r, y, block):
    out = []
    for dz in range(-int(r), int(r) + 1):
        if r * r < dz * dz:
            continue
        h = int(math.sqrt(r * r - dz * dz))
        out.append(fill(CX - h, y, CZ + dz, CX + h, y, CZ + dz, block))
    return out


def in_disc(x, z, r=R):
    dz = z - CZ
    return r * r >= dz * dz and abs(x - CX) <= int(math.sqrt(r * r - dz * dz))


def label(x, y, z, text, color='white', scale=1.0):
    return (f'summon minecraft:text_display {x} {y} {z} {{Tags:["poke.deco"],billboard:"center",'
            f'background:-1442840576,transformation:{{scale:[{scale}f,{scale}f,{scale}f],translation:[0f,0f,0f],'
            f'left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}},'
            f'text:\'{{"text":"{text}","color":"{color}","bold":true}}\'}}')


def building(b, wall, pillar, roof, rim, window, floor, name, color):
    x1, x2, z1, z2 = b
    top = Y + 7
    door = (x1 + x2) // 2
    out = [f'# {name}',
           fill(x1, Y, z1, x2, Y, z2, floor),
           fill(x1, Y + 1, z1, x2, top, z2, wall, 'hollow'),
           fill(x1 + 1, Y + 1, z1 + 1, x2 - 1, top - 1, z2 - 1, 'minecraft:air')]
    for x in (x1, x2):
        for z in (z1, z2):
            out.append(fill(x, Y + 1, z, x, top, z, pillar))
    out.append(fill(x1, top + 1, z1, x2, top + 1, z2, roof))
    out.append(fill(x1, top + 2, z1, x2, top + 2, z2, rim, 'hollow'))
    out.append(fill(x1 + 1, top + 2, z1 + 1, x2 - 1, top + 2, z2 - 1, 'minecraft:air'))
    for x in range(x1 + 2, x2 - 1, 3):          # 앞·뒤 창문
        out += [fill(x, Y + 3, z1, x, Y + 4, z1, window), fill(x, Y + 3, z2, x, Y + 4, z2, window)]
    for z in range(z1 + 3, z2 - 1, 3):          # 옆 창문
        out += [fill(x1, Y + 3, z, x1, Y + 4, z, window), fill(x2, Y + 3, z, x2, Y + 4, z, window)]
    for x in range(x1 + 3, x2 - 1, 5):          # 천장 조명
        for z in range(z1 + 3, z2 - 1, 5):
            out.append(f'setblock {x} {top} {z} minecraft:sea_lantern')
    out.append(fill(door - 1, Y + 1, z2, door + 1, Y + 4, z2, 'minecraft:air'))  # 남쪽 문
    out.append(label(door + 0.5, top + 3.5, z2 + 0.5, name, color, 2.0))
    return out


def village():
    L = ['# 자동 생성: tools/build_world.py (직접 수정하지 말고 생성기를 고치세요)',
         'kill @e[type=minecraft:text_display,tag=poke.deco]',
         fill(-34, Y + 1, 120, 34, Y + 12, 230, 'minecraft:air'),
         fill(-34, Y, 120, 34, Y, 230, 'minecraft:air')]
    # 원형 돌 바닥
    L += disc(R, Y - 1, 'minecraft:stone_bricks') + disc(R, Y, 'minecraft:stone_bricks')
    L += disc(R - 1.95, Y, 'minecraft:polished_andesite') + disc(R * 0.59, Y, 'minecraft:smooth_stone')
    L += disc(R * 0.52, Y, 'minecraft:polished_andesite') + disc(R * 0.17, Y, 'minecraft:chiseled_stone_bricks')
    for i in range(8):                           # 가로등
        a = i * math.pi / 4 + math.pi / 8
        x, z = CX + round(15 * math.cos(a)), CZ + round(15 * math.sin(a))
        L += [f'setblock {x} {Y + 1} {z} minecraft:stone_brick_wall', f'setblock {x} {Y + 2} {z} minecraft:lantern']
    # 북쪽 길 + 광장
    x1, x2, z1, z2 = ROAD
    L += [fill(x1, Y, z1, x2, Y, z2, 'minecraft:polished_andesite'), fill(x1, Y, z1, x1, Y, z2, 'minecraft:stone_bricks'),
          fill(x2, Y, z1, x2, Y, z2, 'minecraft:stone_bricks')]
    for z in range(z1 + 2, z2, 7):
        L += [f'setblock {x1 - 1} {Y} {z} minecraft:stone_bricks', f'setblock {x1 - 1} {Y + 1} {z} minecraft:stone_brick_wall',
              f'setblock {x1 - 1} {Y + 2} {z} minecraft:lantern']
    px1, px2, pz1, pz2 = PLAZA
    L.append(fill(px1, Y, pz1, px2, Y, pz2, 'minecraft:polished_andesite'))
    L += building(SHOP, 'minecraft:spruce_planks', 'minecraft:stripped_dark_oak_log', 'minecraft:dark_oak_planks',
                  'minecraft:dark_oak_slab', 'minecraft:glass_pane', 'minecraft:polished_andesite', '상점', 'gold')
    L += building(CENTER, 'minecraft:white_concrete', 'minecraft:red_concrete', 'minecraft:red_concrete',
                  'minecraft:red_terracotta', 'minecraft:light_blue_stained_glass_pane', 'minecraft:smooth_quartz',
                  '포켓몬센터', 'red')
    cx1, cx2, cz1, _ = CENTER                    # 포켓몬센터 접수대 (회복 장치·PC는 mod/build_center)
    L.append(fill(cx1 + 4, Y + 1, cz1 + 4, cx2 - 4, Y + 1, cz1 + 4, 'minecraft:quartz_block'))
    sx1, sx2, sz1, _ = SHOP                      # 상점 진열대
    L.append(fill(sx1 + 4, Y + 1, sz1 + 4, sx2 - 4, Y + 1, sz1 + 4, 'minecraft:barrel[facing=up]'))
    # 워프 발판: 동쪽 농장, 서쪽 채집맵
    for key, (x1, x2, z1, z2) in PADS.items():
        glass = 'minecraft:lime_stained_glass' if key == 'farm' else 'minecraft:light_blue_stained_glass'
        L += [fill(x1, Y - 1, z1, x2, Y - 1, z2, 'minecraft:sea_lantern'), fill(x1, Y, z1, x2, Y, z2, glass),
              label((x1 + x2) / 2 + 0.5, Y + 3, (z1 + z2) / 2 + 0.5,
                    '▶ 농장' if key == 'farm' else '◀ 채집 맵', 'green' if key == 'farm' else 'aqua', 1.5)]
    # 허공 추락 방지: 걸을 수 있는 칸 바로 바깥에 보이지 않는 벽
    walk = set()
    for x in range(-40, 41):
        for z in range(110, 240):
            if (in_disc(x, z) or ROAD[0] <= x <= ROAD[1] and ROAD[2] <= z <= ROAD[3]
                    or PLAZA[0] <= x <= PLAZA[1] and PLAZA[2] <= z <= PLAZA[3]
                    or any(b[0] <= x <= b[1] and b[2] <= z <= b[3] for b in (SHOP, CENTER))):
                walk.add((x, z))
    edge = sorted({(x + dx, z + dz) for x, z in walk for dx in (-1, 0, 1) for dz in (-1, 0, 1)} - walk)
    L += [fill(x, Y + 1, z, x, Y + 4, z, 'minecraft:barrier') for x, z in edge]
    return L


def farm():
    L = ['# 자동 생성: tools/build_world.py. 주의: 다시 지으면 길·경계 위의 블록을 덮어씀',
         'kill @e[type=minecraft:text_display,tag=poke.farmdeco]']
    xs = [p[1] for p in plots()] + [p[3] for p in plots()]
    zs = [p[2] for p in plots()] + [p[4] for p in plots()]
    bx1, bx2, bz1, bz2 = min(xs) - 3, max(xs) + 3, -12, max(zs) + 3
    L.append(fill(bx1 + 1, FY, bz1 + 1, bx2 - 1, FY, bz2 - 1, 'minecraft:dirt_path'))   # 전체를 길로 깔고
    for n, x1, z1, x2, z2 in plots():                                                  # 땅만 잔디로
        L += [fill(x1, FY, z1, x2, FY, z2, 'minecraft:polished_andesite'),
              fill(x1 + 1, FY, z1 + 1, x2 - 1, FY, z2 - 1, 'minecraft:grass_block'),
              label(x1 + PLOT / 2, FY + 3, z1 - 1, f'농장 {n} (빈 땅)', 'yellow', 1.5)
              .replace('"poke.deco"', f'"poke.farmdeco","poke.plot{n}"')]
    x1, x2, z1, z2 = FARM_RETURN
    L += [fill(x1, FY, z1, x2, FY, z2, 'minecraft:light_blue_stained_glass'),
          label(0.5, FY + 3, (z1 + z2) / 2 + 0.5, '◀ 마을로', 'aqua', 1.5).replace('poke.deco', 'poke.farmdeco')]
    # 둘레 벽 (지면~높이 제한, fill 한 번 최대 32768칸이라 나눠서)
    for a in range(bx1, bx2 + 1, 80):
        b = min(a + 79, bx2)
        L += [fill(a, FY + 1, bz1, b, 319, bz1, 'minecraft:barrier'), fill(a, FY + 1, bz2, b, 319, bz2, 'minecraft:barrier')]
    for a in range(bz1, bz2 + 1, 80):
        b = min(a + 79, bz2)
        L += [fill(bx1, FY + 1, a, bx1, 319, b, 'minecraft:barrier'), fill(bx2, FY + 1, a, bx2, 319, b, 'minecraft:barrier')]
    return L, (bx1, bz1, bx2, bz2)


def center_mod():
    x1, x2, z1, _ = CENTER
    mid = (x1 + x2) // 2
    return ['# 자동 생성: tools/build_world.py. 포켓몬센터 회복 장치·PC (Cobblemon 블록)',
            f'setblock {mid - 2} {Y + 2} {z1 + 4} cobblemon:healing_machine[facing=south,natural=false]',
            f'setblock {mid + 2} {Y + 2} {z1 + 4} cobblemon:healing_machine[facing=south,natural=false]',
            f'setblock {x1 + 1} {Y + 1} {z1 + 8} cobblemon:pc[facing=east,part=bottom]',
            f'setblock {x1 + 1} {Y + 2} {z1 + 8} cobblemon:pc[facing=east,part=top]',
            f'setblock {x1 + 1} {Y + 1} {z1 + 10} cobblemon:pc[facing=east,part=bottom]',
            f'setblock {x1 + 1} {Y + 2} {z1 + 10} cobblemon:pc[facing=east,part=top]']


if __name__ == '__main__':
    v = village()
    (FN / 'build/village.mcfunction').write_text('\n'.join(v) + '\n', encoding='utf-8')
    f, box = farm()
    (FN / 'build/farm.mcfunction').write_text('\n'.join(f) + '\n', encoding='utf-8')
    (FN / 'mod/build_center.mcfunction').write_text('\n'.join(center_mod()) + '\n', encoding='utf-8')
    # 모드(땅 문서·보호)가 읽는 땅 목록
    import json
    cfg = FN.parents[5] / 'config/pokeserver/farms.json'
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(json.dumps({'dimension': 'poke:farm', 'plots': [
        {'id': n, 'x1': x1, 'z1': z1, 'x2': x2, 'z2': z2} for n, x1, z1, x2, z2 in plots()]}, indent=2), encoding='utf-8')
    print(f'village {len(v)} lines, farm {len(f)} lines, farm box {box}, plots {len(plots())}')
    for p in plots():
        print(p)
