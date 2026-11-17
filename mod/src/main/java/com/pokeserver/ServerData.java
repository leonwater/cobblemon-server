package com.pokeserver;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/** 월드에 저장되는 서버 데이터: 땅 주인. (world/data/pokeserver.dat) */
public class ServerData extends SavedData {
    public record Owner(UUID id, String name) {}

    public final Map<Integer, Owner> plotOwners = new HashMap<>();

    public static ServerData get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(
                new SavedData.Factory<>(ServerData::new, ServerData::load, null), PokeServer.ID);
    }

    static ServerData load(CompoundTag tag, HolderLookup.Provider registries) {
        ServerData d = new ServerData();
        CompoundTag plots = tag.getCompound("plots");
        for (String k : plots.getAllKeys()) {
            CompoundTag o = plots.getCompound(k);
            d.plotOwners.put(Integer.parseInt(k), new Owner(o.getUUID("id"), o.getString("name")));
        }
        return d;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
        CompoundTag plots = new CompoundTag();
        plotOwners.forEach((n, o) -> {
            CompoundTag t = new CompoundTag();
            t.putUUID("id", o.id());
            t.putString("name", o.name());
            plots.put(String.valueOf(n), t);
        });
        tag.put("plots", plots);
        return tag;
    }
}
