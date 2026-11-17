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
        boolean contains(BlockPos p) { return p.getX() >= x1 && p.getX() <= x2 && p.getZ() >= z1 && p.getZ() <= z2; }
    }

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
            PokeServer.LOG.info("농장 땅 {}칸 불러옴", PLOTS.size());
        } catch (Exception ex) {
            // 목록이 없어도 농장 전체가 보호되므로 안전함 (아무도 편집 못 함)
            PokeServer.LOG.warn("농장 땅 목록을 못 읽음: {} ({})", f, ex.toString());
        }
    }

    public static boolean isFarm(Level level) {
        return level.dimension().location().toString().equals(dimension);
    }

    public static Plot plotAt(BlockPos pos) {
        for (Plot p : PLOTS) if (p.contains(pos)) return p;
        return null;
    }

    /** 농장에서 이 위치를 편집해도 되는가: 자기 땅 안이거나 관리자. */
    public static boolean canEdit(Player player, Level level, BlockPos pos) {
        if (!isFarm(level) || player.hasPermissions(2)) return true;
        Plot p = plotAt(pos);
        if (p == null || level.isClientSide()) return false;
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
        if (farm == null) return;
        ServerData data = ServerData.get(server);
        AABB all = new AABB(-30_000, -64, -30_000, 30_000, 320, 30_000);
        for (Display.TextDisplay d : farm.getEntities(EntityType.TEXT_DISPLAY, all, e -> true)) {
            for (String tag : d.getTags()) {
                if (!tag.startsWith("poke.plot")) continue;
                int id = Integer.parseInt(tag.substring("poke.plot".length()));
                ServerData.Owner o = data.plotOwners.get(id);
                Component text = o == null
                        ? Component.literal("농장 " + id + " (빈 땅)").withStyle(ChatFormatting.YELLOW, ChatFormatting.BOLD)
                        : Component.literal("농장 " + id + " · " + o.name()).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD);
                if (!text.equals(d.getText())) d.setText(text);
            }
        }
    }
}
