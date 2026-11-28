"""건물 빈칸 검사: build/terrain/*(지형→마을 건물, + mod/build_town)의 fill·setblock을 그대로 따라 해 블록 지도를 만들고,
건물마다 벽·바닥에 빈칸이 있는지, 실내 위가 지붕으로 덮였는지 확인. 문·통로처럼 일부러 비운 곳은 제외.
사용: python3 tools/check_holes.py   (빈칸이 있으면 위치를 출력하고 종료 코드 1)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world as W  # noqa: E402

G = W.G


def town_paths():
    """지형 → 마을 건물 조각 순서대로 (build/terrain/0, 1, …) + 모드 블록."""
    ks = sorted(int(p.stem) for p in (W.FN / 'build/terrain').glob('*.mcfunction') if p.stem.isdigit())
    return tuple(f'build/terrain/{k}.mcfunction' for k in ks) + ('mod/build_town.mcfunction',)


def simulate(boxes, paths=None, ground=G, hub=False, lines=None):
    """hub=True: 튜토리얼 방 차원(poke:hub) 줄만, 아니면 마을 줄만."""
    """boxes 안의 칸만 기록 (세상 전체를 다 들고 있지 않게). 땅(G 이하)은 지형이 채워 둔 것으로 봄."""
    world = {}

    def inside(x, y, z):
        return any(a <= x <= b and c <= z <= d for a, b, c, d in boxes)

    def get(x, y, z):
        return world.get((x, y, z), 'ground' if y <= ground and abs(x) < 2800 else 'air')

    sources = [lines] if lines is not None else [(W.FN / path).read_text(encoding='utf-8').splitlines() for path in paths or town_paths()]
    for path, src in zip(paths or town_paths() if lines is None else ['plaza'], sources):
        for line in src:
            p = line.split()
            in_hub = p[:4] == ['execute', 'in', 'poke:hub', 'run']
            if in_hub:
                p = p[4:]
            if in_hub != hub and path != 'build/tutorial.mcfunction':
                continue
            if not p or p[0] not in ('fill', 'setblock'):
                continue
            if p[0] == 'setblock':
                x, y, z = map(int, p[1:4])
                if inside(x, y, z):
                    world[(x, y, z)] = p[4].split('[')[0]
                continue
            x1, y1, z1, x2, y2, z2 = map(int, p[1:7])
            block = p[7].split('[')[0]
            only = p[9].split('[')[0] if len(p) > 9 and p[8] == 'replace' else None
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    if not inside(x, 0, z):
                        continue
                    for y in range(min(y1, y2), max(y1, y2) + 1):
                        if only is None or get(x, y, z) == only:
                            world[(x, y, z)] = block
    return get


def empty(b):
    return b in ('air', 'minecraft:air', 'minecraft:light')


def check(name, box, floor, top, openings, get, roof_scan=14):
    """box 둘레 벽(floor+1~top), 바닥(floor), 실내 위 지붕(top+1~top+roof_scan)을 검사."""
    x1, x2, z1, z2 = box
    holes = []

    def opened(x, y, z):
        return any(a <= x <= b and c <= y <= d and e <= z <= f for a, b, c, d, e, f in openings)

    for y in range(floor + 1, top + 1):
        for x in range(x1, x2 + 1):
            for z in (z1, z2):
                if empty(get(x, y, z)) and not opened(x, y, z):
                    holes.append(('벽', x, y, z))
        for z in range(z1 + 1, z2):
            for x in (x1, x2):
                if empty(get(x, y, z)) and not opened(x, y, z):
                    holes.append(('벽', x, y, z))
    for x in range(x1 + 1, x2):
        for z in range(z1 + 1, z2):
            if empty(get(x, floor, z)):
                holes.append(('바닥', x, floor, z))
            if all(empty(get(x, y, z)) for y in range(top + 1, top + roof_scan + 1)):
                holes.append(('지붕', x, top + 1, z))
    return [(name,) + h for h in holes]


def buildings():
    """(이름, 칸, 바닥 y, 벽 꼭대기 y, 일부러 비운 곳 [(x1,x2,y1,y2,z1,z2)])"""
    out = []
    x1, x2, z1, z2 = W.LOBBY
    xm = (x1 + x2) // 2
    out.append(('체육관 선택 건물', W.LOBBY, W.LOBBY_Y, W.LOBBY_Y + 10, [(xm - 3, xm + 3, W.LOBBY_Y + 1, W.LOBBY_Y + 5, z1, z1)]))
    for n in range(1, 9):
        out.append((f'{n}번 경기장', W.gym_geom(n)['box'], G, G + 12, []))
    out.append(('사천왕 본부', W.E4, G, G + W.E4_TOP, []))
    return out


def door_tops(get, box, ys, label):
    """문(위쪽 칸) 바로 위가 비었는지: 문을 넣으려고 넓게 비운 뒤 다시 안 채운 곳."""
    x1, x2, z1, z2 = box
    return [(label, '문 위', x, y + 1, z) for x in range(x1, x2 + 1) for z in range(z1, z2 + 1) for y in ys
            if get(x, y, z).endswith('_door') and empty(get(x, y + 1, z))]


if __name__ == '__main__':
    bs = buildings()
    get = simulate([(b[1][0] - 1, b[1][1] + 1, b[1][2] - 1, b[1][3] + 1) for b in bs])
    holes = []
    for name, box, floor, top, openings in bs:
        holes += check(name, box, floor, top, openings, get)
    # 튜토리얼 방(오박사 연구소, poke:hub): 출입문 없음
    x1, x2, z1, z2 = W.LAB
    hub = simulate([(x1 - 1, x2 + 1, z1 - 1, z2 + 1)], ('build/tutorial.mcfunction', 'mod/build_town.mcfunction'), ground=62, hub=True)
    holes += check('오박사 연구소', W.LAB, 64, 72, [], hub)
    # 광장(야생) 포켓몬센터·숍: tools/plaza.py 명령(광장 기준 좌표, 땅 y=0)
    import plaza as P
    pl, _ = P.plaza()
    c1, c2, cz1, cz2 = P.CENTER_P
    m1, m2, mz1, mz2 = P.MART_P
    pg = simulate([(c1 - 1, c2 + 1, cz1 - 1, cz2 + 1), (m1 - 1, m2 + 1, mz1 - 1, mz2 + 1)], ground=0, lines=pl)
    holes += check('광장 포켓몬센터', P.CENTER_P, 0, 10, [(c1, c1, 1, 4, -1, 1)], pg)
    mzm = (mz1 + mz2) // 2
    holes += check('광장 프렌들리 숍', P.MART_P, 0, 9, [(m2, m2, 1, 4, mzm - 1, mzm + 1)], pg)
    x1, x2, z1, _ = W.LOBBY                                    # 체육관 문 앞 바닥 (계단과 건물 사이 한 줄)
    holes += [('체육관 문 앞', '바닥', x, W.LOBBY_Y, z1 - 1) for x in range(x1 + 3, x2 - 2) if empty(get(x, W.LOBBY_Y, z1 - 1))]
    # 문 위 빈칸: 광장 전체(집·식당 등)와 마을
    whole = simulate([(-P.R - 5, P.R + 5, -P.R - 5, P.R + 5)], ground=0, lines=pl)
    holes += door_tops(whole, (-P.R - 5, P.R + 5, -P.R - 5, P.R + 5), range(-2, 30), '광장')
    holes += door_tops(get, (x1 - 1, x2 + 1, z1 - 1, W.LOBBY[3] + 1), range(G - 2, G + 30), '체육관')
    for h in holes[:80]:
        print('빈칸', h)
    print(f'검사한 건물 {len(bs) + 3}채, 빈칸 {len(holes)}개')
    sys.exit(1 if holes else 0)
