package com.pokeserver;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.entity.EntityTypeTest;

/** 렉 줄이기: 10분마다 바닥에 떨어진 아이템을 모두 지움 (1분·10초 전에 채팅으로 알림). */
public final class ItemCleaner {
    private ItemCleaner() {}

    static final int PERIOD = 20 * 60 * 10;

    static void tick(MinecraftServer server) {
        int t = server.getTickCount() % PERIOD;
        if (t == PERIOD - 20 * 60) say(server, "1분 뒤 바닥에 떨어진 아이템을 정리합니다. 필요한 아이템은 주워 두세요!");
        else if (t == PERIOD - 20 * 10) say(server, "10초 뒤 바닥에 떨어진 아이템을 정리합니다!");
        else if (t == 0 && server.getTickCount() > 0) {
            int n = clear(server);
            say(server, "바닥에 떨어진 아이템 " + n + "개를 정리했습니다.");
        }
    }

    static int clear(MinecraftServer server) {
        int n = 0;
        for (ServerLevel level : server.getAllLevels()) {
            for (ItemEntity e : level.getEntities(EntityTypeTest.forClass(ItemEntity.class), e -> true)) {
                e.discard();
                n++;
            }
        }
        return n;
    }

    private static void say(MinecraftServer server, String s) {
        server.getPlayerList().broadcastSystemMessage(Component.literal("[서버] ").withStyle(ChatFormatting.GOLD)
                .append(Component.literal(s).withStyle(ChatFormatting.GRAY)), false);
    }
}
