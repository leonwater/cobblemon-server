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
    i = m['heldItem']
    if m.get('gimmicks'): return '거다이맥스'
    if i.endswith('_z'): return 'Z기술'
    if i.startswith('mega_showdown:'): return '메가진화'
    return ''
def table(team):
    out = ['| 포켓몬 | Lv | 지닌 도구 | 기술 | 특수 |', '| --- | --- | --- | --- | --- |']
    for k, m in enumerate(team):
        star = ' ★' if k == len(team) - 1 else ''
        ab = f" (특성 {ko.get('cobblemon.ability.' + m['ability'], m['ability'])})" if m.get('ability') else ''
        out.append(f"| {sp(m['species'])}{star}{ab} | {m['level']} | {it(m['heldItem'])} | {', '.join(mv(x) for x in m['moveset'])} | {special(m)} |")
    return out
L_ = ['# 관장·사천왕 팀 (v2, 지금 서버)', '',
      '`tools/build_league.py`가 만든 팀입니다 (이 문서도 같은 데이터로 만듦). 이전 팀은 `docs/관장팀_v1.md`.', '',
      '## 규칙', '',
      '- **레벨 제한** = 다음 상대 에이스(★) 레벨 + 5 (RCT `relativeLevelCap = 5`). 관장 에이스 15·25·…·85 → 제한 20·30·…·90.',
      '- **사천왕**: 성호·단델·난천 에이스 90, 마지막 레드 95 (제한 95 → 100). 4명을 한 번에 이겨야 클리어.',
      '- **모든 포켓몬이 지닌 도구**를 가짐 (메가스톤·Z크리스탈 포함).',
      '- **관장이 쓰는 특수 기믹**: 메가진화는 4번째 관장부터, Z기술은 7번째부터, 사천왕은 거다이맥스도.',
      '- **플레이어가 배틀에서 쓸 수 있는 때**: 메가진화 배지 3개, Z기술 배지 6개, 다이맥스·거다이맥스 배지 8개, 테라스탈 사천왕 클리어.',
      '- 상금: 레벨 제한 × 100원 (2,000~9,000원), 사천왕 클리어 10,000원.', '',
      '## 실제 배틀 확인 (2026-11-21, 기믹 기록 근거)', '',
      '- **메가진화 9/9 발동**: 우츠보트·독침붕·후딘·헬가·몰드류·메타그로스·마폭시·한카리아스·리자몽(Y).',
      '- **거다이맥스 4/4 발동**: 대왕끼리동·리자몽·두랄루돈·이상해꽃.',
      '- **Z기술**: 6마리 모두 쓸 수 있는 상태로 전달됨. 실제 사용은 RCT AI가 그 턴에 가장 좋다고 판단할 때만 → 보스로라·피카츄는 사용, 윈디·거대코뿌리·에이스번·망나뇽은 시험 상대(물타입 가이오가)에게 상성이 나빠 다른 기술을 고름.',
      '- **플레이어**: 메가진화(뮤츠)·Z기술(물Z)·다이맥스·테라스탈 모두 배틀 중 사용 후 배틀이 끝까지 정상 진행.', '']
for n, (tid, name, typ, badge, color, team) in enumerate(L.GYMS, 1):
    L_ += [f'## {n}번째 관장 {name} ({typ}) · {badge} · 레벨 제한 {max(m["level"] for m in team) + L.CAP}', ''] + table(team) + ['']
for k, (tid, name, title, team) in enumerate(L.ELITE, 1):
    L_ += [f'## 사천왕 {k} · {name} ({title})', ''] + table(team) + ['']
(ROOT / 'docs/관장팀.md').write_text('\n'.join(L_), encoding='utf-8')
print('ok')
