package com.pokeserver;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.function.ToLongFunction;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/** 7. 별명: 조건을 채우면 얻고, G 메뉴 → 별명에서 고름 (안 고르면 우선순위가 가장 높은 것). 화면엔 "[별명] 닉네임". */
public final class Titles {
    private Titles() {}

    /** need: 조건 값이 이 이상이면 얻음. announce: 얻으면 서버 전체 공지. */
    record Title(String id, String name, String color, String how, ToLongFunction<ServerPlayer> value, long need, boolean announce) {
        boolean has(ServerPlayer p) { return value.applyAsLong(p) >= need; }
        String shown() { return color + "[" + name + "]"; }
    }

    static long op(ServerPlayer p) { return p.server.getPlayerList().isOp(p.getGameProfile()) ? 1 : 0; }
    static long champ(ServerPlayer p) { return p.getTags().contains("poke.e4clear") ? 1 : 0; }
    static long badges(ServerPlayer p) { return Nicknames.badges(p); }
    static long dex(ServerPlayer p) {
        return net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon") ? CobblemonHooks.dex(p).get(0) : 0;
    }
    static long stat(ServerPlayer p, String k) { return ServerData.get(p.server).stats.getOrDefault(p.getUUID(), new net.minecraft.nbt.CompoundTag()).getLong(k); }
    static long plots(ServerPlayer p) {
        return ServerData.get(p.server).plotOwners.values().stream().filter(o -> o.id().equals(p.getUUID())).count();
    }

    /** 우선순위 순 (앞이 높음). */
    static final List<Title> ALL = List.of(
            new Title("op", "운영자", "§c", "서버 관리자", Titles::op, 1, false),
            new Title("champion", "챔피언", "§6", "사천왕 클리어", Titles::champ, 1, true),
            new Title("dex_all", "도감 완성", "§e", "잡은 포켓몬 1025종", Titles::dex, 1025, true),
            new Title("tycoon", "재벌", "§6", "지금까지 번 돈 1억원", p -> stat(p, "earned"), 100_000_000, false),
            new Title("duel2", "결투왕", "§c", "플레이어 배틀 50승", p -> stat(p, "pvp"), 50, false),
            new Title("legend", "전설의 사냥꾼", "§5", "전설·환상 포켓몬 포획", p -> stat(p, "legend"), 1, true),
            new Title("badge8", "배지 마스터", "§d", "배지 8개", Titles::badges, 8, false),
            new Title("dex500", "도감 박사", "§b", "잡은 포켓몬 500종", Titles::dex, 500, false),
            new Title("rich", "부자", "§e", "지금까지 번 돈 1,000만원", p -> stat(p, "earned"), 10_000_000, false),
            new Title("bigspender", "큰손", "§e", "상점에서 쓴 돈 1,000만원", p -> stat(p, "spent"), 10_000_000, false),
            new Title("duel1", "결투가", "§c", "플레이어 배틀 10승", p -> stat(p, "pvp"), 10, false),
            new Title("badge4", "베테랑 트레이너", "§b", "배지 4개", Titles::badges, 4, false),
            new Title("dex200", "도감 연구원", "§3", "잡은 포켓몬 200종", Titles::dex, 200, false),
            new Title("landlord", "대지주", "§2", "농장 땅 3칸", Titles::plots, 3, false),
            new Title("merchant", "알뜰 상인", "§a", "지금까지 번 돈 100만원", p -> stat(p, "earned"), 1_000_000, false),
            new Title("regular", "단골 손님", "§a", "상점에서 쓴 돈 100만원", p -> stat(p, "spent"), 1_000_000, false),
            new Title("dex50", "포켓몬 수집가", "§a", "잡은 포켓몬 50종", Titles::dex, 50, false),
            new Title("badge1", "견습 트레이너", "§a", "배지 1개", Titles::badges, 1, false));

    static void add(ServerPlayer p, String key, long n) {
        var t = ServerData.get(p.server).stats(p.getUUID());
        t.putLong(key, t.getLong(key) + n);
    }

    static void add(net.minecraft.server.MinecraftServer server, java.util.UUID id, String key, long n) {
        var t = ServerData.get(server).stats(id);
        t.putLong(key, t.getLong(key) + n);
    }

    /** 보이는 별명 (§색[이름]) 또는 "" — 고른 것이 아직 있으면 그것, "none"이면 숨김, 아니면 가장 높은 것. */
    static String shown(ServerPlayer p) {
        String pick = stat(p) .getString("title");
        if (pick.equals("none")) return "";
        Title best = null;
        for (Title t : ALL) {
            if (!t.has(p)) continue;
            if (t.id().equals(pick)) return t.shown();
            if (best == null) best = t;
        }
        return best == null ? "" : best.shown();
    }

    static net.minecraft.nbt.CompoundTag stat(ServerPlayer p) {
        return ServerData.get(p.server).stats.getOrDefault(p.getUUID(), new net.minecraft.nbt.CompoundTag());
    }

    /** 1초마다: 새로 얻은 별명 알림 (처음 한 번은 조용히 기록만). */
    static void check(ServerPlayer p) {
        var st = ServerData.get(p.server).stats.get(p.getUUID());
        boolean first = st == null || !st.contains("got");
        var got = new LinkedHashSet<>(st == null || st.getString("got").isEmpty() ? List.of() : Arrays.asList(st.getString("got").split(",")));
        boolean changed = false;
        for (Title t : ALL) {
            if (got.contains(t.id()) || !t.has(p)) continue;
            got.add(t.id());
            changed = true;
            if (first) continue;
            p.sendSystemMessage(Component.literal("새 별명을 얻었어요: ").withStyle(ChatFormatting.GOLD)
                    .append(Component.literal(t.shown())).append(Component.literal("  (G 메뉴 → 별명에서 고를 수 있어요)").withStyle(ChatFormatting.GRAY)));
            if (t.announce()) p.server.getPlayerList().broadcastSystemMessage(Component.literal("[별명] ").withStyle(ChatFormatting.GOLD)
                    .append(Component.literal(Nicknames.nick(p) + "님이 ")).append(Component.literal(t.shown()))
                    .append(Component.literal(" 별명을 얻었습니다!").withStyle(ChatFormatting.YELLOW)), false);
        }
        if (changed || first) ServerData.get(p.server).stats(p.getUUID()).putString("got", String.join(",", got));
    }

    /** 별명 고르기 창 내용: 한 줄에 id \t 보이는 이름 \t 조건 \t 얻음(1/0) \t 사용 중(1/0). 맨 위 "none" = 숨기기. */
    static String list(ServerPlayer p) {
        String now = shown(p);
        List<String> rows = new ArrayList<>();
        rows.add("none\t§7[표시 안 함]\t별명을 숨겨요\t1\t" + (now.isEmpty() ? 1 : 0));
        for (Title t : ALL) rows.add(t.id() + "\t" + t.shown() + "\t" + t.how() + "\t" + (t.has(p) ? 1 : 0) + "\t" + (t.shown().equals(now) ? 1 : 0));
        return String.join("\n", rows);
    }

    static void pick(ServerPlayer p, String id) {
        if (!id.equals("none") && ALL.stream().noneMatch(t -> t.id().equals(id) && t.has(p))) return;
        ServerData.get(p.server).stats(p.getUUID()).putString("title", id);
    }
}
