"""스폰 광장 건물 안 '포켓몬 상식' NPC: 건물마다 비슷한 주제, 우클릭하면 Cobblemon 대화창으로 설명.
생김새는 RCT 트레이너 스킨. build_world.py 가 위치를 정하고 이 파일의 내용을 씀.
(아이템 이름·배지 수는 Cobblemon 1.8.4와 tools/build_shop.py 상점에 실제로 있는 것만: 성격민트·특성캡슐/패치·비타민·파워 아이템·
 개체값 사탕(하이퍼 트레이닝, 능력 하나 +1)·변함없는돌·경험치 사탕·TM 머신)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'pack/world/datapacks/pokeserver/data/poke'
ASSETS = ROOT / 'mod/src/main/resources/assets/pokeserver'

# 건물: (키, 간판 이름)
BUILDINGS = {
    'academy': '트레이너 아카데미 · 개체값·노력치',
    'nature': '성격 연구소 · 성격·민트·특성',
    'types': '타입 상성 교실',
    'catch': '포획 상담소 · 포획·레벨 제한',
    'evolve': '진화의 사당',
    'dojo': '수련의 도장 · 기술·도구',
}

# (id, 건물, 이름, 역할, RCT 스킨, 쪽들 [(줄1, 줄2), ...])
TIPS = [   # 쪽마다 (줄1, 줄2). §e…§r = 노란색 강조 (중요한 부분만)
    ('iv', 'academy', '노장 트레이너 철수', '개체값', 'veteran_brian_031d', [
        ('§e개체값§r = 포켓몬마다 타고난 능력 (각 능력 §e0~31§r).', '잡을 때 정해지지만 §e개체값 사탕§r으로 1씩 올릴 수 있다네.'),
        ('기력·힘·수비·지식·마음·속도의사탕 (상점: 배지 7개).', '내림 사탕(나약의사탕 등)은 반대로 1씩 내리지.'),
        ('§eM 키§r 상태창의 능력치 쪽에서 확인할 수 있지.', '강한 포켓몬을 원하면 여러 마리를 만나 보게.'),
    ]),
    ('ev', 'academy', '연구원 시우', '노력치', 'scientist_shaun_0453', [
        ('§e노력치§r = 배틀로 쌓이는 훈련 점수예요.', '한 능력 §e최대 252§r, 합계 §e510§r까지.'),
        ('§e비타민§r(맥스업·타우린 등)으로 바로 올리고,', '§e파워 아이템§r을 들면 더 빨리 쌓여요. (상점: 배지 3·4개)'),
    ]),
    ('nature', 'nature', '레이디 미연', '성격', 'lady_melissa_032c', [
        ('§e성격§r에 따라 한 능력 §e+10%§r, 다른 능력 §e-10%§r.', '예: 고집 = 공격↑ 특수공격↓'),
        ('§eM 키§r 상태창에서 성격을 확인하세요.', ''),
    ]),
    ('mint', 'nature', '브리더 지은', '성격민트·특성', 'pokemon_breeder_jennifer_0311', [
        ('§e성격민트§r를 먹이면 능력치 변화가 그 성격대로 바뀌어요.', '상점(배지 6개) 또는 민트 잎으로 제작.'),
        ('§e특성캡슐§r: 보통 특성 두 개 사이를 바꿔요 (배지 5개).', '§e특성패치§r: 숨겨진 특성으로 바꿔요 (배지 8개).'),
    ]),
    ('types', 'types', '선생님 은비', '타입 상성', 'psychic_abigail_0345', [
        ('물 > 불 > 풀 > 물! 유리하면 §e2배§r, 불리하면 §e0.5배§r.', '두 타입 모두 유리하면 §e4배§r.'),
        ('땅은 전기 기술, 고스트는 노말·격투 기술을', '§e받지 않아요§r (효과 없음).'),
    ]),
    ('stab', 'types', '도감 마니아 민혁', '자속 보정', 'pokemaniac_mark_00a2', [
        ('자기 타입과 같은 타입 기술은 위력 §e1.5배§r!', '이걸 §e자속 보정§r이라고 해요.'),
        ('관장은 §e한 타입§r만 써요.', '안내원 화면에서 타입을 보고 상성을 맞춰 가세요.'),
    ]),
    ('catch', 'catch', '등산가 태호', '포획 요령', 'hiker_theodore_043a', [
        ('§eHP를 낮추고§r §e잠듦·마비§r 상태로 만들면 잘 잡혀!', '좋은 볼은 배지를 모을수록 상점에 나와.'),
        ('내 최고 레벨보다 §e5레벨 넘게 높으면§r', '1레벨마다 포획률 §e-5%§r (최저 10%).'),
    ]),
    ('cap', 'catch', '탐험가 하준', '레벨 제한', 'ruin_maniac_harry_0433', [
        ('§e레벨 제한§r보다 높게는 못 키워.', '처음 §e20§r, 체육관을 이길 때마다 §e+10§r!'),
        ('지금 제한은 §eG 메뉴 왼쪽 위§r에서 확인.', '야생 첫 스폰 근처는 §e15레벨 이하§r라 키우기 좋아.'),
    ]),
    ('evolve', 'evolve', '신사 영길', '진화', 'gentleman_jeremy_032d', [
        ('§e레벨·진화의 돌·친밀도·교환§r으로 진화한다네.', '알림이 뜨면 §e상태창에서 진화§r를 누르게.'),
        ('§e변함없는돌§r을 들리면 진화하지 않지.', ''),
    ]),
    ('moves', 'dojo', '격투가 철민', '기술', 'black_belt_hugh_022a', [
        ('기술은 §e4개§r까지! 레벨이 오르면 새로 배운다.', '§eM 키§r 기술 쪽에서 언제든 바꿔 낄 수 있지.'),
        ('예전에 배운 기술도 다시 고를 수 있다.', '§eTM 머신§r에 빈 TM과 재료를 넣으면 기술머신도 만든다.'),
    ]),
    ('items', 'dojo', '마담 레이나', '지닌 도구', 'madame_reina_032e', [
        ('포켓몬에게 §e도구 하나§r를 들릴 수 있어요.', '§e오랭열매§r는 HP가 줄면 알아서 먹어요.'),
        ('§e학습장치§r를 들리면 배틀에 안 나가도', '경험치를 나눠 받아요. (상점: 배지 1개)'),
    ]),
]


def write():
    """NPC 종류·대화·외형 파일을 씀."""
    for tid, _b, name, _role, skin, pages in TIPS:
        (DATA / f'npcs/tip_{tid}.json').write_text(json.dumps({
            'names': [name], 'hitbox': 'player', 'canDespawn': False, 'isInvulnerable': True, 'isMovable': False,
            'isLeashable': False, 'allowProjectileHits': False,
            'interaction': {'type': 'dialogue', 'dialogue': f'poke:tip_{tid}'}}, ensure_ascii=False, indent=2), encoding='utf-8')
        ps = [{'id': f'p{i}', 'speaker': 'npc', 'lines': [l for l in lines if l], 'textColor': 'FFFFFF'} for i, lines in enumerate(pages)]
        ps[-1]['input'] = {'type': 'option', 'vertical': False, 'options': [
            {'text': '고마워요!', 'value': 'bye', 'action': 'q.dialogue.close();'},
            {'text': '처음부터 다시', 'value': 'again', 'action': "q.dialogue.set_page('p0');"}]}
        (DATA / f'dialogues/tip_{tid}.json').write_text(json.dumps({
            'speakers': {'npc': {'face': 'q.npc.face();', 'name': {'type': 'expression', 'expression': 'q.npc.name'}}},
            'pages': ps}, ensure_ascii=False, indent=2), encoding='utf-8')
        (ASSETS / f'bedrock/npcs/variations/tip_{tid}.json').write_text(json.dumps({
            'name': f'poke:tip_{tid}', 'order': 0, 'variations': [
                {'aspects': [], 'layers': [], 'model': 'cobblemon:steve.geo', 'poser': 'cobblemon:standard',
                 'texture': f'rctmod:textures/trainers/single/{skin}.png'}]}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    write()
    print(len(TIPS), 'tip NPCs')
