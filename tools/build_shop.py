"""상점 목록 생성기 → pack/config/pokeserver/shop.json.  사용: python3 tools/build_shop.py

- 포켓몬 물품(Cobblemon·Mega Showdown)만 배지로 해금. 키우는 순서대로: 잡기·회복·기본 성장은 낮은 배지,
  실전용 희귀 물품(지닌 도구 상위·성격·개체값)은 높은 배지. 마인크래프트 물품(건축·농장·광물·도구)은 처음부터.
- 특수 기믹 물품은 그 기믹을 배틀에서 쓸 수 있게 되는 배지에 맞춰 풀림: Z크리스탈 2 (Z링), 메가스톤 4, 다이맥스 6, 테라 조각 8.
- 판매: 거의 모든 물품을 팔 수 있음. 판매가 = 구매가 ÷ 4 (사서 바로 되팔아 이득 보는 일 없음). 구매 0원 = 판매만.
- 가격 근거: 몬스터볼·회복약·진화의 돌·비타민은 원작(스칼렛·바이올렛) 상점 가격, 원작에서 BP 교환인 실전 도구는 희귀도에 맞춰 정함.
- 검사: 아이템 id가 실제로 있는지(모드 jar·마인크래프트 jar 언어 파일), 조합 재료보다 완성품이 싸지 않은지.
"""
import json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C, M, MS = 'cobblemon:', 'minecraft:', 'mega_showdown:'


def e(item, buy, badges=0, sell=None):
    return {'item': item, 'buy': buy, 'sell': buy // 4 if sell is None else sell, **({'badges': badges} if badges else {})}


def sell_only(item, sell):
    return {'item': item, 'buy': 0, 'sell': sell}


def ms_items():
    """Mega Showdown jar에서 메가스톤·Z크리스탈·테라 조각 목록."""
    jar = next((ROOT / 'tools/.jarcache').glob('mega_showdown-*.jar'))
    with zipfile.ZipFile(jar) as z:
        en = json.loads(z.read('assets/mega_showdown/lang/en_us.json'))
        zc = json.loads(z.read('data/mega_showdown/tags/item/z_crystal.json'))['values']
    ids = [k.split('.')[2] for k in en if k.startswith('item.mega_showdown.') and k.count('.') == 2]
    megas = sorted(i for i in ids if i.endswith('ite') or i[:-2].endswith('ite_') and i[-1] in 'xyz')
    return megas, [z.split(':')[1] for z in zc], sorted(i for i in ids if i.endswith('_tera_shard'))


TYPES = ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug', 'rock',
         'ghost', 'dragon', 'dark', 'steel', 'fairy']
TYPE_Z = {'normalium_z', 'firium_z', 'waterium_z', 'electrium_z', 'grassium_z', 'icium_z', 'fightinium_z', 'poisonium_z', 'groundium_z',
          'flyinium_z', 'psychium_z', 'buginium_z', 'rockium_z', 'ghostium_z', 'dragonium_z', 'darkinium_z', 'steelium_z', 'fairium_z'}
LEGEND_MEGA = {'mewtwonite_x', 'mewtwonite_y', 'latiasite', 'latiosite', 'diancite', 'zygardite', 'darkranite', 'heatranite', 'magearnite', 'zeraorite'}


