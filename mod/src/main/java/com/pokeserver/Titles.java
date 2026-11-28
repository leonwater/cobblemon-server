package com.pokeserver;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.ToLongFunction;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.phys.Vec3;

/** 7. 칭호: 조건을 채우면 얻고, G 메뉴 → 칭호에서 고름 (안 고르면 우선순위(rank)가 가장 높은 것). 화면엔 "[칭호] 닉네임".
 *  이름은 포켓몬 게임 속 직함·장소·도구에서 따옴, 정확한 조건 수치는 docs/칭호.md에만 (화면엔 hint만). */
public final class Titles {
    private Titles() {}

    /** group: 고르기 창에서 같은 줄로 묶는 갈래 (0 숨기기·운영자, 1 리그, 2 대결, 3 도감, 4 포획, 5 야생·육성, 6 배틀 기믹, 7 돈, 8 농장, 9 꾸준함).
     *  rank: 우선순위 (작을수록 높음, 안 고르면 이것이 붙음). need: 조건 값이 이 이상이면 얻음. announce: 얻으면 서버 전체 공지. */
    record Title(String id, int group, int rank, String name, String color, String hint, ToLongFunction<ServerPlayer> value, long need, boolean announce) {
        boolean has(ServerPlayer p) { return value.applyAsLong(p) >= need; }
        String shown() { return color + "[" + name + "]"; }
    }

    static long op(ServerPlayer p) { return p.server.getPlayerList().isOp(p.getGameProfile()) ? 1 : 0; }
    static ToLongFunction<ServerPlayer> tag(String t) { return p -> p.getTags().contains(t) ? 1 : 0; }
    static ToLongFunction<ServerPlayer> stat(String k) { return p -> stat(p, k); }
    static long badges(ServerPlayer p) { return Nicknames.badges(p); }
    /** 잡은 종·마주친 종: 1초에 한 번만 셈 (여러 칭호가 같은 값을 씀, Nicknames.tick이 비움). */
    static final Map<UUID, List<Integer>> DEX = new HashMap<>();
    static long dex(ServerPlayer p, int i) {
        if (!net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) return 0;
        return DEX.computeIfAbsent(p.getUUID(), id -> CobblemonHooks.dex(p)).get(i);
    }
    static long stat(ServerPlayer p, String k) { return ServerData.get(p.server).stats.getOrDefault(p.getUUID(), new net.minecraft.nbt.CompoundTag()).getLong(k); }
    static long plots(ServerPlayer p) {
        return ServerData.get(p.server).plotOwners.values().stream().filter(o -> o.id().equals(p.getUUID())).count();
    }
    static long hours(ServerPlayer p) { return p.getStats().getValue(Stats.CUSTOM.get(Stats.PLAY_TIME)) / 72_000; }

