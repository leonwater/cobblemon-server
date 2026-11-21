"""스폰 광장 건물 안 '포켓몬 상식' NPC: 건물마다 비슷한 주제, 우클릭하면 Cobblemon 대화창으로 설명.
생김새는 RCT 트레이너 스킨. build_world.py 가 위치를 정하고 이 파일의 내용을 씀.
(아이템 이름은 Cobblemon 1.8.4에 실제로 있는 것만. 배지 개수 같은 서버 조건은 적지 않음: 성격민트·특성캡슐/패치·비타민·파워 아이템·
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
TIPS = [   # 쪽마다 (줄1, 줄2). §e…§r = 노란색 강조. 인물 말투대로, 배지 개수 같은 서버 조건은 적지 않음
    ('iv', 'academy', '노장 트레이너 철수', '개체값', 'veteran_brian_031d', [
        ('§e개체값§r은 포켓몬이 타고난 재능이라네.', '능력마다 §e0에서 31§r까지 있지.'),
        ('§eM 키§r 상태창의 능력치 쪽을 보면 알 수 있다네.', '아쉬우면 §e개체값 사탕§r으로 조금씩 올려 주게.'),
    ]),
    ('ev', 'academy', '연구원 시우', '노력치', 'scientist_shaun_0453', [
        ('§e노력치§r는 배틀로 쌓이는 훈련의 결과예요.', '한 능력에 §e252§r, 모두 합쳐 §e510§r까지 쌓여요.'),
        ('§e비타민§r이나 §e날개§r로 바로 올릴 수도 있고요,', '§e파워 도구§r를 들려 두면 훨씬 빨리 쌓인답니다.'),
    ]),
    ('nature', 'nature', '레이디 미연', '성격', 'lady_melissa_032c', [
        ('§e성격§r에 따라 한 능력은 §e10%§r 오르고,', '다른 하나는 §e10%§r 내려간답니다.'),
        ('고집이라면 공격은 오르고 특수공격은 내려가지요.', '§eM 키§r 상태창에서 확인해 보세요.'),
    ]),
    ('mint', 'nature', '브리더 지은', '성격민트·특성', 'pokemon_breeder_jennifer_0311', [
        ('성격이 마음에 안 들면 §e민트§r를 먹여 보세요!', '능력치가 그 성격대로 바뀌어요.'),
        ('§e특성캡슐§r은 다른 보통 특성으로,', '§e특성패치§r는 숨겨진 특성으로 바꿔 줘요.'),
    ]),
    ('types', 'types', '선생님 은비', '타입 상성', 'psychic_abigail_0345', [
        ('물은 불에, 불은 풀에, 풀은 물에 강해요.', '유리하면 §e2배§r, 불리하면 §e절반§r이에요.'),
        ('두 타입 모두 유리하면 무려 §e4배§r!', '땅에는 전기가, 고스트에는 노말·격투가 §e안 통해요§r.'),
    ]),
    ('stab', 'types', '도감 마니아 민혁', '자속 보정', 'pokemaniac_mark_00a2', [
        ('자기 타입과 같은 기술은 위력이 §e1.5배§r나 돼요!', '이걸 §e자속 보정§r이라고 하거든요.'),
        ('관장님들은 §e한 타입§r만 쓰거든요.', '상성이 맞는 포켓몬을 데려가세요!'),
    ]),
    ('catch', 'catch', '등산가 태호', '포획 요령', 'hiker_theodore_043a', [
        ('§e체력을 깎고§r §e잠재우거나 마비§r시키면 훨씬 잘 잡혀!', '좋은 볼을 쓰면 더 좋고!'),
        ('내 포켓몬보다 레벨이 한참 높은 녀석은', '잘 안 잡히더라고. 차근차근 키워서 가!'),
    ]),
    ('cap', 'catch', '탐험가 하준', '레벨 제한', 'ruin_maniac_harry_0433', [
        ('§e체육관 배지§r를 모을수록', '포켓몬을 더 높은 레벨까지 키울 수 있어.'),
        ('지금 키울 수 있는 레벨은 §eG 메뉴§r에서 봐.', '광장 근처엔 약한 녀석들이 많으니 거기서부터 시작해!'),
    ]),
    ('evolve', 'evolve', '신사 영길', '진화', 'gentleman_jeremy_032d', [
        ('포켓몬은 §e레벨·진화의 돌·친밀도·교환§r으로', '진화하지요.'),
        ('때가 되면 알림이 뜬다오. §e상태창§r에서 진화시키시오.', '진화를 막고 싶다면 §e변함없는돌§r을 들려 두시오.'),
    ]),
    ('moves', 'dojo', '격투가 철민', '기술', 'black_belt_hugh_022a', [
        ('기술은 §e넷§r까지! 레벨이 오르면 새 기술을 배운다.', '§eM 키§r 상태창에서 언제든 바꿔 낄 수 있다.'),
        ('예전에 배운 기술도 다시 고를 수 있다.', '§e기술머신§r으로 새 기술도 가르칠 수 있지. 상대에 맞춰 바꿔라!'),
    ]),
    ('items', 'dojo', '마담 레이나', '지닌 도구', 'madame_reina_032e', [
        ('포켓몬에게 §e도구 하나§r를 들려 줄 수 있어요.', '§e오랭열매§r는 체력이 줄면 스스로 먹는답니다.'),
        ('§e학습장치§r를 들려 두면 배틀에 나가지 않아도', '경험치를 나눠 받아요.'),
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