def categories():
    megas, zs, shards = ms_items()
    return [
        ('몬스터볼', C + 'poke_ball', [
            e(C + 'poke_ball', 200), e(C + 'premier_ball', 300), e(C + 'heal_ball', 300),
            e(C + 'great_ball', 600, 1), e(C + 'nest_ball', 1000, 1), e(C + 'net_ball', 1000, 1),
            e(C + 'dive_ball', 1000, 2), e(C + 'repeat_ball', 1000, 2), e(C + 'ultra_ball', 800, 3), e(C + 'dusk_ball', 1000, 3),
            e(C + 'luxury_ball', 1000, 4), *[e(C + b, 1000, 5) for b in ('level_ball', 'lure_ball', 'heavy_ball', 'moon_ball', 'love_ball', 'friend_ball', 'fast_ball')],
            e(C + 'timer_ball', 1500, 8), e(C + 'quick_ball', 1500, 8)]),
        ('회복', C + 'potion', [
            e(C + 'potion', 200), e(C + 'antidote', 100), e(C + 'awakening', 100), e(C + 'ice_heal', 100),
            e(C + 'paralyze_heal', 300), e(C + 'burn_heal', 300), e(C + 'super_potion', 700, 1),
            e(C + 'revive', 2000, 2), e(C + 'full_heal', 400, 2), e(C + 'hyper_potion', 1500, 3), e(C + 'ether', 1200, 3),
            e(C + 'elixir', 3000, 4), e(C + 'max_potion', 2500, 5), e(C + 'max_ether', 2000, 5), e(C + 'full_restore', 3000, 6),
            e(C + 'max_revive', 4000, 7), e(C + 'max_elixir', 4500, 7)]),
        ('성장·진화', C + 'exp_candy_m', [
            e(C + 'exp_candy_xs', 300), e(C + 'everstone', 1000), e(C + 'exp_candy_s', 800, 1), e(C + 'exp_share', 8000, 1),
            *[e(C + s, 3000, 1) for s in ('fire_stone', 'water_stone', 'thunder_stone', 'leaf_stone')],
            e(C + 'exp_candy_m', 1500, 2), e(C + 'moon_stone', 3000, 2),
            *[e(C + s, 3000, 3) for s in ('sun_stone', 'shiny_stone', 'dusk_stone', 'dawn_stone', 'ice_stone')],
            e(C + 'exp_candy_l', 3000, 4), e(C + 'lucky_egg', 10000, 4),
            *[e(C + s, 5000, 4) for s in ('link_cable', 'metal_coat', 'kings_rock', 'dragon_scale', 'upgrade', 'dubious_disc', 'protector',
                                          'electirizer', 'magmarizer', 'reaper_cloth', 'prism_scale', 'razor_claw', 'razor_fang',
                                          'deep_sea_tooth', 'deep_sea_scale', 'sachet', 'whipped_dream')],
            e(C + 'exp_candy_xl', 6000, 6), e(C + 'rare_candy', 4800, 6), e(C + 'pp_up', 9800, 3), e(C + 'pp_max', 20000, 7)]),
        ('지닌 도구', C + 'leftovers', [
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
            *[e(C + i, 25000, 6) for i in ('choice_band', 'choice_specs', 'choice_scarf', 'life_orb')]]),
        ('성격·노력치', C + 'modest_mint', [
            *[e(C + v, 10000, 3) for v in ('hp_up', 'protein', 'iron', 'calcium', 'zinc', 'carbos')],
            *[e(C + p, 3000, 4) for p in ('power_weight', 'power_bracer', 'power_belt', 'power_lens', 'power_band', 'power_anklet')],
            e(C + 'ability_capsule', 10000, 5),
            *[e(C + n + '_mint', 20000, 6) for n in ('lonely', 'adamant', 'naughty', 'brave', 'bold', 'impish', 'lax', 'relaxed', 'modest',
                                                     'mild', 'rash', 'quiet', 'calm', 'gentle', 'careful', 'sassy', 'timid', 'hasty', 'jolly',
                                                     'naive', 'serious')],
            # 개체값 사탕 (Cobblemon 1.8 하이퍼 트레이닝: 그 능력 개체값 +1 / 내림 사탕은 -1)
            *[e(C + c + '_candy', 5000, 7) for c in ('health', 'mighty', 'tough', 'smart', 'courage', 'quick')],
            *[e(C + c + '_candy', 1000, 7) for c in ('sickly', 'weak', 'brittle', 'numb', 'coward', 'slow')],
            e(C + 'ability_patch', 50000, 8)]),
        ('특수 기믹', MS + 'mega_bracelet', [
            *[e(MS + z, 10000 if z in TYPE_Z else 15000, 2) for z in zs],
            *[e(MS + m, 50000 if m in LEGEND_MEGA else 30000, 4) for m in megas],
            e(MS + 'dynamax_candy', 3000, 6), e(MS + 'max_mushroom', 10000, 6),
            *[e(MS + s, 500, 8) for s in shards]]),
        ('농장·작물', M + 'wheat', [
            e('pokeserver:farm_deed', 50000, sell=0), e(M + 'wheat_seeds', 10), e(M + 'carrot', 20), e(M + 'potato', 20),
            e(M + 'beetroot_seeds', 10), e(M + 'pumpkin_seeds', 30), e(M + 'melon_seeds', 30), e(M + 'sugar_cane', 30), e(M + 'bone_meal', 15),
            e(M + 'wheat', 20), e(M + 'pumpkin', 60), e(M + 'melon_slice', 10), e(M + 'beetroot', 20), e(M + 'apple', 30),
            e(M + 'cocoa_beans', 20), e(M + 'sweet_berries', 15),
            *[sell_only(C + c + '_apricorn', 10) for c in ('red', 'yellow', 'green', 'blue', 'pink', 'black', 'white')],
            *[sell_only(C + b + '_berry', 10) for b in ('oran', 'pecha', 'cheri', 'chesto', 'rawst', 'aspear', 'persim', 'leppa')],
            sell_only(C + 'sitrus_berry', 30), sell_only(C + 'lum_berry', 30),
            sell_only(M + 'egg', 2), sell_only(M + 'honeycomb', 10), sell_only(M + 'honey_bottle', 15),
            sell_only(M + 'beef', 6), sell_only(M + 'porkchop', 6), sell_only(M + 'chicken', 5), sell_only(M + 'mutton', 5),
            sell_only(M + 'cod', 5), sell_only(M + 'salmon', 8), sell_only(M + 'tropical_fish', 10), sell_only(M + 'pufferfish', 10)]),
        ('광물·블록', M + 'bricks', [
            e(M + 'coal', 30), e(M + 'copper_ingot', 25), e(M + 'iron_ingot', 120), e(M + 'gold_ingot', 240), e(M + 'redstone', 30),
            e(M + 'lapis_lazuli', 45), e(M + 'quartz', 45), e(M + 'emerald', 400), e(M + 'diamond', 1200), e(M + 'netherite_ingot', 20000),
            *[e(M + w + '_log', 20) for w in ('oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry')],
            e(M + 'stone', 5), e(M + 'cobblestone', 3), e(M + 'smooth_stone', 8), e(M + 'stone_bricks', 8), e(M + 'deepslate', 5),
            e(M + 'sand', 3), e(M + 'gravel', 3), e(M + 'dirt', 2), e(M + 'grass_block', 5), e(M + 'clay_ball', 5), e(M + 'glass', 10),
            e(M + 'bricks', 20), e(M + 'white_concrete', 15), e(M + 'terracotta', 12), e(M + 'white_wool', 15), e(M + 'quartz_block', 200),
            sell_only(M + 'raw_iron', 30), sell_only(M + 'raw_gold', 60), sell_only(M + 'raw_copper', 6), sell_only(M + 'amethyst_shard', 10),
            sell_only(M + 'obsidian', 20), sell_only(M + 'flint', 2),
            *[sell_only(C + t + '_gem', 20) for t in TYPES]]),
        ('도구·기타', M + 'iron_pickaxe', [
            e(M + 'iron_pickaxe', 400), e(M + 'iron_axe', 400), e(M + 'iron_shovel', 150), e(M + 'iron_hoe', 300), e(M + 'shears', 300),
            e(M + 'fishing_rod', 150), e(M + 'bucket', 400), e(M + 'torch', 10), e(M + 'lantern', 150), e(M + 'chest', 50),
            e(M + 'crafting_table', 25), e(M + 'furnace', 30), e(M + 'oak_door', 30), e(M + 'ladder', 10),
            *[sell_only(M + i, p) for i, p in (('rotten_flesh', 2), ('bone', 5), ('string', 5), ('spider_eye', 5), ('gunpowder', 10),
                                               ('ender_pearl', 30), ('slime_ball', 10), ('leather', 10), ('feather', 3), ('ink_sac', 5),
                                               ('blaze_rod', 30), ('ghast_tear', 50), ('phantom_membrane', 20), ('prismarine_shard', 5),
                                               ('rabbit_hide', 3), ('arrow', 1))]]),
    ]


