package com.pokeserver;

import com.google.gson.Gson;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** 4. 상점: 목록은 config/pokeserver/shop.json (서버가 열 때 클라이언트로 그대로 보냄). */
public final class Shop {
    public record Entry(String item, long buy, long sell, int badges) {}   // badges: 구매에 필요한 배지 수 (판매는 제한 없음)
    public record Category(String name, String icon, List<Entry> items) {}
    public record Data(List<Category> categories) {}

    static final Gson GSON = new Gson();
    static String json = "{\"categories\":[]}";
    static Data data = new Data(List.of());

    static void load() {
        Path f = FabricLoader.getInstance().getConfigDir().resolve("pokeserver/shop.json");
        try {
            String s = Files.readString(f);
            data = parse(s);
            json = s;
            PokeServer.LOG.info("상점 분류 {}개 불러옴", data.categories().size());
        } catch (Exception ex) {
            PokeServer.LOG.warn("상점 목록을 못 읽음: {} ({})", f, ex.toString());
        }
    }

    public static Data parse(String s) { return GSON.fromJson(s, Data.class); }

    /** 상점 항목 → 아이템. "pokeserver:farm_deed"는 땅 문서. */
    public static ItemStack stack(String id) {
        if ("pokeserver:farm_deed".equals(id)) return Farms.deed();
        ResourceLocation rl = ResourceLocation.tryParse(id);
        return rl == null ? ItemStack.EMPTY : new ItemStack(BuiltInRegistries.ITEM.get(rl));
    }

    public static boolean matches(ItemStack have, String id) {
        if ("pokeserver:farm_deed".equals(id)) return Farms.isDeed(have);
        return !have.isEmpty() && !Farms.isDeed(have) && have.is(stack(id).getItem()) && !have.is(Items.AIR);
    }

    /** 플레이어 주 인벤토리(입고 있는 장비 제외)에 몇 개 있나. */
    public static int count(net.minecraft.world.entity.player.Player p, String id) {
        int n = 0;
        for (ItemStack s : p.getInventory().items) if (matches(s, id)) n += s.getCount();
        return n;
    }

    static void open(ServerPlayer p) {
        net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking.send(p, new Net.ShopOpen(json, Money.get(p), badges(p)));
    }

    /** 모은 배지 수 (태그 poke.badge1~8). */
    public static int badges(net.minecraft.world.entity.player.Player p) {
        int n = 0;
        for (int i = 1; i <= 8; i++) if (p.getTags().contains("poke.badge" + i)) n++;
        return n;
    }

    /** 클라이언트 요청 검증 후 거래. 수량은 1~64. */
    static void trade(ServerPlayer p, boolean sell, int cat, int idx, int qty) {
        if (cat < 0 || cat >= data.categories().size()) return;
        List<Entry> items = data.categories().get(cat).items();
        if (idx < 0 || idx >= items.size() || qty < 1 || qty > 64) return;
        Entry e = items.get(idx);
        ItemStack proto = stack(e.item());
        if (proto.isEmpty()) return;
        if (!sell) {
            if (e.buy() <= 0 || e.badges() > badges(p)) return;
            long total = e.buy() * qty;
            if (!Money.take(p, total)) {
                msg(p, "잔액이 부족합니다.", ChatFormatting.RED);
            } else {
                for (int left = qty; left > 0; left -= proto.getMaxStackSize()) {
                    p.getInventory().placeItemBackInInventory(proto.copyWithCount(Math.min(left, proto.getMaxStackSize())));
                }
                msg(p, proto.getHoverName().getString() + " " + qty + "개 구매 (-" + Money.fmt(total) + ")", ChatFormatting.GREEN);
            }
        } else {
            if (e.sell() <= 0) return;
            int n = Math.min(qty, count(p, e.item()));
            if (n == 0) {
                msg(p, "판매할 아이템이 없습니다.", ChatFormatting.RED);
            } else {
                int left = n;
                for (ItemStack s : p.getInventory().items) {
                    if (left == 0) break;
                    if (!matches(s, e.item())) continue;
                    int take = Math.min(left, s.getCount());
                    s.shrink(take);
                    left -= take;
                }
                Money.add(p.server, p.getUUID(), e.sell() * n);
                msg(p, proto.getHoverName().getString() + " " + n + "개 판매 (+" + Money.fmt(e.sell() * n) + ")", ChatFormatting.GREEN);
            }
        }
        net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking.send(p, new Net.Balance(Money.get(p)));
    }

    static void msg(ServerPlayer p, String s, ChatFormatting c) {
        p.displayClientMessage(Component.literal(s).withStyle(c), true);
    }
}
