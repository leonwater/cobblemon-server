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
            wildCount++;
            var mon = pe.getPokemon();
            boolean near = nearFirstSpawn(level.getServer(), e.getSpawnablePosition().getPosition());
            // 전설·환상·울트라비스트·패러독스(Complete Cobblemon Collection의 야생 출현)는 첫 스폰 근처에선 아예 안 나옴 (15레벨로 깎이면 너무 쉬움)
            if (near && mon.getSpecies().getLabels().stream().anyMatch(STRONG::contains)) { e.cancel(); return Unit.INSTANCE; }
            if (mon.getLevel() > SAFE_LEVEL && near) {
                mon.setLevel(SAFE_LEVEL - 7 + level.getRandom().nextInt(8));   // 8~15
                mon.initializeMoveset(true);
            }
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
        installStarters();
        PokeServer.LOG.info("배틀 제한 등록: 야생·플레이어 배틀은 야생(광장 포함)에서만");
        // 9. 야생·플레이어 배틀은 야생(광장 마을 포함)에서만. NPC(체육관 관장 등) 배틀은 어디서나.
        CobblemonEvents.BATTLE_STARTED_PRE.subscribe(Priority.NORMAL, e -> {
            var b = e.getBattle();
            boolean outside = b.getPlayers().stream().anyMatch(p -> !battleArea(p));
            if (!b.isPvN() && outside) {
                e.setReason(Component.literal("배틀은 야생·광장에서만 할 수 있어요.").withStyle(ChatFormatting.RED));
                e.cancel();
            }
            // 체육관·사천왕: 도전자를 필드 끝 자리로 (포켓몬 위치는 holdGymPokemon이 1초마다 맞춤)
            if (b.isPvN()) for (var p : b.getPlayers()) if (inGym(p)) Menu.run(p, "function poke:gym/place");
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

    static final int SAFE_LEVEL = 15, SAFE_RADIUS = 200;
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
    static boolean inGym(net.minecraft.server.level.ServerPlayer p) { return gymNo(p) > 0; }

    /** 지금 들어가 있는 경기장 번호 (1~8 체육관, 9 사천왕, 0 없음). */
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
    /** 1초마다: 체육관·사천왕 배틀 중 내 포켓몬을 도전자 앞 7칸(필드 가운데 쪽)으로. 처음 나올 때와 교체로 나올 때 모두
     *  관장 앞에 나오는 경우가 있어(실측) 멀리 있으면 옮김. */
    static void holdGymPokemon(MinecraftServer server) {
        for (var p : server.getPlayerList().getPlayers()) {
            if (!inGym(p)) continue;
            var battle = com.cobblemon.mod.common.battles.BattleRegistry.INSTANCE.getBattleByParticipatingPlayer(p);
            if (battle == null || !battle.isPvN()) continue;
            var f = p.getForward();
            double x = p.getX() + f.x * 7, z = p.getZ() + f.z * 7;   // 7칸: 필드 가운데 몬스터볼 쪽 (4칸이면 큰 포켓몬이 화면을 가림)
            for (var a : battle.getActors()) {
                if (!a.getPlayerUUIDs().iterator().hasNext() || !a.getPlayerUUIDs().iterator().next().equals(p.getUUID())) continue;
                for (var act : a.getActivePokemon()) {
                    var bp = act.getBattlePokemon();
                    if (bp == null) continue;
                    var en = bp.getEffectedPokemon().getEntity();   // RCT는 배틀용 복제본을 넘길 수 있어, 나와 있는 엔티티는 원본 쪽에
                    if (en == null) en = bp.getOriginalPokemon().getEntity();
                    if (en != null && en.distanceToSqr(x, p.getY(), z) > 9) en.teleportTo(x, p.getY(), z);
                }
            }
        }
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
