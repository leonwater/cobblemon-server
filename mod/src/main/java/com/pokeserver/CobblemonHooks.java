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
final class CobblemonHooks {
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
            if (!level.dimension().location().toString().equals("poke:wild")) { e.cancel(); return Unit.INSTANCE; }
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
        PokeServer.LOG.info("배틀 제한 등록: 야생·플레이어 배틀은 야생·광장에서만");
        // 9. 야생·플레이어 배틀은 야생과 스폰 광장(회의장 섬)에서만. NPC(체육관 관장 등) 배틀은 어디서나.
        CobblemonEvents.BATTLE_STARTED_PRE.subscribe(Priority.NORMAL, e -> {
            var b = e.getBattle();
            boolean outside = b.getPlayers().stream().anyMatch(p -> !battleArea(p));
            if (!b.isPvN() && outside) {
                e.setReason(Component.literal("배틀은 야생·광장에서만 할 수 있어요.").withStyle(ChatFormatting.RED));
                e.cancel();
            }
            return Unit.INSTANCE;
        });
        // 체육관·사천왕: NPC 배틀이 끝나면 승패를 데이터팩에 알림 (체육관 안이 아니면 함수가 아무것도 안 함)
        CobblemonEvents.BATTLE_VICTORY.subscribe(Priority.NORMAL, e -> {
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
        CobblemonEvents.BATTLE_FLED.subscribe(Priority.NORMAL, e -> {
            if (e.getBattle().isPvN()) gymResult(e.getPlayer().getEntity().server, e.getPlayer().getUuid(), "lose");
            return Unit.INSTANCE;
        });
    }

    /** 야생 또는 광장(poke:town 회의장 섬, tools/build_world.py HALL_PLAY). */
    static boolean battleArea(net.minecraft.server.level.ServerPlayer p) {
        String dim = p.level().dimension().location().toString();
        return dim.equals("poke:wild") || dim.equals("poke:town") && p.getX() >= -66 && p.getX() < 67 && p.getZ() >= -122 && p.getZ() < 35;
    }

    static final int SAFE_LEVEL = 15, SAFE_RADIUS = 200;
    static final Set<String> STRONG = Set.of("legendary", "mythical", "ultra_beast", "paradox");
    /** 스타팅 포켓몬 세대 (Cobblemon 기본 분류 이름). 피카츄·이브이(Special)와 히스이는 뺌. */
    static final java.util.List<String> GENS = java.util.List.of("kanto", "johto", "hoenn", "sinnoh", "unova", "kalos", "alola", "galar", "paldea");

    /** 4. 스타팅 포켓몬: 플레이어마다 세대 하나를 무작위로 정해(태그 poke.gen_<세대>로 기억) 그 세대 3마리만 보여 줌.
     *  고르기 검사(chooseStarter)도 같은 목록을 써서 다른 세대는 고를 수 없음. 튜토리얼을 끝내야 고를 수 있음. */
    static void installStarters() {
        com.cobblemon.mod.common.Cobblemon.INSTANCE.setStarterHandler(new com.cobblemon.mod.common.starter.CobblemonStarterHandler() {
            @Override
            public java.util.List<com.cobblemon.mod.common.config.starter.StarterCategory> getStarterList(net.minecraft.server.level.ServerPlayer p) {
                var all = super.getStarterList(p);
                var gens = all.stream().filter(c -> GENS.contains(c.getName().toLowerCase(java.util.Locale.ROOT))).toList();
                if (gens.isEmpty()) return all;
                String saved = p.getTags().stream().filter(t -> t.startsWith("poke.gen_")).map(t -> t.substring(9)).findFirst().orElse("");
                for (var c : gens) if (c.getName().toLowerCase(java.util.Locale.ROOT).equals(saved)) return java.util.List.of(c);
                var c = gens.get(p.getRandom().nextInt(gens.size()));
                p.getTags().removeIf(t -> t.startsWith("poke.gen_"));
                p.addTag("poke.gen_" + c.getName().toLowerCase(java.util.Locale.ROOT));
                return java.util.List.of(c);
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
        for (var p : server.getPlayerList().getPlayers()) {
            var data = com.cobblemon.mod.common.Cobblemon.INSTANCE.getPlayerDataManager().getGenericData(p);
            boolean lock = !p.getTags().contains("poke.tutorial_done");
            if (!data.getStarterSelected() && data.getStarterLocked() != lock) {
                data.setStarterLocked(lock);
                data.sendToPlayer(p);
            }
        }
    }

    /** 전체 초기화: 파티·PC의 포켓몬을 모두 지우고 스타팅 포켓몬을 다시 고를 수 있게 (세대도 새로 뽑음). */
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
        p.getTags().removeIf(t -> t.startsWith("poke.gen_"));
    }

    /** 튜토리얼을 끝냈고 아직 안 골랐으면 스타팅 포켓몬 선택 창을 엶. */
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
    /** 6. 1시간마다(서버가 켜져 있는 동안) 야생의 무작위 플레이어 근처에, 그 바이옴에 출현 설정이 있는 전설·환상 포켓몬 하나.
     *  첫 스폰 근처(초보 구역, 15레벨 이하 규칙)에 있는 플레이어는 고르지 않음. 맞는 플레이어·전설이 없으면 이번 시간은 건너뜀. */
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

    static boolean nearFirstSpawn(MinecraftServer server, net.minecraft.core.BlockPos pos) {
        var spawn = server.getCommandStorage().get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("poke", "state")).getCompound("wildspawn");
        if (!spawn.contains("x")) return false;
        double dx = pos.getX() - spawn.getDouble("x"), dz = pos.getZ() - spawn.getDouble("z");
        return dx * dx + dz * dz <= SAFE_RADIUS * SAFE_RADIUS;
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
