package com.pokeserver;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

/** 농장 땅: 목록(config/pokeserver/farms.json), 땅 문서, 주인 확인. */
public final class Farms {
    public record Plot(int id, int x1, int z1, int x2, int z2) {
        boolean contains(BlockPos p) { return p.getX() >= x1 && p.getX() <= x2 && p.getZ() >= z1 && p.getZ() <= z2 && p.getY() >= MIN_Y && p.getY() <= MAX_Y; }
    }
    /** 농장 높이 제한: 땅(y -60) 아래 5칸 ~ 위 10칸 (월드 바닥은 -64라 아래는 사실상 끝까지). 밖은 누구의 땅도 아니라 못 고침. */
    static final int MIN_Y = -65, MAX_Y = -50;

    static String dimension = "poke:farm";
    static final List<Plot> PLOTS = new ArrayList<>();

    static void load() {
        PLOTS.clear();
        Path f = FabricLoader.getInstance().getConfigDir().resolve("pokeserver/farms.json");
        try {
            JsonObject o = JsonParser.parseString(Files.readString(f)).getAsJsonObject();
            dimension = o.get("dimension").getAsString();
            for (var e : o.getAsJsonArray("plots")) {
                JsonObject p = e.getAsJsonObject();
                PLOTS.add(new Plot(p.get("id").getAsInt(), p.get("x1").getAsInt(), p.get("z1").getAsInt(),
                        p.get("x2").getAsInt(), p.get("z2").getAsInt()));
            }
            CHUNKS.clear();
            for (Plot p : PLOTS) for (int cx = p.x1() >> 4; cx <= p.x2() >> 4; cx++) for (int cz = p.z1() >> 4; cz <= p.z2() >> 4; cz++)
                CHUNKS.add(net.minecraft.world.level.ChunkPos.asLong(cx, cz));
            PokeServer.LOG.info("농장 땅 {}칸 불러옴", PLOTS.size());
        } catch (Exception ex) {
            // 목록이 없어도 농장 전체가 보호되므로 안전함 (아무도 편집 못 함)
            PokeServer.LOG.warn("농장 땅 목록을 못 읽음: {} ({})", f, ex.toString());
        }
    }

    /** 땅이 걸친 청크 (ChunkPos.asLong). */
    static final java.util.Set<Long> CHUNKS = new java.util.LinkedHashSet<>();

    /** 3.4.0: 아무도 없어도 농장 시간이 감. 1.21.1은 플레이어 128칸 안 청크만 무작위 틱(작물·나무열매 성장)을 받음
     *  → 땅 청크를 강제 로드해 두고, 근처(128칸)에 사람이 없는 청크만 직접 틱 (사람이 있으면 바닐라가 하므로 두 번 안 함). */
    static void forceLoad(MinecraftServer server) {
        ServerLevel level = farmLevel(server);
        if (level == null) return;
        var forced = level.getForcedChunks();
        for (long c : CHUNKS) if (!forced.contains(c)) level.setChunkForced(net.minecraft.world.level.ChunkPos.getX(c), net.minecraft.world.level.ChunkPos.getZ(c), true);
    }

    static ServerLevel farmLevel(MinecraftServer server) {
        for (ServerLevel l : server.getAllLevels()) if (isFarm(l)) return l;
        return null;
    }

    static void tickEmpty(ServerLevel level) {
        int speed = level.getGameRules().getInt(net.minecraft.world.level.GameRules.RULE_RANDOMTICKING);
        if (speed <= 0) return;
        for (long c : CHUNKS) {
            int cx = net.minecraft.world.level.ChunkPos.getX(c), cz = net.minecraft.world.level.ChunkPos.getZ(c);
            double mx = cx * 16 + 8, mz = cz * 16 + 8;
            if (level.players().stream().anyMatch(p -> !p.isSpectator() && (p.getX() - mx) * (p.getX() - mx) + (p.getZ() - mz) * (p.getZ() - mz) < 128 * 128)) continue;
            var chunk = level.getChunkSource().getChunkNow(cx, cz);
            if (chunk != null) level.tickChunk(chunk, speed);
        }
    }

    public static boolean isFarm(Level level) {
        return level.dimension().location().toString().equals(dimension);
    }

    /** 이 위치를 왜 편집할 수 없는지: 체력바 위 알림 문구. */
    public static Component denyReason(Level level, BlockPos pos) {
        if (Plaza.protects(level, pos)) return Component.literal("광장 둘레는 수정할 수 없어요").withStyle(ChatFormatting.RED);
        if (!isFarm(level)) return Component.literal("블록은 야생에서만 캘 수 있어요").withStyle(ChatFormatting.RED);
        Plot p = plotAt(pos);
        if (p == null) return Component.literal("공용 길은 편집할 수 없습니다").withStyle(ChatFormatting.RED);
        ServerData.Owner o = level.isClientSide() ? null : ServerData.get(level.getServer()).plotOwners.get(p.id());
        return o == null
                ? Component.literal("농장 " + p.id() + "번 · 주인 없는 땅입니다 (땅 문서로 등록)").withStyle(ChatFormatting.YELLOW)
                : Component.literal("농장 " + p.id() + "번 · " + o.name() + "님의 땅입니다").withStyle(ChatFormatting.RED);
    }

