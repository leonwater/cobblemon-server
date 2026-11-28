package com.pokeserver;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** 서버↔클라이언트 패킷. */
public final class Net {
    private Net() {}

    static <T extends CustomPacketPayload> CustomPacketPayload.Type<T> id(String name) {
        return new CustomPacketPayload.Type<>(ResourceLocation.fromNamespaceAndPath(PokeServer.ID, name));
    }

    /** 서버 → 클라이언트: 땅 등록 확인 팝업 띄우기. */
    public record ClaimPopup(int plot) implements CustomPacketPayload {
        public static final Type<ClaimPopup> TYPE = id("claim_popup");
        public static final StreamCodec<RegistryFriendlyByteBuf, ClaimPopup> CODEC =
                StreamCodec.composite(ByteBufCodecs.VAR_INT, ClaimPopup::plot, ClaimPopup::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 클라이언트 → 서버: 팝업에서 확인을 누름. */
    public record ClaimConfirm(int plot) implements CustomPacketPayload {
        public static final Type<ClaimConfirm> TYPE = id("claim_confirm");
        public static final StreamCodec<RegistryFriendlyByteBuf, ClaimConfirm> CODEC =
                StreamCodec.composite(ByteBufCodecs.VAR_INT, ClaimConfirm::plot, ClaimConfirm::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 클라이언트 → 서버: 5. 배틀 배속 (1·2·4). 서버가 값 검사. */
    /** 11. 클라이언트 → 서버: 배틀의 "도망·포기" 버튼 = 배틀 바로 끝내기 (값은 안 씀). */
    public record BattleQuit(int unused) implements CustomPacketPayload {
        public static final Type<BattleQuit> TYPE = id("battle_quit");
        public static final StreamCodec<RegistryFriendlyByteBuf, BattleQuit> CODEC =
                StreamCodec.composite(ByteBufCodecs.VAR_INT, BattleQuit::unused, BattleQuit::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    public record BattleSpeed(int speed) implements CustomPacketPayload {
        public static final Type<BattleSpeed> TYPE = id("battle_speed");
        public static final StreamCodec<RegistryFriendlyByteBuf, BattleSpeed> CODEC =
                StreamCodec.composite(ByteBufCodecs.VAR_INT, BattleSpeed::speed, BattleSpeed::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 상점 열기 (목록 JSON + 잔액). */
    public record ShopOpen(String json, long balance, int badges) implements CustomPacketPayload {
        public static final Type<ShopOpen> TYPE = id("shop_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, ShopOpen> CODEC = StreamCodec.composite(
                ByteBufCodecs.stringUtf8(1 << 20), ShopOpen::json, ByteBufCodecs.VAR_LONG, ShopOpen::balance,
                ByteBufCodecs.VAR_INT, ShopOpen::badges, ShopOpen::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 보이는 이름 목록 ("uuid\t[칭호] 닉네임" 줄들). */
    /** 서버 → 클라이언트: 칭호 고르기 창 (Titles.list 형식). */
    public record TitlesOpen(String data) implements CustomPacketPayload {
        public static final Type<TitlesOpen> TYPE = id("titles_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, TitlesOpen> CODEC =
                StreamCodec.composite(ByteBufCodecs.stringUtf8(1 << 14), TitlesOpen::data, TitlesOpen::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    public record Names(String data) implements CustomPacketPayload {
        public static final Type<Names> TYPE = id("names");
        public static final StreamCodec<RegistryFriendlyByteBuf, Names> CODEC =
                StreamCodec.composite(ByteBufCodecs.stringUtf8(1 << 16), Names::data, Names::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 오른쪽 정보창 (잔액, 배지 수, 지금 있는 곳 이름). 1초마다. */
    public record Hud(long balance, int badges, String place) implements CustomPacketPayload {
        public static final Type<Hud> TYPE = id("hud");
        public static final StreamCodec<RegistryFriendlyByteBuf, Hud> CODEC = StreamCodec.composite(
                ByteBufCodecs.VAR_LONG, Hud::balance, ByteBufCodecs.VAR_INT, Hud::badges, ByteBufCodecs.stringUtf8(64), Hud::place, Hud::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 잔액 갱신. */
    public record Balance(long balance) implements CustomPacketPayload {
        public static final Type<Balance> TYPE = id("balance");
        public static final StreamCodec<RegistryFriendlyByteBuf, Balance> CODEC =
                StreamCodec.composite(ByteBufCodecs.VAR_LONG, Balance::balance, Balance::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 클라이언트 → 서버: 구매/판매 요청 (서버가 목록·잔액·인벤토리로 다시 검증). */
    public record ShopTrade(boolean sell, int category, int item, int qty) implements CustomPacketPayload {
        public static final Type<ShopTrade> TYPE = id("shop_trade");
        public static final StreamCodec<RegistryFriendlyByteBuf, ShopTrade> CODEC = StreamCodec.composite(
                ByteBufCodecs.BOOL, ShopTrade::sell, ByteBufCodecs.VAR_INT, ShopTrade::category,
                ByteBufCodecs.VAR_INT, ShopTrade::item, ByteBufCodecs.VAR_INT, ShopTrade::qty, ShopTrade::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 메인 메뉴 열기 (잔액, 공지, 튜토리얼을 끝냈는지 — 끝내기 전엔 워프 잠금). */
    /** stats: 잡은 종, 마주친 종, 전체 종, 배지 (composite 칸 수 제한이라 목록으로). */
    public record MenuOpen(long balance, String notice, boolean tutorialDone, java.util.List<Integer> stats) implements CustomPacketPayload {
        public static final Type<MenuOpen> TYPE = id("menu_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, MenuOpen> CODEC = StreamCodec.composite(
                ByteBufCodecs.VAR_LONG, MenuOpen::balance, ByteBufCodecs.stringUtf8(4096), MenuOpen::notice,
                ByteBufCodecs.BOOL, MenuOpen::tutorialDone, ByteBufCodecs.VAR_INT.apply(ByteBufCodecs.list(4)), MenuOpen::stats, MenuOpen::new);
        public int caught() { return stats.get(0); }
        public int seen() { return stats.get(1); }
        public int total() { return stats.get(2); }
        public int badges() { return stats.get(3); }
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 클라이언트 → 서버: 메인 메뉴 동작 (open, pc, trash, tutorial, tutorial_done, starter, warp:hall|gym|farm). */
    public record MenuAction(String action) implements CustomPacketPayload {
        public static final Type<MenuAction> TYPE = id("menu_action");
        public static final StreamCodec<RegistryFriendlyByteBuf, MenuAction> CODEC =
                StreamCodec.composite(ByteBufCodecs.stringUtf8(64), MenuAction::action, MenuAction::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 체육관 도전 목록 (클리어·도전 가능한 것만). */
    public record GymOpen(String json) implements CustomPacketPayload {
        public static final Type<GymOpen> TYPE = id("gym_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, GymOpen> CODEC =
                StreamCodec.composite(ByteBufCodecs.stringUtf8(1 << 16), GymOpen::json, GymOpen::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 클라이언트 → 서버: 도전할 체육관 (1~8, 사천왕 9). */
    public record GymPick(int n) implements CustomPacketPayload {
        public static final Type<GymPick> TYPE = id("gym_pick");
        public static final StreamCodec<RegistryFriendlyByteBuf, GymPick> CODEC =
                StreamCodec.composite(ByteBufCodecs.VAR_INT, GymPick::n, GymPick::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 서버 → 클라이언트: 튜토리얼 설명 창 열기 (오박사 우클릭). */
    /** nick: 이미 정한 닉네임 (없으면 ""). 있으면 튜토리얼 마지막 쪽에서 바꿀 수 없음. */
    /** error: 닉네임을 못 쓰는 이유 (겹침 등). 있으면 닉네임 쪽을 바로 열고 빨간 글씨로 보여 줌. */
    public record TutorialOpen(String nick, String error) implements CustomPacketPayload {
        public static final Type<TutorialOpen> TYPE = id("tutorial_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, TutorialOpen> CODEC =
                StreamCodec.composite(ByteBufCodecs.stringUtf8(64), TutorialOpen::nick, ByteBufCodecs.stringUtf8(256), TutorialOpen::error, TutorialOpen::new);
        public static TutorialOpen of(net.minecraft.server.level.ServerPlayer p) { return of(p, ""); }
        public static TutorialOpen of(net.minecraft.server.level.ServerPlayer p, String error) {
            return new TutorialOpen(ServerData.get(p.server).nicks.getOrDefault(p.getUUID(), ""), error);
        }
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }
}