    /** 고르기 창 순서 = 이 순서 (갈래별, 갈래 안은 쉬운 것 → 어려운 것). */
    static final List<Title> ALL = List.of(
            new Title("op", 0, 1, "운영자", "§c", "서버를 지키는 사람", Titles::op, 1, false),
            // 리그
            new Title("badge1", 1, 37, "포켓몬 트레이너", "§a", "첫 체육관을 이긴 트레이너", Titles::badges, 1, false),
            new Title("badge4", 1, 28, "엘리트트레이너", "§b", "체육관 절반을 이긴 트레이너", Titles::badges, 4, false),
            new Title("badge8", 1, 12, "베테랑", "§d", "여덟 체육관을 모두 이긴 트레이너", Titles::badges, 8, false),
            new Title("champion", 1, 2, "챔피언", "§6", "리그 정상에 오른 트레이너", tag("poke.e4clear"), 1, true),
            new Title("e4first", 1, 3, "무적의 챔피언", "§6", "한 번에 정상에 선 트레이너", tag("poke.e4first"), 1, true),
            new Title("perfect", 1, 11, "퍼펙트", "§6", "관장 앞에서 한 마리도 쓰러지지 않은 승리", stat("perfect"), 1, false),
            new Title("firstclear", 1, 6, "퍼스트 클리어", "§5", "누구보다 먼저 이긴 트레이너", tag("poke.firstclear"), 1, true),
            // 대결 (플레이어끼리)
            new Title("duel1", 2, 24, "배틀 타워 도전자", "§c", "대결에 익숙해진 트레이너", stat("pvp"), 10, false),
            new Title("duel2", 2, 7, "프런티어 브레인", "§c", "수많은 대결을 이긴 강자", stat("pvp"), 50, false),
            new Title("streak", 2, 8, "타워 타이쿤", "§c", "지지 않고 이어 가는 연승", stat("streakmax"), 10, false),
            // 도감
            new Title("dex50", 3, 36, "연구소 조수", "§a", "도감 채우기를 시작한 트레이너", p -> dex(p, 0), 50, false),
            new Title("dex200", 3, 29, "포켓몬 연구원", "§3", "도감 연구에 익숙한 연구자", p -> dex(p, 0), 200, false),
            new Title("dex500", 3, 15, "포켓몬 박사", "§b", "도감 절반을 채운 연구자", p -> dex(p, 0), 500, false),
            new Title("dex_all", 3, 4, "포켓몬 마스터", "§e", "모든 포켓몬을 잡은 트레이너", p -> dex(p, 0), 1025, true),
            new Title("seen", 3, 14, "포켓몬 워처", "§7", "모든 포켓몬을 본 관찰자", p -> dex(p, 1), 1025, false),
            // 포획
            new Title("legend", 4, 9, "영웅", "§5", "전설의 포켓몬이 인정한 트레이너", stat("legend"), 1, true),
            new Title("shiny1", 4, 10, "럭키", "§e", "색이 다른 포켓몬을 만난 행운", stat("shiny"), 1, true),
            new Title("shiny10", 4, 5, "빛나는부적", "§6", "빛나는 포켓몬을 여럿 모은 트레이너", stat("shiny"), 10, true),
            new Title("fish", 4, 25, "낚시꾼", "§9", "물가를 지키는 트레이너", stat("fish"), 100, false),
            new Title("fossil", 4, 26, "유적마니아", "§4", "오래전 포켓몬을 되살린 트레이너", stat("fossil"), 10, false),
            // 야생·육성
            new Title("wild", 5, 20, "포켓몬레인저", "§2", "야생을 누비며 싸운 트레이너", stat("wild"), 1000, false),
            new Title("alpha", 5, 19, "우두머리 사냥꾼", "§6", "무리를 이끄는 큰 포켓몬을 이긴 트레이너", stat("alpha"), 10, false),
            new Title("walk", 5, 27, "백팩커", "§3", "야생을 멀리 누빈 여행자", stat("walk"), 100_000, false),
            new Title("lv100", 5, 16, "포켓몬브리더", "§5", "한 마리를 끝까지 키운 트레이너", stat("lv100"), 1, false),
            // 배틀 기믹
            new Title("mega", 6, 13, "키스톤의 주인", "§d", "메가진화를 다루는 트레이너", stat("mega"), 50, false),
            new Title("zmove", 6, 13, "섬킹", "§e", "Z의 힘을 끌어낸 트레이너", stat("zmove"), 50, false),
            new Title("dmax", 6, 13, "가라르 스타", "§c", "거대해진 포켓몬과 싸운 트레이너", stat("dmax"), 50, false),
            new Title("tera", 6, 13, "테라 레이드 마스터", "§b", "결정의 힘을 다루는 트레이너", stat("tera"), 50, false),
            new Title("megastones", 6, 17, "메가스톤 콜렉터", "§d", "여러 메가스톤을 모은 트레이너", stat("megastones"), 20, false),
            new Title("zcrystals", 6, 17, "크리스탈 콜렉터", "§e", "모든 타입의 결정을 모은 트레이너", stat("zcrystals"), 18, false),
            // 돈
            new Title("merchant", 7, 34, "도련님", "§a", "물건을 팔아 돈을 모은 트레이너", stat("earned"), 1_000_000, false),
            new Title("rich", 7, 21, "신사", "§e", "큰돈을 모은 트레이너", stat("earned"), 10_000_000, false),
            new Title("regular", 7, 35, "프렌들리숍 단골", "§a", "상점을 자주 찾는 손님", stat("spent"), 1_000_000, false),
            new Title("bigspender", 7, 22, "백화점 VIP", "§e", "상점의 최고 손님", stat("spent"), 10_000_000, false),
            // 농장
            new Title("landlord", 8, 31, "텃밭 농부", "§a", "여러 칸 땅을 가꾸는 농부", Titles::plots, 3, false),
            new Title("harvest", 8, 30, "나무열매 명인", "§2", "부지런히 거둔 농부", stat("harvest"), 1000, false),
            // 꾸준함
            new Title("hours", 9, 32, "오랜 파트너", "§b", "오랜 시간 함께한 트레이너", Titles::hours, 100, false));

