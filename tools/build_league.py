"""잡켓몬 리그(배지 체육관 8 + 사천왕 4) 데이터 생성기 — Radical Cobblemon Trainers(RCT) 형식.

RCT에 이미 있는 관장·사천왕 ID를 덮어써서, RCT의 원작 캐릭터 스킨은 그대로 쓰고 팀·레벨·순서만 우리 것으로 바꿈.
사용: python3 tools/build_league.py   (채팅용 체육관 정보도 출력)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'pack/world/datapacks/pokeserver/data'
SERIES = 'pokeserver'


def mon(species, level, moves, item, dmax=False, tera=None, ability=None, gmax=False, nature=None, evs=None):
    """item: 지닌 도구 (메가스톤·Z크리스탈이면 그 기믹을 씀). dmax: 다이맥스(gmax면 거다이맥스 모습), tera: 테라스탈 타입. 한 포켓몬은 기믹 하나만.
    개체값은 모두 31, 기술·특성·성격·노력치는 Smogon 실전 세트 (줄 끝 주석 = pkmn/smogon data/sets의 형식/세트 이름)."""
    if 'stealthrock' in moves:   # 스텔스록이 있으면 첫 기술로 (이 포켓몬이 선봉으로 나와 첫 턴에 씀)
        moves = ['stealthrock'] + [mv for mv in moves if mv != 'stealthrock']
    m = {'species': species, 'level': level, 'moveset': moves, 'heldItem': item if ':' in item else 'cobblemon:' + item,
         'ivs': dict.fromkeys(('hp', 'atk', 'def', 'spa', 'spd', 'spe'), 31)}
    if evs:
        m['evs'] = evs
    if nature:
        m['nature'] = nature
    if dmax:
        m['gimmicks'] = {'dynamax': True, 'gmax': gmax}
    if tera:
        m['gimmicks'] = {'tera': tera}
    if ability:
        m['ability'] = ability
    return m


MS = 'mega_showdown:'
# v3 (docs/관장팀.md): 순서 = 같은 레벨 기준 강함 (원작 최종 팀의 종족값 합 평균, tools/teamdoc.py가 계산해 문서에 적음).
# 팀 = 원작 대표 포켓몬 (파이어레드·하트골드 재대결·에메랄드·플래티넘 데이터 = pret 디스어셈블리, 단델 = 소드실드 공략).
# 2번(마티스)·5번(초련)은 사용자 지정으로 맞바꿈. 관장 기믹: Z기술 3번째부터, 메가진화 5번째부터, 다이맥스 7번째부터. 사천왕 1~3은 4가지 중 3가지(조합이 서로 다름), 마지막은 4가지 모두.
# 한 포켓몬은 기믹 하나만. 에이스(★) = 팀 마지막 = 레벨 제한 - 5. 선봉은 에이스를 뺀 나머지 중 무작위(TrainerLeadMixin).
# (RCT ID, 이름, 타입, 배지 이름, 배지 색, 팀)
GYMS = [
    ('leader_brock_019e', '웅', '바위', '회색배지', (150, 150, 155), [
        mon('geodude', 13, ['stealthrock', 'rockblast', 'earthquake', 'suckerpunch'], 'berry_juice', ability='sturdy', nature='adamant', evs={'hp': 36, 'atk': 196, 'def': 116, 'spd': 36, 'spe': 116}),   # gen7lc/Stealth Rock
        mon('kabuto', 13, ['rapidspin', 'stealthrock', 'knockoff', 'rockslide'], 'focus_sash', ability='weakarmor', nature='careful', evs={'hp': 116, 'atk': 36, 'def': 36, 'spd': 156, 'spe': 156}),   # gen8lc/Support, 도구는 진화의휘석 대신 기합의띠 (진화의휘석은 안 씀) (2.2.0: 관장 4마리)
        mon('rhyhorn', 13, ['swordsdance', 'rockpolish', 'earthquake', 'stoneedge'], 'life_orb', nature='adamant', evs={'atk': 236, 'spd': 116, 'spe': 156}),   # gen9lc/Setup Sweeper
        mon('onix', 15, ['earthquake', 'rockblast', 'stealthrock', 'explosion'], 'rocky_helmet', ability='sturdy', nature='jolly', evs={'hp': 76, 'atk': 236, 'spe': 196})]),   # gen8lc/SturdyJuice
    ('leader_lt_surge_01a0', '마티스', '전기', '오렌지배지', (240, 150, 40), [
        mon('voltorb', 22, ['reflect', 'lightscreen', 'voltswitch', 'taunt'], 'light_clay', ability='aftermath', nature='timid', evs={'hp': 196, 'def': 36, 'spd': 76, 'spe': 196}),   # gen7lc/Dual Screens
        mon('magnemite', 23, ['thunderbolt', 'flashcannon', 'thunderwave', 'voltswitch'], 'choice_scarf', nature='modest', evs={'def': 36, 'spa': 236, 'spe': 236}),   # gen9lc/Trapper
        mon('pikachu', 23, ['substitute', 'thunderbolt', 'grassknot', 'encore'], 'light_ball', nature='timid', evs={'def': 4, 'spa': 252, 'spe': 252}),   # gen4uu/Substitute
        mon('raichu', 25, ['nastyplot', 'thunderbolt', 'grassknot', 'focusblast'], 'life_orb', ability='lightningrod', nature='timid', evs={'def': 4, 'spa': 252, 'spe': 252})]),   # gen7pu/Nasty Plot
    ('leader_blaine_01a3', '강연', '불꽃', '크림슨배지', (210, 50, 50), [
        mon('ponyta', 33, ['flareblitz', 'wildcharge', 'flamecharge', 'highhorsepower'], 'berry_juice', ability='flamebody', nature='jolly', evs={'hp': 36, 'atk': 236, 'spe': 196}),   # gen8lc/Berry Juice Attacker
        mon('torkoal', 33, ['lavaplume', 'rapidspin', 'stealthrock', 'willowisp'], 'heat_rock', ability='drought', nature='bold', evs={'hp': 248, 'def': 252, 'spd': 8}),   # gen9ou/Sun Setter
        mon('camerupt', 34, ['stealthrock', 'lavaplume', 'earthpower', 'roar'], 'leftovers', ability='solidrock', nature='calm', evs={'hp': 252, 'def': 4, 'spd': 252}),   # gen9zu/Specially Defensive
        mon('magmar', 34, ['flamethrower', 'thunderpunch', 'focusblast', 'psychic'], 'life_orb', ability='flamebody', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # 직접(실전 특수형)
        mon('arcanine', 35, ['flareblitz', 'wildcharge', 'extremespeed', 'morningsun'], MS + 'firium_z', ability='flashfire', nature='jolly', evs={'atk': 252, 'def': 4, 'spe': 252})]),   # gen7ru/Wallbreaker
    ('leader_koga_01a2', '독수', '독', '핑크배지', (240, 120, 180), [
        mon('weezing', 43, ['sludgebomb', 'flamethrower', 'taunt', 'painsplit'], 'rocky_helmet', ability='levitate', nature='bold', evs={'hp': 252, 'def': 212, 'spe': 44}),   # gen9nu/Physical Wall
        mon('venomoth', 43, ['quiverdance', 'bugbuzz', 'sludgebomb', 'morningsun'], 'heavy_duty_boots', ability='tintedlens', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # gen9pu/Quiver Dance
        mon('toxicroak', 44, ['swordsdance', 'closecombat', 'gunkshot', 'suckerpunch'], 'life_orb', ability='dryskin', nature='adamant', evs={'atk': 252, 'spd': 4, 'spe': 252}),   # gen9ru/Swords Dance
        mon('muk', 44, ['toxic', 'protect', 'knockoff', 'drainpunch'], 'leftovers', ability='stickyhold', nature='impish', evs={'hp': 248, 'def': 252, 'spd': 8}),   # gen9pu/ToxTect
        mon('crobat', 45, ['nastyplot', 'sludgebomb', 'heatwave', 'gigadrain'], MS + 'poisonium_z', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252})]),   # gen8ru/Nasty Plot
    ('leader_sabrina_01a4', '초련', '에스퍼', '골드배지', (240, 200, 60), [
        mon('slowbro', 53, ['calmmind', 'psychicnoise', 'scald', 'slackoff'], 'heavy_duty_boots', ability='regenerator', nature='bold', evs={'hp': 252, 'def': 252, 'spd': 4}),   # gen9uu/Calm Mind (2.2.0: 관장 6마리)
        mon('gallade', 53, ['swordsdance', 'sacredsword', 'psychocut', 'leafblade'], 'lum_berry', ability='sharpness', nature='jolly', evs={'atk': 252, 'spd': 4, 'spe': 252}),   # gen9ru/Setup Sweeper
        mon('mrmime', 53, ['nastyplot', 'dazzlinggleam', 'focusblast', 'psyshock'], 'life_orb', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # gen7pu/Nasty Plot
        mon('jynx', 53, ['lovelykiss', 'nastyplot', 'icebeam', 'psyshock'], 'focus_sash', ability='dryskin', nature='timid', evs={'def': 4, 'spa': 252, 'spe': 252}),   # gen7pu/Z-Lovely Kiss
        mon('espeon', 54, ['calmmind', 'psychic', 'shadowball', 'morningsun'], MS + 'psychium_z', ability='magicbounce', nature='timid', evs={'def': 4, 'spa': 252, 'spe': 252}),   # gen7ru/Calm Mind
        mon('alakazam', 55, ['nastyplot', 'psychic', 'focusblast', 'shadowball'], MS + 'alakazite', ability='magicguard', nature='timid', evs={'def': 4, 'spa': 252, 'spe': 252})]),   # gen9nationaldexuu/Nasty Plot
    ('leader_giovanni_015e', '비주기', '땅', '그린배지', (70, 170, 80), [
        mon('marowak', 63, ['bonemerang', 'doubleedge', 'stoneedge', 'knockoff'], 'choice_band', ability='rockhead', nature='adamant', evs={'atk': 252, 'def': 4, 'spe': 252}),   # gen6nu/Bone Crusher (Wallbreaker), 굵은뼈가 코블몬에 없어 구애머리띠 + 공격 기술 4개 (2.2.0: 관장 6마리)
        mon('dugtrio', 63, ['earthquake', 'screech', 'substitute', 'memento'], 'focus_sash', ability='arenatrap', nature='adamant', evs={'atk': 252, 'def': 4, 'spe': 252}),   # gen7ubers/Utility Trapper
        mon('nidoqueen', 63, ['stealthrock', 'earthpower', 'sludgewave', 'fireblast'], 'leftovers', ability='sheerforce', nature='modest', evs={'hp': 120, 'spa': 252, 'spe': 136}),   # gen8uu/Offensive Stealth Rock
        mon('steelix', 64, ['stealthrock', 'earthquake', 'heavyslam', 'toxic'], MS + 'steelixite', ability='sturdy', nature='careful', evs={'hp': 252, 'def': 4, 'spd': 252}),   # gen8ru/Defensive
        mon('nidoking', 64, ['sludgewave', 'earthpower', 'icebeam', 'flamethrower'], 'life_orb', ability='sheerforce', nature='modest', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # gen8ou/Wallbreaker
        mon('rhyperior', 65, ['stealthrock', 'earthquake', 'stoneedge', 'icepunch'], MS + 'groundium_z', ability='solidrock', nature='adamant', evs={'hp': 252, 'atk': 16, 'spd': 240})]),   # gen7uu/Tank
    ('leader_erika_01a1', '민화', '풀', '무지개배지', (120, 200, 90), [
        mon('jumpluff', 73, ['swordsdance', 'strengthsap', 'sleeppowder', 'acrobatics'], 'flying_gem', ability='infiltrator', nature='jolly', evs={'atk': 252, 'def': 4, 'spe': 252}),   # gen7pu/Swords Dance
        mon('shiftry', 73, ['growth', 'solarblade', 'knockoff', 'heatwave'], 'life_orb', nature='hasty', evs={'atk': 252, 'spa': 4, 'spe': 252}),   # gen9ru/Chlorophyll Sweeper
        mon('roserade', 73, ['gigadrain', 'sludgebomb', 'spikes', 'sleeppowder'], 'black_sludge', nature='timid', evs={'hp': 248, 'def': 8, 'spe': 252}),   # gen8uu/Spikes
        mon('tangrowth', 74, ['gigadrain', 'knockoff', 'focusblast', 'sleeppowder'], 'rocky_helmet', dmax=True, ability='regenerator', nature='relaxed', evs={'hp': 252, 'def': 252, 'spd': 4}),   # gen8ou/Physically Defensive
        mon('bellossom', 74, ['strengthsap', 'quiverdance', 'gigadrain', 'moonblast'], MS + 'grassium_z', nature='timid', evs={'hp': 248, 'def': 8, 'spe': 252}),   # gen7pu/Bulky Quiver Dance
        mon('victreebel', 75, ['strengthsap', 'powerwhip', 'poisonjab', 'knockoff'], MS + 'victreebelite', nature='adamant', evs={'atk': 252, 'def': 4, 'spe': 252})]),   # gen9zu/All-Out Attacker
    ('leader_misty_019f', '이슬', '물', '블루배지', (60, 120, 230), [
        mon('quagsire', 83, ['stealthrock', 'recover', 'toxic', 'counter'], 'rocky_helmet', ability='unaware', nature='bold', evs={'hp': 252, 'def': 252, 'spd': 4}),   # gen9ou/Defensive
        mon('lanturn', 83, ['scald', 'voltswitch', 'rest', 'sleeptalk'], 'heavy_duty_boots', ability='waterabsorb', nature='calm', evs={'hp': 216, 'spd': 252, 'spe': 40}),   # gen9pu/RestTalk
        mon('floatzel', 83, ['wavecrash', 'flipturn', 'aquajet', 'icespinner'], MS + 'waterium_z', ability='waterveil', nature='jolly', evs={'atk': 252, 'def': 4, 'spe': 252}),   # gen9pu/Choice Band
        mon('milotic', 84, ['scald', 'recover', 'toxic', 'refresh'], 'leftovers', nature='calm', evs={'hp': 252, 'def': 108, 'spd': 148}),   # gen7ru/Defensive
        mon('lapras', 84, ['freezedry', 'hydropump', 'alluringvoice', 'icebeam'], 'assault_vest', dmax=True, gmax=True, nature='modest', evs={'def': 196, 'spa': 252, 'spe': 60}),   # gen9zu/Special Tank
        mon('starmie', 85, ['hydropump', 'icebeam', 'thunderbolt', 'recover'], MS + 'starminite', ability='analytic', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252})]),   # gen8uu/Offensive
]

# 사천왕 = 역대 챔피언 4명. 레드는 최종 보스로 맨 뒤 고정, 앞 3명은 같은 레벨 기준 약한 순서. 마지막 에이스 95, 나머지 90 → 레벨 제한 95·100.
# 1~3번째는 기믹 3가지(조합이 서로 다름: 다이맥스·Z·메가를 하나씩 뺌), 레드는 4가지. 단델·성호는 RCT에 없어 새 ID + 우리 스킨.
# 리그 전체에서 (포켓몬, 기믹)이 겹치지 않음: 리자몽은 단델이 다이맥스, 레드가 메가진화.
# (RCT ID, 이름, 칭호, 팀)
ELITE = [
    ('champion_steven_ps', '성호', '호연 챔피언', [
        mon('skarmory', 87, ['spikes', 'roost', 'bodypress', 'irondefense'], 'rocky_helmet', tera='dragon', ability='sturdy', nature='bold', evs={'hp': 252, 'def': 160, 'spe': 96}),   # gen9ou/Defensive
        mon('claydol', 87, ['stealthrock', 'toxic', 'psychic', 'teleport'], 'colbur_berry', nature='bold', evs={'hp': 252, 'def': 240, 'spe': 16}),   # gen8pu/Defensive
        mon('cradily', 87, ['stealthrock', 'recover', 'toxic', 'rockslide'], 'leftovers', ability='stormdrain', nature='careful', evs={'hp': 252, 'def': 4, 'spd': 252}),   # gen7pu/Specially Defensive
        mon('armaldo', 88, ['rapidspin', 'stoneedge', 'knockoff', 'earthquake'], 'heavy_duty_boots', nature='adamant', evs={'hp': 252, 'atk': 92, 'spe': 164}),   # gen7pu/Offensive Spinner
        mon('aggron', 88, ['headsmash', 'heavyslam', 'aquatail', 'earthquake'], 'choice_band', dmax=True, ability='rockhead', nature='adamant', evs={'atk': 252, 'def': 4, 'spe': 252}),   # gen8pu/Choice Band
        mon('metagross', 90, ['heavyslam', 'earthquake', 'knockoff', 'bulletpunch'], MS + 'metagrossite', nature='adamant', evs={'atk': 252, 'spd': 4, 'spe': 252})]),   # gen9uu/Choice Band
    ('champion_cynthia_03a5', '난천', '신오 챔피언', [
        mon('spiritomb', 87, ['trickroom', 'nastyplot', 'darkpulse', 'psyshock'], 'leftovers', ability='infiltrator', nature='quiet', evs={'hp': 252, 'spa': 252, 'spd': 4}),   # gen9pu/Trick Room Sweeper
        mon('roserade', 87, ['gigadrain', 'sludgebomb', 'spikes', 'sleeppowder'], 'black_sludge', nature='timid', evs={'hp': 248, 'def': 8, 'spe': 252}),   # gen8uu/Spikes
        mon('milotic', 87, ['recover', 'scald', 'flipturn', 'alluringvoice'], 'rocky_helmet', ability='marvelscale', nature='bold', evs={'hp': 252, 'def': 248, 'spe': 8}),   # gen9pu/Physically Defensive
        mon('togekiss', 88, ['nastyplot', 'airslash', 'roost', 'healbell'], 'heavy_duty_boots', tera='fairy', ability='serenegrace', nature='timid', evs={'hp': 252, 'def': 120, 'spe': 136}),   # gen8ou/Stallbreaker
        mon('lucario', 88, ['nastyplot', 'focusblast', 'flashcannon', 'vacuumwave'], MS + 'fightinium_z', ability='innerfocus', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # gen7uu/Nasty Plot
        mon('garchomp', 90, ['earthquake', 'dragontail', 'stoneedge', 'spikes'], MS + 'garchompite', ability='roughskin', nature='impish', evs={'hp': 252, 'def': 216, 'spe': 40})]),   # gen9ou/TankChomp
    ('champion_leon_ps', '단델', '가라르 챔피언', [
        mon('aegislash', 87, ['substitute', 'toxic', 'kingsshield', 'shadowball'], 'leftovers', tera='ghost', nature='modest', evs={'hp': 252, 'spa': 56, 'spd': 156, 'spe': 44}),   # gen9nationaldexuu/SubToxic
        mon('rhyperior', 87, ['stealthrock', 'earthquake', 'stoneedge', 'swordsdance'], 'weakness_policy', ability='solidrock', nature='adamant', evs={'hp': 252, 'atk': 16, 'spd': 184, 'spe': 56}),   # gen9uu/Offensive
        mon('cinderace', 87, ['pyroball', 'uturn', 'courtchange', 'suckerpunch'], 'heavy_duty_boots', ability='libero', nature='jolly', evs={'atk': 252, 'spd': 4, 'spe': 252}),   # gen9ou/Offensive Pivot
        mon('haxorus', 88, ['swordsdance', 'outrage', 'earthquake', 'poisonjab'], MS + 'dragonium_z', ability='moldbreaker', nature='jolly', evs={'atk': 252, 'spd': 4, 'spe': 252}),   # gen7uu/Swords Dance
        mon('dragapult', 88, ['dragondarts', 'hex', 'willowisp', 'uturn'], 'expert_belt', ability='infiltrator', nature='naive', evs={'atk': 4, 'spa': 252, 'spe': 252}),   # gen9ou/Boots Pivot
        mon('charizard', 90, ['weatherball', 'overheat', 'focusblast', 'roost'], 'life_orb', dmax=True, gmax=True, ability='solarpower', nature='timid', evs={'spa': 252, 'spd': 4, 'spe': 252})]),   # gen8ou/Sun Wallbreaker
    ('trainer_red_0003', '레드', '관동 전설의 챔피언', [
        mon('lapras', 92, ['freezedry', 'hydropump', 'alluringvoice', 'icebeam'], 'heavy_duty_boots', nature='modest', evs={'def': 196, 'spa': 252, 'spe': 60}),   # gen9zu/Special Tank
        mon('blastoise', 92, ['shellsmash', 'surf', 'icebeam', 'aurasphere'], 'white_herb', nature='modest', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # gen9uu/Shell Smash
        mon('venusaur', 93, ['growth', 'gigadrain', 'weatherball', 'earthpower'], 'life_orb', dmax=True, gmax=True, ability='chlorophyll', nature='modest', evs={'spa': 252, 'spd': 4, 'spe': 252}),   # gen8ou/Sun Sweeper
        mon('pikachu', 93, ['volttackle', 'irontail', 'knockoff', 'quickattack'], MS + 'pikanium_z', ability='lightningrod', nature='jolly', evs={'atk': 252, 'spd': 4, 'spe': 252}),   # 직접(볼트태클 = 피카츄Z 필요)
        mon('snorlax', 93, ['curse', 'bodyslam', 'crunch', 'rest'], 'leftovers', tera='fairy', ability='thickfat', nature='careful', evs={'hp': 12, 'def': 244, 'spd': 252}),   # gen9nu/CurseLax
        mon('charizard', 95, ['weatherball', 'solarbeam', 'focusblast', 'flamethrower'], MS + 'charizardite_y', ability='solarpower', nature='timid', evs={'def': 4, 'spa': 252, 'spe': 252})]),   # gen9pu/Sun Wallbreaker
]
# 원작 팀: 순서(같은 레벨 기준 강함)와 대표 포켓몬의 근거. (출처, 강함 계산용 최종 팀, 그 밖에 원작에 나온 포켓몬·진화 전후)
# 파이어레드·하트골드·에메랄드·플래티넘 = pret 디스어셈블리의 트레이너 데이터, 단델 = Bulbapedia 소드실드 공략
ORIGINAL = {
    'leader_brock_019e': ('하트골드 재대결 최종', ['golem', 'relicanth', 'omastar', 'onix', 'kabutops', 'rampardos'], {'geodude', 'graveler', 'rhyhorn'}),
    'leader_sabrina_01a4': ('하트골드 재대결 최종', ['alakazam', 'espeon', 'mrmime', 'jynx', 'wobbuffet', 'gallade'], {'kadabra', 'venomoth', 'kirlia'}),
    'leader_blaine_01a3': ('하트골드 재대결 최종', ['torkoal', 'camerupt', 'rapidash', 'magcargo', 'houndoom', 'magmortar'], {'growlithe', 'ponyta', 'arcanine', 'magmar'}),
    'leader_koga_01a2': ('하트골드 사천왕 재대결', ['skuntank', 'venomoth', 'toxicroak', 'muk', 'crobat', 'swalot'], {'koffing', 'weezing', 'ariados', 'forretress', 'golbat'}),
    'leader_lt_surge_01a0': ('하트골드 재대결 최종', ['raichu', 'manectric', 'magnezone', 'electrode', 'pachirisu', 'electivire'], {'voltorb', 'pikachu', 'magneton', 'electabuzz'}),
    'leader_giovanni_015e': ('파이어레드 체육관, 뿔카노 2마리는 진화형으로', ['rhyperior', 'dugtrio', 'nidoqueen', 'nidoking', 'rhydon'], {'rhyhorn', 'onix', 'steelix', 'kangaskhan'}),
    'leader_erika_01a1': ('하트골드 재대결 최종', ['shiftry', 'jumpluff', 'victreebel', 'bellossom', 'tangrowth', 'roserade'], {'tangela', 'vileplume'}),
    'leader_misty_019f': ('하트골드 재대결 최종', ['starmie', 'quagsire', 'lapras', 'lanturn', 'floatzel', 'milotic'], {'staryu', 'golduck'}),
    'trainer_red_0003': ('하트골드 은빛산', ['pikachu', 'lapras', 'snorlax', 'venusaur', 'charizard', 'blastoise'], set()),
    'champion_steven_ps': ('에메랄드', ['skarmory', 'claydol', 'aggron', 'cradily', 'armaldo', 'metagross'], set()),
    'champion_cynthia_03a5': ('플래티넘', ['spiritomb', 'roserade', 'togekiss', 'lucario', 'milotic', 'garchomp'], set()),
    'champion_leon_ps': ('소드실드', ['aegislash', 'dragapult', 'haxorus', 'rhyperior', 'cinderace', 'charizard'], {'seismitoad', 'mrrime', 'inteleon', 'rillaboom'}),
}


def strength():
    """{RCT ID: 원작 최종 팀의 종족값 합 평균} (Cobblemon jar의 종 데이터, tools/.jarcache에 있을 때만)."""
    import zipfile
    jar = next((ROOT / 'tools/.jarcache').glob('Cobblemon-*.jar'), None)
    if not jar:
        return {}
    with zipfile.ZipFile(jar) as z:
        files = {Path(f).stem: f for f in z.namelist() if f.startswith('data/cobblemon/species/') and f.endswith('.json')}
        bst = lambda s: sum(json.loads(z.read(files[s]))['baseStats'].values())
        return {tid: sum(map(bst, final)) / len(final) for tid, (_, final, _) in ORIGINAL.items()}


# 거다이맥스 모습이 있는 종 (Cobblemon 1.8.4·Mega Showdown 1.3.3 종 데이터의 gmax 폼)
GMAX = {'alcremie', 'appletun', 'blastoise', 'butterfree', 'centiskorch', 'charizard', 'cinderace', 'coalossal', 'copperajah', 'corviknight',
        'drednaw', 'duraludon', 'eevee', 'flapple', 'garbodor', 'gengar', 'grimmsnarl', 'hatterene', 'inteleon', 'kingler', 'lapras', 'machamp',
        'melmetal', 'meowth', 'orbeetle', 'pikachu', 'rillaboom', 'sandaconda', 'snorlax', 'toxtricity', 'urshifu', 'venusaur'}
CAP = 5   # RCT relativeLevelCap: 레벨 제한 = 다음 상대 에이스 + 5


def COOLDOWN(n):
    """12. 관장·사천왕에게 지면 1분(1200틱) 뒤에 다시 도전 (gym/lose가 poke.gymcd에 다시 도전 가능 시각을 적음)."""
    return ['execute store result score #now poke.gymcd run time query gametime',
            f'execute if score @s poke.gymcd > #now poke.gymcd run return run function poke:gym/deny/{n} '
            '{msg:"관장에게 진 뒤 1분 동안은 다시 도전할 수 없어요."}']


def validate():
    """팀 검사: 기술을 그 포켓몬이 배울 수 있는지 (Cobblemon 종 데이터, COBBLEMON_SPECIES 폴더가 있을 때만)."""
    import os
    root = os.environ.get('COBBLEMON_SPECIES')   # 없으면 기술 검사만 건너뛰고 도구·레벨·기믹 검사는 언제나
    learn, bst = {}, {}
    for f in (Path(root).rglob('*.json') if root else []):
        d = json.loads(f.read_text(encoding='utf-8'))
        learn[f.stem] = {m.split(':', 1)[1] for m in d.get('moves', [])}
        bst[f.stem] = sum(d.get('baseStats', {}).values())
    bad = []
    for team in [g[5] for g in GYMS] + [e[3] for e in ELITE]:
        for m in (team if root else []):
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
        assert not any(m['heldItem'].endswith('eviolite') for m in team), '진화의 휘석은 쓰지 않음'
        items = [m['heldItem'] for m in team]
        assert len(items) == len(set(items)), f'한 팀에 같은 도구 두 번: {sorted(i for i in items if items.count(i) > 1)}'
        for m in team:   # Cobblemon·Mega Showdown 종 데이터에 거다이맥스 모습이 있는 포켓몬은 다이맥스할 때 거다이맥스로
            if m.get('gimmicks', {}).get('dynamax'):
                assert m['gimmicks'].get('gmax') == (m['species'] in GMAX), f"{m['species']}: 거다이맥스 설정 확인"
    check_gimmicks()
    for tid, *_, team in [(g[0], g[5]) for g in GYMS] + [(e[0], e[3]) for e in ELITE]:   # 원작 대표 포켓몬이 절반 이상
        src, final, extra = ORIGINAL[tid]
        assert sum(m['species'] in set(final) | extra for m in team) * 2 >= len(team), f'{tid}: 원작 대표 포켓몬이 절반 미만'
    st = strength()   # 순서 = 같은 레벨 기준 약한 순서
    if st:
        gyms = [g[0] for g in GYMS]
        gyms[1], gyms[4] = gyms[4], gyms[1]   # 2번·5번 관장은 사용자 지정으로 맞바꿈 (마티스 2번, 초련 5번)
        for group in (gyms, [e[0] for e in ELITE[:3]]):   # 레드는 최종 보스로 맨 뒤 고정
            assert [st[t] for t in group] == sorted(st[t] for t in group), f'강함 순서가 아님: {[(t, round(st[t], 1)) for t in group]}'


def gimmick_of(m):
    """포켓몬 하나가 쓰는 기믹 (M 메가, Z, D 다이맥스, T 테라) 또는 None. 둘 이상이면 오류."""
    g = [k for k, on in (('Z', m['heldItem'].endswith('ium_z')),
                         ('M', m['heldItem'].startswith(MS) and not m['heldItem'].endswith('ium_z')),
                         ('D', m.get('gimmicks', {}).get('dynamax')), ('T', 'tera' in m.get('gimmicks', {}))) if on]
    assert len(g) <= 1, f"{m['species']}: 기믹 여러 개 {g}"
    return g[0] if g else None


def gimmicks(team):
    """팀이 쓰는 기믹 집합. 같은 기믹을 두 번 쓰면 오류."""
    out = [g for m in team for g in [gimmick_of(m)] if g]
    assert len(out) == len(set(out)), f'같은 기믹 두 번: {out}'
    return set(out)


def check_gimmicks():
    """관장: Z 3번째부터, 메가 5번째부터, 다이맥스 7번째부터. 사천왕: 1~3은 3가지(조합이 서로 다름), 마지막은 4가지."""
    for n, g in enumerate(GYMS, 1):
        want = {k for k, start in (('Z', 3), ('M', 5), ('D', 7)) if n >= start}
        assert gimmicks(g[5]) == want, (n, gimmicks(g[5]), want)
    assert ELITE[-1][0] == 'trainer_red_0003', '레드는 맨 뒤'
    pairs = [(m['species'], g) for t in [g[5] for g in GYMS] + [e[3] for e in ELITE] for m in t for g in [gimmick_of(m)] if g]
    assert len(pairs) == len(set(pairs)), f'같은 포켓몬이 같은 기믹을 두 번: {sorted(p for p in pairs if pairs.count(p) > 1)}'
    e4 = [frozenset(gimmicks(e[3])) for e in ELITE]
    assert all(len(x) == 3 for x in e4[:3]) and len(set(e4[:3])) == 3 and e4[3] == {'Z', 'M', 'D', 'T'}, e4
    import zipfile, re   # 도구 id가 실제로 있는지 (모드 jar의 언어 파일 기준, 캐시가 있을 때만)
    known = set()
    for jar in (ROOT / 'tools/.jarcache').glob('*.jar'):
        with zipfile.ZipFile(jar) as z:
            for f in z.namelist():
                if re.fullmatch(r'assets/(cobblemon|mega_showdown)/lang/en_us\.json', f):
                    ns = f.split('/')[1]
                    known |= {f'{ns}:' + k.split('.')[2] for k in json.loads(z.read(f)) if k.startswith(f'item.{ns}.') and k.count('.') == 2}
    if known:
        bad = sorted({m['heldItem'] for t in [g[5] for g in GYMS] + [e[3] for e in ELITE] for m in t} - known)
        assert not bad, f'없는 도구: {bad}'


def text(s):
    return {'literal': s}


def write(path, obj):
    p = DATA / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')


LANG = {}   # 관장 대사 번역 키 → 한국어 (main 끝에서 모드 언어 파일로)


# 관장·사천왕마다 말투에 맞춘 대사: (배틀 시작, 도전자가 이겼을 때, 도전자가 졌을 때)
LINES = {
    'leader_brock_019e': ('바위처럼 단단한 내 포켓몬을 넘을 수 있겠어?', '훌륭해! 네 의지가 바위보다 단단했구나.', '아직 단단함이 부족해. 다시 와!'),
    'leader_lt_surge_01a0': ('짜릿하게 가 보자고! 전기 맛 좀 볼래?', '크으, 감전된 건 나였군! 배지는 네 거다.', '하하! 아직 찌릿함이 모자라!'),
    'leader_blaine_01a3': ('불꽃처럼 뜨거운 배틀을 보여 주지!', '내 불꽃이 꺼지다니… 대단하군!', '다 타 버렸군! 화상 치료제는 챙겨 왔나?'),
    'leader_koga_01a2': ('독은 조용히 스며드는 법… 각오는 됐나?', '독에도 굴하지 않다니, 훌륭하군.', '독이 온몸에 퍼졌군. 다시 오너라.'),
    'leader_sabrina_01a4': ('네가 어떻게 싸울지… 이미 보여.', '…이 결과는 보이지 않았어. 인정할게.', '예상대로야. 다시 와.'),
    'leader_giovanni_015e': ('땅을 뒤흔드는 힘을 보여 주마.', '흠… 네 힘을 인정하지. 배지를 가져가라.', '아직 내 상대가 아니다.'),
    'leader_erika_01a1': ('어머, 도전자시네요. 꽃처럼 우아하게 싸워 볼까요?', '어머나… 제가 졌네요. 정말 멋진 배틀이었어요.', '후훗, 조금 더 꽃을 피워서 오세요.'),
    'leader_misty_019f': ('물 타입의 진짜 실력, 보여 줄게!', '으으, 졌다! 너 정말 강하구나.', '흥! 물살에 다 쓸려 갔네!'),
    'champion_steven_ps': ('강철처럼 단단한 힘을 보여 주지.', '훌륭해. 너와 포켓몬의 유대가 빛나는군.', '아직이야. 더 단단해져서 와.'),
    'champion_cynthia_03a5': ('챔피언으로서 전력을 다할게.', '…대단해. 너와 포켓몬의 힘은 진짜야.', '좋은 승부였어. 다시 기다릴게.'),
    'champion_leon_ps': ('자, 챔피언 타임이다!', '하하, 최고의 배틀이었어! 넌 진짜 챔피언이야!', '아직 챔피언 타임은 끝나지 않았어!'),
    'trainer_red_0003': ('……', '……! (조용히 고개를 끄덕인다)', '……'),
}


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
        })
    # 3.4.0: RCT 기본 전리품(관장 그룹: 특성패치·특성캡슐·변함없는돌·행복의알 중 하나)이 관장 발밑에 떨어졌음 → 비움 (보상은 데이터팩 award가 줌)
    write(f'rctmod/loot_table/trainers/single/{tid}.json', {'pools': []})
    # RCT 0.19는 대사를 dialogs/trainers/<ID>.json에서 읽음 (mobs 파일의 dialog는 무시돼 영어 기본 대사가 나왔음)
    lines = {
        'on_battle_start': LINES[tid][0], 'on_battle_won': LINES[tid][2], 'trainer_won': LINES[tid][2],
        'on_battle_lost': LINES[tid][1], 'trainer_lost': LINES[tid][1],
        'on_cooldown': '조금 쉬었다가 다시 와 줘.', 'over_level_cap': '레벨이 너무 높은 포켓몬이 있네. 레벨 제한에 맞춰서 와 줘!',
        'low_level_cap': '아직 나와 싸울 때가 아니야. 앞 체육관부터 이기고 와!',
        'missing_pokemon': '싸울 수 있는 포켓몬이 없잖아!', 'missing_required_trainer': '앞 체육관의 배지를 먼저 모아 와!',
        'missing_required_trainer_leader': '앞 체육관의 배지를 먼저 모아 와!', 'missing_required_trainer_e4': '사천왕은 순서대로 이겨야 해!',
        'missing_required_trainer_champ': '사천왕은 순서대로 이겨야 해!', 'missing_required_series': '아직 도전할 수 없어.',
        'wrong_series': '아직 도전할 수 없어.', 'player_busy': '지금은 다른 배틀 중이구나.', 'trainer_busy': '지금은 다른 도전자와 싸우는 중이야.',
        'unknown_reason': '지금은 배틀할 수 없어.'}
    # 말풍선은 번역 키만 씀(ChatUtils.reply → addMessage(getTranslatable())): 키가 없으면 배틀이 끝날 때 서버가 꺼짐.
    # 그래서 키 + 같은 문장(채팅용 대체 문장)을 넣고, 키의 한국어는 모드 언어 파일(LANG)에 둠
    keys = {k: f'pokeserver.dialog.{tid}.{k}' for k in lines}
    LANG.update({keys[k]: v for k, v in lines.items()})
    write(f'rctmod/dialogs/trainers/single/{tid}.json', {k: [{'translatable': keys[k], 'literal': v}] for k, v in lines.items()})   # 몹 파일과 같은 하위 폴더


def main():
    validate()
    write(f'rctmod/series/{SERIES}.json', {
        'title': text('잡켓몬 리그'), 'description': text('배지 8개를 모은 뒤 사천왕을 한 번에 모두 이겨라'),
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
    # 모든 언어가 en_us로 되돌아가므로 en_us 한 파일에 한국어를 둠
    lang = ROOT / 'mod/src/main/resources/assets/pokeserver/lang/en_us.json'
    lang.parent.mkdir(parents=True, exist_ok=True)
    lang.write_text(json.dumps(LANG, ensure_ascii=False, indent=1, sort_keys=True), encoding='utf-8')
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
ARENA_CHUNKS = [W.chunks(W.ARENA_REGION), W.chunks(W.E4_REGION)]   # 경기장·사천왕 본부 청크 (관장 소환 때 불러옴, 256청크 한도라 둘로)


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
            f"minecraft:lore=['{{\"text\":\"잡켓몬 리그 {n}번 체육관 배지\",\"color\":\"gray\",\"italic\":false}}'],"
            f"minecraft:custom_model_data={1000 + n},minecraft:custom_data={{pokeserver:\"badge{n}\"}}] 1")


# 관장 보상 기술머신: 그 타입 대표 기술 (Cobblemon data/cobblemon/tms에 있는 것), 경험사탕은 뒤로 갈수록 큰 것
GYM_TM = {'바위': 'stoneedge', '전기': 'thunderbolt', '불꽃': 'flamethrower', '독': 'sludgebomb',
          '에스퍼': 'psychic', '땅': 'earthquake', '풀': 'energyball', '물': 'surf'}
CANDY_N = 10   # 관장 보상 경험사탕 개수
CANDY = ['exp_candy_s'] * 2 + ['exp_candy_m'] * 2 + ['exp_candy_l'] * 2 + ['exp_candy_xl'] * 2


def gym_items(n, typ):
    """관장 보상 물품: 경험사탕 CANDY_N개 + 그 타입 기술머신 1장."""
    return [f'give @s cobblemon:{CANDY[n - 1]} {CANDY_N}',
            f'give @s cobblemon:technical_machine[cobblemon:tm_move={{move:"{GYM_TM[typ]}"}}] 1',
            f'tellraw @s {{"text":"보상: 경험사탕 {CANDY_N}개, 기술머신({GYM_TM[typ]}) 1장","color":"aqua"}}']


def prize(amount):
    """상금: 관장은 레벨 제한 × 200원 (4,000~18,000), 사천왕 클리어 30,000원. 돈은 모드 명령이라 mod/prize/<금액> (기본 물품 mod/kit과 같은 방식)."""
    fn(f'mod/prize/{amount}.mcfunction', ['# 자동 생성: tools/build_league.py. 체육관·사천왕 상금',
                                         f'pokeserver money give @s {amount}',
                                         f'tellraw @s {{"text":"상금 {amount:,}원을 받았어요!","color":"gold"}}'])
    return f'function poke:mod/prize/{amount}'


# 다음 관장이 새 기믹을 처음 쓰기 바로 전 관장을 이기면 그 기믹 도구를 줌 (배틀 잠금은 CobblemonHooks.gimmickLocked가 같은 배지 수로)
KEY_ITEMS = {2: ('z_ring', 'Z링', 'Z기술'), 4: ('mega_bracelet', '메가링', '메가진화'),
             6: ('dynamax_band', '다이맥스밴드', '다이맥스'), 8: ('tera_orb', '테라스탈 오브', '테라스탈')}


def key_item(n):
    if n not in KEY_ITEMS:
        return []
    item, name, gimmick = KEY_ITEMS[n]
    return [f'give @s mega_showdown:{item} 1',
            f'tellraw @s {{"text":"{name}{josa(name)} 받았어요! 손에 들거나 장신구 칸에 끼면 배틀에서 {gimmick}{josa(gimmick)} 쓸 수 있어요.","color":"aqua"}}']


def functions():
    assert [g[2] for g in GYMS] == W.GYM_TYPES, '경기장 꾸밈 순서(build_world.GYM_TYPES)가 관장 순서와 다름'
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
            'tellraw @s {"text":"관장을 우클릭하면 배틀이 시작돼요. 포기하려면 관장 맞은편 주황 발판을 밟으세요. 도전 중엔 G 메뉴 이동을 못 해요.","color":"gray"}'])
        fn(f'gym/award/{n}.mcfunction', [
            f'tag @s add poke.badge{n}', badge_item(n, badge, color), f'function poke:mod/reward/{n}',
            f'title @s title {{"text":"{badge} 획득!","color":"gold"}}',
            # 16. 클리어 공지 (축하). 서버 전체에서 처음 깬 사람은 이 공지 대신 다른 색 "퍼스트 클리어" 공지 (기록은 storage poke:first, 월드 초기화 때 같이 지워짐)
            f'execute if data storage poke:first g{n} run tellraw @a [{{"text":"[리그] ","color":"gold"}},{{"selector":"@s"}},{{"text":"님이 {n}번째 체육관을 클리어하였습니다! (관장 {name} · {badge}) 축하합니다!","color":"yellow"}}]',
            f'execute unless data storage poke:first g{n} run tellraw @a [{{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true}},{{"selector":"@s"}},{{"text":"님이 서버 최초로 {n}번째 체육관을 클리어하였습니다! (관장 {name} · {badge}) 모두 축하해 주세요!","color":"aqua"}}]',
            f'execute unless data storage poke:first g{n} run tag @s add poke.firstclear',   # 칭호 "퍼스트 클리어"
            f'data modify storage poke:first g{n} set value 1',
            prize((max(m['level'] for m in GYMS[n - 1][5]) + CAP) * 200), 'function poke:gym/leave'])
        # 모드 아이템(기믹 도구·경험사탕·기술머신)은 mod/ 함수로: 모드가 없는 데이터팩 시험에서 이 함수만 못 읽고 배지 지급은 그대로
        fn(f'mod/reward/{n}.mcfunction', [*key_item(n), *gym_items(n, typ)])
        px, pz, w, d = g['exit']
        pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1},tag=!poke.battling] run function poke:gym/leave')
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
        'execute if entity @s[tag=poke.e4tried] run tag @s add poke.e4retry', 'tag @s add poke.e4tried',   # 두 번째 도전부터 표시
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
    fn('mod/reward/e4.mcfunction', ['give @s cobblemon:rare_candy 10', 'give @s cobblemon:ability_patch 1'])
    fn('e4/clear.mcfunction', ['tag @s add poke.e4clear', tp(e['inside'][4]), prize(30000), 'function poke:mod/reward/e4',
                               'title @s title {"text":"사천왕 클리어!","color":"gold"}',
                               'title @s subtitle {"text":"명예의 전당에 이름을 올렸습니다","color":"yellow"}',
                               'execute if data storage poke:first e4 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕을 클리어하고 챔피언이 되었습니다! 축하합니다!","color":"gold"}]',
                               'execute unless data storage poke:first e4 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 사천왕을 클리어하고 첫 챔피언이 되었습니다! 모두 축하해 주세요!","color":"aqua"}]',
                               'execute unless data storage poke:first e4 run tag @s add poke.firstclear',
                               'execute unless entity @s[tag=poke.e4retry] run tag @s add poke.e4first',   # 칭호 "무적의 챔피언": 첫 도전에 클리어
                               'data modify storage poke:first e4 set value 1',
                               '# 도전 끝: 점수를 풀어야 G 메뉴 이동이 되고 다음 도전자가 사천왕에 들어올 수 있음',
                               'function poke:gym/release'])
    px, pz, w, d = e['exit']
    pads.append(f'execute in poke:town as @a[x={px},y={Y},z={pz},dx={w - 1},dy=1,dz={d - 1}] run function poke:util/tp with storage poke:config gym')   # 명예의 전당 나가기 (도전은 클리어 때 이미 풀림)
    # 배틀 중엔 발판이 안 먹음 (poke.battling은 모드가 매 틱 붙임): 배틀 도중 순간이동으로 빠져 재도전 대기를 피하지 못하게
    pads += [f'execute in poke:town as @a[x={gx},y={Y},z={gz},dx=0,dy=1,dz=0,tag=!poke.battling] run function poke:gym/leave' for gx, gz, _, _ in e['giveup']]
    win.append('execute if score @s poke.gym matches 9 run function poke:e4/win')
    for k, (tid, *_r) in enumerate(ELITE):
        mx, mz, myaw = e['member'][k]
        spawn += spawn_lines(tid, mx, mz, myaw)
    fn('league/pads.mcfunction', pads)
    fn('league/spawn_tick.mcfunction', [
        '# 관장 소환 준비: 경기장 청크를 불러오고 3초 뒤 접속한 플레이어 한 명으로 소환',
        'execute unless data storage poke:state {leaders:2} run scoreboard players set #lead poke.timer 0',
        *[f'execute unless data storage poke:state {{leaders:2}} in poke:town run forceload add {c}' for c in ARENA_CHUNKS],
        'data modify storage poke:state leaders set value 2', 'scoreboard players add #lead poke.timer 1',
        'execute if score #lead poke.timer matches 60.. as @a[limit=1] run function poke:mod/spawn_leaders'])
    # 체육관 안내원 화면(모드)이 읽는 목록
    rgb = lambda c: c[0] << 16 | c[1] << 8 | c[2]
    league = [dict(n=n, title=f'{n}번 체육관', leader=f'관장 {name}', type=f'{typ} 타입', badge=badge, color=rgb(color),
                   level=max(m['level'] for m in team) + CAP, prize=(max(m['level'] for m in team) + CAP) * 200,   # 상금 = award의 prize()와 같은 식
                   reward=[f'경험사탕 {CANDY_N}', '기술머신'] + ([KEY_ITEMS[n][1]] if n in KEY_ITEMS else []))
              for n, (_, name, typ, badge, color, team) in enumerate(GYMS, 1)]
    league.append(dict(n=9, title='사천왕 (챔피언 4명 연속)', leader='·'.join(e[1] for e in ELITE), type='·'.join(e[2].split()[0] for e in ELITE) + ' 챔피언',
                       badge='명예의 전당', color=0x8A4FD0, level=100))
    (ROOT / 'pack/config/pokeserver/league.json').write_text(json.dumps(league, ensure_ascii=False, indent=1), encoding='utf-8')
    fn('gym/leave.mcfunction', ['# 경기장·사천왕에서 나가기 (나가기 발판, 승리, 패배, 재접속): 체육관 로비로',
                                'execute if score @s poke.gym matches 1.. run function poke:util/tp with storage poke:config gym',
                                'function poke:gym/release'])
    fn('gym/win.mcfunction', ['# 모드가 호출: 체육관 안에서 NPC 배틀을 이겼을 때', *win])
    # 배틀이 시작되는 순간(모드 BATTLE_STARTED_PRE) 도전자를 정해진 자리로: 관장과 필드를 사이에 두고 마주 봄 → 포켓몬이 가운데에 나와 화면에 잘 보임
    place = [f'execute if score @s poke.gym matches {n} run {tp(W.gym_geom(n)["battle"])}' for n in range(1, len(GYMS) + 1)]
    place += [f'execute if score @s poke.gym matches 9 if score @s poke.e4 matches {k} run {tp(e["inside"][k])}' for k in range(4)]
    fn('gym/place.mcfunction', ['# 모드가 호출: 체육관·사천왕 배틀이 시작될 때', *place])
    fn('gym/lose.mcfunction', ['# 모드가 호출: 체육관 안에서 NPC 배틀을 지거나 도망쳤을 때',
                               'execute unless score @s poke.gym matches 1.. run return 0',
                               'execute if score @s poke.gym matches 9 run tellraw @s {"text":"사천왕 도전 실패... 1분 뒤에 처음(첫 번째 사천왕)부터 다시 도전해요.","color":"red"}',
                               'execute if score @s poke.gym matches 1..8 run tellraw @s {"text":"관장에게 졌어요. 포켓몬을 회복하고 1분 뒤에 다시 도전하세요!","color":"red"}',
                               'execute store result score @s poke.gymcd run time query gametime',
                               'scoreboard players add @s poke.gymcd 1200',
                               'function poke:gym/leave'])
    fn('mod/spawn_leaders.mcfunction', [
        '# 관장·사천왕 소환 (RCT 소환 명령은 플레이어가 실행해야 해서, 접속한 플레이어로 실행됨)',
        'kill @e[type=rctmod:trainer,tag=poke.leader]', *spawn,
        'data modify storage poke:state leaders set value 1', *[f'execute in poke:town run forceload remove {c}' for c in ARENA_CHUNKS]])


def spawn_lines(tid, x, z, yaw):
    # Invulnerable: 플레이어가 때려서 관장을 없애지 못하게 (없어지면 서버를 다시 켤 때까지 도전 불가)
    at = f'execute in poke:town positioned {x} {Y} {z}'
    return [f'{at} run rctmod trainer summon_persistent {tid} ~ ~ ~',
            f'{at} run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {{NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}}',
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
    shape = {'회색배지': 1, '블루배지': 2, '오렌지배지': 3, '무지개배지': 4, '핑크배지': 5, '골드배지': 6, '크림슨배지': 7, '그린배지': 8}   # 배지 모양은 관장을 따라감
    for n, (_, _, _, badge, color, _) in enumerate(GYMS, 1):
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        shapes[shape[badge]](d, color + (255,))
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
