package com.pokeserver;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/** 월드에 저장되는 서버 데이터: 땅 주인, 잔액, NPC 스킨. (world/data/pokeserver.dat) */
public class ServerData extends SavedData {
    public record Owner(UUID id, String name) {}

    public final Map<Integer, Owner> plotOwners = new HashMap<>();
    public final Map<UUID, Long> money = new HashMap<>();
    public final Map<String, String> npcSkins = new HashMap<>();   // NPC 태그 → 플레이어 이름 또는 URL
    public final Map<UUID, Integer> deedsBought = new HashMap<>();  // 플레이어별로 산 땅 문서 수 (살수록 비싸짐)
    public final Map<UUID, String> nicks = new HashMap<>();         // 8. 튜토리얼에서 정한 닉네임
    /** 별명용 기록: earned(번 돈) spent(상점에서 쓴 돈) pvp(플레이어 배틀 승) legend(전설 포획) title(고른 별명) got(얻은 별명 목록). */
    public final Map<UUID, CompoundTag> stats = new HashMap<>();

    public CompoundTag stats(UUID id) {
        setDirty();
        return stats.computeIfAbsent(id, k -> new CompoundTag());
    }

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
        CompoundTag money = tag.getCompound("money");
        for (String k : money.getAllKeys()) d.money.put(UUID.fromString(k), money.getLong(k));
        CompoundTag skins = tag.getCompound("npcSkins");
        for (String k : skins.getAllKeys()) d.npcSkins.put(k, skins.getString(k));
        CompoundTag deeds = tag.getCompound("deedsBought");
        for (String k : deeds.getAllKeys()) d.deedsBought.put(UUID.fromString(k), deeds.getInt(k));
        CompoundTag nicks = tag.getCompound("nicks");
        for (String k : nicks.getAllKeys()) d.nicks.put(UUID.fromString(k), nicks.getString(k));
        CompoundTag stats = tag.getCompound("stats");
        for (String k : stats.getAllKeys()) d.stats.put(UUID.fromString(k), stats.getCompound(k));
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
        CompoundTag money = new CompoundTag();
        this.money.forEach((id, n) -> money.putLong(id.toString(), n));
        tag.put("money", money);
        CompoundTag skins = new CompoundTag();
        npcSkins.forEach(skins::putString);
        tag.put("npcSkins", skins);
        CompoundTag deeds = new CompoundTag();
        deedsBought.forEach((id, n) -> deeds.putInt(id.toString(), n));
        tag.put("deedsBought", deeds);
        CompoundTag nicks = new CompoundTag();
        this.nicks.forEach((id, n) -> nicks.putString(id.toString(), n));
        tag.put("nicks", nicks);
        CompoundTag stats = new CompoundTag();
        this.stats.forEach((id, t) -> stats.put(id.toString(), t));
        tag.put("stats", stats);
        return tag;
    }
}
