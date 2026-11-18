"""판타지 지형 생성기: 마을 섬(회의장·상점가·체육관) 둘레의 석회암 절벽, 공중 바위 아치, 나무가 자란 돌기둥,
사바나·벚꽃 언덕과 계단식 흙길, 떠 있는 바위섬.

높이맵을 만든 뒤 같은 블록이 이어진 칸을 큰 사각형(fill 한 번)으로 합쳐 명령 수를 줄임.
build_world.py 가 불러 씀 (직접 실행하지 않음).
"""
import math
import random

FILL_MAX = 32768   # fill 한 번에 바꿀 수 있는 최대 칸 수


class Island:
    """play = 걸어 다닐 수 있는 칸(x1, x2, z1, z2). 그 바깥 margin 칸은 보기만 하는 배경(절벽)."""

    def __init__(self, name, play, g, seed, keep=(), margin=40, hill=14):
        self.name, self.play, self.g, self.margin, self.hill = name, play, g, margin, hill
        self.keep = list(keep)                 # 평평하게 둘 칸 (건물·광장)
        self.rnd = random.Random(seed)
        r = self.rnd
        # 부드러운 잡음: 서로 다른 방향·주기의 사인파 합 (0~1)
        self.waves = [(r.uniform(0.015, 0.05), r.uniform(0.015, 0.05), r.uniform(0, 6.3), r.uniform(0, 6.3)) for _ in range(5)]
        self.paths = []                        # 계단식 흙길 칸
        self.trees = []                        # (x, y, z, 나무 종류)
        self.extra = []                        # 아치·바위섬·기둥 꼭대기 등 추가 명령
        x1, x2, z1, z2 = play
        self.outer = (x1 - margin, x2 + margin, z1 - margin, z2 + margin)

    # ── 잡음·높이 ──
    def noise(self, x, z, k=0):
        s = sum(math.sin(x * fx + px + k) * math.sin(z * fz + pz - k) for fx, fz, px, pz in self.waves)
        return 0.5 + s / (2 * len(self.waves)) * 1.6

    def cherry(self, x, z):
        """벚꽃(True) / 사바나(False) 구역."""
        return self.noise(x * 0.6, z * 0.6, 3.1) > 0.5

    def inside(self, x, z):
        x1, x2, z1, z2 = self.play
        return x1 <= x <= x2 and z1 <= z <= z2

    def kept(self, x, z):
        return any(a - 2 <= x <= b + 2 and c - 2 <= z <= d + 2 for a, b, c, d in self.keep)

    def height(self, x, z):
        g, (x1, x2, z1, z2) = self.g, self.play
        if self.inside(x, z):
            d = min(x - x1, x2 - x, z - z1, z2 - z)
            w = self.hill * (0.5 + 0.9 * self.noise(x * 4, z * 4, 5.3))                  # 언덕 폭도 곳곳이 다르게
            if d >= w or self.kept(x, z):
                return g
            t = (w - d) / w
            bump = 0.3 + 1.0 * self.noise(x * 4.5, z * 4.5, 2.2)                 # 굽이치는 언덕
            return g + max(0, round(t ** 1.4 * 10 * bump))
        dx, dz = max(x1 - x, 0, x - x2), max(z1 - z, 0, z - z2)
        e = math.hypot(dx, dz)
        valley = self.g + 6 + round(4 * self.noise(x * 1.3, z * 1.3, 1.7))      # 울타리 바로 밖 골짜기
        start = 5 + 14 * self.noise(x * 0.8, z * 0.8, 7.7)                       # 절벽이 시작되는 거리도 들쭉날쭉
        if e < start:
            return valley
        cliff = self.g + 18 + 20 * self.noise(x, z, 4.2) + 10 * self.noise(x * 2.3, z * 2.3, 9.1)
        h = valley + min(1.0, (e - start) / 3) * (cliff - valley)
        return int(h // 3 * 3)                                                    # 3칸 단위 층층이 (절벽 결)

    # ── 장식 ──
    def plan(self, path_dirs):
        """흙길·돌기둥·아치·바위섬·나무 위치를 정함. path_dirs: 흙길을 낼 방향 목록 ('n','s','e','w')."""
        g, (x1, x2, z1, z2), r = self.g, self.play, self.rnd
        xm, zm = (x1 + x2) // 2, (z1 + z2) // 2
        self.H = {}
        X1, X2, Z1, Z2 = self.outer
        for x in range(X1, X2 + 1):
            for z in range(Z1, Z2 + 1):
                self.H[(x, z)] = self.height(x, z)
        # 계단식 흙길: 평지 끝에서 언덕 위 전망대까지, 2칸마다 한 칸씩 오름
        for d in path_dirs:
            for k in range(self.hill + 1):
                for w in (-1, 0, 1):
                    x, z = {'n': (xm + w, z1 + self.hill - k), 's': (xm + w, z2 - self.hill + k),
                            'w': (x1 + self.hill - k, zm + w), 'e': (x2 - self.hill + k, zm + w)}[d]
                    self.H[(x, z)] = g + (k + 1) // 2
                    self.paths.append((x, z))
        # 나무가 자란 돌기둥 (골짜기에 우뚝)
        pillars = []
        for _ in range(60):
            if len(pillars) >= 6:
                break
            ang = r.uniform(0, 2 * math.pi)
            x, z = self.edge_point(ang, r.uniform(3, 8))
            if all(math.hypot(x - a, z - b) > 22 for a, b, _ in pillars):
                pillars.append((x, z, g + 27 + 3 * r.randint(0, 5)))
        for px, pz, top in pillars:
            rad = r.choice((2, 2, 3))
            for dx in range(-rad, rad + 1):
                for dz in range(-rad, rad + 1):
                    if dx * dx + dz * dz <= rad * rad + 1 and (px + dx, pz + dz) in self.H:
                        self.H[(px + dx, pz + dz)] = max(self.H[(px + dx, pz + dz)], top - (0 if dx * dx + dz * dz <= rad * rad - 1 else 3))
            self.trees.append((px, top + 1, pz, 'cherry' if self.cherry(px, pz) else 'acacia'))
        # 공중 바위 아치: 골짜기 위로 넘어가는 반원
        for _ in range(2):
            ang = r.uniform(0, 2 * math.pi)
            cx, cz = self.edge_point(ang, r.uniform(4, 8))
            along_x = abs(math.cos(ang)) < 0.7
            R = r.randint(10, 14)
            base = self.g + 7
            for i in range(int(math.pi * R) + 1):
                t = i / (math.pi * R) * math.pi
                ax = cx + (round(R * math.cos(t)) if along_x else 0)
                az = cz + (0 if along_x else round(R * math.cos(t)))
                ay = base + round(R * 1.3 * math.sin(t))
                blk = 'calcite' if i % 5 else 'diorite'
                self.extra.append(f'fill {ax - 1} {ay - 1} {az - 1} {ax + 1} {ay + 1} {az + 1} minecraft:{blk}')
            top = base + round(R * 1.3)
            self.extra.append(f'fill {cx - 1} {top + 2} {cz - 1} {cx + 1} {top + 2} {cz + 1} minecraft:grass_block')
        # 떠 있는 바위섬: 아래가 뾰족한 돌덩이 + 잔디 + 나무
        for _ in range(3):
            ang = r.uniform(0, 2 * math.pi)
            cx, cz = self.edge_point(ang, r.uniform(6, 16))
            cy, rad = self.g + 34 + r.randint(0, 12), r.randint(4, 6)
            for dy in range(0, rad + 2):
                rr = max(0, rad - dy)
                if rr == 0:
                    self.extra.append(f'setblock {cx} {cy - dy} {cz} minecraft:calcite')
                else:
                    self.extra.append(f'fill {cx - rr} {cy - dy} {cz - rr // 2} {cx + rr} {cy - dy} {cz + rr // 2} minecraft:'
                                      + ('dirt' if dy == 0 else 'calcite'))
                    self.extra.append(f'fill {cx - rr // 2} {cy - dy} {cz - rr} {cx + rr // 2} {cy - dy} {cz + rr} minecraft:'
                                      + ('dirt' if dy == 0 else 'calcite'))
            self.extra.append(f'fill {cx - rad} {cy + 1} {cz - rad // 2} {cx + rad} {cy + 1} {cz + rad // 2} minecraft:grass_block')
            self.extra.append(f'fill {cx - rad // 2} {cy + 1} {cz - rad} {cx + rad // 2} {cy + 1} {cz + rad} minecraft:grass_block')
            self.trees.append((cx, cy + 2, cz, 'cherry' if self.cherry(cx, cz) else 'acacia'))
        # 언덕·골짜기·절벽 위 나무
        cells = [c for c in self.H if not self.inside(*c) or self.H[c] > g + 2]
        r.shuffle(cells)
        for x, z in cells:
            if len(self.trees) >= 40:
                break
            if (x, z) in self.paths or any(abs(x - a) < 7 and abs(z - c) < 7 for a, _, c, _ in self.trees):
                continue
            if self.inside(x, z) and min(x - x1, x2 - x, z - z1, z2 - z) < 3:
                continue                                                           # 울타리에 붙은 나무는 넘어가는 발판이 됨
            self.trees.append((x, self.H[(x, z)] + 1, z, 'cherry' if self.cherry(x, z) else 'acacia'))

    def edge_point(self, ang, out):
        """섬 가운데에서 ang 방향으로, 울타리 밖 out칸 지점."""
        x1, x2, z1, z2 = self.play
        cx, cz = (x1 + x2) / 2, (z1 + z2) / 2
        hx, hz = (x2 - x1) / 2, (z2 - z1) / 2
        k = min(hx / max(1e-6, abs(math.cos(ang))), hz / max(1e-6, abs(math.sin(ang))))
        return round(cx + math.cos(ang) * (k + out)), round(cz + math.sin(ang) * (k + out))

    # ── 블록 ──
    def block(self, x, z, y):
        h, g = self.H[(x, z)], self.g
        if y == g - 4:
            return 'bedrock'
        if y == h:
            return 'dirt_path' if (x, z) in self.paths else 'grass_block'
        if y >= h - 3 and h <= g + 12:
            return 'dirt'
        band = (y - g) // 3 % 6                                                   # 석회암 결: 흰 방해석에 섞인 줄
        return {0: 'calcite', 1: 'calcite', 2: 'diorite', 3: 'calcite', 4: 'stone', 5: 'smooth_sandstone'}[band]

    def commands(self):
        """지형 fill 명령 목록 (층마다 같은 블록을 사각형으로 합치고, 위아래로 같은 층은 하나로)."""
        g = self.g
        top = max(self.H.values())
        layers = []
        for y in range(g - 4, top + 1):
            mats = {}
            for (x, z), h in self.H.items():
                if h >= y:
                    mats.setdefault(self.block(x, z, y), set()).add((x, z))
            layers.append((y, {m: frozenset(c) for m, c in mats.items()}))
        out = []
        i = 0
        while i < len(layers):                                                    # 같은 모양의 층은 위아래로 합침
            y0, mats = layers[i]
            j = i
            while j + 1 < len(layers) and layers[j + 1][1] == mats and j - i < 15:
                j += 1
            for m, cells in mats.items():
                for x1, x2, z1, z2 in rectangles(cells, j - i + 1):
                    out.append(f'fill {x1} {y0} {z1} {x2} {layers[j][0]} {z2} minecraft:{m}')
            i = j + 1
        return out + self.extra + [tree(*t) for t in self.trees]

    def biomes(self):
        """벚꽃 숲·사바나 섞기 (16x16 칸, fillbiome 한 번 32768칸)."""
        X1, X2, Z1, Z2 = self.outer
        out = []
        for x in range(X1, X2 + 1, 16):
            for z in range(Z1, Z2 + 1, 16):
                b = 'cherry_grove' if self.cherry(x + 8, z + 8) else 'savanna'
                for y in (-64, 64, 192):
                    out.append(f'fillbiome {x} {y} {z} {min(x + 15, X2)} {y + 127} {min(z + 15, Z2)} minecraft:{b}')
        return out


def tree(x, y, z, kind):
    return f'place feature minecraft:{"cherry" if kind == "cherry" else "acacia"} {x} {y} {z}'


def rectangles(cells, height=1):
    """칸 집합 → (x1, x2, z1, z2) 사각형들. x줄마다 z구간을 찾고, 같은 구간이 이어진 x줄을 합침."""
    rows = {}
    for x, z in cells:
        rows.setdefault(x, []).append(z)
    runs = {}
    for x, zs in rows.items():
        zs.sort()
        a = prev = zs[0]
        for z in zs[1:] + [None]:
            if z is not None and z == prev + 1:
                prev = z
                continue
            runs.setdefault(x, []).append((a, prev))
            if z is not None:
                a = prev = z
    out, open_ = [], {}
    for x in sorted(runs):
        nxt = {}
        for run in runs[x]:
            if run in open_ and open_[run][1] == x - 1 and (x - open_[run][0] + 1) * (run[1] - run[0] + 1) * height <= FILL_MAX:
                nxt[run] = (open_[run][0], x)
            else:
                nxt[run] = (x, x)
        for run, (a, b) in open_.items():
            if run not in nxt or nxt[run][0] != a:
                out.append((a, b, run[0], run[1]))
        open_ = nxt
    out += [(a, b, run[0], run[1]) for run, (a, b) in open_.items()]
    # 한 줄 구간이 너무 길면(높이 포함 32768칸 초과) 나눔
    res = []
    for x1, x2, z1, z2 in out:
        step = max(1, FILL_MAX // ((x2 - x1 + 1) * height))
        for a in range(z1, z2 + 1, step):
            res.append((x1, x2, a, min(z2, a + step - 1)))
    return res


if __name__ == '__main__':
    # 자체 검사: 사각형이 칸을 정확히 한 번씩 덮는지
    import itertools
    rnd = random.Random(1)
    cells = {(x, z) for x, z in itertools.product(range(40), range(40)) if rnd.random() < 0.7}
    covered = []
    for x1, x2, z1, z2 in rectangles(cells, 3):
        assert (x2 - x1 + 1) * (z2 - z1 + 1) * 3 <= FILL_MAX
        covered += [(x, z) for x in range(x1, x2 + 1) for z in range(z1, z2 + 1)]
    assert sorted(covered) == sorted(cells), 'rectangles mismatch'
    big = {(x, z) for x in range(200) for z in range(200)}
    assert sum((b - a + 1) * (d - c + 1) for a, b, c, d in rectangles(big)) == 40000
    print('terrain self-check ok')
