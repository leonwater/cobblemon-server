"""상점 목록 생성기 → pack/config/pokeserver/shop.json.  사용: python3 tools/build_shop.py

- 포켓몬 물품(Cobblemon·Mega Showdown)만 배지로 해금. 키우는 순서대로: 잡기·회복·기본 성장은 낮은 배지,
  실전용 희귀 물품(지닌 도구 상위·성격·개체값)은 높은 배지. 마인크래프트 물품(건축·농장·광물·도구)은 처음부터.
- 특수 기믹 물품은 그 기믹을 배틀에서 쓸 수 있게 되는 배지에 맞춰 풀림: Z크리스탈 2 (Z링), 메가스톤 4, 다이맥스 6, 테라 조각 8.
- 판매: 배지 해금 없이 전부 팔 수 있음. 판매가 = 구매가 ÷ 4 (사서 바로 되팔아 이득 보는 일 없음). 구매 0원 = 판매만.\n- 코블몬에서 얻을 수 있는 물품은 상점 목록에 없더라도 모두 '판매만'으로 들어감 (obtainable_missing·sell_rule, 새 분류 '기타').
- 가격 근거: 몬스터볼·회복약·진화의 돌·비타민은 원작(스칼렛·바이올렛) 상점 가격, 원작에서 BP 교환인 실전 도구는 희귀도에 맞춰 정함.
- 검사: 아이템 id가 실제로 있는지(모드 jar·마인크래프트 jar 언어 파일), 조합 재료보다 완성품이 싸지 않은지.
"""
import json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C, M, MS = 'cobblemon:', 'minecraft:', 'mega_showdown:'


