"""스폰 광장 건물 안 '포켓몬 상식' NPC: 건물마다 비슷한 주제, 우클릭하면 Cobblemon 대화창으로 설명.
생김새는 RCT 트레이너 스킨. build_world.py 가 위치를 정하고 이 파일의 내용을 씀.
(아이템 이름은 Cobblemon 1.8.4에 실제로 있는 것만: 성격민트·특성캡슐/패치·비타민·파워 아이템·노력치 열매·변함없는돌·경험치 사탕)
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
TIPS = [
    ('iv', 'academy', '노장 트레이너 철수', '개체값', 'veteran_brian_031d', [
        ('허허, 같은 종이라도 포켓몬마다 타고난 능력이 조금씩 다르다네.', '그걸 "개체값"이라고 하지.'),
        ('개체값은 HP·공격·방어·특수공격·특수방어·스피드', '여섯 능력마다 0부터 31까지 정해져 있어.'),
        ('잡거나 태어나는 순간 정해지고, 레벨을 올려도 바뀌지 않는다네.', '그래서 강한 포켓몬을 원하면 여러 마리를 만나 보는 게 좋지.'),
        ('M 키로 상태창을 열고 능력치 쪽을 보면', '개체값과 노력치를 그래프로 확인할 수 있다네.'),
    ]),
    ('ev', 'academy', '연구원 시우', '노력치', 'scientist_shaun_0453', [
        ('노력치는 배틀로 쌓이는 "훈련 점수"예요.', '쓰러뜨린 포켓몬 종류에 따라 정해진 능력이 올라가요.'),
        ('한 능력은 최대 252, 모든 능력을 합쳐 510까지 쌓여요.', '4 노력치마다 레벨 100 기준 능력치가 1씩 올라요.'),
        ('비타민(HP업·타우린·사포닌·리보플라빈·키토산·알칼로이드)을', '먹이면 해당 노력치를 바로 올릴 수 있어요.'),
        ('파워웨이트 같은 파워 아이템을 들고 싸우면 노력치가 더 쌓이고,', '유석열매 같은 열매는 노력치를 줄여 줘서 다시 분배할 수 있어요.'),
    ]),
    ('nature', 'nature', '레이디 미연', '성격', 'lady_melissa_032c', [
        ('포켓몬에게는 25가지 성격이 있어요.', '대부분 한 능력이 10% 오르고 다른 능력이 10% 내려가요.'),
        ('예를 들어 "고집"은 공격↑ 특수공격↓, "겁쟁이"는 스피드↑ 공격↓.', '노력·온순처럼 아무 변화가 없는 성격도 있어요.'),
        ('상태창(M 키)에서 성격과 능력치를 확인할 수 있어요.', '성격에 맞춰 기술과 역할을 정해 주면 더 강해져요.'),
    ]),
    ('mint', 'nature', '브리더 지은', '성격민트·특성', 'pokemon_breeder_jennifer_0311', [
        ('성격이 마음에 안 들면 "성격민트"를 먹여 보세요!', '먹이면 능력치 변화가 그 민트의 성격처럼 바뀌어요.'),
        ('민트는 민트 잎으로 만들고,', '민트 잎은 민트 씨앗을 심어 키우면 얻을 수 있어요.'),
        ('"특성캡슐"은 보통 특성 두 개 사이를 바꿔 주고,', '"특성패치"는 숨겨진 특성으로 바꿔 줘요.'),
    ]),
    ('types', 'types', '선생님 은비', '타입 상성', 'psychic_abigail_0345', [
        ('기술과 포켓몬에는 타입이 있어요. 기본은 가위바위보!', '물은 불에, 불은 풀에, 풀은 물에 강해요.'),
        ('"효과가 굉장했다"는 2배, "별로인 듯하다"는 0.5배예요.', '두 타입 모두에 강하면 4배까지 들어가요.'),
        ('효과가 없는 조합도 있어요.', '땅 타입은 전기 기술을, 고스트 타입은 노말·격투 기술을 받지 않아요.'),
    ]),
    ('stab', 'types', '도감 마니아 민혁', '자속 보정', 'pokemaniac_mark_00a2', [
        ('포켓몬이 자기 타입과 같은 타입의 기술을 쓰면 위력이 1.5배!', '이걸 "자속 보정"이라고 해요.'),
        ('체육관 관장은 한 가지 타입을 써요.', '도전하기 전에 안내원 화면에서 타입을 확인하고 상성을 맞춰 가세요!'),
    ]),
    ('catch', 'catch', '등산가 태호', '포획 요령', 'hiker_theodore_043a', [
        ('포켓몬을 잘 잡으려면 HP를 낮추고 상태이상을 걸어!', '잠듦·얼음이 가장 잘 잡히고, 마비·독·화상도 도움이 돼.'),
        ('슈퍼볼·하이퍼볼처럼 좋은 볼일수록 잘 잡혀.', '좋은 볼은 배지를 모을수록 상점에 나와.'),
        ('이 서버에선 내 파티 최고 레벨보다 5레벨 넘게 높은 포켓몬은', '1레벨마다 잡을 확률이 5%씩 떨어져 (최저 10%). 조심해!'),
    ]),
    ('cap', 'catch', '탐험가 하준', '레벨 제한', 'ruin_maniac_harry_0433', [
        ('포켓몬은 "레벨 제한"보다 높게 키울 수 없어.', '처음엔 20, 체육관을 이길 때마다 10씩 올라가!'),
        ('지금 내 레벨 제한은 G 키 메인 메뉴 위쪽에서 볼 수 있어.', '관장의 권장 레벨도 레벨 제한과 같아.'),
        ('경험치 사탕을 먹이면 배틀 없이도 경험치를 얻을 수 있어.', '야생 첫 스폰 근처는 15레벨 이하라 처음 키우기 좋아!'),
    ]),
    ('evolve', 'evolve', '신사 영길', '진화', 'gentleman_jeremy_032d', [
        ('진화하는 방법은 여러 가지라네.', '레벨을 올리거나, 진화의 돌을 쓰거나, 친밀도를 높이거나, 교환하는 식이지.'),
        ('진화할 수 있게 되면 알림이 뜨고,', '상태창에서 진화를 눌러야 진화한다네. 원하지 않으면 미뤄도 되지.'),
        ('"변함없는돌"을 들려 두면 진화하지 않는다네.', '진화 전 모습이 좋다면 써 보게.'),
    ]),
    ('moves', 'dojo', '격투가 철민', '기술', 'black_belt_hugh_022a', [
        ('포켓몬은 레벨이 오르면 새 기술을 배워! 한 번에 4개까지 쓸 수 있지.', '상태창(M 키)의 기술 쪽에서 언제든 바꿔 낄 수 있다.'),
        ('예전에 배운 기술도 그 목록에서 다시 고를 수 있어.', '상대 타입에 맞춰 기술을 바꿔 가며 싸워라!'),
    ]),
    ('items', 'dojo', '마담 레이나', '지닌 도구', 'madame_reina_032e', [
        ('포켓몬에게 도구를 하나 들게 할 수 있어요.', '상태창에서 도구 칸을 눌러 들려 줄 수 있어요.'),
        ('오랭열매·자뭉열매는 HP가 줄면 스스로 먹고 회복해요.', '나무열매는 농장에서 길러 쓸 수도 있답니다.'),
        ('학습장치를 지니게 하면 배틀에 나가지 않은 포켓몬도', '경험치를 나눠 받아요. 상점에서 살 수 있어요.'),
    ]),
]


def write():
    """NPC 종류·대화·외형 파일을 씀."""
    for tid, _b, name, _role, skin, pages in TIPS:
        (DATA / f'npcs/tip_{tid}.json').write_text(json.dumps({
            'names': [name], 'hitbox': 'player', 'canDespawn': False, 'isInvulnerable': True, 'isMovable': False,
            'isLeashable': False, 'allowProjectileHits': False,
            'interaction': {'type': 'dialogue', 'dialogue': f'poke:tip_{tid}'}}, ensure_ascii=False, indent=2), encoding='utf-8')
        ps = [{'id': f'p{i}', 'speaker': 'npc', 'lines': list(lines), 'textColor': 'FFFFFF'} for i, lines in enumerate(pages)]
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
