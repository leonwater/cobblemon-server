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
