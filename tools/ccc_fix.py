"""Complete Cobblemon Collection(1.8.4) 경로 오류 보정: 모델 설정은 textures/pokemon/<이름>/... 을 찾는데
실제 그림은 textures/pokemon/<번호_이름>/... 에 있는 종(아르세우스·우라오스)이 보라·검정으로 보임.
→ 같은 변형을 올바른 경로로 다시 적은 설정을 우리 모드에 넣음 (order를 높여 덮어씀). 애드온 파일은 그대로.
사용: python3 tools/ccc_fix.py <CCC jar> [다른 모드 jar ...]   (CCC를 올리면 다시 실행)
"""
import json
import re
import sys
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'mod/src/main/resources/assets/cobblemon/bedrock/pokemon/resolvers'


def main(ccc, *others):
    z = zipfile.ZipFile(ccc)
    files = set(z.namelist())
    for o in others:
        files |= set(zipfile.ZipFile(o).namelist())
    by_name = {}
    for f in files:
        m = re.match(r'assets/cobblemon/textures/pokemon/[^/]+/([^/]+\.png)$', f)
        if m:
            by_name.setdefault(m.group(1), f)

    def fix(t):
        if 'assets/cobblemon/' + t.split(':', 1)[1] in files:
            return t
        real = by_name.get(t.split('/')[-1])
        return 'cobblemon:' + real[len('assets/cobblemon/'):] if real else t

    n = 0
    for name in z.namelist():
        if '/resolvers/' not in name or not name.endswith('.json'):
            continue
        text = z.read(name).decode()
        refs = re.findall(r'"(cobblemon:textures/[^"]+\.png)"', text)
        if all(fix(t) == t for t in refs):
            continue
        d = json.loads(text)
        d['order'] = d.get('order', 0) + 1000
        for v in d['variations']:
            if 'texture' in v:
                v['texture'] = fix(v['texture'])
            for layer in v.get('layers', []):
                if 'texture' in layer:
                    layer['texture'] = fix(layer['texture'])
        out = OUT / name.split('/')[-2] / ('zz_pokeserver_fix_' + name.split('/')[-1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(d, indent=1), encoding='utf-8')
        n += 1
        print('보정', out.relative_to(OUT.parents[4]))
    print(n, '개 설정 보정')


if __name__ == '__main__':
    main(*sys.argv[1:])
