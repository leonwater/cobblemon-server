#!/usr/bin/env python3
"""포켓몬 모델 고치기: 모드 jar들의 resolver가 가리키는 모델·텍스처·poser 파일이 없는 경우를 찾아,
우리 모드에 order 99 보정 resolver(그 종의 전체 변형 목록 + 고친 참조)를 만든다.

사용: python3 tools/fix_models.py <모드 jar 폴더>   (예: /tmp/pokeserver-shots/client/game-prod/mods)
- 같은 경로의 resolver가 여러 jar에 있으면(CCC·Mega Showdown 등) 한쪽만 로드되는데 어느 쪽인지 장담 못 함
  → 참조가 다 맞는 쪽을 골라 전체 목록을 order 99로 다시 씀 (99는 원래 것들 뒤에 적용되어, 어느 쪽이 이겨도 결과가 같음).
- 고치는 법: 없는 모델 → 그 종의 기본([]) 모델, 없는 텍스처 → 같은 종 폴더에서 같은 파일 이름 → 없으면 기본 텍스처(빛나는 것은 기본 빛나는 텍스처),
  없는 poser → 기본 poser (뼈 이름이 다르면 POSERS에 직접 쓴 것).
"""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'mod/src/main/resources/assets/cobblemon/bedrock/pokemon'

# 뼈 이름이 기본 모델과 달라 기본 poser를 못 쓰는 것: 직접 쓴 poser (애니메이션 파일이 없어 고개·걷기만)
POSERS = {
    'cobblemon:growlithe_hisuian': ('0058_growlithe', {
        'head': 'head', 'rootBone': 'growlithe',
        'portraitScale': 2.1, 'portraitTranslation': [-0.53, -0.33, 0], 'profileScale': 0.9, 'profileTranslation': [0, 0.4, 0],
        'poses': {
            'standing': {'poseName': 'standing', 'poseTypes': ['STAND', 'NONE', 'FLOAT', 'PORTRAIT', 'PROFILE', 'SLEEP'],
                         'animations': ["q.look('head')"]},
            'walking': {'poseName': 'walking', 'poseTypes': ['WALK', 'SWIM'],
                        'animations': ["q.look('head')", "q.quadruped_walk(0.66, 1.4, 'left_shoulder', 'right_shoulder', 'left_thigh', 'right_thigh')"]},
        }}),
}


