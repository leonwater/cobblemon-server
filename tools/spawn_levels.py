"""바이옴별 '그 바이옴 땅에서 나오는 포켓몬의 평균 레벨'을 Cobblemon 스폰 데이터로 계산.

야생 첫 스폰 위치를 '주변 포켓몬 평균 레벨이 가장 낮은 바이옴'으로 정할 때 씀.
계산: 버킷(common/uncommon/rare/ultra-rare) 확률 × 버킷 안 가중치로 레벨 범위 중간값을 평균. 땅(grounded) 스폰만, 포케스낵 전용 제외.
사용: python3 -I tools/spawn_levels.py <cobblemon.jar> <minecraft-server.jar> <fabric-api.jar> <wild.json>
"""
import io, json, re, sys, zipfile
from collections import defaultdict

BUCKETS = {'common': 93.8, 'uncommon': 5.0, 'rare': 1.0, 'ultra-rare': 0.2}  # Cobblemon 기본 설정값


def zips(path):
    """jar와 그 안에 든 jar(jar-in-jar)까지 모두 연다."""
    z = zipfile.ZipFile(path)
    yield z
    for n in z.namelist():
        if n.endswith('.jar'):
            yield from zips(io.BytesIO(z.read(n)))


def main(cobble, server, fabric, wild):
    tags, spawns, presets = {}, [], {}
    for path in (cobble, server, fabric):
        for z in zips(path):
            for n in z.namelist():
                m = re.match(r'data/([^/]+)/tags/worldgen/biome/(.+)\.json$', n)
                if m:
                    vals = json.loads(z.read(n)).get('values', [])
                    tags.setdefault(f'{m[1]}:{m[2]}', []).extend(v if isinstance(v, str) else v['id'] for v in vals)
                elif n.startswith('data/cobblemon/spawn_pool_world/') and n.endswith('.json'):
                    spawns += json.loads(z.read(n)).get('spawns', [])
                elif n.startswith('data/cobblemon/spawn_detail_presets/') and n.endswith('.json'):
                    presets[n.rsplit('/', 1)[1][:-5]] = json.loads(z.read(n))

    def expand(ref, seen=()):
        if not ref.startswith('#'):
            return {ref if ':' in ref else 'minecraft:' + ref}
        key = ref[1:]
        if key in seen:
            return set()
        return set().union(*(expand(v, seen + (key,)) for v in tags.get(key, []))) if key in tags else set()

    biomes = json.loads(open(wild).read())['generator']['biome_source']['biomes']
    sums = {b: defaultdict(lambda: [0.0, 0.0]) for b in biomes}   # 바이옴 → 버킷 → [가중치 합, 가중치×레벨 합]
    for s in spawns:
        cond = dict(s.get('condition') or {})
        for p in s.get('presets', []):
            for k, v in (presets.get(p, {}).get('condition') or {}).items():
                cond.setdefault(k, v)
        ctx = s.get('spawnablePositionType') or s.get('context')
        # 땅 스폰만, 포케스낵(미끼)으로만 나오는 것은 제외
        if ctx != 'grounded' or s.get('type') != 'pokemon' or 'level' not in s or s.get('bucket') not in BUCKETS or cond.get('isPokeSnack'):
            continue
        lo, _, hi = str(s['level']).partition('-')
        mid = (int(lo) + int(hi or lo)) / 2
        allowed = set().union(*(expand(b) for b in cond.get('biomes', []))) if cond.get('biomes') else set(biomes)
        allowed -= set().union(set(), *(expand(b) for b in (s.get('anticondition') or {}).get('biomes', [])))
        for b in biomes:
            if b in allowed:
                acc = sums[b][s['bucket']]
                acc[0] += s.get('weight', 1)
                acc[1] += s.get('weight', 1) * mid
    out = []
    for b in biomes:
        present = {k: v for k, v in sums[b].items() if v[0] > 0}
        if not present:
            continue
        total = sum(BUCKETS[k] for k in present)
        avg = sum(BUCKETS[k] / total * v[1] / v[0] for k, v in present.items())
        out.append((avg, b, sum(v[0] for v in present.values())))
    for avg, b, w in sorted(out):
        print(f'{avg:7.3f}  {b}  (스폰 항목 가중치 합 {w:.0f})')


if __name__ == '__main__':
    main(*sys.argv[1:])