def e(item, buy, badges=0, sell=None, daily=None):
    """daily: 매일 그중 몇 개만 살 수 있는 묶음 ('tm' 기술머신, 'gimmick' 특수 기믹 물품) — 판매는 늘 가능 (Shop.java가 날마다 고름)."""
    return {'item': item, 'buy': buy, 'sell': buy // 4 if sell is None else sell, **({'badges': badges} if badges else {}), **({'daily': daily} if daily else {})}


# 야생에서 얻을 수 있는 귀중품(메가스톤·Z크리스탈·다이버섯·진화의 돌)은 파는 값을 구매가의 1/20로 (평소 1/4). 야생에서 주워 팔아 큰돈 버는 것 막기
WILD_SELL = 20


def wild(item, buy, badges=0, daily=None):
    return e(item, buy, badges, sell=buy // WILD_SELL, daily=daily)


def sell_only(item, sell):
    return {'item': item, 'buy': 0, 'sell': sell}


def ms_items():
    """Mega Showdown jar에서 메가스톤·Z크리스탈·테라 조각 목록."""
    jar = next((ROOT / 'tools/.jarcache').glob('mega_showdown-*.jar'))
    with zipfile.ZipFile(jar) as z:
        en = json.loads(z.read('assets/mega_showdown/lang/en_us.json'))
        zc = json.loads(z.read('data/mega_showdown/tags/item/z_crystal.json'))['values']
    ids = [k.split('.')[2] for k in en if k.startswith('item.mega_showdown.') and k.count('.') == 2]
    megas = sorted(i for i in ids if i.endswith('ite') or i[:-1].endswith('ite_') and i[-1] in 'xyz')   # 리자몽나이트 X·Y처럼 _x·_y로 끝나는 것도 (예전엔 빠졌음)
    return megas, [z.split(':')[1] for z in zc], sorted(i for i in ids if i.endswith('_tera_shard'))


TYPES = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug', 'rock',
         'ghost', 'dragon', 'dark', 'steel', 'fairy']
TYPE_Z = {'normalium_z', 'firium_z', 'waterium_z', 'electrium_z', 'grassium_z', 'icium_z', 'fightinium_z', 'poisonium_z', 'groundium_z',
          'flyinium_z', 'psychium_z', 'buginium_z', 'rockium_z', 'ghostium_z', 'dragonium_z', 'darkinium_z', 'steelium_z', 'fairium_z'}
LEGEND_MEGA = {'mewtwonite_x', 'mewtwonite_y', 'latiasite', 'latiosite', 'diancite', 'zygardite', 'darkranite', 'heatranite', 'magearnite', 'zeraorite'}


def categories():
    megas, zs, shards = ms_items()
    cats = base_categories(megas, zs, shards)
    have = {x['item'] for _, _, xs in cats for x in xs}
    extra = {}
    for i in obtainable_missing(have):
        cat, price = sell_rule(i)
        extra.setdefault(cat, []).append(sell_only(C + i, price))
    by = {n: xs for n, _, xs in cats}
    for cat, xs in extra.items():
        if cat in by: by[cat].extend(xs)                         # 기존 분류는 끝에 붙임 (앞쪽 순서가 안 바뀌게)
    return cats + [build_category()]   # '기타'(판매만 되는 코블몬 물품)는 2.6.0에서 뺌: 배지 8개여도 살 게 없는 분류


COLORS = ['white', 'light_gray', 'gray', 'black', 'brown', 'red', 'orange', 'yellow', 'lime', 'green', 'cyan', 'light_blue', 'blue',
          'purple', 'magenta', 'pink']
WOODS = ['oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry']


def build_category():
    """건축 블록 (생활 상인). 값은 재료 값 이상: 판자 = 원목 20 ÷ 4, 사암 = 모래 4개, 색 블록 = 기본 블록 + 염료 몫."""
    return ('건축', M + 'oak_planks', [
        *[e(M + w + '_log', 20) for w in WOODS],
        e(M + 'stone', 5), e(M + 'cobblestone', 3), e(M + 'smooth_stone', 8), e(M + 'stone_bricks', 8), e(M + 'deepslate', 5),
        e(M + 'sand', 3), e(M + 'gravel', 3), e(M + 'dirt', 2), e(M + 'grass_block', 5), e(M + 'clay_ball', 5), e(M + 'glass', 10),
        e(M + 'bricks', 20), e(M + 'white_concrete', 15), e(M + 'terracotta', 12), e(M + 'white_wool', 15), e(M + 'quartz_block', 200),
        *[e(M + w + '_planks', 5) for w in WOODS], e(M + 'bamboo_planks', 5),
        *[e(M + s, 6) for s in ('andesite', 'diorite', 'granite', 'polished_andesite', 'polished_diorite', 'polished_granite',
                                'cobbled_deepslate', 'polished_deepslate', 'deepslate_bricks', 'deepslate_tiles', 'tuff', 'polished_tuff',
                                'tuff_bricks', 'calcite')],
        *[e(M + s, 10) for s in ('mossy_cobblestone', 'mossy_stone_bricks', 'cracked_stone_bricks', 'chiseled_stone_bricks')],
        e(M + 'red_sand', 3), *[e(M + s, 15) for s in ('sandstone', 'cut_sandstone', 'smooth_sandstone', 'red_sandstone',
                                                         'cut_red_sandstone', 'smooth_red_sandstone')],
        e(M + 'packed_mud', 8), e(M + 'mud_bricks', 8), e(M + 'moss_block', 10), e(M + 'snow_block', 5), e(M + 'hay_block', 200),
        e(M + 'glass_pane', 4),
        *[e(M + s, 200) for s in ('quartz_bricks', 'quartz_pillar', 'smooth_quartz', 'chiseled_quartz_block')],
        e(M + 'prismarine', 30), e(M + 'prismarine_bricks', 60), e(M + 'dark_prismarine', 60),
        e(M + 'copper_block', 250), e(M + 'cut_copper', 250),
        *[e(M + c + '_concrete', 15) for c in COLORS if c != 'white'],
        *[e(M + c + '_wool', 15) for c in COLORS if c != 'white'],
        *[e(M + c + '_terracotta', 15) for c in COLORS],
        *[e(M + c + '_stained_glass', 15) for c in COLORS]])


TM_PRICE = 10000   # 기술머신 1장 (배지 없이). 원작 상점 기술머신 값(썬·문 포켓몬센터 10,000~30,000)의 기본값, 몬스터볼 200원 기준을 원작과 같게 맞춘 이 서버 물가에 그대로


def tm_moves():
    """코블몬 기술머신이 있는 기술 이름 (data/cobblemon/tms/*.json)."""
    jar = next((ROOT / 'tools/.jarcache').glob('Cobblemon-*.jar'))
    with zipfile.ZipFile(jar) as z:
        return sorted(f.split('/')[-1][:-5] for f in z.namelist() if f.startswith('data/cobblemon/tms/') and f.endswith('.json'))


# 4. 농장 물품으로 만든 것 (판매만): 결과 1개(쿠키는 8개 중 1개)를 만드는 재료. 우유·그릇처럼 값이 없는 재료도 종류에는 셈
CRAFTED = {
    M + 'bread': {M + 'wheat': 3}, M + 'cookie': {M + 'wheat': 2 / 8, M + 'cocoa_beans': 1 / 8},
    M + 'cake': {M + 'wheat': 3, M + 'sugar': 2, M + 'egg': 1, M + 'milk_bucket': 3}, M + 'pumpkin_pie': {M + 'pumpkin': 1, M + 'sugar': 1, M + 'egg': 1},
    M + 'sugar': {M + 'sugar_cane': 1}, M + 'baked_potato': {M + 'potato': 1}, M + 'beetroot_soup': {M + 'beetroot': 6, M + 'bowl': 1},
    M + 'golden_carrot': {M + 'carrot': 1, M + 'gold_nugget': 8}, M + 'golden_apple': {M + 'apple': 1, M + 'gold_ingot': 8},
    M + 'melon': {M + 'melon_slice': 9},
}
# 판매가 = 재료 판매가 합 × (1.1 + 0.15 × (재료 종류 - 1)), 올림: 재료 1종 +10%, 2종 +25%, 3종 +40%, 4종 +55%
#   (재료가 단순하면 그냥 파는 것과 큰 차이 없고, 여러 가지를 모아 만들수록 더 받음)
BASE_SELL = {M + 'wheat': 5, M + 'cocoa_beans': 5, M + 'egg': 2, M + 'pumpkin': 15, M + 'sugar_cane': 7, M + 'potato': 5, M + 'beetroot': 5,
             M + 'carrot': 5, M + 'gold_nugget': 60 / 9, M + 'apple': 7, M + 'gold_ingot': 60, M + 'melon_slice': 2}


def crafted_sell():
    import math
    sell = dict(BASE_SELL)
    out = {}
    for item in (M + 'sugar',) + tuple(k for k in CRAFTED if k != M + 'sugar'):   # 설탕 값이 케이크·파이 재료라 먼저
        mats = CRAFTED[item]
        cost = sum(sell.get(m, 0) * n for m, n in mats.items())
        out[item] = sell[item] = math.ceil(cost * (1.1 + 0.15 * (len(mats) - 1)))
    return {k[len(M):]: v for k, v in out.items()}


CRAFTED_SELL = crafted_sell()
# 5. 광물 블록 판매가: 재료 9개 판매가 합 + 약 10%
MINERAL_BLOCKS = {'coal_block': 70, 'iron_block': 300, 'gold_block': 600, 'redstone_block': 70, 'lapis_block': 110, 'emerald_block': 1000,
                  'diamond_block': 3000, 'netherite_block': 50000, 'amethyst_block': 45}
MINERAL_OF = {'coal_block': ('coal', 9), 'iron_block': ('iron_ingot', 9), 'gold_block': ('gold_ingot', 9), 'redstone_block': ('redstone', 9),
              'lapis_block': ('lapis_lazuli', 9), 'emerald_block': ('emerald', 9), 'diamond_block': ('diamond', 9),
              'netherite_block': ('netherite_ingot', 9), 'amethyst_block': ('amethyst_shard', 4)}


def base_categories(megas, zs, shards):
    return [
        ('볼', C + 'poke_ball', [   # ── 코블몬 상인 ──
            e(C + 'poke_ball', 200), e(C + 'premier_ball', 300), e(C + 'heal_ball', 300),
            e(C + 'great_ball', 600, 1), e(C + 'nest_ball', 1000, 1), e(C + 'net_ball', 1000, 1),
            e(C + 'dive_ball', 1000, 2), e(C + 'repeat_ball', 1000, 2), e(C + 'ultra_ball', 800, 3), e(C + 'dusk_ball', 1000, 3),
            e(C + 'luxury_ball', 1000, 4), *[e(C + b, 1000, 5) for b in ('level_ball', 'lure_ball', 'heavy_ball', 'moon_ball', 'love_ball', 'friend_ball', 'fast_ball')],
            e(C + 'timer_ball', 1500, 8), e(C + 'quick_ball', 1500, 8),
            e(C + 'poke_rod', 500), e(C + 'pokerod_smithing_template', 2000, sell=200)]),   # 포켓몬은 코블몬 낚싯대로만 낚임. 형판 + 낚싯대 + 볼 → 그 볼 낚싯대
        ('회복', C + 'potion', [
            e(C + 'potion', 200), e(C + 'antidote', 100), e(C + 'awakening', 100), e(C + 'ice_heal', 100),
            e(C + 'paralyze_heal', 300), e(C + 'burn_heal', 300), e(C + 'super_potion', 700, 1),
            e(C + 'revive', 2000, 2), e(C + 'full_heal', 400, 2), e(C + 'hyper_potion', 1500, 3), e(C + 'ether', 1200, 3),
            e(C + 'elixir', 3000, 4), e(C + 'max_potion', 2500, 5), e(C + 'max_ether', 2000, 5), e(C + 'full_restore', 3000, 6),
            e(C + 'max_revive', 4000, 7), e(C + 'max_elixir', 4500, 7)]),
        ('성장', C + 'exp_candy_m', [
            e(C + 'exp_candy_xs', 300), e(C + 'exp_candy_s', 800), e(C + 'everstone', 1000), e(C + 'exp_candy_m', 1500, 1), e(C + 'exp_share', 8000, 1),
            *[wild(C + s, 3000, 1) for s in ('fire_stone', 'water_stone', 'thunder_stone', 'leaf_stone')],
            wild(C + 'moon_stone', 3000, 2), e(C + 'blank_tm', 1000, 2), e(C + 'tm_machine', 5000, 2),
            *[wild(C + s, 3000, 3) for s in ('sun_stone', 'shiny_stone', 'dusk_stone', 'dawn_stone', 'ice_stone')],
            e(C + 'exp_candy_l', 3000, 3), e(C + 'lucky_egg', 10000, 4),
            *[e(C + s, 5000, 4) for s in ('link_cable', 'metal_coat', 'kings_rock', 'dragon_scale', 'upgrade', 'dubious_disc', 'protector',
                                          'electirizer', 'magmarizer', 'reaper_cloth', 'prism_scale', 'razor_claw', 'razor_fang',
                                          'deep_sea_tooth', 'deep_sea_scale', 'sachet', 'whipped_dream')],
            e(C + 'exp_candy_xl', 6000, 5), e(C + 'rare_candy', 12000, 6), e(C + 'pp_up', 9800, 3), e(C + 'pp_max', 20000, 7)]),
        ('기술머신', C + 'technical_machine', [   # 7. 코블몬 기술머신 전부 중 마인크래프트 하루마다 5개만, 배지 없이 (사기만)
            e(C + 'technical_machine#' + m, TM_PRICE, sell=0, daily='tm') for m in tm_moves()]),
        ('도구', C + 'leftovers', [
            # 배지 1: 배틀용 열매 (지니면 알아서 먹음)
            *[e(C + b + '_berry', 200, 1) for b in ('oran', 'cheri', 'chesto', 'pecha', 'rawst', 'aspear', 'persim')],
            e(C + 'sitrus_berry', 500, 2), e(C + 'lum_berry', 800, 3), e(C + 'leppa_berry', 500, 3),
            # 배지 2: 타입 강화 도구 (원작 상점 판매), 3~4: 날씨 바위·허브 등 보조, 5: 실전 기본, 6: 구애 시리즈·생명의구슬
            *[e(C + i, 3000, 2) for i in ('charcoal_stick', 'mystic_water', 'magnet', 'miracle_seed', 'never_melt_ice', 'black_belt',
                                          'poison_barb', 'soft_sand', 'sharp_beak', 'twisted_spoon', 'silver_powder', 'hard_stone',
                                          'spell_tag', 'dragon_fang', 'black_glasses', 'silk_scarf', 'fairy_feather')],
            e(C + 'quick_claw', 4000, 3), e(C + 'scope_lens', 4000, 3), e(C + 'shell_bell', 4000, 3), e(C + 'white_herb', 4000, 3),
            e(C + 'mental_herb', 4000, 3), e(C + 'power_herb', 4000, 3), e(C + 'wide_lens', 4000, 3), e(C + 'zoom_lens', 4000, 3),
            *[e(C + i, 8000, 4) for i in ('heat_rock', 'damp_rock', 'icy_rock', 'smooth_rock', 'light_clay', 'focus_band', 'muscle_band',
                                          'wise_glasses', 'expert_belt', 'toxic_orb', 'flame_orb', 'binding_band', 'grip_claw', 'eject_button',
                                          'red_card', 'throat_spray', 'blunder_policy', 'room_service', 'terrain_extender', 'loaded_dice')],
            *[e(C + i, 15000, 5) for i in ('leftovers', 'black_sludge', 'rocky_helmet', 'focus_sash', 'eviolite', 'assault_vest',
                                           'heavy_duty_boots', 'weakness_policy', 'covert_cloak', 'clear_amulet', 'safety_goggles',
                                           'protective_pads', 'utility_umbrella', 'punching_glove', 'air_balloon')],
            *[e(C + i, 25000, 6) for i in ('choice_band', 'choice_specs', 'choice_scarf', 'life_orb')],
            *[sell_only(C + t + '_gem', 20) for t in TYPES]]),   # 타입 주얼 (포켓몬 지닌 도구, 판매만)
        ('능력치', C + 'modest_mint', [
            # 노력치: 날개(+1) 배지 2, 비타민(+10)·내리는 열매(-10) 배지 3, 경단(+10)·리셋 경단 배지 4
            *[e(C + f + '_feather', 300, 2) for f in ('health', 'muscle', 'resist', 'genius', 'clever', 'swift')],
            *[e(C + v, 10000, 3) for v in ('hp_up', 'protein', 'iron', 'calcium', 'zinc', 'carbos')],
            *[e(C + b + '_berry', 1000, 3) for b in ('pomeg', 'kelpsy', 'qualot', 'hondew', 'grepa', 'tamato')],
            *[e(C + f + '_mochi', 5000, 4) for f in ('health', 'muscle', 'resist', 'genius', 'clever', 'swift')], e(C + 'fresh_start_mochi', 8000, 4),
            *[e(C + p, 3000, 4) for p in ('power_weight', 'power_bracer', 'power_belt', 'power_lens', 'power_band', 'power_anklet')],
            e(C + 'ability_capsule', 10000, 5),
            *[e(C + n + '_mint', 20000, 6, sell=100) for n in ('lonely', 'adamant', 'naughty', 'brave', 'bold', 'impish', 'lax', 'relaxed', 'modest',
                                                     'mild', 'rash', 'quiet', 'calm', 'gentle', 'careful', 'sassy', 'timid', 'hasty', 'jolly',
                                                     'naive', 'serious')],
            # 개체값 사탕 (Cobblemon 1.8 하이퍼 트레이닝: 그 능력 개체값 +1 / 내림 사탕은 -1)
            *[e(C + c + '_candy', 5000, 7) for c in ('health', 'mighty', 'tough', 'smart', 'courage', 'quick')],
            *[e(C + c + '_candy', 1000, 7) for c in ('sickly', 'weak', 'brittle', 'numb', 'coward', 'slow')],
            e(C + 'ability_patch', 50000, 8)]),
        ('기믹', MS + 'mega_bracelet', [   # 8. 매일 이 중 5개만 살 수 있음 (판매는 늘)
            *[wild(MS + z, 10000 if z in TYPE_Z else 15000, 2, daily='gimmick') for z in zs],
            *[wild(MS + m, 50000 if m in LEGEND_MEGA else 30000, 4, daily='gimmick') for m in megas],
            e(MS + 'dynamax_candy', 3000, 6, daily='gimmick'), wild(MS + 'max_mushroom', 10000, 6, daily='gimmick'),
            *[e(MS + s, 500, 8, daily='gimmick') for s in shards]]),

        ('작물', M + 'wheat', [   # ── 마인크래프트 상인 ── (판매 분류: 작물 / 광물 / 건축 / 잡화)
            # 씨앗은 사기만 (판매 목록에서 뺌, 당근·감자처럼 작물 자체가 심는 것은 그대로)
            e('pokeserver:farm_deed', 50000, sell=0), e(M + 'wheat_seeds', 10, sell=0), e(M + 'carrot', 20), e(M + 'potato', 20),
            e(M + 'beetroot_seeds', 10, sell=0), e(M + 'pumpkin_seeds', 30, sell=0), e(M + 'melon_seeds', 30, sell=0), e(M + 'sugar_cane', 30), e(M + 'bone_meal', 15),
            e(M + 'wheat', 20), e(M + 'pumpkin', 60), e(M + 'melon_slice', 10), e(M + 'beetroot', 20), e(M + 'apple', 30),
            e(M + 'cocoa_beans', 20), e(M + 'sweet_berries', 15),
            # 4. 농장 물품으로 만든 것 (판매만): 재료를 그냥 파는 것보다 비싸게, 재료를 사서 만들어 팔면 손해 (CRAFTED 검사)
            *[sell_only(M + i, p) for i, p in CRAFTED_SELL.items()],
            *[sell_only(C + c + '_apricorn', 10) for c in ('red', 'yellow', 'green', 'blue', 'pink', 'black', 'white')],
            sell_only(M + 'egg', 2), sell_only(M + 'honeycomb', 10), sell_only(M + 'honey_bottle', 15)]),
        ('광물', M + 'diamond', [
            e(M + 'coal', 30), e(M + 'copper_ingot', 25), e(M + 'iron_ingot', 120), e(M + 'gold_ingot', 240), e(M + 'redstone', 30),
            e(M + 'lapis_lazuli', 45), e(M + 'quartz', 45), e(M + 'emerald', 400), e(M + 'diamond', 1200), e(M + 'netherite_ingot', 20000),
            sell_only(M + 'amethyst_shard', 10),   # 광물 원석(raw_*)은 판매 안 함 (녹여서 주괴로)
            sell_only(M + 'iron_nugget', 3), sell_only(M + 'gold_nugget', 6), sell_only(M + 'obsidian', 20), sell_only(M + 'flint', 2),
            # 5. 광물 블록 (판매만): 재료 9개(자수정은 4개)를 따로 파는 것보다 조금 비싸게
            *[sell_only(M + b, p) for b, p in MINERAL_BLOCKS.items()]]),
        ('잡화', M + 'bucket', [   # 도구는 사기만 (판매 목록에서 뺌). 철 곡괭이는 튜토리얼 기본 물품이라 철 도구(곡괭이·도끼·삽·괭이)는 상점에 없음
            *[e(M + i, p, sell=0) for i, p in (('shears', 300), ('fishing_rod', 150), ('bucket', 400))],
            # 7. 나무·돌·석탄 같은 기본 재료로 바로 만드는 생활용 설치물(문·사다리·제작대·화로·횃불·랜턴·상자·책장)은 상점에서 뺌
            *[sell_only(M + i, p) for i, p in (('rotten_flesh', 2), ('bone', 5), ('string', 5), ('spider_eye', 5), ('gunpowder', 10),
                                               ('ender_pearl', 30), ('slime_ball', 10), ('leather', 10), ('feather', 3), ('ink_sac', 5),
                                               ('blaze_rod', 30), ('ghast_tear', 50), ('phantom_membrane', 20), ('prismarine_shard', 5),
                                               ('rabbit_hide', 3), ('arrow', 1))],
            *[sell_only(M + i, p) for i, p in (('beef', 6), ('porkchop', 6), ('chicken', 5), ('mutton', 5), ('cod', 5), ('salmon', 8),
                                               ('tropical_fish', 10), ('pufferfish', 10))]]),
    ]


# ── 판매만: 코블몬에서 얻을 수 있는데 위 목록에 없는 물품 전부 (배지 해금 없음, 구매 불가) ──
# 얻는 길 = 코블몬 jar의 조합법 결과·전리품 표·포켓몬 드롭에 나오는 것. 아래 NOT_OBTAINABLE은 이벤트·크리에이티브 전용이라 뺌.
NOT_OBTAINABLE = {'cherish_ball', 'ancient_origin_ball', 'npc_editor', 'habitat_block', 'gimmighoul_chest', 'lectern'}
HELD = {'ability_shield', 'absorb_bulb', 'big_root', 'bright_powder', 'cell_battery', 'cleanse_tag', 'destiny_knot', 'eject_pack',
        'float_stone', 'iron_ball', 'lagging_tail', 'light_ball', 'luminous_moss', 'metal_powder', 'metronome', 'mirror_herb',
        'quick_powder', 'shed_shell', 'smoke_ball', 'soothe_bell', 'sticky_barb', 'electric_seed', 'grassy_seed', 'misty_seed',
        'psychic_seed', 'oval_stone', 'black_augurite', 'galarica_cuff', 'galarica_wreath', 'auspicious_armor', 'malicious_armor',
        'scroll_of_darkness', 'scroll_of_waters', 'sweet_apple', 'tart_apple', 'syrupy_apple', 'metal_alloy', 'shell_helmet',
        'masterpiece_teacup', 'unremarkable_teacup', 'cracked_pot', 'chipped_pot'}
RARE_BERRY = {'enigma', 'micle', 'custap', 'jaboca', 'rowap', 'kee', 'maranga', 'starf', 'lansat', 'liechi', 'ganlon', 'salac', 'petaya', 'apicot'}


def obtainable_missing(have):
    """코블몬 물품 중 상점에 없고 생존에서 얻을 수 있는 것 (id 목록)."""
    import re
    jar = next((ROOT / 'tools/.jarcache').glob('Cobblemon-*.jar'))
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        en = json.loads(z.read('assets/cobblemon/lang/en_us.json'))
        models = {f.split('/')[-1][:-5] for f in names if f.startswith('assets/cobblemon/models/item/')}
        ids = sorted({k.split('.')[2] for k in en if re.match(r'^(item|block)\.cobblemon\.[a-z0-9_]+$', k)} & models)
    return [i for i in ids if C + i not in have and i not in NOT_OBTAINABLE]


def sell_rule(i):
    """(분류, 판매가). 원칙: 같은 계열의 상점 판매가(구매가÷4)에 맞추고, 상점에서 살 수 있는 재료로 만드는 것은 재료값보다 싸게."""
    if i in HELD: return '도구', 1000                            # 쇠구슬·전기구슬처럼 이름이 _ball이어도 지닌 도구
    if i == 'master_ball': return '볼', 5000
    if i.endswith('_ball'): return '볼', 50 if i.startswith('ancient_') else 200
    if i.startswith(('x_', 'dire_hit', 'guard_spec')) or i in ('heal_powder', 'energy_root', 'revival_herb', 'remedy', 'fine_remedy',
                                                               'superb_remedy', 'medicinal_brew', 'berry_juice', 'moomoo_milk'):
        return '회복', 100
    if i.endswith('_berry'): return '도구', 100 if i[:-6] in RARE_BERRY else 20
    stone = next((st for st in ('fire', 'water', 'thunder', 'leaf', 'moon', 'sun', 'shiny', 'dusk', 'dawn', 'ice') if f'{st}_stone' in i), None)
    if stone and i.endswith('_ore'): return '성장', 3000 // WILD_SELL     # 캐면 돌 1개
    if stone and i.endswith('_block'): return '성장', 9 * 3000 // WILD_SELL   # 진화의 돌 9개
    if i.endswith('_mint_leaf'): return '성장', 20                 # 야생에 저절로 나고 농장에서 씨앗째 계속 자람 (흔한 열매와 같은 값)
    if 'fossil' in i and i != 'fossil_analyzer': return '기타', 300
    if i == 'relic_coin': return '기타', 100
    if i == 'relic_coin_pouch': return '기타', 900
    if i == 'relic_coin_sack': return '기타', 8100
    if i.endswith('_gem_block'): return '기타', 180              # 타입 보석 9개 (보석 판매가 20 × 9)
    if i.endswith(('_gem_cluster', '_gem_bud')) or 'tumblestone_cluster' in i: return '기타', 40
    if i.endswith(('_sherd', '_plaque', '_smithing_template')) or i.startswith('pokedex_'): return '기타', 50
    if i in ('pc', 'healing_machine', 'monitor', 'damaged_monitor', 'display_case', 'fossil_analyzer', 'restoration_tank', 'pasture',
             'disc_shelf', 'technical_machine', 'ring_target') or i.startswith(('campfire_pot_', 'gilded_chest')) \
            or i.endswith('_gilded_chest'):
        return '기타', 50
    if i.endswith(('_seed', '_seeds')) or 'mulch' in i or i.startswith(('apricorn_', 'saccharine_', 'stripped_')) \
            or 'tumblestone' in i or i.startswith('tatami'):
        return '기타', 5
    return '기타', 10                                            # 요리·사탕·차·식물 등 (상점 재료로 만들 수 있어도 손해 안 보게 낮게)


# 조합 재료 (상점에 있는 것만): 완성품 구매가 ≥ 재료 구매가 합
RECIPES = {
    M + 'bucket': {M + 'iron_ingot': 3}, M + 'shears': {M + 'iron_ingot': 2},
    M + 'quartz_block': {M + 'quartz': 4},
    M + 'smooth_stone': {M + 'stone': 1}, M + 'stone': {M + 'cobblestone': 1}, M + 'stone_bricks': {M + 'stone': 1},
    M + 'bricks': {M + 'clay_ball': 4}, M + 'glass': {M + 'sand': 1},
    M + 'oak_planks': {M + 'oak_log': 0.25}, M + 'sandstone': {M + 'sand': 4}, M + 'red_sandstone': {M + 'red_sand': 4},
    M + 'glass_pane': {M + 'glass': 6 / 16}, M + 'hay_block': {M + 'wheat': 9}, M + 'copper_block': {M + 'copper_ingot': 9},
    M + 'quartz_bricks': {M + 'quartz_block': 1}, M + 'red_stained_glass': {M + 'glass': 1}, M + 'red_terracotta': {M + 'terracotta': 1},
    M + 'mossy_cobblestone': {M + 'cobblestone': 1}, M + 'cracked_stone_bricks': {M + 'stone_bricks': 1},
    C + 'poke_rod': {M + 'fishing_rod': 1, C + 'poke_ball': 1},
}


def check(cats):
    known = set()
    for jar in list((ROOT / 'tools/.jarcache').glob('*.jar')) + [Path('/tmp/pokeserver-shots/client/client-1.21.1.jar')]:
        if not jar.exists():
            continue
        with zipfile.ZipFile(jar) as z:
            for f in z.namelist():
                if f.endswith('/lang/en_us.json') and f.count('/') == 3:
                    ns = f.split('/')[1]
                    for k in json.loads(z.read(f)):
                        p = k.split('.')
                        if len(p) == 3 and p[0] in ('item', 'block'):
                            known.add(f'{ns}:{p[2]}')
    items = [x for _, _, xs in cats for x in xs]
    ids = [x['item'] for x in items]
    assert len(ids) == len(set(ids)), f'같은 물품 두 번: {sorted({i for i in ids if ids.count(i) > 1})}'
    if any(k.startswith('minecraft:') for k in known):
        bad = sorted(i for i in ids if i.split('#')[0] not in known and not i.startswith('pokeserver:'))
        assert not bad, f'없는 물품: {bad}'
    price = {x['item']: x['buy'] for x in items if x['buy']}
    for x in items:
        assert x['buy'] == 0 or x['sell'] < x['buy'], f"되팔아 이득: {x['item']}"
    for out, mats in RECIPES.items():
        cost = sum(price[m] * n for m, n in mats.items())
        assert price[out] >= cost, f'{out} {price[out]}원 < 재료 {cost:.0f}원'
    sell = {x['item']: x['sell'] for x in items}
    sell[M + 'gold_nugget'] = sell[M + 'gold_ingot'] / 9
    for out, mats in CRAFTED.items():   # 만든 것 > 재료를 그냥 판 값, 재료를 사서 만들어 팔면 손해
        assert sell[out] > sum(sell.get(m, 0) * n for m, n in mats.items()), f'{out} 판매가가 재료 판매가보다 쌈'
    for m, v in BASE_SELL.items():   # 계산에 쓴 재료 값 = 실제 상점 판매가
        assert m == M + 'gold_nugget' or sell[m] == v, f'{m} 판매가 {sell[m]} ≠ {v}'
        if all(m in price for m in mats):
            assert sell[out] < sum(price[m] * n for m, n in mats.items()), f'{out} 사서 만들면 이득'
    for b, (m, n) in MINERAL_OF.items():
        assert sell[M + m] * n < sell[M + b] < price.get(M + m, 10 ** 9) * n, f'{b} 판매가 {sell[M + b]} (재료 {sell[M + m]}×{n})'


if __name__ == '__main__':
    cats = categories()
    check(cats)
    POKE = {'볼', '회복', '성장', '도구', '능력치', '기믹', '기술머신'}   # 코블몬 상인(포켓몬 상점)
    MC = {'작물', '광물', '잡화', '건축'}                                 # 마인크래프트 상인(생활 상점)
    assert {n for n, _, _ in cats} == POKE | MC and not POKE & MC, f'분류가 어느 상점인지 정해야 함: {[n for n, _, _ in cats]}'
    assert all(len(n.split()) == 1 for n, _, _ in cats), '분류 이름은 한 단어'
    out = {'categories': [{'name': n, 'icon': i, 'shop': 'poke' if n in POKE else 'mc', 'items': xs} for n, i, xs in cats]}
    (ROOT / 'pack/config/pokeserver/shop.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print({n: len(xs) for n, _, xs in cats})
    print('상점 문서도 다시 만들어 올리기: python3 tools/shop_doc.py <폴더> (docs/작업규칙.md 상점·가격)')