    /** 우선순위 순 (shown()이 앞에서부터 찾음). */
    static final List<Title> BY_RANK = ALL.stream().sorted(java.util.Comparator.comparingInt(Title::rank)).toList();

    static void add(ServerPlayer p, String key, long n) {
        var t = ServerData.get(p.server).stats(p.getUUID());
        t.putLong(key, t.getLong(key) + n);
    }

    static void add(net.minecraft.server.MinecraftServer server, UUID id, String key, long n) {
        var t = ServerData.get(server).stats(id);
        t.putLong(key, t.getLong(key) + n);
    }

    /** 플레이어 배틀 결과: 이기면 연승 +1 (최고 연승 기록), 지면 0. */
    static void pvp(net.minecraft.server.MinecraftServer server, UUID id, boolean won) {
        var t = ServerData.get(server).stats(id);
        if (!won) { t.putLong("streak", 0); return; }
        t.putLong("pvp", t.getLong("pvp") + 1);
        t.putLong("streak", t.getLong("streak") + 1);
        t.putLong("streakmax", Math.max(t.getLong("streakmax"), t.getLong("streak")));
    }

    /** 보이는 칭호 (§색[이름]) 또는 "" — 고른 것이 아직 있으면 그것, "none"이면 숨김, 아니면 가장 높은 것. */
    static String shown(ServerPlayer p) {
        String pick = stat(p).getString("title");
        if (pick.equals("none")) return "";
        Title best = null;
        for (Title t : BY_RANK) {
            if (!t.has(p)) continue;
            if (t.id().equals(pick)) return t.shown();
            if (best == null) best = t;
        }
        return best == null ? "" : best.shown();
    }

    static net.minecraft.nbt.CompoundTag stat(ServerPlayer p) {
        return ServerData.get(p.server).stats.getOrDefault(p.getUUID(), new net.minecraft.nbt.CompoundTag());
    }

