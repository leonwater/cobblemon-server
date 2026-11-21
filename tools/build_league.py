"""포켓서버 리그(배지 체육관 8 + 사천왕 4) 데이터 생성기 — Radical Cobblemon Trainers(RCT) 형식.

RCT에 이미 있는 관장·사천왕 ID를 덮어써서, RCT의 원작 캐릭터 스킨은 그대로 쓰고 팀·레벨·순서만 우리 것으로 바꿈.
사용: python3 tools/build_league.py   (채팅용 체육관 정보도 출력)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'pack/world/datapacks/pokeserver/data'
SERIES = 'pokeserver'


def mon(species, level, moves, item, gmax=False, ability=None):
    """item: 지닌 도구 (메가스톤·Z크리스탈이면 그 기믹을 씀). gmax: 거다이맥스."""
    m = {'species': species, 'level': level, 'moveset': moves, 'heldItem': item if ':' in item else 'cobblemon:' + item}
    if gmax:
        m['gimmicks'] = {'dynamax': True, 'gmax': True}
    if ability:
        m['ability'] = ability
    return m


MS = 'mega_showdown:'
# v2 (관장팀 v2 문서, v1은 tools/league_v1.json): 관장 에이스 = 레벨 제한 - 5 (RCT relativeLevelCap 5 → 제한 20, 30, …, 90),
# 메가진화는 4번째 관장부터, Z기술은 7번째부터, 사천왕은 거다이맥스도. 4번째부터 약점 견제 1마리, 7번째부터 3마리. 모든 포켓몬이 도구를 지님.
# (RCT ID, 이름, 타입, 배지 이름, 배지 색, 팀)
GYMS = [
    ('leader_brock_019e', '웅', '바위', '회색배지', (150, 150, 155), [
        mon('geodude', 13, ['tackle', 'defensecurl', 'rockthrow', 'rollout'], 'hard_stone'),
        mon('rhyhorn', 13, ['hornattack', 'stomp', 'rockblast', 'tailwhip'], 'eviolite'),
        mon('onix', 15, ['rocktomb', 'bind', 'dragonbreath', 'harden'], 'sitrus_berry')]),
    ('leader_misty_019f', '이슬', '물', '블루배지', (60, 120, 230), [
        mon('staryu', 22, ['waterpulse', 'rapidspin', 'swift', 'recover'], 'eviolite'),
        mon('psyduck', 23, ['waterpulse', 'confusion', 'scratch', 'disable'], 'sitrus_berry'),
        mon('horsea', 23, ['bubblebeam', 'smokescreen', 'dragonbreath', 'twister'], 'mystic_water'),
        mon('starmie', 25, ['bubblebeam', 'psybeam', 'swift', 'recover'], 'life_orb')]),
    ('leader_lt_surge_01a0', '마티스', '전기', '오렌지배지', (240, 150, 40), [
        mon('electrode', 32, ['spark', 'screech', 'swift', 'selfdestruct'], 'focus_sash'),
        mon('magneton', 33, ['spark', 'thunderwave', 'flashcannon', 'triattack'], 'eviolite'),
        mon('electabuzz', 33, ['thunderpunch', 'quickattack', 'lowkick', 'lightscreen'], 'eviolite'),
        mon('pikachu', 33, ['thunderbolt', 'quickattack', 'irontail', 'doubleteam'], 'light_ball'),
        mon('raichu', 35, ['thunderbolt', 'quickattack', 'irontail', 'thunderwave'], 'magnet')]),
    ('leader_erika_01a1', '민화', '풀', '무지개배지', (120, 200, 90), [
        mon('tangela', 42, ['gigadrain', 'ancientpower', 'sleeppowder', 'slam'], 'eviolite'),
        mon('vileplume', 43, ['petaldance', 'sludgebomb', 'sleeppowder', 'moonblast'], 'black_sludge'),
        mon('ludicolo', 43, ['gigadrain', 'surf', 'icebeam', 'raindance'], 'damp_rock'),
        mon('bellossom', 43, ['petalblizzard', 'moonblast', 'quiverdance', 'gigadrain'], 'leftovers'),
        mon('victreebel', 45, ['leafblade', 'sludgebomb', 'sleeppowder', 'suckerpunch'], MS + 'victreebelite')]),
    ('leader_koga_01a2', '독수', '독', '핑크배지', (240, 120, 180), [
        mon('muk', 52, ['gunkshot', 'poisonjab', 'minimize', 'toxic'], 'black_sludge'),
        mon('venomoth', 53, ['bugbuzz', 'sludgebomb', 'sleeppowder', 'psychic'], 'wise_glasses'),
        mon('weezing', 53, ['sludgebomb', 'toxic', 'willowisp', 'explosion'], 'rocky_helmet', ability='levitate'),
        mon('crobat', 54, ['crosspoison', 'airslash', 'confuseray', 'uturn'], 'poison_barb'),
        mon('beedrill', 55, ['poisonjab', 'xscissor', 'drillrun', 'uturn'], MS + 'beedrillite')]),
    ('leader_sabrina_01a4', '초련', '에스퍼', '골드배지', (240, 200, 60), [
        mon('hypno', 62, ['psychic', 'hypnosis', 'dreameater', 'nastyplot'], 'twisted_spoon'),
        mon('jynx', 62, ['psychic', 'icebeam', 'lovelykiss', 'nastyplot'], 'never_melt_ice'),
        mon('slowking', 63, ['psychic', 'surf', 'icebeam', 'slackoff'], 'leftovers'),
        mon('mrmime', 63, ['psychic', 'dazzlinggleam', 'reflect', 'lightscreen'], 'light_clay'),
        mon('alakazam', 65, ['psychic', 'shadowball', 'focusblast', 'calmmind'], MS + 'alakazite')]),
    ('leader_blaine_01a3', '강연', '불꽃', '크림슨배지', (210, 50, 50), [
        mon('rapidash', 72, ['flareblitz', 'bounce', 'agility', 'poisonjab'], 'charcoal_stick'),
        mon('arcanine', 73, ['flareblitz', 'extremespeed', 'crunch', 'wildcharge'], MS + 'firium_z'),
        mon('camerupt', 73, ['earthpower', 'lavaplume', 'rockslide', 'yawn'], 'soft_sand'),
        mon('volcarona', 73, ['fierydance', 'bugbuzz', 'gigadrain', 'quiverdance'], 'lum_berry'),
        mon('charizard', 73, ['flamethrower', 'airslash', 'dragonpulse', 'solarbeam'], 'life_orb'),
        mon('houndoom', 75, ['flamethrower', 'darkpulse', 'sludgebomb', 'nastyplot'], MS + 'houndoominite')]),
    ('leader_giovanni_015e', '비주기', '땅', '그린배지', (70, 170, 80), [
        mon('dugtrio', 82, ['earthquake', 'stoneedge', 'suckerpunch', 'slash'], 'focus_sash'),
        mon('nidoking', 83, ['earthpower', 'sludgewave', 'thunderbolt', 'icebeam'], 'life_orb'),
        mon('rhyperior', 83, ['earthquake', 'stoneedge', 'megahorn', 'icepunch'], MS + 'groundium_z'),
        mon('swampert', 83, ['earthquake', 'waterfall', 'icepunch', 'stealthrock'], 'leftovers'),
        mon('steelix', 83, ['earthquake', 'ironhead', 'stoneedge', 'dragontail'], 'rocky_helmet'),
        mon('excadrill', 85, ['earthquake', 'ironhead', 'rockslide', 'swordsdance'], MS + 'excadrite')]),
]

# 사천왕 = 역대 챔피언 4명, 타입 하나씩 (약한 순서로 도전). 마지막(레드) 에이스 95, 나머지 90 → 레벨 제한 95·100.
# 단델·성호는 RCT에 없어 새 ID + 우리 스킨. (RCT ID, 이름, 칭호, 팀)
ELITE = [
    ('champion_steven_ps', '성호', '강철 · 호연 챔피언', [
        mon('skarmory', 87, ['bravebird', 'ironhead', 'spikes', 'roost'], 'rocky_helmet'),
        mon('scizor', 87, ['bulletpunch', 'xscissor', 'uturn', 'swordsdance'], 'life_orb'),
        mon('magnezone', 87, ['thunderbolt', 'flashcannon', 'voltswitch', 'thunderwave'], 'magnet'),
        mon('aggron', 88, ['heavyslam', 'stoneedge', 'earthquake', 'ironhead'], MS + 'steelium_z'),
        mon('copperajah', 88, ['heavyslam', 'superpower', 'playrough', 'stealthrock'], 'leftovers', gmax=True),
        mon('metagross', 90, ['meteormash', 'zenheadbutt', 'earthquake', 'bulletpunch'], MS + 'metagrossite')]),
    ('champion_leon_ps', '단델', '불꽃 · 가라르 챔피언', [
        mon('coalossal', 87, ['flamethrower', 'stoneedge', 'stealthrock', 'rapidspin'], 'heavy_duty_boots'),
        mon('centiskorch', 87, ['firelash', 'leechlife', 'powerwhip', 'coil'], 'sitrus_berry'),
        mon('torkoal', 87, ['lavaplume', 'earthpower', 'solarbeam', 'stealthrock'], 'heat_rock', ability='drought'),
        mon('cinderace', 88, ['pyroball', 'highjumpkick', 'uturn', 'suckerpunch'], MS + 'firium_z'),
        mon('delphox', 88, ['mysticalfire', 'psychic', 'shadowball', 'nastyplot'], MS + 'delphoxite'),
        mon('charizard', 90, ['flareblitz', 'airslash', 'dragonpulse', 'solarbeam'], 'life_orb', gmax=True)]),
    ('champion_cynthia_03a5', '난천', '드래곤 · 신오 챔피언', [
        mon('flygon', 87, ['earthquake', 'dragonclaw', 'uturn', 'firepunch'], 'choice_scarf'),
        mon('kingdra', 87, ['hydropump', 'dracometeor', 'icebeam', 'raindance'], 'damp_rock'),
        mon('goodra', 87, ['dracometeor', 'sludgebomb', 'thunderbolt', 'fireblast'], 'assault_vest'),
        mon('dragonite', 88, ['outrage', 'extremespeed', 'earthquake', 'dragondance'], MS + 'dragonium_z'),
        mon('duraludon', 88, ['dracometeor', 'flashcannon', 'thunderbolt', 'bodypress'], 'expert_belt', gmax=True),
        mon('garchomp', 90, ['earthquake', 'dragonclaw', 'stoneedge', 'swordsdance'], MS + 'garchompite')]),
    ('trainer_red_0003', '레드', '관동 전설의 챔피언', [
        mon('pikachu', 92, ['volttackle', 'irontail', 'quickattack', 'thunderbolt'], MS + 'pikanium_z'),
        mon('espeon', 92, ['psychic', 'shadowball', 'dazzlinggleam', 'morningsun'], 'twisted_spoon'),
        mon('snorlax', 93, ['bodyslam', 'crunch', 'rest', 'sleeptalk'], 'leftovers'),
        mon('blastoise', 93, ['hydropump', 'icebeam', 'flashcannon', 'aurasphere'], 'assault_vest'),
        mon('venusaur', 93, ['solarbeam', 'sludgebomb', 'earthquake', 'sleeppowder'], 'black_sludge', gmax=True),
        mon('charizard', 95, ['flareblitz', 'airslash', 'dragonpulse', 'solarbeam'], MS + 'charizardite_y')]),
]
CAP = 5   # RCT relativeLevelCap: 레벨 제한 = 다음 상대 에이스 + 5


def COOLDOWN(n):
    """12. 관장·사천왕에게 지면 5분(6000틱) 뒤에 다시 도전 (gym/lose가 poke.gymcd에 다시 도전 가능 시각을 적음)."""
    return ['execute store result score #now poke.gymcd run time query gametime',
            f'execute if score @s poke.gymcd > #now poke.gymcd run return run function poke:gym/deny/{n} '
            '{msg:"관장에게 진 뒤 5분 동안은 다시 도전할 수 없어요."}']


def validate():
    """팀 검사: 기술을 그 포켓몬이 배울 수 있는지 (Cobblemon 종 데이터, COBBLEMON_SPECIES 폴더가 있을 때만)."""
    import os
    root = os.environ.get('COBBLEMON_SPECIES')
    if not root:
        return
    learn, bst = {}, {}
    for f in Path(root).rglob('*.json'):
        d = json.loads(f.read_text(encoding='utf-8'))
        learn[f.stem] = {m.split(':', 1)[1] for m in d.get('moves', [])}
        bst[f.stem] = sum(d.get('baseStats', {}).values())
    bad = []
    for team in [g[5] for g in GYMS] + [e[3] for e in ELITE]:
        for m in team:
            if m['species'] not in learn:
                bad.append(f"{m['species']}: 종 없음")
                continue
            bad += [f"{m['species']}: {mv}" for mv in m['moveset'] if mv not in learn[m['species']]]
    assert not bad, '배울 수 없는 기술: ' + ', '.join(bad)
    caps = [max(m['level'] for m in g[5]) + CAP for g in GYMS]
    assert caps == [20, 30, 40, 50, 60, 70, 80, 90], caps
    assert [max(m['level'] for m in e[3]) for e in ELITE] == [90, 90, 90, 95]
    for team in [g[5] for g in GYMS] + [e[3] for e in ELITE]:   # 에이스(마지막)가 가장 높고, 모두 도구를 지님
        assert team[-1]['level'] == max(m['level'] for m in team) and all(m['heldItem'] for m in team)


def text(s):
    return {'literal': s}


def write(path, obj):
    p = DATA / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')


def trainer(tid, name, title, team, kind, required, max_defeats):
    write(f'rctmod/trainers/{tid}.json', {
        'name': name, 'identity': f'{title} {name}', 'ai': {'type': 'rct', 'data': {'maxSelectMargin': 0.15}},
        'battleRules': {'maxItemUses': 2 if kind == 'leader' else 3},
        'bag': [{'item': 'cobblemon:hyper_potion' if kind == 'leader' else 'cobblemon:full_restore', 'quantity': 2}],
        'team': team})
    write(f'rctmod/mobs/trainers/single/{tid}.json', {
        'type': kind, 'series': [SERIES], 'requiredDefeats': required, 'optional': False,
        'maxTrainerDefeats': max_defeats, 'maxTrainerWins': -1, 'battleCooldownTicks': 100,
        'spawnWeightFactor': 0.0, 'biomeTagBlacklist': [], 'biomeTagWhitelist': [], 'forceBattleOnSight': False,
        'dialog': {
            'on_battle_start': [text(f'{title} {name}: 좋아, 실력을 보여줘!')],
            'on_battle_won': [text(f'{title} {name}: 아직 멀었어. 다시 도전해!')],
            'on_battle_lost': [text(f'{title} {name}: 훌륭해! 네가 이겼어.')],
            'missing_required_trainer': [text('앞 체육관의 배지를 먼저 모아 와!')],
            'missing_required_trainer_leader': [text('앞 체육관의 배지를 먼저 모아 와!')],
            'missing_required_trainer_e4': [text('사천왕은 순서대로 이겨야 해!')],
            'over_level_cap': [text('네 포켓몬 레벨이 너무 높아! 레벨 제한을 지켜 줘.')],
            'missing_pokemon': [text('싸울 수 있는 포켓몬이 없잖아!')],
        }})


def main():
    validate()
    write(f'rctmod/series/{SERIES}.json', {
        'title': text('포켓서버 리그'), 'description': text('배지 8개를 모은 뒤 사천왕을 한 번에 모두 이겨라'),
        'difficulty': 3, 'requiredSeries': [], 'initialLevelCap': 20})
    info = []
    prev = None
    for i, (tid, name, typ, badge, _, team) in enumerate(GYMS, 1):
        # 배지 체육관: 앞 관장을 이겨야 도전 가능, 한 번 이기면 다시 못 이김
        trainer(tid, name, '관장', team, 'leader', [[prev]] if prev else [], 1)
        info.append((f'{i}번 체육관 · {typ} · 관장 {name} · {badge}', team))
        prev = tid
    for i, (tid, name, typ, team) in enumerate(ELITE, 1):
        # 사천왕: 8번째 관장을 이겨야 도전. 다시 도전할 수 있어야 해서(한 번에 4연승 규칙) 횟수 제한 없음
        trainer(tid, name, '사천왕', team, 'e4', [[GYMS[-1][0]]], -1)
        info.append((f'사천왕 {i} · {typ} · {name}', team))
    for title, team in info:
        print(f'\n■ {title}  (팀 최고 레벨 {max(m["level"] for m in team)})')
        for m in team:
            print(f'   - {m["species"]} Lv{m["level"]}: {", ".join(m["moveset"])}')


if __name__ == '__main__':
    main()


# ───────── 체육관 진행(입장·승패·배지) 함수와 배지 아이템 ─────────
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_world as W  # noqa: E402  (체육관 위치는 build_world.py 한 곳에서)

FN = DATA / 'poke/function'
ASSETS = ROOT / 'mod/src/main/resources/assets'
Y = W.G + 1
ARENA_CHUNKS = f'{W.ARENA_X} {W.E4[2]} {W.E4[1]} 18'   # 경기장·사천왕 본부 청크 (관장 소환 때 불러옴)


def fn(path, lines):
    p = FN / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('\n'.join(['# 자동 생성: tools/build_league.py'] + lines) + '\n', encoding='utf-8')


def josa(name):
    """을/를: 마지막 글자에 받침이 있으면 을."""
    c = ord(name[-1]) - 0xAC00
    return '을' if 0 <= c < 11172 and c % 28 else '를'


def tp(pos):
    x, z, yaw = pos
    return f'execute in poke:town run tp @s {x} {Y} {z} {yaw} 0'


def badge_item(n, name, color):
    hexc = '#%02X%02X%02X' % color
    return (f"give @s minecraft:gold_nugget[minecraft:custom_name='{{\"text\":\"{name}\",\"color\":\"{hexc}\",\"italic\":false}}',"
            f"minecraft:lore=['{{\"text\":\"포켓서버 리그 {n}번 체육관 배지\",\"color\":\"gray\",\"italic\":false}}'],"
            f"minecraft:custom_model_data={1000 + n},minecraft:custom_data={{pokeserver:\"badge{n}\"}}] 1")


def prize(amount):
    """상금: 관장은 레벨 제한 × 100원 (2,000~9,000), 사천왕 클리어 10,000원. 돈은 모드 명령이라 mod/prize/<금액> (기본 물품 mod/kit과 같은 방식)."""
    fn(f'mod/prize/{amount}.mcfunction', ['# 자동 생성: tools/build_league.py. 체육관·사천왕 상금',
                                         f'pokeserver money give @s {amount}',
                                         f'tellraw @s {{"text":"상금 {amount:,}원을 받았어요!","color":"gold"}}'])
    return f'function poke:mod/prize/{amount}'


def functions():
    fn('mod/rct_reset.mcfunction', ['# 전체 초기화(/초기화): RCT 진행도를 첫 관장 전으로 → 레벨 제한 20으로',
                                    f'rctmod player set progress @s before {GYMS[0][0]}'])
    pads, win, spawn = [], [], []
    for n, (tid, name, typ, badge, color, _) in enumerate(GYMS, 1):
        g = W.gym_geom(n)
        fn(f'gym/deny/{n}.mcfunction', ['$tellraw @s {"text":"$(msg)","color":"red"}'])
        need = [] if n == 1 else [f'execute unless entity @s[tag=poke.badge{n - 1}] run return run function poke:gym/deny/{n} '
                                  f'{{msg:"{n - 1}번 체육관 배지를 먼저 얻어야 도전할 수 있어요."}}']
        fn(f'gym/try/{n}.mcfunction', [
            f'# {n}번 체육관 도전 (체육관 안내원 화면에서 고름): 순서·재도전·혼자만 도전 확인 후 경기장으로',
            'execute if score @s poke.gym matches 1.. run return 0',
            f'execute unless entity @s[tag=poke.tutorial_done] run return run function poke:gym/deny/{n} {{msg:"튜토리얼을 먼저 끝내 주세요."}}',
            f'execute if entity @s[tag=poke.badge{n}] run return run function poke:gym/deny/{n} {{msg:"이미 이긴 체육관이에요. 다시 도전할 수 없어요."}}',
            *need,
            *COOLDOWN(n),
            f'execute if entity @a[scores={{poke.gym={n}}}] run return run function poke:gym/deny/{n} {{msg:"다른 도전자가 관장과 싸우는 중이에요. 잠시 후 다시 와 주세요."}}',
            f'scoreboard players set @s poke.gym {n}', tp(g['inside']),
            f'title @s title {{"text":"{n}번 체육관","color":"gold"}}',
            f'title @s subtitle {{"text":"{typ} 타입 · 관장 {name}","color":"white"}}',
            'tellraw @s {"text":"관장을 우클릭하면 배틀이 시작돼요. 나가려면 주황 발판을 밟으세요.","color":"gray"}'])
        fn(f'gym/award/{n}.mcfunction', [
            f'tag @s add poke.badge{n}', badge_item(n, badge, color),
            f'title @s title {{"text":"{badge} 획득!","color":"gold"}}',
            f'tellraw @a [{{"text":"[리그] ","color":"gold"}},{{"selector":"@s"}},{{"text":"님이 {n}번째 체육관을 클리어하였습니다! (관장 {name} · {badge})","color":"yellow"}}]',
            prize((max(m['level'] for m in GYMS[n - 1][5]) + CAP) * 100), 'function poke:gym/leave'])
        px, pz, w, d = g['exit']
        pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:gym/leave')
        win.append(f'execute if score @s poke.gym matches {n} run return run function poke:gym/award/{n}')
        lx, lz, lyaw = g['leader']
        spawn += spawn_lines(tid, lx, lz, lyaw)
    e = W.e4_geom()
    fn('gym/deny/9.mcfunction', ['$tellraw @s {"text":"$(msg)","color":"red"}'])
    fn('gym/try/9.mcfunction', [
        '# 사천왕 도전: 배지 8개, 이미 클리어했으면 불가, 한 번에 한 명',
        'execute if score @s poke.gym matches 1.. run return 0',
        'execute if entity @s[tag=poke.e4clear] run return run function poke:gym/deny/9 {msg:"이미 사천왕을 모두 이겼어요. 다시 도전할 수 없어요."}',
        'execute unless entity @s[tag=poke.badge8] run return run function poke:gym/deny/9 {msg:"배지 8개를 모두 모아야 사천왕에 도전할 수 있어요."}',
        *COOLDOWN(9),
        'execute if entity @a[scores={poke.gym=9}] run return run function poke:gym/deny/9 {msg:"다른 도전자가 사천왕에 도전 중이에요. 잠시 후 다시 와 주세요."}',
        'scoreboard players set @s poke.gym 9', 'scoreboard players set @s poke.e4 0', tp(e['inside'][0]),
        'title @s title {"text":"사천왕","color":"gold"}',
        f'title @s subtitle {{"text":"첫 번째: {ELITE[0][1]} ({ELITE[0][2]})","color":"white"}}',
        'tellraw @s {"text":"사천왕 4명을 한 번에 모두 이겨야 클리어예요. 한 번이라도 지면 처음부터!","color":"gray"}'])
    nxt = []
    for k in range(1, 4):
        nxt += [f'execute if score @s poke.e4 matches {k} run {tp(e["inside"][k])}',
                f'execute if score @s poke.e4 matches {k} run title @s subtitle {{"text":"{k + 1}번째: {ELITE[k][1]} ({ELITE[k][2]})","color":"white"}}',
                f'execute if score @s poke.e4 matches {k} run title @s title {{"text":"다음 방으로","color":"gold"}}',
                f'execute if score @s poke.e4 matches {k} run tellraw @a [{{"text":"[리그] ","color":"gold"}},{{"selector":"@s"}},{{"text":"님이 사천왕 {k}번째({ELITE[k - 1][1]}){josa(ELITE[k - 1][1])} 클리어하였습니다!","color":"yellow"}}]']
    fn('e4/win.mcfunction', ['# 사천왕 한 명을 이기면 다음 방, 네 명 모두 이기면 클리어',
                             'scoreboard players add @s poke.e4 1',
                             'execute if score @s poke.e4 matches 4.. run return run function poke:e4/clear', *nxt])
    fn('e4/clear.mcfunction', ['tag @s add poke.e4clear', tp(e['inside'][4]), prize(10000),
                               'title @s title {"text":"사천왕 클리어!","color":"gold"}',
                               'title @s subtitle {"text":"명예의 전당에 이름을 올렸습니다","color":"yellow"}',
                               'tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕을 클리어하고 챔피언이 되었습니다!","color":"gold"}]'])
    px, pz, w, d = e['exit']
    pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:gym/leave')
    win.append('execute if score @s poke.gym matches 9 run function poke:e4/win')
    for k, (tid, *_r) in enumerate(ELITE):
        mx, mz, myaw = e['member'][k]
        spawn += spawn_lines(tid, mx, mz, myaw)
    fn('league/pads.mcfunction', pads)
    fn('league/spawn_tick.mcfunction', [
        '# 관장 소환 준비: 경기장 청크를 불러오고 3초 뒤 접속한 플레이어 한 명으로 소환',
        'execute unless data storage poke:state {leaders:2} run scoreboard players set #lead poke.timer 0',
        f'execute unless data storage poke:state {{leaders:2}} in poke:town run forceload add {ARENA_CHUNKS}',
        'data modify storage poke:state leaders set value 2', 'scoreboard players add #lead poke.timer 1',
        'execute if score #lead poke.timer matches 60.. as @a[limit=1] run function poke:mod/spawn_leaders'])
    # 체육관 안내원 화면(모드)이 읽는 목록
    rgb = lambda c: c[0] << 16 | c[1] << 8 | c[2]
    league = [dict(n=n, title=f'{n}번 체육관', leader=f'관장 {name}', type=f'{typ} 타입', badge=badge, color=rgb(color),
                   level=max(m['level'] for m in team) + CAP) for n, (_, name, typ, badge, color, team) in enumerate(GYMS, 1)]
    league.append(dict(n=9, title='사천왕 (챔피언 4명 연속)', leader='·'.join(e[1] for e in ELITE), type='강철·불꽃·드래곤·관동 챔피언',
                       badge='명예의 전당', color=0x8A4FD0, level=100))
    (ROOT / 'pack/config/pokeserver/league.json').write_text(json.dumps(league, ensure_ascii=False, indent=1), encoding='utf-8')
    fn('gym/leave.mcfunction', ['# 경기장·사천왕에서 나가기 (나가기 발판, 승리, 패배, 재접속): 체육관 로비로',
                                'execute if score @s poke.gym matches 1.. run function poke:util/tp with storage poke:config gym',
                                'function poke:gym/release'])
    fn('gym/win.mcfunction', ['# 모드가 호출: 체육관 안에서 NPC 배틀을 이겼을 때', *win])
    fn('gym/lose.mcfunction', ['# 모드가 호출: 체육관 안에서 NPC 배틀을 지거나 도망쳤을 때',
                               'execute unless score @s poke.gym matches 1.. run return 0',
                               'execute if score @s poke.gym matches 9 run tellraw @s {"text":"사천왕 도전 실패... 5분 뒤에 처음(첫 번째 사천왕)부터 다시 도전해요.","color":"red"}',
                               'execute if score @s poke.gym matches 1..8 run tellraw @s {"text":"관장에게 졌어요. 포켓몬을 회복하고 5분 뒤에 다시 도전하세요!","color":"red"}',
                               'execute store result score @s poke.gymcd run time query gametime',
                               'scoreboard players add @s poke.gymcd 6000',
                               'function poke:gym/leave'])
    fn('mod/spawn_leaders.mcfunction', [
        '# 관장·사천왕 소환 (RCT 소환 명령은 플레이어가 실행해야 해서, 접속한 플레이어로 실행됨)',
        'kill @e[type=rctmod:trainer,tag=poke.leader]', *spawn,
        'data modify storage poke:state leaders set value 1', f'execute in poke:town run forceload remove {ARENA_CHUNKS}',
        'say [pokeserver] 체육관 관장·사천왕을 배치했습니다.'])


def spawn_lines(tid, x, z, yaw):
    at = f'execute in poke:town positioned {x} {Y} {z}'
    return [f'{at} run rctmod trainer summon_persistent {tid} ~ ~ ~',
            f'{at} run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {{NoAI:1b,Tags:["poke.leader"]}}',
            f'{at} run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ {yaw} 0']


def badges():
    """배지 아이콘 16x16 (금 조각 + custom_model_data 1001~1008)."""
    from PIL import Image, ImageDraw
    tex = ASSETS / 'pokeserver/textures/item'
    tex.mkdir(parents=True, exist_ok=True)
    shapes = {
        1: lambda d, c: d.polygon([(5, 1), (10, 1), (14, 5), (14, 10), (10, 14), (5, 14), (1, 10), (1, 5)], fill=c),
        2: lambda d, c: (d.polygon([(7.5, 1), (12, 8), (3, 8)], fill=c), d.ellipse([3, 5, 12, 14], fill=c)),
        3: lambda d, c: d.polygon([(7.5, 0), (9.5, 5), (15, 5), (10.5, 9), (12.5, 15), (7.5, 11), (2.5, 15), (4.5, 9), (0, 5), (5.5, 5)], fill=c),
        4: lambda d, c: [d.ellipse([x, y, x + 6, y + 6], fill=col) for (x, y), col in
                         zip([(5, 0), (9, 4), (5, 9), (0, 4)], [(230, 60, 60), (60, 120, 230), (240, 200, 60), (120, 200, 90)])] + [d.ellipse([5, 5, 10, 10], fill=c)],
        5: lambda d, c: (d.ellipse([1, 2, 8, 9], fill=c), d.ellipse([7, 2, 14, 9], fill=c), d.polygon([(1, 6), (14, 6), (7.5, 14)], fill=c)),
        6: lambda d, c: (d.ellipse([1, 1, 14, 14], fill=c), d.ellipse([5, 5, 10, 10], fill=(0, 0, 0, 0))),
        7: lambda d, c: d.polygon([(7.5, 0), (12, 6), (13, 11), (10, 15), (5, 15), (2, 11), (3, 6), (6, 8)], fill=c),
        8: lambda d, c: d.polygon([(7.5, 0), (14, 7.5), (7.5, 15), (1, 7.5)], fill=c),
    }
    overrides = []
    for n, (_, _, _, _, color, _) in enumerate(GYMS, 1):
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        shapes[n](d, color + (255,))
        px = img.load()
        for y in range(16):        # 외곽선 + 위쪽 하이라이트
            for x in range(16):
                if px[x, y][3] == 0:
                    continue
                edge = any(not (0 <= x + dx < 16 and 0 <= y + dy < 16) or px[x + dx, y + dy][3] == 0
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                r, g, b, _ = px[x, y]
                k = 0.55 if edge else (1.25 if y < 6 else 1.0)
                px[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
        img.save(tex / f'badge_{n}.png')
        m = ASSETS / f'pokeserver/models/item/badge_{n}.json'
        m.parent.mkdir(parents=True, exist_ok=True)
        m.write_text(json.dumps({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'pokeserver:item/badge_{n}'}}))
        overrides.append({'predicate': {'custom_model_data': 1000 + n}, 'model': f'pokeserver:item/badge_{n}'})
    base = ASSETS / 'minecraft/models/item/gold_nugget.json'
    base.parent.mkdir(parents=True, exist_ok=True)
    base.write_text(json.dumps({'parent': 'minecraft:item/generated', 'textures': {'layer0': 'minecraft:item/gold_nugget'},
                                'overrides': overrides}, indent=1))


if __name__ == '__main__':
    functions()
    badges()


def refresh_pack():
    """생성한 파일이 바뀌면 모드팩 목록(index.toml)의 지문도 갱신해야 함. 안 하면 설치 프로그램이 "Hash invalid"로 멈춤."""
    import os
    import shutil
    import subprocess
    exe = shutil.which('packwiz') or os.path.expanduser('~/go/bin/packwiz')
    if os.path.exists(exe):
        subprocess.run([exe, 'refresh'], cwd=Path(__file__).resolve().parent.parent / 'pack', check=True, capture_output=True)
    else:
        print('경고: packwiz가 없어 pack/index.toml을 갱신하지 못함 → 올리기 전에 packwiz refresh 실행 필요')


if __name__ == '__main__':
    refresh_pack()
