package com.pokeserver;

import com.cobblemon.mod.common.api.Priority;
import com.cobblemon.mod.common.api.events.CobblemonEvents;
import kotlin.Unit;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;

/** Cobblemon이 있을 때만 불림 (테스트 서버엔 Cobblemon이 없음). */
final class CobblemonHooks {
    private CobblemonHooks() {}

    static void register() {
        PokeServer.LOG.info("배틀 제한 등록: 야생·플레이어 배틀은 채집 맵에서만");
        // 9. 야생·플레이어 배틀은 채집 맵에서만. NPC(체육관 관장 등) 배틀은 어디서나.
        CobblemonEvents.BATTLE_STARTED_PRE.subscribe(Priority.NORMAL, e -> {
            var b = e.getBattle();
            boolean outside = b.getPlayers().stream().anyMatch(p -> !p.level().dimension().location().toString().equals("poke:wild"));
            if (!b.isPvN() && outside) {
                e.setReason(Component.literal("배틀은 채집 맵에서만 할 수 있어요.").withStyle(ChatFormatting.RED));
                e.cancel();
            }
            return Unit.INSTANCE;
        });
    }
}
