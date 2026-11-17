package com.pokeserver;

import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/** 화폐. 잔액은 ServerData(월드 저장)에 있음. */
public final class Money {
    private Money() {}

    public static String fmt(long n) { return String.format("%,d원", n); }

    public static long get(ServerPlayer p) { return ServerData.get(p.server).money.getOrDefault(p.getUUID(), 0L); }

    public static void add(MinecraftServer server, UUID id, long amount) {
        ServerData d = ServerData.get(server);
        d.money.merge(id, amount, Long::sum);
        d.setDirty();
    }

    /** 잔액이 충분하면 빼고 true. */
    public static boolean take(ServerPlayer p, long amount) {
        if (amount < 0 || get(p) < amount) return false;
        add(p.server, p.getUUID(), -amount);
        return true;
    }

    public static void set(MinecraftServer server, UUID id, long amount) {
        ServerData d = ServerData.get(server);
        d.money.put(id, amount);
        d.setDirty();
    }
}