    // 타입 Z크리스탈 18종 (전용 Z크리스탈은 빼고 셈)
    static final Set<String> TYPE_Z = Set.of("normalium_z", "firium_z", "waterium_z", "grassium_z", "electrium_z", "icium_z", "fightinium_z", "poisonium_z", "groundium_z",
            "flyinium_z", "psychium_z", "buginium_z", "rockium_z", "ghostium_z", "dragonium_z", "darkinium_z", "steelium_z", "fairium_z");
    static final TagKey<Item> MEGA_STONE = TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("mega_showdown", "mega_stone"));
    static final Map<UUID, Vec3> LAST_POS = new HashMap<>();

    /** 1초마다 기록: 야생 이동 거리, 가방의 메가스톤·타입 Z크리스탈 종류(가장 많았을 때), 레벨 100 포켓몬. */
    static void track(ServerPlayer p) {
        var st = ServerData.get(p.server).stats(p.getUUID());
        Vec3 now = p.position(), before = LAST_POS.put(p.getUUID(), now);
        if (before != null && p.level().dimension().location().toString().equals("poke:wild")) {
            double d = Math.hypot(now.x - before.x, now.z - before.z);
            if (d < 64) st.putDouble("walkf", st.getDouble("walkf") + d);   // 순간이동(64칸 이상)은 안 셈
            st.putLong("walk", (long) st.getDouble("walkf"));
        }
        Set<Item> stones = new HashSet<>(), crystals = new HashSet<>();
        for (var s : p.getInventory().items) {
            if (s.isEmpty()) continue;
            if (s.is(MEGA_STONE)) stones.add(s.getItem());
            var id = BuiltInRegistries.ITEM.getKey(s.getItem());
            if (id.getNamespace().equals("mega_showdown") && TYPE_Z.contains(id.getPath())) crystals.add(s.getItem());
        }
        st.putLong("megastones", Math.max(st.getLong("megastones"), stones.size()));
        st.putLong("zcrystals", Math.max(st.getLong("zcrystals"), crystals.size()));
        if (st.getLong("lv100") == 0 && net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon") && CobblemonHooks.maxPartyLevel(p) >= 100)
            st.putLong("lv100", 1);
    }

    /** 1초마다: 기록 갱신 후 새로 얻은 칭호 알림 (처음 한 번은 조용히 기록만). */
    static void check(ServerPlayer p) {
        track(p);
        var st = ServerData.get(p.server).stats.get(p.getUUID());
        boolean first = st == null || !st.contains("got");
        var got = new LinkedHashSet<>(st == null || st.getString("got").isEmpty() ? List.of() : Arrays.asList(st.getString("got").split(",")));
        boolean changed = false;
        for (Title t : BY_RANK) {
            if (got.contains(t.id()) || !t.has(p)) continue;
            got.add(t.id());
            changed = true;
            if (first) continue;
            p.sendSystemMessage(Component.literal("새 칭호를 얻었어요: ").withStyle(ChatFormatting.GOLD)
                    .append(Component.literal(t.shown())).append(Component.literal("  (G 메뉴 → 칭호에서 고를 수 있어요)").withStyle(ChatFormatting.GRAY)));
            if (t.announce()) p.server.getPlayerList().broadcastSystemMessage(Component.literal("[칭호] ").withStyle(ChatFormatting.GOLD)
                    .append(Component.literal(Nicknames.nick(p) + "님이 ")).append(Component.literal(t.shown()))
                    .append(Component.literal(" 칭호를 얻었습니다!").withStyle(ChatFormatting.YELLOW)), false);
        }
        if (changed || first) ServerData.get(p.server).stats(p.getUUID()).putString("got", String.join(",", got));
    }

    /** 칭호 고르기 창 내용: 한 줄에 id \t 보이는 이름 \t 힌트(정확한 수치 없음) \t 얻음(1/0) \t 사용 중(1/0) \t 갈래. 맨 위 "none" = 숨기기. */
    static String list(ServerPlayer p) {
        String now = shown(p);
        List<String> rows = new ArrayList<>();
        rows.add("none\t§7[표시 안 함]\t칭호 숨기기\t1\t" + (now.isEmpty() ? 1 : 0) + "\t0");
        for (Title t : ALL) rows.add(t.id() + "\t" + t.shown() + "\t" + t.hint() + "\t" + (t.has(p) ? 1 : 0) + "\t" + (t.shown().equals(now) ? 1 : 0) + "\t" + t.group());
        return String.join("\n", rows);
    }

    static void pick(ServerPlayer p, String id) {
        if (!id.equals("none") && ALL.stream().noneMatch(t -> t.id().equals(id) && t.has(p))) return;
        ServerData.get(p.server).stats(p.getUUID()).putString("title", id);
    }
}