def main(mods):
    files, models, posers, kotlin, bones = set(), set(), set(), set(), {}
    resolvers = {}   # 경로 → [(jar, json)]
    for j in sorted(Path(mods).glob('*.jar')):
        if j.name.startswith('pokeserver'): continue   # 우리가 만든 보정은 빼고 원래 상태를 봄
        z = zipfile.ZipFile(j)
        for n in z.namelist():
            files.add(n)
            m = re.match(r'assets/([^/]+)/bedrock/pokemon/models/(?:.*/)?([^/]+)\.json$', n)
            if m:
                models.add(f'{m.group(1)}:{m.group(2)}')
                try:
                    g = json.loads(z.read(n))['minecraft:geometry'][0]
                    bones[f'{m.group(1)}:{m.group(2)}'] = {b['name'] for b in g.get('bones', [])}
                except Exception: pass
            m = re.match(r'assets/([^/]+)/bedrock/pokemon/posers/(?:.*/)?([^/]+)\.json$', n)
            if m: posers.add(f'{m.group(1)}:{m.group(2)}')
            m = re.match(r'com/cobblemon/mod/common/client/render/models/blockbench/pokemon/gen\d+/(\w+)Model\.class$', n)
            if m: kotlin.add(m.group(1).lower())
            if re.match(r'assets/[^/]+/bedrock/pokemon/resolvers/.+\.json$', n):
                resolvers.setdefault(n, []).append((j.name, json.loads(z.read(n))))
    posers |= set(POSERS)

    def tex_ok(t): ns, p = t.split(':', 1); return f'assets/{ns}/{p}' in files
    def poser_ok(p): return p in posers or p.split(':')[1].replace('-', '').replace('_', '') in kotlin
    def broken(v):
        return [k for k, ok in (('model', lambda x: x in models), ('texture', tex_ok), ('poser', poser_ok))
                if isinstance(v.get(k), str) and not ok(v[k])]

    # 종별로: 경로마다 참조가 다 맞는 쪽(없으면 덜 깨진 쪽)을 골라 order 순으로
    species = {}
    for path, vers in resolvers.items():
        # 덜 깨진 쪽, 같으면 변형이 많은 쪽 (Mega Showdown이 메가·거다이 변형을 더 넣은 경우)
        best = min(vers, key=lambda jv: (sum(len(broken(v)) for v in jv[1].get('variations', [])), -len(jv[1].get('variations', []))))[1]
        bad_any = any(broken(v) for _, d in vers for v in d.get('variations', [])) \
            or len({json.dumps(d.get('variations', []), sort_keys=True) for _, d in vers}) > 1   # 같은 경로인데 내용이 다르면 어느 쪽이 이길지 몰라 다시 씀
        sp = best['species']
        folder = path.split('/')[-2]
        species.setdefault(sp, {'folder': folder, 'files': [], 'bad': False})
        species[sp]['files'].append((best.get('order', 0), path, best))
        species[sp]['bad'] |= bad_any

    fixed = []
    for sp, s in sorted(species.items()):
        if not s['bad']: continue
        variations = [v for _, _, d in sorted(s['files'], key=lambda f: (f[0], f[1])) for v in d.get('variations', [])]
        base = next((v for v in variations if not v.get('aspects')), {})
        shiny = next((v for v in variations if v.get('aspects') == ['shiny']), {})
        out, notes = [], []
        for v in variations:
            v = json.loads(json.dumps(v))
            for k in broken(v):
                old = v[k]
                if k == 'model': v[k] = base.get('model')
                elif k == 'poser': v[k] = base.get('poser')
                else:
                    name = old.split('/')[-1]
                    same = [f for f in files if f.startswith(f'assets/cobblemon/textures/pokemon/{s["folder"]}/') and f.endswith('/' + name)]
                    v[k] = ('cobblemon:' + same[0].split('assets/cobblemon/', 1)[1]) if same else \
                        ((shiny if 'shiny' in v.get('aspects', []) else base).get('texture') or base.get('texture'))
                notes.append(f'{v.get("aspects", [])} {k}: {old} → {v[k]}')
            if broken(v): sys.exit(f'고칠 수 없음 {sp} {v.get("aspects")}: {broken(v)}')
            out.append(v)
        # poser를 바꾼 경우 그 poser의 뼈가 모델에 있는지 (기본 poser는 기본 모델 뼈를 씀)
        d = OUT / 'resolvers' / s['folder']
        d.mkdir(parents=True, exist_ok=True)
        (d / '99_pokeserver_fix.json').write_text(json.dumps({'order': 99, 'species': sp, 'variations': out}, ensure_ascii=False, indent=1), encoding='utf-8')
        fixed.append((sp, notes))
    for name, (folder, body) in POSERS.items():
        d = OUT / 'posers' / folder; d.mkdir(parents=True, exist_ok=True)
        (d / (name.split(':')[1] + '.json')).write_text(json.dumps(body, indent=1), encoding='utf-8')
        # 직접 쓴 poser의 뼈(고개·뿌리·걷기 다리)가 모델에 다 있어야 함
        need = {body['head'], body['rootBone']} | set(re.findall(r"'(\w+)'", json.dumps(body['poses'])))
        miss = need - bones.get(name + '.geo', set())
        assert not miss, f'{name}: 모델에 없는 뼈 {miss}'
    for sp, notes in fixed:
        if notes: print(sp); [print('   ', n) for n in notes]
    print(f'보정 resolver {len(fixed)}개, 직접 쓴 poser {len(POSERS)}개')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/tmp/pokeserver-shots/client/game-prod/mods')
