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
        PokeServer.LOG.info("배틀 제한 등록: 야생·플레이어 배틀은 야생에서만");
        // 9. 야생·플레이어 배틀은 야생에서만. NPC(체육관 관장 등) 배틀은 어디서나.
        CobblemonEvents.BATTLE_STARTED_PRE.subscribe(Priority.NORMAL, e -> {
            var b = e.getBattle();
            boolean outside = b.getPlayers().stream().anyMatch(p -> !p.level().dimension().location().toString().equals("poke:wild"));
            if (!b.isPvN() && outside) {
                e.setReason(Component.literal("배틀은 야생에서만 할 수 있어요.").withStyle(ChatFormatting.RED));
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
