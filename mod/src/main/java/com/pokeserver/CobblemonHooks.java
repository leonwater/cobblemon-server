package com.pokeserver;

import com.cobblemon.mod.common.api.Priority;
import com.cobblemon.mod.common.api.events.CobblemonEvents;
import com.cobblemon.mod.common.entity.npc.NPCEntity;
import com.cobblemon.mod.common.entity.npc.NPCPlayerModelType;
import java.net.URI;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import kotlin.Unit;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.ChatFormatting;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;

/** Cobblemon이 있을 때만 불림 (테스트 서버엔 Cobblemon이 없음). */
public final class CobblemonHooks {
    private CobblemonHooks() {}

    static void register() {
        // 배틀 뒤 나와 있는 플레이어 포켓몬이 서버 종료(청크 저장) 중 목록을 바꿔 종료가 멈춤 → 저장 전에 먼저 거둠
        net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
            for (ServerLevel level : server.getAllLevels()) {
                var owned = new java.util.ArrayList<com.cobblemon.mod.common.entity.pokemon.PokemonEntity>();
                for (var en : level.getAllEntities())
                    if (en instanceof com.cobblemon.mod.common.entity.pokemon.PokemonEntity pe && pe.getOwnerUUID() != null) owned.add(pe);
                owned.forEach(net.minecraft.world.entity.Entity::discard);
            }
        });
        // 15. 포켓몬은 야생에서만 나옴. 5. 야생 첫 스폰 근처(반경 SAFE_RADIUS)는 15레벨 이하
        CobblemonEvents.ENTITY_SPAWN.subscribe(Priority.NORMAL, e -> {
            if (!(e.getEntity() instanceof com.cobblemon.mod.common.entity.pokemon.PokemonEntity pe)) return Unit.INSTANCE;
            var level = e.getSpawnablePosition().getWorld();
            if (!level.dimension().location().toString().equals("poke:wild") || Plaza.noSpawn(level, e.getSpawnablePosition().getPosition())) {
                e.cancel(); return Unit.INSTANCE;                         // 15. 광장 둘레(마을의 1.5배)엔 포켓몬이 안 나옴
            }
            // 10. 렉 방지: 야생 포켓몬 수 상한 (야생에 있는 사람 1명당 WILD_PER_PLAYER마리)
            if (wildCount >= wildCap) { e.cancel(); return Unit.INSTANCE; }
            var mon = pe.getPokemon();
            // 전설·환상은 자연 출현(낚시 포함) 없음: 1시간마다 서버가 직접 소환하는 것만 (spawnLegend는 이 이벤트를 안 거침)
            if (mon.getSpecies().getLabels().contains("legendary") || mon.getSpecies().getLabels().contains("mythical")) { e.cancel(); return Unit.INSTANCE; }
            boolean near = nearFirstSpawn(level.getServer(), e.getSpawnablePosition().getPosition());
            // 전설·환상·울트라비스트·패러독스(Complete Cobblemon Collection의 야생 출현)는 첫 스폰 근처에선 아예 안 나옴 (15레벨로 깎이면 너무 쉬움)
            if (near && mon.getSpecies().getLabels().stream().anyMatch(STRONG::contains)) { e.cancel(); return Unit.INSTANCE; }
            if (mon.getLevel() > SAFE_LEVEL && near) mon.setLevel(SAFE_LEVEL - 7 + level.getRandom().nextInt(8));   // 8~15
            // 첫 스폰 근처: 종족값 합 SAFE_BST 넘는 종, 그 레벨엔 아직 진화 못 했을 종(예: 30레벨 진화형이 15레벨)은 안 나옴
            if (near && (bst(mon.getForm()) > SAFE_BST || evolveLevel(mon.getForm()) > mon.getLevel())) { e.cancel(); return Unit.INSTANCE; }
            if (near) mon.initializeMoveset(true);
            wildCount++;   // 실제로 나온 것만 셈 (취소된 스폰까지 세면 상한이 일찍 참)
            return Unit.INSTANCE;
        });
        // 6. 내 포켓몬보다 레벨이 많이 높은 포켓몬은 잡기 어려움: 5레벨 넘게 차이 나면 1레벨당 5%씩, 최저 10%
        CobblemonEvents.POKEMON_CATCH_RATE.subscribe(Priority.NORMAL, e -> {
            if (e.getThrower() instanceof net.minecraft.server.level.ServerPlayer p) {
                int target = e.getPokemonEntity().getPokemon().getLevel(), mine = partyMax(p);
                float f = catchFactor(target, mine);
                if (f < 1f) PokeServer.LOG.info("포획률 감소: {} Lv{} (내 최고 Lv{}) {} → {}", p.getGameProfile().getName(), target, mine, e.getCatchRate(), e.getCatchRate() * f);
                e.setCatchRate(e.getCatchRate() * f);
            }
            return Unit.INSTANCE;
        });
        // 레벨 제한(RCT): 제한에 닿으면 경험치·레벨이 더 안 오름 (넘칠 경험치는 제한 레벨까지만), 사탕도 못 씀 (안 닳게)
        CobblemonEvents.EXPERIENCE_GAINED_EVENT_PRE.subscribe(Priority.NORMAL, e -> {
            var mon = e.getPokemon();
            int cap = mon.getOwnerPlayer() == null ? 0 : levelCap(mon.getOwnerPlayer());
            if (cap <= 0) return Unit.INSTANCE;
            if (mon.getLevel() >= cap) e.cancel();
            else e.setExperience(Math.min(e.getExperience(), mon.getExperienceToLevel(cap)));
            return Unit.INSTANCE;
        });
        CobblemonEvents.EXPERIENCE_CANDY_USE_PRE.subscribe(Priority.NORMAL, e -> {
            int cap = levelCap(e.getPlayer());
            if (cap > 0 && e.getPokemon().getLevel() >= cap) {
                e.cancel();
                e.getPlayer().displayClientMessage(Component.literal("레벨 제한(Lv." + cap + ")에 닿아 더 키울 수 없어요. 체육관을 이기면 제한이 올라가요.").withStyle(ChatFormatting.YELLOW), true);
            }
            return Unit.INSTANCE;
        });
        // 레벨 제한보다 높은 포켓몬은 못 잡음 (볼이 맞는 순간 막음)
        CobblemonEvents.THROWN_POKEBALL_HIT.subscribe(Priority.NORMAL, e -> {
            if (!(e.getPokeBall().getOwner() instanceof net.minecraft.server.level.ServerPlayer p)) return Unit.INSTANCE;
            int cap = levelCap(p), lv = e.getPokemon().getPokemon().getLevel();
            if (cap > 0 && lv > cap) {
                e.cancel();
                p.displayClientMessage(Component.literal("레벨 제한(Lv." + cap + ")보다 높은 포켓몬(Lv." + lv + ")은 잡을 수 없어요.").withStyle(ChatFormatting.RED), true);
            }
            return Unit.INSTANCE;
        });
        installStarters();
        PokeServer.LOG.info("배틀 제한 등록: 야생·플레이어 배틀은 야생(광장 포함)에서만");
        // 9. 야생·플레이어 배틀은 야생(광장 마을 포함)에서만. NPC(체육관 관장 등) 배틀은 어디서나.
        // 배틀 중인 플레이어는 무적 (몹·다른 플레이어·낙하 등 모든 피해)
        net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents.ALLOW_DAMAGE.register((victim, source, amount) ->
                !(victim instanceof net.minecraft.server.level.ServerPlayer p && com.cobblemon.mod.common.battles.BattleRegistry.INSTANCE.getBattleByParticipatingPlayer(p) != null));
        CobblemonEvents.BATTLE_STARTED_PRE.subscribe(Priority.NORMAL, e -> {
            var b = e.getBattle();
            boolean outside = b.getPlayers().stream().anyMatch(p -> !battleArea(p));
            if (!b.isPvN() && outside) {
                e.setReason(Component.literal("배틀은 야생·광장에서만 할 수 있어요.").withStyle(ChatFormatting.RED));
                e.cancel();
            }
            // 체육관·사천왕: 도전자를 필드 끝 자리로 (포켓몬 위치는 holdBattlePokemon이 고정)
            if (b.isPvN()) for (var p : b.getPlayers()) if (inGym(p)) Menu.run(p, "function poke:gym/place");
            // 레벨 제한(RCT)을 넘은 포켓몬은 어떤 배틀에도 못 나감 (못 잡고 못 키우지만, 교환 등으로 들어온 경우 대비): 그 배틀 팀에서 빼고, 나갈 포켓몬이 없으면 배틀 취소
            for (var a : b.getActors()) if (a instanceof com.cobblemon.mod.common.battles.actor.PlayerBattleActor pa && pa.getEntity() != null) {
                int cap = levelCap(pa.getEntity());
                var over = pa.getPokemonList().stream().filter(bp -> cap > 0 && bp.getOriginalPokemon().getLevel() > cap).toList();
                if (over.isEmpty()) continue;
                pa.getPokemonList().removeAll(over);
                pa.getEntity().sendSystemMessage(Component.literal("레벨 제한(Lv." + cap + ")을 넘은 포켓몬은 배틀에 못 나가요: "
                        + over.stream().map(bp -> bp.getOriginalPokemon().getDisplayName(false).getString()).collect(java.util.stream.Collectors.joining(", "))).withStyle(ChatFormatting.YELLOW));
                if (pa.getPokemonList().stream().allMatch(bp -> bp.getOriginalPokemon().isFainted())) {
                    e.setReason(Component.literal("레벨 제한(Lv." + cap + ") 안의 포켓몬이 없어서 배틀할 수 없어요.").withStyle(ChatFormatting.RED));
                    e.cancel();
                    return Unit.INSTANCE;
                }
            }
            // 배틀 BGM (음악 볼륨, 배틀이 끝나면 코블몬이 끔): 체육관 관장(1~8번)은 28번, 그 밖(야생·트레이너·플레이어·사천왕)은 7번.
            // RCT 트레이너 배틀은 원래 곡이 비어 있어 아무것도 안 나옴 → 여기서 모든 플레이어 쪽에 곡을 정해 줌
            for (var a : b.getActors()) if (a instanceof com.cobblemon.mod.common.battles.actor.PlayerBattleActor pa && pa.getEntity() != null) {
                int g = gymNo(pa.getEntity());
                pa.setBattleTheme(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(PokeServer.ID, "bgm.bgm_" + (b.isPvN() && g >= 1 && g <= 8 ? 28 : 7)));
            }
            return Unit.INSTANCE;
        });
        // 체육관·사천왕: NPC 배틀이 끝나면 승패를 데이터팩에 알림 (체육관 안이 아니면 함수가 아무것도 안 함)
        CobblemonEvents.BATTLE_VICTORY.subscribe(Priority.NORMAL, e -> {
            if (e.getBattle().isPvP()) {   // 7. 칭호: 플레이어 배틀 승수
                MinecraftServer server = null;
                for (var p : e.getBattle().getPlayers()) server = p.server;
                if (server != null) for (var a : e.getWinners()) for (UUID id : a.getPlayerUUIDs()) Titles.add(server, id, "pvp", 1);
            }
            if (e.getBattle().isPvW()) wildZCrystal(e);
            if (e.getBattle().isPvN()) {
                MinecraftServer server = null;
                for (var p : e.getBattle().getPlayers()) server = p.server;
                if (server != null) {
                    for (var a : e.getWinners()) for (UUID id : a.getPlayerUUIDs()) gymResult(server, id, "win");
                    for (var a : e.getLosers()) for (UUID id : a.getPlayerUUIDs()) gymResult(server, id, "lose");
                }
            }
            return Unit.INSTANCE;
        });
        // 7. 칭호: 전설·환상 포켓몬을 잡으면 기록
        CobblemonEvents.POKEMON_CAPTURED.subscribe(Priority.NORMAL, e -> {
            var labels = e.getPokemon().getSpecies().getLabels();
            if (labels.contains("legendary") || labels.contains("mythical")) Titles.add(e.getPlayer(), "legend", 1);
            return Unit.INSTANCE;
        });
        CobblemonEvents.BATTLE_FLED.subscribe(Priority.NORMAL, e -> {
            if (e.getBattle().isPvN()) gymResult(e.getPlayer().getEntity().server, e.getPlayer().getUuid(), "lose");
            return Unit.INSTANCE;
        });
    }

    /** 야생 (광장 마을도 야생 안에 있음). */
    static boolean battleArea(net.minecraft.server.level.ServerPlayer p) {
        return p.level().dimension().location().toString().equals("poke:wild");
    }

    static final int SAFE_LEVEL = 15, SAFE_RADIUS = 170, SAFE_BST = 300;

    static int bst(com.cobblemon.mod.common.pokemon.FormData f) {
        return f.getBaseStats().values().stream().mapToInt(Integer::intValue).sum();
    }

    /** 이 모습이 되려면 필요한 레벨 (레벨 진화만 셈, 앞 단계까지 거슬러 올라감). 진화형이 아니면 1. */
    static int evolveLevel(com.cobblemon.mod.common.pokemon.FormData f) {
        var pre = f.getPreEvolution();
        if (pre == null) return 1;
        int need = evolveLevel(pre.getForm());
        String me = f.getSpecies().getResourceIdentifier().getPath();
        for (var ev : pre.getForm().getEvolutions()) {
            String to = String.valueOf(ev.getResult().getSpecies()).toLowerCase();
            if (!to.substring(to.indexOf(':') + 1).equals(me)) continue;
            for (var r : ev.getRequirements())
                if (r instanceof com.cobblemon.mod.common.pokemon.requirements.LevelRequirement l) need = Math.max(need, l.getMinLevel());
        }
        return need;
    }
    static final Set<String> STRONG = Set.of("legendary", "mythical", "ultra_beast", "paradox");
    /** 스타팅 포켓몬 세대 (Cobblemon 기본 분류 이름). 피카츄·이브이(Special)와 히스이는 뺌. */
    static final java.util.List<String> GENS = java.util.List.of("kanto", "johto", "hoenn", "sinnoh", "unova", "kalos", "alola", "galar", "paldea");

    /** 4. 스타팅 포켓몬: 플레이어마다 세대 하나를 무작위로 정해(태그 poke.gen_<세대>로 기억) 그 세대 3마리만 보여 줌.
     *  고르기 검사(chooseStarter)도 같은 목록을 써서 다른 세대는 고를 수 없음. 튜토리얼을 끝내야 고를 수 있음. */
    /** 7. 스타팅 포켓몬: 레벨 5, 기술은 그 포켓몬이 처음 나온 원작(레드·블루 ~ 스칼렛·바이올렛)에서 레벨 5까지 배우는 것.
     *  출처: Pokémon Showdown 세대별 레벨업 기술 데이터 (Cobblemon 데이터는 여러 세대가 섞여 있어 따로 정함). */
    static final int STARTER_LEVEL = 5;
    static final java.util.Map<String, java.util.List<String>> STARTER_MOVES = java.util.Map.ofEntries(
            java.util.Map.entry("bulbasaur", java.util.List.of("growl", "tackle")),
            java.util.Map.entry("charmander", java.util.List.of("growl", "scratch")),
            java.util.Map.entry("squirtle", java.util.List.of("tackle", "tailwhip")),
            java.util.Map.entry("chikorita", java.util.List.of("growl", "tackle")),
            java.util.Map.entry("cyndaquil", java.util.List.of("leer", "tackle")),
            java.util.Map.entry("totodile", java.util.List.of("leer", "scratch")),
            java.util.Map.entry("treecko", java.util.List.of("leer", "pound")),
            java.util.Map.entry("torchic", java.util.List.of("growl", "scratch")),
            java.util.Map.entry("mudkip", java.util.List.of("growl", "tackle")),
            java.util.Map.entry("turtwig", java.util.List.of("tackle", "withdraw")),
            java.util.Map.entry("chimchar", java.util.List.of("leer", "scratch")),
            java.util.Map.entry("piplup", java.util.List.of("pound", "growl")),
            java.util.Map.entry("snivy", java.util.List.of("tackle", "leer")),
            java.util.Map.entry("tepig", java.util.List.of("tackle", "tailwhip")),
            java.util.Map.entry("oshawott", java.util.List.of("tackle", "tailwhip")),
            java.util.Map.entry("chespin", java.util.List.of("growl", "tackle", "vinewhip")),
            java.util.Map.entry("fennekin", java.util.List.of("scratch", "tailwhip", "ember")),
            java.util.Map.entry("froakie", java.util.List.of("growl", "pound", "bubble")),
            java.util.Map.entry("rowlet", java.util.List.of("leafage", "tackle", "growl")),
            java.util.Map.entry("litten", java.util.List.of("ember", "scratch", "growl")),
            java.util.Map.entry("popplio", java.util.List.of("pound", "watergun", "growl")),
            java.util.Map.entry("grookey", java.util.List.of("growl", "scratch")),
            java.util.Map.entry("scorbunny", java.util.List.of("growl", "tackle")),
            java.util.Map.entry("sobble", java.util.List.of("growl", "pound")),
            java.util.Map.entry("sprigatito", java.util.List.of("leafage", "scratch", "tailwhip")),
            java.util.Map.entry("fuecoco", java.util.List.of("ember", "leer", "tackle")),
            java.util.Map.entry("quaxly", java.util.List.of("growl", "pound", "watergun")));

    static com.cobblemon.mod.common.config.starter.StarterCategory starterLv5(com.cobblemon.mod.common.config.starter.StarterCategory c) {
        var list = new java.util.ArrayList<com.cobblemon.mod.common.api.pokemon.PokemonProperties>();
        for (var props : c.getPokemon()) {
            var q = props.copy();
            q.setLevel(STARTER_LEVEL);
            var moves = STARTER_MOVES.get(String.valueOf(q.getSpecies()).toLowerCase(java.util.Locale.ROOT));
            if (moves != null) q.setMoves(new java.util.ArrayList<>(moves));
            list.add(q);
        }
        return new com.cobblemon.mod.common.config.starter.StarterCategory(c.getName(), c.getOrder(), c.getDisplayName(), list, c.getRandomStarter());
    }

    static void installStarters() {
        com.cobblemon.mod.common.Cobblemon.INSTANCE.setStarterHandler(new com.cobblemon.mod.common.starter.CobblemonStarterHandler() {
            @Override
            public java.util.List<com.cobblemon.mod.common.config.starter.StarterCategory> getStarterList(net.minecraft.server.level.ServerPlayer p) {
                var all = super.getStarterList(p);
                var gens = all.stream().filter(c -> GENS.contains(c.getName().toLowerCase(java.util.Locale.ROOT))).toList();
                if (gens.isEmpty()) return all;
                String saved = p.getTags().stream().filter(t -> t.startsWith("poke.gen_")).map(t -> t.substring(9)).findFirst().orElse("");
                for (var c : gens) if (c.getName().toLowerCase(java.util.Locale.ROOT).equals(saved)) return java.util.List.of(starterLv5(c));
                var c = gens.get(p.getRandom().nextInt(gens.size()));
                p.getTags().removeIf(t -> t.startsWith("poke.gen_"));
                p.addTag("poke.gen_" + c.getName().toLowerCase(java.util.Locale.ROOT));
                return java.util.List.of(starterLv5(c));
            }

            @Override
            public void requestStarterChoice(net.minecraft.server.level.ServerPlayer p) {
                if (!p.getTags().contains("poke.tutorial_done")) {
                    p.displayClientMessage(Component.literal("오박사의 튜토리얼을 끝내면 스타팅 포켓몬을 고를 수 있어요.").withStyle(ChatFormatting.YELLOW), true);
                    return;
                }
                super.requestStarterChoice(p);
            }
        });
    }

    /** 튜토리얼 전에는 고르기를 잠가 "스타팅 포켓몬을 선택하세요" 안내가 뜨지 않게, 끝낸 뒤엔 풂. */
    static void starterLocks(MinecraftServer server) {
        STARTER_AT.entrySet().removeIf(e -> {
            if (server.getTickCount() < e.getValue()) return false;
            var p = server.getPlayerList().getPlayer(e.getKey());
            if (p != null) offerStarter(p);
            return true;
        });
        for (var p : server.getPlayerList().getPlayers()) {
            var data = com.cobblemon.mod.common.Cobblemon.INSTANCE.getPlayerDataManager().getGenericData(p);
            boolean lock = !p.getTags().contains("poke.tutorial_done");
            if (!data.getStarterSelected() && data.getStarterLocked() != lock) {
                data.setStarterLocked(lock);
                data.sendToPlayer(p);
            }
        }
    }

    /** 초기화: 파티·PC의 포켓몬·도감을 모두 지우고 스타팅 포켓몬을 다시 고를 수 있게 (세대도 새로 뽑음). */
    static void wipe(net.minecraft.server.level.ServerPlayer p) {
        com.cobblemon.mod.common.util.PlayerExtensionsKt.party(p).clearParty();
        var pc = com.cobblemon.mod.common.util.PlayerExtensionsKt.pc(p);
        var mons = new java.util.ArrayList<com.cobblemon.mod.common.pokemon.Pokemon>();
        pc.forEach(mons::add);
        mons.forEach(pc::remove);
        var data = com.cobblemon.mod.common.Cobblemon.INSTANCE.getPlayerDataManager().getGenericData(p);
        data.setStarterSelected(false);
        data.setStarterUUID(null);
        data.setStarterPrompted(false);
        data.setStarterLocked(true);   // 튜토리얼을 다시 끝내면 starterLocks가 풂
        data.sendToPlayer(p);
        // 1. 도감 기록도 처음부터 (도감 칭호·보상이 다시 쌓이게)
        var mgr = com.cobblemon.mod.common.Cobblemon.INSTANCE.getPlayerDataManager();
        var dex = mgr.getPokedexData(p);
        dex.getSpeciesRecords().clear();
        mgr.saveSingle(dex, com.cobblemon.mod.common.api.storage.player.PlayerInstancedDataStoreTypes.INSTANCE.getPOKEDEX());
        mgr.syncAllToPlayer(p);
        p.getTags().removeIf(t -> t.startsWith("poke.gen_"));
    }

    /** 튜토리얼을 끝냈고 아직 안 골랐으면 스타팅 포켓몬 선택 창을 엶. */
    /** 튜토리얼을 끝낸 사람: 이 틱이 지나면 스타팅 고르기 창을 띄움 (starterLocks가 1초마다 확인). */
    static final java.util.Map<UUID, Integer> STARTER_AT = new java.util.HashMap<>();

    static void offerStarter(net.minecraft.server.level.ServerPlayer p) {
        var data = com.cobblemon.mod.common.Cobblemon.INSTANCE.getPlayerDataManager().getGenericData(p);
        if (data.getStarterSelected()) return;
        data.setStarterLocked(false);
        com.cobblemon.mod.common.Cobblemon.INSTANCE.getStarterHandler().requestStarterChoice(p);
    }

    /** 레벨 차이에 따른 포획률 배율. */
    static float catchFactor(int target, int mine) {
        int over = target - mine - 5;
        return over <= 0 ? 1f : Math.max(0.1f, 1f - over * 0.05f);
    }

    static int partyMax(net.minecraft.server.level.ServerPlayer p) {
        int max = 1;
        for (var mon : com.cobblemon.mod.common.util.PlayerExtensionsKt.party(p)) if (mon != null) max = Math.max(max, mon.getLevel());
        return max;
    }

    /** 데이터팩이 저장한 야생 첫 스폰(storage poke:state wildspawn) 근처인가. */
    /** 6. 1시간마다(서버가 켜져 있는 동안) 야생 맵의 무작위 플레이어 근처에, 그 바이옴에 출현 설정이 있는 전설·환상 포켓몬 하나.
     *  초보 구역(첫 스폰 근처)엔 안 나옴. 그 시각에 야생에 (초보 구역 밖) 아무도 없으면 이번은 건너뛰고 다음 시각에. */
    static final int LEGEND_TICKS = 72000;
    static java.util.List<com.cobblemon.mod.common.api.spawning.detail.PokemonSpawnDetail> legends;

    static String spawnLegend(MinecraftServer server) {
        if (legends == null) {
            legends = new java.util.ArrayList<>();
            for (var d : com.cobblemon.mod.common.api.spawning.CobblemonSpawnPools.WORLD_SPAWN_POOL.getDetails()) {
                if (!(d instanceof com.cobblemon.mod.common.api.spawning.detail.PokemonSpawnDetail pd) || pd.getPokemon().getSpecies() == null) continue;
                String name = pd.getPokemon().getSpecies();
                var sp = name.contains(":") ? com.cobblemon.mod.common.api.pokemon.PokemonSpecies.getByIdentifier(net.minecraft.resources.ResourceLocation.parse(name))
                        : com.cobblemon.mod.common.api.pokemon.PokemonSpecies.getByName(name);
                if (sp != null && (sp.getLabels().contains("legendary") || sp.getLabels().contains("mythical"))) legends.add(pd);
            }
            PokeServer.LOG.info("전설·환상 출현 설정 {}개", legends.size());
        }
        var players = new java.util.ArrayList<>(server.getPlayerList().getPlayers().stream()
                .filter(p -> p.level().dimension().location().toString().equals("poke:wild") && !p.isSpectator()
                        && !nearFirstSpawn(server, p.blockPosition())).toList());
        java.util.Collections.shuffle(players);
        for (var p : players) {
            var level = p.serverLevel();
            var biome = level.getBiome(p.blockPosition());
            // 바이옴 조건이 있는 설정은 그중 하나가 맞아야 함 (프리셋이 바이옴 없는 조건을 덧붙여도 무시). 바이옴 조건이 아예 없으면 어디서나
            var fit = legends.stream().filter(d -> {
                var withBiome = d.getConditions().stream().filter(c -> c.getBiomes() != null && !c.getBiomes().isEmpty()).toList();
                return withBiome.isEmpty() || withBiome.stream().anyMatch(c -> c.getBiomes().stream().anyMatch(b -> b.fits(biome)));
            }).toList();
            if (fit.isEmpty()) continue;
            var d = fit.get(level.getRandom().nextInt(fit.size()));
            var props = d.getPokemon().copy();
            var range = d.getLevelRange();
            if (props.getLevel() == null) props.setLevel(range != null ? range.getFirst() + level.getRandom().nextInt(range.getLast() - range.getFirst() + 1) : 70);
            var mon = props.createEntity(level);
            double a = level.getRandom().nextDouble() * Math.PI * 2;
            int x = (int) (p.getX() + Math.cos(a) * 16), z = (int) (p.getZ() + Math.sin(a) * 16);
            if (nearFirstSpawn(server, new net.minecraft.core.BlockPos(x, 0, z))) continue;   // 6. 나올 자리도 초보 구역이면 안 됨
            int y = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            mon.moveTo(x + .5, y, z + .5, level.getRandom().nextFloat() * 360, 0);
            level.addFreshEntity(mon);
            var name = mon.getPokemon().getSpecies().getTranslatedName();
            server.getPlayerList().broadcastSystemMessage(Component.literal("✦ 전설의 포켓몬 ").withStyle(ChatFormatting.GOLD)
                    .append(name.copy().withStyle(ChatFormatting.YELLOW)).append(Component.literal(" 이(가) " + p.getGameProfile().getName() + " 근처에 나타났다!").withStyle(ChatFormatting.GOLD)), false);
            PokeServer.LOG.info("전설 출현: {} Lv{} → {} ({} {} {})", d.getPokemon().getSpecies(), mon.getPokemon().getLevel(), p.getGameProfile().getName(), x, y, z);
            return d.getPokemon().getSpecies();
        }
        return null;
    }

    /** 메뉴 카드: 잡은 종, 마주친 종(잡은 것 포함), 전체 종. */
    static java.util.List<Integer> dex(net.minecraft.server.level.ServerPlayer p) {
        int own = 0, seen = 0;
        for (var r : com.cobblemon.mod.common.Cobblemon.INSTANCE.getPlayerDataManager().getPokedexData(p).getSpeciesRecords().values()) {
            var k = r.getKnowledge();
            if (k == com.cobblemon.mod.common.api.pokedex.PokedexEntryProgress.OWNED) own++;
            if (k != com.cobblemon.mod.common.api.pokedex.PokedexEntryProgress.UNREGISTERED) seen++;
        }
        return java.util.List.of(own, seen, com.cobblemon.mod.common.api.pokemon.PokemonSpecies.INSTANCE.getImplemented().size());
    }

    /** 다이맥스 장소 제한을 푸는 배틀: 플레이어끼리, 또는 체육관·사천왕 도전 중(점수 poke.gym 1~9)의 NPC 배틀. */
    public static boolean dynamaxAnywhere(net.minecraft.server.level.ServerPlayer p) {
        var battle = com.cobblemon.mod.common.battles.BattleRegistry.INSTANCE.getBattleByParticipatingPlayer(p);
        if (battle == null) return false;
        return battle.isPvP() || inGym(p);
    }

    /** 체육관·사천왕 경기장 안 (poke.gym 1~9). */
    /** /관전 닉네임 (/spectate): 누구나 다른 사람의 배틀을 거리 상관없이 관전. 코블몬 기본(파티 포켓몬을 고른 채 배틀 중인 사람을 보고 R)은
     *  포켓몬이 없거나 닫힌 경기장 밖이면 못 써서 명령으로도 열어 줌. 조건 검사(자기 자신·배틀 중 아님·내가 배틀 중)는 코블몬이 함. */
    static void registerSpectate(com.mojang.brigadier.CommandDispatcher<net.minecraft.commands.CommandSourceStack> d) {
        for (String name : new String[]{"관전", "spectate"}) d.register(net.minecraft.commands.Commands.literal(name)
                .then(net.minecraft.commands.Commands.argument("player", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).suggests(Nicknames::suggest).executes(c -> {
                    var me = c.getSource().getPlayerOrException();
                    var other = Nicknames.find(me.server, com.mojang.brigadier.arguments.StringArgumentType.getString(c, "player"));
                    if (other == null) { me.sendSystemMessage(Component.literal("접속 중인 사람의 닉네임을 적어 주세요.").withStyle(ChatFormatting.RED)); return 0; }
                    com.cobblemon.mod.common.net.serverhandling.battle.SpectateBattleHandler.INSTANCE.spectateBattle(other, me);   // (대상, 관전자) 순서
                    return 1;
                })));
    }

    /** 특수 기믹 도구는 그 도구를 주는 체육관을 깨야 낄 수 있음 (Z링 2, 메가링 4, 다이맥스 밴드 6, 테라스탈 오브 8 — 관장 보상과 같은 배지).
     *  액세서리 칸에 끼워 두면 1초 안에 가방으로 돌려줌. 손에 든 것은 배틀에서 gimmickLocked가 막음. Accessories 모드는 빌드 의존성이 아니라 리플렉션. */
    record Gear(net.minecraft.tags.TagKey<net.minecraft.world.item.Item> tag, int badges, String name) {}
    static final java.util.List<Gear> GEAR = java.util.List.of(
            gear("z_ring", 2, "Z링"), gear("mega_bracelet", 4, "메가링"), gear("dynamax_band", 6, "다이맥스 밴드"), gear("tera_orb", 8, "테라스탈 오브"));
    static Gear gear(String tag, int badges, String name) {
        return new Gear(net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM,
                net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("mega_showdown", tag)), badges, name);
    }
    private static java.lang.reflect.Method capOf, allEquipped, entryStack, entryRef, setStack;

    static void gimmickGear(MinecraftServer server) {
        if (!net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("accessories")) return;
        try {
            if (capOf == null) {
                Class<?> cap = Class.forName("io.wispforest.accessories.api.AccessoriesCapability"), entry = Class.forName("io.wispforest.accessories.api.slot.SlotEntryReference");
                capOf = cap.getMethod("getOptionally", net.minecraft.world.entity.LivingEntity.class);
                allEquipped = cap.getMethod("getAllEquipped");
                entryStack = entry.getMethod("stack");
                entryRef = entry.getMethod("reference");
                setStack = Class.forName("io.wispforest.accessories.api.slot.SlotReference").getMethod("setStack", net.minecraft.world.item.ItemStack.class);
            }
            for (var p : server.getPlayerList().getPlayers()) {
                Object cap = ((java.util.Optional<?>) capOf.invoke(null, p)).orElse(null);
                if (cap == null) continue;
                int badges = Nicknames.badges(p);
                for (Object e : (java.util.List<?>) allEquipped.invoke(cap)) {
                    var stack = (net.minecraft.world.item.ItemStack) entryStack.invoke(e);
                    Gear g = GEAR.stream().filter(x -> stack.is(x.tag())).findFirst().orElse(null);
                    if (g == null || badges >= g.badges()) continue;
                    var back = stack.copy();
                    if (!(boolean) setStack.invoke(entryRef.invoke(e), net.minecraft.world.item.ItemStack.EMPTY)) continue;
                    p.getInventory().placeItemBackInInventory(back);
                    p.displayClientMessage(Component.literal(g.name() + "은(는) 배지 " + g.badges() + "개(" + g.badges() + "번째 체육관)를 모아야 낄 수 있어요.").withStyle(ChatFormatting.RED), true);
                }
            }
        } catch (ReflectiveOperationException | RuntimeException ex) {
            PokeServer.LOG.warn("기믹 도구 장착 검사 실패: {}", ex.toString());
        }
    }

    static boolean inGym(net.minecraft.server.level.ServerPlayer p) { return gymNo(p) > 0; }

    /** RCT 레벨 제한 (모드가 없거나 못 읽으면 0 = 제한 없음). RCT는 빌드 의존성이 아니라 리플렉션으로 읽음 (클라이언트 MenuScreen.minecraftCap과 같은 방식). */
    static int levelCap(net.minecraft.server.level.ServerPlayer p) {
        try {
            Object mod = Class.forName("com.gitlab.srcmc.rctmod.api.RCTMod").getMethod("getInstance").invoke(null);
            Object tm = mod.getClass().getMethod("getTrainerManager").invoke(mod);
            Object data = tm.getClass().getMethod("getData", net.minecraft.world.entity.player.Player.class).invoke(tm, p);
            return (int) data.getClass().getMethod("getLevelCap").invoke(data);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return 0;
        }
    }

    /** 지금 들어가 있는 경기장 번호 (1~8 체육관, 9 사천왕, 0 없음). */
    static void tagBattling(MinecraftServer server) {
        for (var p : server.getPlayerList().getPlayers())
            if (com.cobblemon.mod.common.battles.BattleRegistry.INSTANCE.getBattleByParticipatingPlayer(p) != null) p.addTag("poke.battling"); else p.removeTag("poke.battling");
    }

    static int gymNo(net.minecraft.server.level.ServerPlayer p) {
        var sb = p.server.getScoreboard();
        var obj = sb.getObjective("poke.gym");
        var score = obj == null ? null : sb.getPlayerScoreInfo(p, obj);
        return score == null ? 0 : score.value();
    }

    /** 배틀 중 특수 기믹 잠금 (배틀 밖은 제한 없음): 메가 = 배지 4, 다이맥스·거다이맥스 = 배지 6, 테라스탈 = 배지 8, Z기술은 제한 없음.
     *  @param gimmick ShowdownMoveset.Gimmick 이름 */
    public static boolean gimmickLocked(net.minecraft.server.level.ServerPlayer p, String gimmick) {
        if (com.cobblemon.mod.common.battles.BattleRegistry.INSTANCE.getBattleByParticipatingPlayer(p) == null) return false;
        int badges = Nicknames.badges(p);
        return switch (gimmick) {
            // 관장이 그 기믹을 처음 쓰기 바로 전 관장을 이기면 도구와 함께 풀림. Z기술은 제한 없음(Z링만 있으면 됨, 2번째 관장 보상)
            case "MEGA_EVOLUTION" -> badges < 4;
            case "DYNAMAX" -> badges < 6;
            case "TERASTALLIZATION" -> badges < 8;
            default -> false;
        };
    }

    static final int WILD_PER_PLAYER = 30, WILD_MIN = 30;
    static int wildCount, wildCap = WILD_MIN;

    /** 1초마다: 야생에 있는 주인 없는 포켓몬 수와 상한을 다시 셈 (스폰 때마다 세면 느려서). */
    /** 배틀 중 포켓몬은 처음 나온 자리에 고정 (R로 배틀 화면을 닫고 걸어도 따라오지 않게). 자리는 배틀이 끝나거나 포켓몬이 들어가면 지움.
     *  3. 체육관·사천왕은 도전자 기준 사선: 내 포켓몬 = 앞 OWN_F·왼쪽 OWN_L, 상대 = 앞 FOE_F·오른쪽 FOE_R (원작처럼 양쪽이 다 보이게).
     *  방향은 배틀 첫 순간(gym/place 직후)의 도전자 방향으로 고정, 서로 마주 보게 돌림. */
    static final java.util.Map<UUID, net.minecraft.world.phys.Vec3> HOLD = new java.util.HashMap<>();
    static final java.util.Map<UUID, net.minecraft.world.phys.Vec3[]> GYM_SPOT = new java.util.HashMap<>();
    static final double OWN_F = 4, OWN_L = 2, FOE_F = 11, FOE_R = 1.5;

    static void holdBattlePokemon(MinecraftServer server) {
        java.util.Set<UUID> seen = new java.util.HashSet<>();
        for (var p : server.getPlayerList().getPlayers()) {
            var battle = com.cobblemon.mod.common.battles.BattleRegistry.INSTANCE.getBattleByParticipatingPlayer(p);
            if (battle == null) continue;
            seen.add(p.getUUID());
            net.minecraft.world.phys.Vec3[] gym = null;   // {내 자리, 상대 자리}
            if (inGym(p) && battle.isPvN()) {
                gym = GYM_SPOT.computeIfAbsent(p.getUUID(), k -> {
                    var f = p.getForward();
                    double fx = f.x, fz = f.z, n = Math.hypot(fx, fz);
                    fx /= n; fz /= n;   // 왼쪽 = (fz, -fx)
                    return new net.minecraft.world.phys.Vec3[]{
                            new net.minecraft.world.phys.Vec3(p.getX() + fx * OWN_F + fz * OWN_L, p.getY(), p.getZ() + fz * OWN_F - fx * OWN_L),
                            new net.minecraft.world.phys.Vec3(p.getX() + fx * FOE_F - fz * FOE_R, p.getY(), p.getZ() + fz * FOE_F + fx * FOE_R)};
                });
            }
            for (var a : battle.getActors()) {
                var ids = a.getPlayerUUIDs().iterator();
                boolean mine = ids.hasNext() && ids.next().equals(p.getUUID());
                if (!mine && gym == null) continue;   // 상대(관장) 포켓몬은 체육관에서만 옮김
                if (!mine && a.getPlayerUUIDs().iterator().hasNext()) continue;
                for (var act : a.getActivePokemon()) {
                    var bp = act.getBattlePokemon();
                    if (bp == null) continue;
                    var en = bp.getEffectedPokemon().getEntity();   // RCT는 배틀용 복제본을 넘길 수 있어, 나와 있는 엔티티는 원본 쪽에
                    if (en == null) en = bp.getOriginalPokemon().getEntity();
                    if (en == null) continue;
                    seen.add(en.getUUID());
                    var spot = gym != null ? gym[mine ? 0 : 1] : HOLD.get(en.getUUID());
                    if (spot == null) { var pos = en.position(); HOLD.put(en.getUUID(), pos); spot = pos; }
                    en.getNavigation().stop();
                    if (en.distanceToSqr(spot) > (gym != null ? 4 : 2.25)) en.teleportTo(spot.x, spot.y, spot.z);
                    if (gym != null) {   // 서로 마주 보게
                        var o = gym[mine ? 1 : 0];
                        float yaw = (float) (Math.toDegrees(Math.atan2(o.z - spot.z, o.x - spot.x)) - 90);
                        en.setYRot(yaw); en.setYHeadRot(yaw); en.setYBodyRot(yaw);
                    }
                }
            }
        }
        HOLD.keySet().retainAll(seen);
        GYM_SPOT.keySet().retainAll(seen);
    }

    /** 5. 배틀 배속 (1·2·4배): 플레이어마다 고른 값. 배틀은 참가한 플레이어 중 가장 느린 값 (플레이어 배틀은 서로 맞춤). */
    static final java.util.Map<UUID, Integer> SPEED = new java.util.concurrent.ConcurrentHashMap<>();

    /** 기술 연출 키프레임이 도는 동안의 배속 (ActionSpeedMixin·DelaySpeedMixin). */
    public static final ThreadLocal<Integer> ACTION_SPEED = ThreadLocal.withInitial(() -> 1);

    static void setSpeed(ServerPlayer p, int speed) {
        if (speed == 1 || speed == 2 || speed == 4) SPEED.put(p.getUUID(), speed);
    }

    public static int battleSpeed(com.cobblemon.mod.common.api.battles.model.PokemonBattle battle) {
        int s = Integer.MAX_VALUE;
        for (var a : battle.getActors()) for (var id : a.getPlayerUUIDs()) s = Math.min(s, SPEED.getOrDefault(id, 1));
        return s == Integer.MAX_VALUE ? 1 : s;
    }

    static void countWild(MinecraftServer server) {
        var level = Plaza.wild(server);
        if (level == null) return;
        wildCount = level.getEntities(net.minecraft.world.level.entity.EntityTypeTest.forClass(com.cobblemon.mod.common.entity.pokemon.PokemonEntity.class),
                pe -> pe.getOwnerUUID() == null).size();
        wildCap = Math.max(WILD_MIN, WILD_PER_PLAYER * level.players().size());
    }

    static boolean nearFirstSpawn(MinecraftServer server, net.minecraft.core.BlockPos pos) {
        var spawn = server.getCommandStorage().get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("poke", "state")).getCompound("wildspawn");
        if (!spawn.contains("x")) return false;
        double dx = pos.getX() - spawn.getDouble("x"), dz = pos.getZ() - spawn.getDouble("z");
        return dx * dx + dz * dz <= SAFE_RADIUS * SAFE_RADIUS;
    }

    /** Z크리스탈은 야생에서: 야생 포켓몬을 배틀로 이기면 그 포켓몬 첫 번째 타입의 Z크리스탈을 Z_DROP 확률로 받음. */
    static final double Z_DROP = Double.parseDouble(System.getProperty("pokeserver.zdrop", "0.05"));   // 시험 때 -Dpokeserver.zdrop=1
    static final java.util.Map<String, String> Z_CRYSTAL = java.util.Map.ofEntries(
            java.util.Map.entry("normal", "normalium_z"), java.util.Map.entry("fire", "firium_z"), java.util.Map.entry("water", "waterium_z"),
            java.util.Map.entry("electric", "electrium_z"), java.util.Map.entry("grass", "grassium_z"), java.util.Map.entry("ice", "icium_z"),
            java.util.Map.entry("fighting", "fightinium_z"), java.util.Map.entry("poison", "poisonium_z"), java.util.Map.entry("ground", "groundium_z"),
            java.util.Map.entry("flying", "flyinium_z"), java.util.Map.entry("psychic", "psychium_z"), java.util.Map.entry("bug", "buginium_z"),
            java.util.Map.entry("rock", "rockium_z"), java.util.Map.entry("ghost", "ghostium_z"), java.util.Map.entry("dragon", "dragonium_z"),
            java.util.Map.entry("dark", "darkinium_z"), java.util.Map.entry("steel", "steelium_z"), java.util.Map.entry("fairy", "fairium_z"));

    private static void wildZCrystal(com.cobblemon.mod.common.api.events.battles.BattleVictoryEvent e) {
        var players = new java.util.ArrayList<UUID>();
        for (var a : e.getWinners()) for (UUID id : a.getPlayerUUIDs()) players.add(id);
        if (players.isEmpty()) return;
        MinecraftServer server = null;
        for (var p : e.getBattle().getPlayers()) server = p.server;
        if (server == null) return;
        for (var a : e.getLosers()) for (var bp : a.getPokemonList()) {
            if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= Z_DROP) continue;
            String id = Z_CRYSTAL.get(bp.getOriginalPokemon().getPrimaryType().getName().toLowerCase(java.util.Locale.ROOT));
            var item = id == null ? null : net.minecraft.core.registries.BuiltInRegistries.ITEM.getOptional(
                    net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("mega_showdown", id)).orElse(null);
            var p = server.getPlayerList().getPlayer(players.get(0));
            if (item == null || p == null) continue;
            var stack = new net.minecraft.world.item.ItemStack(item);
            p.sendSystemMessage(Component.literal("야생 포켓몬이 ").withStyle(ChatFormatting.GOLD)
                    .append(stack.getHoverName()).append(Component.literal("을(를) 떨어뜨렸어요!").withStyle(ChatFormatting.GOLD)));
            if (!p.getInventory().add(stack)) p.drop(stack, false);
        }
    }

    private static void gymResult(MinecraftServer server, UUID id, String result) {
        var p = server.getPlayerList().getPlayer(id);
        if (p != null) Menu.run(p, "function poke:gym/" + result);
    }

    private static final Set<UUID> SKINNED = new HashSet<>();

    /** 태그가 붙은 NPC들의 스킨을 바꿈. value: 플레이어 이름, http(s) URL, reset. @return 바뀐 NPC 수 */
    static int setSkin(MinecraftServer server, String tag, String value) {
        var data = ServerData.get(server);
        if (value.equals("reset")) data.npcSkins.remove(tag); else data.npcSkins.put(tag, value);
        data.setDirty();
        int n = 0;
        for (ServerLevel level : server.getAllLevels()) {
            for (var e : level.getAllEntities()) {
                if (e instanceof NPCEntity npc && e.getTags().contains(tag)) { apply(npc, value); n++; }
            }
        }
        return n;
    }

    private static void apply(NPCEntity npc, String value) {
        SKINNED.add(npc.getUUID());
        if (value.equals("reset")) npc.unloadTexture();
        else if (value.startsWith("http://") || value.startsWith("https://")) npc.loadTexture(URI.create(value), NPCPlayerModelType.DEFAULT);
        else npc.loadTextureFromGameProfileName(value);
    }

    /** 마을을 다시 지어 새로 소환된 NPC에도 저장된 스킨을 다시 입힘 (주기적으로 호출). */
    static void reapply(MinecraftServer server) {
        var skins = ServerData.get(server).npcSkins;
        if (skins.isEmpty()) return;
        for (ServerLevel level : server.getAllLevels()) {
            for (var e : level.getAllEntities()) {
                if (!(e instanceof NPCEntity npc) || SKINNED.contains(e.getUUID())) continue;
                for (String tag : e.getTags()) if (skins.containsKey(tag)) apply(npc, skins.get(tag));
            }
        }
    }
}
