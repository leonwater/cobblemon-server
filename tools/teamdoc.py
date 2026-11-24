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
def reward_table():
    """관장별 보상 표: build_league.py의 실제 지급 값(상금 식·사탕·기술머신·기믹 도구)에서 만듦."""
    rows = ['## 관장별 보상', '',
            f'처음 이길 때 한 번만 받음 (클리어한 체육관은 다시 도전 못 함). 상금 = 레벨 제한 × 200원. 만드는 곳: `tools/build_league.py` → `gym/award/N`·`mod/reward/N`.', '',
            '| 순서 | 관장 (타입) | 배지 | 레벨 제한 | 상금 | 경험사탕 | 기술머신 | 기믹 도구 (이때부터 장신구 칸에 낌) |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for n, g in enumerate(L.GYMS, 1):
        cap = max(m['level'] for m in g[5]) + L.CAP
        rows.append(f"| {n} | {g[1]} ({g[2]}) | {g[3]} | {cap} | {cap * 200:,}원 | {it('cobblemon:' + L.CANDY[n - 1])} {L.CANDY_N}개 | "
                    f"{mv(L.GYM_TM[g[2]])} | {L.KEY_ITEMS[n][1] if n in L.KEY_ITEMS else '-'} |")
    rows += ['| 사천왕 | 성호·난천·단델·레드 (4명 연속) | 명예의 전당 | 100 | 30,000원 | 이상한사탕 10개 | - | 특성패치 1개 (기믹 도구 아님) |', '']
    return rows


def it(i):
    ns, n = i.split(':'); return ko.get(f'item.{ns}.{n}', n)
def special(m):
    i, g = m['heldItem'], m.get('gimmicks', {})
    if g.get('dynamax'): return '거다이맥스' if g.get('gmax') else '다이맥스'
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
VERIFIED = [   # 2026-11-21 실제 배틀 기록(-Dpokeserver.gimmicklog=true)
    '- **선봉**: 웅 뿔카노, 강연 폭타, 독수 질뻐기·도나리, 민화 로즈레이드, 레드 잠만보 등 — 에이스가 선봉인 적 없음.',
    '- **Z기술**: 민화 벨로젬이 나오자마자 Z (물타입 상대, 풀 Z = 2배). 윈디는 물타입 상대(반감)라 Z를 안 씀 = 의도대로.',
    '- **메가·다이맥스·테라**: 마티스 라이츄(이전 팀)·레드 리자몽 메가, 민화 덩쿠림보 다이맥스, 레드 이상해꽃 거다이맥스, 레드 잠만보 테라스탈(노말).',
    '- **보상**: 2번째 관장 클리어 → Z링, 4번째 → 메가링 지급 확인. 보상 함수로 경험사탕·기술머신(10만볼트, `cobblemon:tm_move`) 지급 확인.',
    '- **배틀 자리**: 시작하면 도전자가 필드 끝으로, 내 포켓몬은 1초마다 도전자 앞 필드로 옮겨짐 (4칸 실측 확인 후 큰 포켓몬이 가려 7칸으로 조정).']   # 기믹 기록(-Dpokeserver.gimmicklog=true)으로 확인한 결과
GIM = {'M': '메가', 'Z': 'Z', 'D': '다이맥스', 'T': '테라스탈'}
gims = lambda team: '·'.join(('거다이맥스' if k == 'D' and any(m.get('gimmicks', {}).get('gmax') for m in team) else GIM[k]) for k in 'ZMDT' if k in L.gimmicks(team)) or '없음'
st = L.strength()
rank = ['| 순서 | 이름 | 원작 팀 (출처) | 종족값 평균 | 쓰는 기믹 |', '| --- | --- | --- | --- | --- |']
for n, (tid, name, *_, team) in enumerate([(g[0], g[1], g[5]) for g in L.GYMS] + [(e[0], e[1], e[3]) for e in L.ELITE], 1):
    src, final, _ = L.ORIGINAL[tid]
    label = f'관장 {n}' if n <= 8 else f'사천왕 {n - 8}'
    rank.append(f"| {label} | {name} | {', '.join(sp(s) for s in final)} ({src}) | {st[tid]:.1f} | {gims(team)} |")
L_ = ['# 관장·사천왕', '',
      '관장·사천왕에 관한 문서는 이것 하나입니다. `tools/build_league.py`의 데이터로 `tools/teamdoc.py`가 만듭니다 (최신 정보만).', '',
      '## 규칙', '',
      '- **순서** = 같은 레벨 기준으로 약한 쪽부터. 단 2번(마티스)·5번(초련)은 운영자 지정으로 맞바꿈, 레드는 최종 보스로 맨 뒤 고정. 기준은 그 인물의 원작 최종 팀 종족값 합 평균 (아래 표). 원작 팀 = pret 디스어셈블리(파이어레드·하트골드·에메랄드·플래티넘) 트레이너 데이터, 단델은 Bulbapedia 소드실드 공략.',
      '- **실전 세트**: 개체값 모두 31, 기술·특성·성격·노력치·도구는 Smogon 분석 세트(pkmn/smogon data/sets, 포켓몬마다 형식/세트 이름을 `tools/build_league.py` 주석에 적음). 진화의 휘석은 쓰지 않음.',
      '- **팀**: 원작 대표 포켓몬이 절반 이상 (실제로는 모두 원작에 나온 포켓몬이나 그 진화 전후). 레벨이 낮은 관장은 진화 전 모습.',
      '- **레벨 제한** = 다음 상대 에이스(★) 레벨 + 5 (RCT `relativeLevelCap = 5`). 관장 에이스 15·25·…·85 → 제한 20·30·…·90.',
      '- **사천왕**: 성호 → 난천 → 단델 → 레드. 1~3번째 에이스 90, 레드 95 (제한 95 → 100). 4명을 한 번에 이겨야 클리어.',
      '- **선봉**: 에이스(★)를 뺀 나머지 중 배틀마다 무작위.',
      '- **관장이 쓰는 특수 기믹**: Z기술 3번째부터, 메가진화 5번째부터, 다이맥스 7번째부터. 사천왕 1~3번째는 4가지 중 3가지(서로 다른 조합), 레드는 4가지 모두. 팀 안에서 같은 도구는 한 번만. 다이맥스는 거다이맥스가 되는 포켓몬이 있으면 그 포켓몬이 (표에 거다이맥스·다이맥스 따로 표시). 한 포켓몬은 기믹 하나만, 리그 전체에서 같은 포켓몬이 같은 기믹을 두 번 쓰지 않음 (리자몽: 단델 거다이맥스, 레드 메가진화).',
      '- **Z기술**: Z 버전이 있는 공격 기술이 상대에게 1배 이상이면 거의 매번 씀 (반감·무효면 안 씀, `TrainerZMoveMixin`). 메가·다이맥스·테라스탈은 나와서 첫 행동 때 씀.',
      '- **배틀 자리**: 배틀이 시작되면 도전자가 필드 끝 자리로 옮겨져 관장과 마주 봄 → 포켓몬이 가운데 몬스터볼 필드에서 싸움.',
      '- **플레이어**: 2번째 관장을 이기면 Z링, 4번째 메가링, 6번째 다이맥스밴드, 8번째 테라스탈 오브를 받음. 메가진화는 배지 4개, 다이맥스는 6개, 테라스탈은 8개부터 배틀에서 쓸 수 있음. Z기술은 제한 없음 (Z링만 있으면 됨).',
      '- **Z크리스탈**: 야생 포켓몬을 배틀로 이기면 5% 확률로 그 포켓몬 첫 번째 타입의 Z크리스탈을 떨어뜨림.',
      '- 보상: 아래 "관장별 보상" 표.', '',
      *reward_table(),
      '## 배틀 AI가 행동을 고르는 방식 (RCT AI)', '',
      '1. **배틀 시작**: 선봉은 에이스를 뺀 나머지 중 무작위 (`TrainerLeadMixin`). 도전자는 필드 끝 자리로, 내 포켓몬은 1초마다 도전자 앞 7칸 필드로.',
      '2. **매 턴**: 행동할 수 있는지 → 이 포켓몬에 설정된 기믹만 남김(팀당 1번) → 후보(기술×대상, 가방 도구, 교체) 모으기 → 점수 → 최고 점수 근처(여유 0~0.15)에서 무작위.',
      '3. **점수**: 상성 48, 상태이상 8, 능력 변화 6, 체력 6 가중치 (상성은 2배까지만). 종류별 보정: 공격 1.0, 변화기 0.85, 도구 0.85, 교체 0.5 → 공격 위주, 교체는 드묾.',
      '4. **기믹**: 메가진화·다이맥스·테라스탈은 나와서 첫 행동 때 바로. Z기술은 Z가 되는 공격 기술이 상대에게 1배 이상이면 점수 +10이라 거의 매번 쓰고, 반감·무효면 안 씀 (`TrainerZMoveMixin`).',
      '5. **가방**: 관장 고급상처약 2개(배틀당 2번), 사천왕 회복약 2개.',
      '- 점수 세부 계산식은 바이트코드로 가중치·상한까지만 확인 (나머지는 모름).', '',
      '## 순서 근거 (같은 레벨 기준 강함)', ''] + rank + ['',
      '## 실제 배틀 확인', '', *VERIFIED, '']
for n, (tid, name, typ, badge, color, team) in enumerate(L.GYMS, 1):
    L_ += [f'## {n}번째 관장 {name} ({typ}) · {badge} · 레벨 제한 {max(m["level"] for m in team) + L.CAP}', ''] + table(team) + ['']
for k, (tid, name, title, team) in enumerate(L.ELITE, 1):
    L_ += [f'## 사천왕 {k} · {name} ({title})', ''] + table(team) + ['']
(ROOT / 'docs/관장팀.md').write_text('\n'.join(L_), encoding='utf-8')
print('ok')
