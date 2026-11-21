"""tools/build_league.py의 팀 → docs/관장팀.md.  사용: python3 tools/teamdoc.py
한국어 이름은 모드팩에 적힌 Cobblemon·Mega Showdown jar의 ko_kr.json에서 읽음 (처음 한 번 받아 tools/.jarcache에 둠)."""
import json, subprocess, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_league as L


def lang(pw, path):
    """pack/mods/<pw>.pw.toml의 jar를 받아(없을 때만) 그 안의 언어 파일을 읽음."""
    t = (ROOT / 'pack/mods' / f'{pw}.pw.toml').read_text()
    name, url = t.split('filename = "')[1].split('"')[0], t.split('url = "')[1].split('"')[0]
    jar = ROOT / 'tools/.jarcache' / name
    if not jar.exists():
        jar.parent.mkdir(exist_ok=True)
        subprocess.run(['curl', '-sfL', '-o', str(jar), url], check=True)
    with zipfile.ZipFile(jar) as z:
        return json.loads(z.read(path).decode('utf-8'))


ko = lang('cobblemon', 'assets/cobblemon/lang/ko_kr.json')
ko.update(lang('cobblemon-mega-showdown', 'assets/mega_showdown/lang/ko_kr.json'))
# Mega Showdown 한국어 사전에 아직 없는 Z-A 메가스톤
ko.update({'item.mega_showdown.excadrite': '몰드류나이트', 'item.mega_showdown.victreebelite': '우츠보트나이트', 'item.mega_showdown.delphoxite': '마폭시나이트'})

sp = lambda s: ko.get(f'cobblemon.species.{s}.name', s)
mv = lambda m: ko.get(f'cobblemon.move.{m}', m)
def it(i):
    ns, n = i.split(':'); return ko.get(f'item.{ns}.{n}', n)
def special(m):
    i, g = m['heldItem'], m.get('gimmicks', {})
    if g.get('dynamax'): return '다이맥스'
    if g.get('tera'): return f"테라스탈 ({ko.get('cobblemon.type.' + g['tera'], g['tera'])})"
    if i.endswith('ium_z'): return 'Z기술'
    if i.startswith('mega_showdown:'): return '메가진화'
    return ''
def table(team):
    out = ['| 포켓몬 | Lv | 지닌 도구 | 기술 | 특수 |', '| --- | --- | --- | --- | --- |']
    for k, m in enumerate(team):
        star = ' ★' if k == len(team) - 1 else ''
        ab = f" (특성 {ko.get('cobblemon.ability.' + m['ability'], m['ability'])})" if m.get('ability') else ''
        out.append(f"| {sp(m['species'])}{star}{ab} | {m['level']} | {it(m['heldItem'])} | {', '.join(mv(x) for x in m['moveset'])} | {special(m)} |")
    return out
VERIFIED = ['- 아직 확인 전.']   # 기믹 기록(-Dpokeserver.gimmicklog=true)으로 확인한 결과
GIM = {'M': '메가', 'Z': 'Z', 'D': '다이맥스', 'T': '테라스탈'}
gims = lambda team: '·'.join(GIM[k] for k in 'ZMDT' if k in L.gimmicks(team)) or '없음'
st = L.strength()
rank = ['| 순서 | 이름 | 원작 팀 (출처) | 종족값 평균 | 쓰는 기믹 |', '| --- | --- | --- | --- | --- |']
for n, (tid, name, *_, team) in enumerate([(g[0], g[1], g[5]) for g in L.GYMS] + [(e[0], e[1], e[3]) for e in L.ELITE], 1):
    src, final, _ = L.ORIGINAL[tid]
    label = f'관장 {n}' if n <= 8 else f'사천왕 {n - 8}'
    rank.append(f"| {label} | {name} | {', '.join(sp(s) for s in final)} ({src}) | {st[tid]:.1f} | {gims(team)} |")
L_ = ['# 관장·사천왕 팀 (v3, 지금 서버)', '',
      '`tools/build_league.py`가 만든 팀입니다 (이 문서도 같은 데이터로 만듦). 이전 팀은 `docs/관장팀_v1.md`.', '',
      '## 규칙', '',
      '- **순서** = 같은 레벨 기준으로 약한 쪽부터. 기준은 그 인물의 원작 최종 팀 종족값 합 평균 (아래 표). 원작 팀 = pret 디스어셈블리(파이어레드·하트골드·에메랄드·플래티넘) 트레이너 데이터, 단델은 Bulbapedia 소드실드 공략.',
      '- **팀**: 원작 대표 포켓몬이 절반 이상 (실제로는 모두 원작에 나온 포켓몬이나 그 진화 전후). 레벨이 낮은 관장은 진화 전 모습.',
      '- **레벨 제한** = 다음 상대 에이스(★) 레벨 + 5 (RCT `relativeLevelCap = 5`). 관장 에이스 15·25·…·85 → 제한 20·30·…·90.',
      '- **사천왕**: 1~3번째 에이스 90, 마지막 95 (제한 95 → 100). 4명을 한 번에 이겨야 클리어.',
      '- **선봉**: 에이스(★)를 뺀 나머지 중 배틀마다 무작위.',
      '- **관장이 쓰는 특수 기믹**: Z기술 3번째부터, 메가진화 5번째부터, 다이맥스 7번째부터. 사천왕 1~3번째는 4가지 중 3가지(서로 다른 조합), 마지막은 4가지 모두. 한 포켓몬은 기믹 하나만.',
      '- **플레이어**: 2번째 관장을 이기면 Z링, 4번째 메가링, 6번째 다이맥스밴드, 8번째 테라스탈 오브를 받음. 메가진화는 배지 4개, 다이맥스는 6개, 테라스탈은 8개부터 배틀에서 쓸 수 있음. Z기술은 제한 없음 (Z링만 있으면 됨).',
      '- **Z크리스탈**: 야생 포켓몬을 배틀로 이기면 5% 확률로 그 포켓몬 첫 번째 타입의 Z크리스탈을 떨어뜨림.',
      '- 상금: 레벨 제한 × 100원 (2,000~9,000원), 사천왕 클리어 10,000원.', '',
      '## 순서 근거 (같은 레벨 기준 강함)', ''] + rank + ['',
      '## 실제 배틀 확인', '', *VERIFIED, '']
for n, (tid, name, typ, badge, color, team) in enumerate(L.GYMS, 1):
    L_ += [f'## {n}번째 관장 {name} ({typ}) · {badge} · 레벨 제한 {max(m["level"] for m in team) + L.CAP}', ''] + table(team) + ['']
for k, (tid, name, title, team) in enumerate(L.ELITE, 1):
    L_ += [f'## 사천왕 {k} · {name} ({title})', ''] + table(team) + ['']
(ROOT / 'docs/관장팀.md').write_text('\n'.join(L_), encoding='utf-8')
print('ok')
