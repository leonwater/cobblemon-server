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
    /** badges: 구매에 필요한 배지 수 (판매는 제한 없음). daily: 매일 DAILY_N개만 살 수 있는 묶음 ("tm"·"gimmick", 없으면 null). */
    public record Entry(String item, long buy, long sell, int badges, String daily) {
        Entry with(long buy) { return new Entry(item, buy, sell, badges, daily); }
    }
    public record Category(String name, String icon, String shop, List<Entry> items) {}   // shop: poke(코블몬 상인) / mc(마인크래프트 상인)
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

    /** 상점 항목 → 아이템. "pokeserver:farm_deed"는 땅 문서, "cobblemon:technical_machine#기술"은 그 기술의 기술머신. */
    public static ItemStack stack(String id) {
        if ("pokeserver:farm_deed".equals(id)) return Farms.deed();
        int hash = id.indexOf('#');
        ResourceLocation rl = ResourceLocation.tryParse(hash < 0 ? id : id.substring(0, hash));
        if (rl == null) return ItemStack.EMPTY;
        ItemStack st = new ItemStack(BuiltInRegistries.ITEM.get(rl));
        if (hash >= 0 && !st.isEmpty()) {   // 코블몬 tm_move 부품 (코블몬이 없으면 아이템도 없어 여기 안 옴)
            var type = BuiltInRegistries.DATA_COMPONENT_TYPE.get(ResourceLocation.fromNamespaceAndPath("cobblemon", "tm_move"));
            var json = new com.google.gson.JsonObject();
            json.addProperty("move", id.substring(hash + 1));
            if (type == null || type.codec() == null) return ItemStack.EMPTY;
            var value = type.codec().parse(com.mojang.serialization.JsonOps.INSTANCE, json).result().orElse(null);
            if (value == null) return ItemStack.EMPTY;
            @SuppressWarnings("unchecked") var t = (net.minecraft.core.component.DataComponentType<Object>) type;
            st.set(t, value);
        }
        return st;
    }

    // 7·8. 매일(한국 시간 자정에 바뀜) 묶음마다 DAILY_N개만 살 수 있음. 같은 날엔 누구에게나 같은 상품.
    static final int DAILY_N = 5;
    static long dailyDay = -1;
    static java.util.Set<String> dailyPick = java.util.Set.of();

    static java.util.Set<String> todays() {
        long day = java.time.LocalDate.now(java.time.ZoneId.of("Asia/Seoul")).toEpochDay();
        if (day != dailyDay) {
            var groups = new java.util.TreeMap<String, java.util.List<String>>();
            for (var c : data.categories()) for (var e : c.items()) if (e.daily() != null && e.buy() > 0) groups.computeIfAbsent(e.daily(), k -> new java.util.ArrayList<>()).add(e.item());
            var pick = new java.util.HashSet<String>();
            groups.forEach((g, list) -> {
                var l = new java.util.ArrayList<>(list);
                java.util.Collections.shuffle(l, new java.util.Random(day * 1_000_003L + g.hashCode()));
                pick.addAll(l.subList(0, Math.min(DAILY_N, l.size())));
            });
            dailyPick = pick;
            dailyDay = day;
        }
        return dailyPick;
    }

    /** 오늘 고른 상품이 아니면 구매만 막음 (판매는 그대로). */
    static Entry today(Entry e) { return e.daily() == null || todays().contains(e.item()) ? e : e.with(0); }

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

    static final java.util.Map<java.util.UUID, String> opened = new java.util.HashMap<>();   // 이 사람이 연 상점 (null = 전체, 관리자 명령)

    static void open(ServerPlayer p) { open(p, null); }

    static void open(ServerPlayer p, String shop) {
        opened.put(p.getUUID(), shop);
        net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking.send(p, new Net.ShopOpen(jsonFor(p), Money.get(p), badges(p)));
    }

    /** 이 사람이 지금 보는 분류 (클라이언트가 보내는 분류 번호도 이 목록 기준). */
    static List<Category> cats(ServerPlayer p) {
        String s = opened.get(p.getUUID());
        return data.categories().stream().filter(c -> s == null || s.equals(c.shop()))
                .map(c -> new Category(c.name(), c.icon(), c.shop(), c.items().stream().map(Shop::today).toList())).toList();
    }

    /** 3. 땅 문서는 한 사람이 살수록 비싸짐: 기본 가격 × (산 개수 + 1). 다른 사람과는 따로 셈. */
    static long deedPrice(ServerPlayer p, long base, int extra) {
        return base * (ServerData.get(p.server).deedsBought.getOrDefault(p.getUUID(), 0) + extra + 1);
    }

    /** 이 플레이어가 보는 목록 (땅 문서 가격만 사람마다 다름). */
    static String jsonFor(ServerPlayer p) {
        return GSON.toJson(new Data(cats(p).stream().map(c -> new Category(c.name(), c.icon(), c.shop(), c.items().stream()
                .map(e -> isDeedEntry(e) ? e.with(deedPrice(p, e.buy(), 0)) : e).toList())).toList()));
    }

    static boolean isDeedEntry(Entry e) { return "pokeserver:farm_deed".equals(e.item()) && e.buy() > 0; }

    /** 모은 배지 수 (태그 poke.badge1~8). */
    public static int badges(net.minecraft.world.entity.player.Player p) {
        int n = 0;
        for (int i = 1; i <= 8; i++) if (p.getTags().contains("poke.badge" + i)) n++;
        return n;
    }

    /** 클라이언트 요청 검증 후 거래. 수량은 1~64. */
    static void trade(ServerPlayer p, boolean sell, int cat, int idx, int qty) {
        var cs = cats(p);
        if (cat < 0 || cat >= cs.size()) return;
        List<Entry> items = cs.get(cat).items();
        if (idx < 0 || idx >= items.size() || qty < 1 || qty > 64) return;
        Entry e = items.get(idx);
        ItemStack proto = stack(e.item());
        if (proto.isEmpty()) return;
        if (!sell) {
            if (e.buy() <= 0 || e.badges() > badges(p)) return;
            long total = 0;
            for (int k = 0; k < qty; k++) total += isDeedEntry(e) ? deedPrice(p, e.buy(), k) : e.buy();
            if (!Money.take(p, total)) {
                msg(p, "잔액이 부족합니다.", ChatFormatting.RED);
            } else {
                Titles.add(p, "spent", total);
                for (int left = qty; left > 0; left -= proto.getMaxStackSize()) {
                    p.getInventory().placeItemBackInInventory(proto.copyWithCount(Math.min(left, proto.getMaxStackSize())));
                }
                msg(p, proto.getHoverName().getString() + " " + qty + "개 구매 (-" + Money.fmt(total) + ")", ChatFormatting.GREEN);
                if (isDeedEntry(e)) {
                    ServerData d = ServerData.get(p.server);
                    d.deedsBought.merge(p.getUUID(), qty, Integer::sum);
                    d.setDirty();
                    open(p, opened.get(p.getUUID()));   // 다음 문서 가격을 바로 보여 줌
                    return;
                }
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
                Titles.add(p, "earned", e.sell() * n);
                msg(p, proto.getHoverName().getString() + " " + n + "개 판매 (+" + Money.fmt(e.sell() * n) + ")", ChatFormatting.GREEN);
            }
        }
        net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking.send(p, new Net.Balance(Money.get(p)));
    }

    static void msg(ServerPlayer p, String s, ChatFormatting c) {
        p.displayClientMessage(Component.literal(s).withStyle(c), true);
    }
}
