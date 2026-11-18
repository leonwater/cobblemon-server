"""건물 빈칸 검사: build/town.mcfunction(+ mod/build_town)의 fill·setblock을 그대로 따라 해 블록 지도를 만들고,
건물마다 벽·바닥에 빈칸이 있는지, 실내 위가 지붕으로 덮였는지 확인. 문·통로처럼 일부러 비운 곳은 제외.
사용: python3 tools/check_holes.py   (빈칸이 있으면 위치를 출력하고 종료 코드 1)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world as W  # noqa: E402

G = W.G


def simulate(boxes):
    """boxes 안의 칸만 기록 (세상 전체를 다 들고 있지 않게). 땅(G 이하)은 지형이 채워 둔 것으로 봄."""
    world = {}

    def inside(x, y, z):
        return any(a <= x <= b and c <= z <= d for a, b, c, d in boxes)

    def get(x, y, z):
        return world.get((x, y, z), 'ground' if y <= G and abs(x) < 2800 else 'air')

    for path in ('build/town.mcfunction', 'mod/build_town.mcfunction'):
        for line in (W.FN / path).read_text(encoding='utf-8').splitlines():
            p = line.split()
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
    x1, x2, z1, z2 = W.HALL
    out.append(('회의장', W.HALL, G, G + 9, [(-1, 1, G + 1, G + 4, z1, z1)]))
    x1, x2, z1, z2 = W.CENTER
    out.append(('포켓몬센터', W.CENTER, G, G + 12, [(x1, x1, G + 1, G + 4, -1, 1), (x1, x1, G + 8, G + 9, -1, 1)]))
    x1, x2, z1, z2 = W.MART
    out.append(('프렌들리 숍', W.MART, G, G + 10, [(x2, x2, G + 1, G + 4, -1, 1)]))
    for k, (x1, x2, z1, z2, door) in enumerate(W.CITY_SHOPS):
        fx, zm = (x2 if door == 'e' else x1), (z1 + z2) // 2
        out.append((f'상가{k + 1}', (x1, x2, z1, z2), G, G + 7, [(fx, fx, G + 1, G + 3, zm - 1, zm + 1)]))
    for k, (x1, x2, z1, z2) in enumerate(W.PAGODAS):
        xm = (x1 + x2) // 2
        out.append((f'동양풍 건물{k + 1}', (x1, x2, z1, z2), G + 1, G + 6, [(xm - 1, xm + 1, G + 2, G + 4, z2, z2)]))
    x1, x2, z1, z2 = W.LOBBY
    xm = (x1 + x2) // 2
    out.append(('체육관 선택 건물', W.LOBBY, W.LOBBY_Y, W.LOBBY_Y + 10, [(xm - 3, xm + 3, W.LOBBY_Y + 1, W.LOBBY_Y + 5, z1, z1)]))
    for n in range(1, 9):
        out.append((f'{n}번 경기장', W.gym_geom(n)['box'], G, G + 12, []))
    out.append(('사천왕 본부', W.E4, G, G + 9, []))
    return out


if __name__ == '__main__':
    bs = buildings()
    get = simulate([(b[1][0] - 1, b[1][1] + 1, b[1][2] - 1, b[1][3] + 1) for b in bs])
    holes = []
    for name, box, floor, top, openings in bs:
        holes += check(name, box, floor, top, openings, get)
    for h in holes[:80]:
        print('빈칸', h)
    print(f'검사한 건물 {len(bs)}채, 빈칸 {len(holes)}개')
    sys.exit(1 if holes else 0)