    public static Plot plotAt(BlockPos pos) {
        for (Plot p : PLOTS) if (p.contains(pos)) return p;
        return null;
    }

    /** 두 위치가 같은 땅 안인가 (둘 다 땅 밖이면 false: 길로 흘러나가는 것도 막음). */
    public static boolean samePlot(BlockPos a, BlockPos b) {
        Plot p = plotAt(a);
        return p != null && p.contains(b);
    }

    /** 이 위치를 편집해도 되는가: 야생은 누구나, 농장은 자기 땅만, 나머지는 불가. 관리자는 크리에이티브일 때만 예외. */
    public static boolean canEdit(Player player, Level level, BlockPos pos) {
        // 클라이언트는 땅 주인 목록이 없으므로 판단은 서버에 맡김 (서버가 막으면 블록이 되돌아감)
        if (level.isClientSide() || player.isCreative() && player.hasPermissions(2)) return true;
        if (level.dimension().location().toString().equals("poke:wild")) return !Plaza.protects(level, pos);   // 15. 광장 둘레만 막음
        if (!isFarm(level)) return false;
        Plot p = plotAt(pos);
        if (p == null) return false;
        ServerData.Owner o = ServerData.get(level.getServer()).plotOwners.get(p.id());
        return o != null && o.id().equals(player.getUUID());
    }

    // ── 땅 문서 (종이 + 표시) ──
    static final String DEED = "farm_deed";

    public static ItemStack deed() {
        ItemStack s = new ItemStack(Items.PAPER);
        CompoundTag t = new CompoundTag();
        t.putString(PokeServer.ID, DEED);
        s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
        s.set(DataComponents.CUSTOM_NAME, Component.literal("땅 문서").setStyle(Style.EMPTY.withItalic(false).withColor(ChatFormatting.GOLD)));
        s.set(DataComponents.LORE, new ItemLore(List.of(
                Component.literal("농장의 빈 땅을 우클릭하면").setStyle(Style.EMPTY.withItalic(false).withColor(ChatFormatting.GRAY)),
                Component.literal("내 땅으로 등록할 수 있습니다").setStyle(Style.EMPTY.withItalic(false).withColor(ChatFormatting.GRAY)))));
        return s;
    }

    public static boolean isDeed(ItemStack s) {
        return s.is(Items.PAPER) && DEED.equals(s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getString(PokeServer.ID));
    }

    /** 팝업에서 확인: 서버에서 다시 검증 후 등록. */
    static void claim(ServerPlayer player, int id) {
        Plot plot = PLOTS.stream().filter(p -> p.id() == id).findFirst().orElse(null);
        ServerData data = ServerData.get(player.server);
        if (plot == null || !isFarm(player.level())) return;
        if (data.plotOwners.containsKey(id)) {
            player.displayClientMessage(Component.literal("이미 주인이 있는 땅입니다.").withStyle(ChatFormatting.RED), false);
            return;
        }
        // 땅 근처에 있어야 함 (멀리서 패킷만 보내는 것 방지)
        AABB near = new AABB(plot.x1() - 8, -1000, plot.z1() - 8, plot.x2() + 9, 1000, plot.z2() + 9);
        if (!near.contains(player.position())) return;
        int slot = -1;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            if (isDeed(player.getInventory().getItem(i))) { slot = i; break; }
        }
        if (slot < 0) {
            player.displayClientMessage(Component.literal("땅 문서가 없습니다.").withStyle(ChatFormatting.RED), false);
            return;
        }
        player.getInventory().getItem(slot).shrink(1);
        data.plotOwners.put(id, new ServerData.Owner(player.getUUID(), player.getGameProfile().getName()));
        data.setDirty();
        player.displayClientMessage(Component.literal("농장 " + id + "번 땅이 내 땅이 되었습니다!").withStyle(ChatFormatting.GREEN), false);
        refreshLabels(player.server);
    }

    /** 땅 이름표(text_display, 태그 poke.plotN)를 주인 이름으로. 불러와진 것만 바뀌므로 주기적으로 호출. */
    static void refreshLabels(MinecraftServer server) {
        ServerLevel farm = null;
        for (ServerLevel l : server.getAllLevels()) if (isFarm(l)) farm = l;
        if (farm == null || farm.players().isEmpty()) return;   // 아무도 없으면 안 봄 (들어오면 5초 안에 맞춰짐)
        ServerData data = ServerData.get(server);
        AABB all = new AABB(-30_000, -64, -30_000, 30_000, 320, 30_000);
        for (Display.TextDisplay d : farm.getEntities(EntityType.TEXT_DISPLAY, all, e -> true)) {
            for (String tag : d.getTags()) {
                if (!tag.startsWith("poke.plot")) continue;
                int id = Integer.parseInt(tag.substring("poke.plot".length()));
                ServerData.Owner o = data.plotOwners.get(id);
                // 빈 땅만 보이게, 주인이 있으면 숨김 (배경 투명이라 빈 글자면 안 보임)
                Component text = o == null
                        ? Component.literal("농장 " + id + "\n").withStyle(ChatFormatting.YELLOW, ChatFormatting.BOLD)
                                .append(Component.literal("빈 땅 · 땅 문서로 등록").withStyle(ChatFormatting.WHITE))
                        : Component.empty();
                if (!text.equals(d.getText())) d.setText(text);
            }
        }
    }
}