# 조합 재료 (상점에 있는 것만): 완성품 구매가 ≥ 재료 구매가 합
RECIPES = {
    M + 'bucket': {M + 'iron_ingot': 3}, M + 'shears': {M + 'iron_ingot': 2}, M + 'iron_pickaxe': {M + 'iron_ingot': 3},
    M + 'iron_axe': {M + 'iron_ingot': 3}, M + 'iron_shovel': {M + 'iron_ingot': 1}, M + 'iron_hoe': {M + 'iron_ingot': 2},
    M + 'lantern': {M + 'iron_ingot': 8 / 9, M + 'torch': 1}, M + 'chest': {M + 'oak_log': 2}, M + 'crafting_table': {M + 'oak_log': 1},
    M + 'furnace': {M + 'cobblestone': 8}, M + 'oak_door': {M + 'oak_log': 1}, M + 'quartz_block': {M + 'quartz': 4},
    M + 'smooth_stone': {M + 'stone': 1}, M + 'stone': {M + 'cobblestone': 1}, M + 'stone_bricks': {M + 'stone': 1},
    M + 'torch': {M + 'coal': 0.25}, M + 'bricks': {M + 'clay_ball': 4}, M + 'glass': {M + 'sand': 1},
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
        bad = sorted(i for i in ids if i not in known and not i.startswith('pokeserver:'))
        assert not bad, f'없는 물품: {bad}'
    price = {x['item']: x['buy'] for x in items if x['buy']}
    for x in items:
        assert x['buy'] == 0 or x['sell'] < x['buy'], f"되팔아 이득: {x['item']}"
    for out, mats in RECIPES.items():
        cost = sum(price[m] * n for m, n in mats.items())
        assert price[out] >= cost, f'{out} {price[out]}원 < 재료 {cost:.0f}원'


if __name__ == '__main__':
    cats = categories()
    check(cats)
    out = {'categories': [{'name': n, 'icon': i, 'items': xs} for n, i, xs in cats]}
    (ROOT / 'pack/config/pokeserver/shop.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print({n: len(xs) for n, _, xs in cats})
