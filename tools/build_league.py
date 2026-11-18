"""포켓서버 리그(배지 체육관 8 + 사천왕 4) 데이터 생성기 — Radical Cobblemon Trainers(RCT) 형식.

RCT에 이미 있는 관장·사천왕 ID를 덮어써서, RCT의 원작 캐릭터 스킨은 그대로 쓰고 팀·레벨·순서만 우리 것으로 바꿈.
사용: python3 tools/build_league.py   (채팅용 체육관 정보도 출력)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'pack/world/datapacks/pokeserver/data'
SERIES = 'pokeserver'


def mon(species, level, moves):
    return {'species': species, 'level': level, 'moveset': moves}


# (RCT ID, 이름, 타입, 배지 이름, 배지 색, 팀)
GYMS = [
    ('leader_brock_019e', '웅', '바위', '회색배지', (150, 150, 155), [
        mon('geodude', 12, ['tackle', 'defensecurl', 'rockthrow', 'mudslap']),
        mon('onix', 14, ['rockthrow', 'bind', 'harden', 'rocktomb'])]),
    ('leader_misty_019f', '이슬', '물', '블루배지', (60, 120, 230), [
        mon('staryu', 18, ['watergun', 'rapidspin', 'swift', 'recover']),
        mon('psyduck', 19, ['watergun', 'confusion', 'scratch', 'disable']),
        mon('starmie', 21, ['bubblebeam', 'swift', 'recover', 'confusion'])]),
    ('leader_lt_surge_01a0', '마티스', '전기', '오렌지배지', (240, 150, 40), [
        mon('voltorb', 24, ['spark', 'sonicboom', 'screech', 'selfdestruct']),
        mon('magnemite', 25, ['thundershock', 'sonicboom', 'supersonic', 'flashcannon']),
        mon('pikachu', 25, ['spark', 'quickattack', 'doubleteam', 'irontail']),
        mon('raichu', 27, ['spark', 'quickattack', 'thunderwave', 'irontail'])]),
    ('leader_erika_01a1', '민화', '풀', '무지개배지', (120, 200, 90), [
        mon('tangela', 30, ['megadrain', 'vinewhip', 'sleeppowder', 'constrict']),
        mon('weepinbell', 31, ['razorleaf', 'poisonpowder', 'wrap', 'acid']),
        mon('gloom', 31, ['megadrain', 'acid', 'sleeppowder', 'moonlight']),
        mon('vileplume', 33, ['gigadrain', 'sludgebomb', 'stunspore', 'moonblast'])]),
    ('leader_koga_01a2', '독수', '독', '핑크배지', (240, 120, 180), [
        mon('koffing', 36, ['sludge', 'smokescreen', 'willowisp', 'selfdestruct']),
        mon('golbat', 36, ['wingattack', 'poisonfang', 'confuseray', 'bite']),
        mon('muk', 37, ['sludge', 'minimize', 'acidarmor', 'bodyslam']),
        mon('weezing', 39, ['sludgebomb', 'toxic', 'willowisp', 'selfdestruct'])]),
    ('leader_sabrina_01a4', '초련', '에스퍼', '골드배지', (240, 200, 60), [
        mon('kadabra', 42, ['psybeam', 'recover', 'reflect', 'shadowball']),
        mon('mrmime', 42, ['psybeam', 'barrier', 'lightscreen', 'dazzlinggleam']),
        mon('venomoth', 43, ['psybeam', 'sleeppowder', 'bugbuzz', 'sludgebomb']),
        mon('alakazam', 45, ['psychic', 'recover', 'shadowball', 'energyball'])]),
    ('leader_blaine_01a3', '강연', '불꽃', '크림슨배지', (210, 50, 50), [
        mon('growlithe', 48, ['flamethrower', 'bite', 'takedown', 'roar']),
        mon('ponyta', 48, ['firespin', 'stomp', 'takedown', 'agility']),
        mon('rapidash', 49, ['flareblitz', 'stomp', 'agility', 'bounce']),
        mon('magmar', 49, ['flamethrower', 'thunderpunch', 'confuseray', 'smokescreen']),
        mon('arcanine', 51, ['flamethrower', 'extremespeed', 'crunch', 'wildcharge'])]),
    ('leader_giovanni_015e', '비주기', '땅', '그린배지', (70, 170, 80), [
        mon('dugtrio', 54, ['earthquake', 'slash', 'suckerpunch', 'sandtomb']),
        mon('nidoqueen', 54, ['earthpower', 'sludgewave', 'icebeam', 'superpower']),
        mon('nidoking', 55, ['earthpower', 'sludgewave', 'thunderbolt', 'icebeam']),
        mon('rhydon', 55, ['earthquake', 'rockslide', 'megahorn', 'hammerarm']),
        mon('marowak', 56, ['bonemerang', 'swordsdance', 'rockslide', 'firepunch']),
        mon('rhyperior', 57, ['earthquake', 'stoneedge', 'megahorn', 'icepunch'])]),
]
ELITE = [
    ('elite_four_lorelei_004d', '칸나', '얼음', [
        mon('dewgong', 58, ['icebeam', 'surf', 'aquajet', 'rest']),
        mon('cloyster', 58, ['iciclespear', 'shellsmash', 'rockblast', 'iceshard']),
        mon('slowbro', 59, ['surf', 'psychic', 'icebeam', 'slackoff']),
        mon('jynx', 59, ['icebeam', 'psychic', 'lovelykiss', 'nastyplot']),
        mon('lapras', 60, ['freezedry', 'hydropump', 'thunderbolt', 'icebeam'])]),
    ('elite_four_bruno_0050', '시바', '격투', [
        mon('onix', 59, ['stoneedge', 'earthquake', 'rockpolish', 'stealthrock']),
        mon('hitmonchan', 59, ['machpunch', 'drainpunch', 'icepunch', 'thunderpunch']),
        mon('hitmonlee', 59, ['highjumpkick', 'blazekick', 'knockoff', 'suckerpunch']),
        mon('poliwrath', 60, ['closecombat', 'waterfall', 'bulkup', 'icepunch']),
        mon('machamp', 61, ['dynamicpunch', 'knockoff', 'stoneedge', 'bulletpunch'])]),
    ('elite_four_agatha_0053', '국화', '고스트', [
        mon('golbat', 60, ['crosspoison', 'airslash', 'confuseray', 'uturn']),
        mon('arbok', 61, ['gunkshot', 'crunch', 'glare', 'earthquake']),
        mon('haunter', 61, ['shadowball', 'sludgebomb', 'destinybond', 'hypnosis']),
        mon('mismagius', 61, ['shadowball', 'dazzlinggleam', 'nastyplot', 'thunderbolt']),
        mon('gengar', 62, ['shadowball', 'sludgebomb', 'hypnosis', 'dreameater'])]),
    ('elite_four_lance_0056', '목호', '드래곤', [
        mon('gyarados', 62, ['waterfall', 'dragondance', 'earthquake', 'icefang']),
        mon('dragonair', 62, ['dragonpulse', 'thunderwave', 'aquatail', 'extremespeed']),
        mon('aerodactyl', 62, ['stoneedge', 'earthquake', 'aerialace', 'icefang']),
        mon('kingdra', 63, ['dracometeor', 'surf', 'icebeam', 'focusenergy']),
        mon('dragonite', 64, ['outrage', 'extremespeed', 'earthquake', 'firepunch'])]),
]


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
    write(f'rctmod/series/{SERIES}.json', {
        'title': text('포켓서버 리그'), 'description': text('배지 8개를 모은 뒤 사천왕을 한 번에 모두 이겨라'),
        'difficulty': 3, 'requiredSeries': [], 'initialLevelCap': 15})
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


def fn(path, lines):
    p = FN / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('\n'.join(['# 자동 생성: tools/build_league.py'] + lines) + '\n', encoding='utf-8')


def tp(pos):
    x, z, yaw = pos
    return f'execute in poke:town run tp @s {x} {Y} {z} {yaw} 0'


def badge_item(n, name, color):
    hexc = '#%02X%02X%02X' % color
    return (f"give @s minecraft:gold_nugget[minecraft:custom_name='{{\"text\":\"{name}\",\"color\":\"{hexc}\",\"italic\":false}}',"
            f"minecraft:lore=['{{\"text\":\"포켓서버 리그 {n}번 체육관 배지\",\"color\":\"gray\",\"italic\":false}}'],"
            f"minecraft:custom_model_data={1000 + n},minecraft:custom_data={{pokeserver:\"badge{n}\"}}] 1")


def functions():
    pads, leave, win, spawn = [], [], [], []
    for n, (tid, name, typ, badge, color, _) in enumerate(GYMS, 1):
        g = W.gym_geom(n)
        ox, oz, oyaw = g['out']
        fn(f'gym/deny/{n}.mcfunction', ['$tellraw @s {"text":"$(msg)","color":"red"}', tp(g['out'])])
        need = [] if n == 1 else [f'execute unless entity @s[tag=poke.badge{n - 1}] run return run function poke:gym/deny/{n} '
                                  f'{{msg:"{n - 1}번 체육관 배지를 먼저 얻어야 도전할 수 있어요."}}']
        fn(f'gym/try/{n}.mcfunction', [
            f'# {n}번 체육관 입장 발판: 순서·재도전·혼자만 도전 확인 후 경기장으로',
            'execute if score @s poke.gym matches 1.. run return 0',
            f'execute unless entity @s[tag=poke.tutorial_done] run return run function poke:gym/deny/{n} {{msg:"튜토리얼을 먼저 끝내 주세요."}}',
            f'execute if entity @s[tag=poke.badge{n}] run return run function poke:gym/deny/{n} {{msg:"이미 이긴 체육관이에요. 다시 도전할 수 없어요."}}',
            *need,
            f'execute if entity @a[scores={{poke.gym={n}}}] run return run function poke:gym/deny/{n} {{msg:"다른 도전자가 관장과 싸우는 중이에요. 잠시 후 다시 와 주세요."}}',
            f'scoreboard players set @s poke.gym {n}', tp(g['inside']),
            f'title @s title {{"text":"{n}번 체육관","color":"gold"}}',
            f'title @s subtitle {{"text":"{typ} 타입 · 관장 {name}","color":"white"}}',
            'tellraw @s {"text":"관장을 우클릭하면 배틀이 시작돼요. 나가려면 주황 발판을 밟으세요.","color":"gray"}'])
        fn(f'gym/award/{n}.mcfunction', [
            f'tag @s add poke.badge{n}', badge_item(n, badge, color),
            f'title @s title {{"text":"{badge} 획득!","color":"gold"}}',
            f'tellraw @a [{{"text":"[리그] ","color":"gold"}},{{"selector":"@s"}},{{"text":"님이 {n}번 체육관 관장 {name}을(를) 이기고 {badge}를 얻었습니다!","color":"yellow"}}]',
            'function poke:gym/leave'])
        px, pz, w, d = g['pad']
        pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:gym/try/{n}')
        px, pz, w, d = g['exit']
        pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:gym/leave')
        leave.append(f'execute if score @s poke.gym matches {n} in poke:town run tp @s {ox} {Y} {oz} {oyaw} 0')
        win.append(f'execute if score @s poke.gym matches {n} run return run function poke:gym/award/{n}')
        lx, lz, lyaw = g['leader']
        spawn += spawn_lines(tid, lx, lz, lyaw)
    e = W.e4_geom()
    ox, oz, oyaw = e['out']
    fn('gym/deny/9.mcfunction', ['$tellraw @s {"text":"$(msg)","color":"red"}', tp(e['out'])])
    fn('gym/try/9.mcfunction', [
        '# 사천왕 입장 발판: 배지 8개, 이미 클리어했으면 불가, 한 번에 한 명',
        'execute if score @s poke.gym matches 1.. run return 0',
        'execute if entity @s[tag=poke.e4clear] run return run function poke:gym/deny/9 {msg:"이미 사천왕을 모두 이겼어요. 다시 도전할 수 없어요."}',
        'execute unless entity @s[tag=poke.badge8] run return run function poke:gym/deny/9 {msg:"배지 8개를 모두 모아야 사천왕에 도전할 수 있어요."}',
        'execute if entity @a[scores={poke.gym=9}] run return run function poke:gym/deny/9 {msg:"다른 도전자가 사천왕에 도전 중이에요. 잠시 후 다시 와 주세요."}',
        'scoreboard players set @s poke.gym 9', 'scoreboard players set @s poke.e4 0', tp(e['inside'][0]),
        'title @s title {"text":"사천왕","color":"gold"}',
        f'title @s subtitle {{"text":"첫 번째: {ELITE[0][1]} ({ELITE[0][2]})","color":"white"}}',
        'tellraw @s {"text":"사천왕 4명을 한 번에 모두 이겨야 클리어예요. 한 번이라도 지면 처음부터!","color":"gray"}'])
    nxt = []
    for k in range(1, 4):
        nxt += [f'execute if score @s poke.e4 matches {k} run {tp(e["inside"][k])}',
                f'execute if score @s poke.e4 matches {k} run title @s subtitle {{"text":"{k + 1}번째: {ELITE[k][1]} ({ELITE[k][2]})","color":"white"}}',
                f'execute if score @s poke.e4 matches {k} run title @s title {{"text":"다음 방으로","color":"gold"}}']
    fn('e4/win.mcfunction', ['# 사천왕 한 명을 이기면 다음 방, 네 명 모두 이기면 클리어',
                             'scoreboard players add @s poke.e4 1',
                             'execute if score @s poke.e4 matches 4.. run return run function poke:e4/clear', *nxt])
    fn('e4/clear.mcfunction', ['tag @s add poke.e4clear', tp(e['inside'][4]),
                               'title @s title {"text":"사천왕 클리어!","color":"gold"}',
                               'title @s subtitle {"text":"명예의 전당에 이름을 올렸습니다","color":"yellow"}',
                               'tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕을 모두 이기고 명예의 전당에 올랐습니다!","color":"yellow"}]'])
    px, pz, w, d = e['pad']
    pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:gym/try/9')
    px, pz, w, d = e['exit']
    pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:gym/leave')
    leave.append(f'execute if score @s poke.gym matches 9 in poke:town run tp @s {ox} {Y} {oz} {oyaw} 0')
    win.append('execute if score @s poke.gym matches 9 run function poke:e4/win')
    for k, (tid, *_r) in enumerate(ELITE):
        mx, mz, myaw = e['member'][k]
        spawn += spawn_lines(tid, mx, mz, myaw)
    fn('league/pads.mcfunction', pads)
    fn('gym/leave.mcfunction', ['# 체육관·사천왕에서 나가기 (나가기 발판, 승리, 패배, 재접속): 그 건물 앞으로', *leave, 'function poke:gym/release'])
    fn('gym/win.mcfunction', ['# 모드가 호출: 체육관 안에서 NPC 배틀을 이겼을 때', *win])
    fn('gym/lose.mcfunction', ['# 모드가 호출: 체육관 안에서 NPC 배틀을 지거나 도망쳤을 때',
                               'execute unless score @s poke.gym matches 1.. run return 0',
                               'execute if score @s poke.gym matches 9 run tellraw @s {"text":"사천왕 도전 실패... 다음엔 처음(첫 번째 사천왕)부터 다시 도전해요.","color":"red"}',
                               'execute if score @s poke.gym matches 1..8 run tellraw @s {"text":"관장에게 졌어요. 포켓몬을 회복하고 다시 도전하세요!","color":"red"}',
                               'function poke:gym/leave'])
    fn('mod/spawn_leaders.mcfunction', [
        '# 관장·사천왕 소환 (RCT 소환 명령은 플레이어가 실행해야 해서, 접속한 플레이어로 실행됨)',
        'kill @e[type=rctmod:trainer,tag=poke.leader]', *spawn,
        'data modify storage poke:state leaders set value 1', 'execute in poke:town run forceload remove 30 -50 250 15',
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
