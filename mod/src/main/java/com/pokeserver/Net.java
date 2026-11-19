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

    /** 서버 → 클라이언트: 상점 열기 (목록 JSON + 잔액). */
    public record ShopOpen(String json, long balance, int badges) implements CustomPacketPayload {
        public static final Type<ShopOpen> TYPE = id("shop_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, ShopOpen> CODEC = StreamCodec.composite(
                ByteBufCodecs.stringUtf8(1 << 20), ShopOpen::json, ByteBufCodecs.VAR_LONG, ShopOpen::balance,
                ByteBufCodecs.VAR_INT, ShopOpen::badges, ShopOpen::new);
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
    public record MenuOpen(long balance, String notice, boolean tutorialDone) implements CustomPacketPayload {
        public static final Type<MenuOpen> TYPE = id("menu_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, MenuOpen> CODEC = StreamCodec.composite(
                ByteBufCodecs.VAR_LONG, MenuOpen::balance, ByteBufCodecs.stringUtf8(4096), MenuOpen::notice,
                ByteBufCodecs.BOOL, MenuOpen::tutorialDone, MenuOpen::new);
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** 클라이언트 → 서버: 메인 메뉴 동작 (open, pc, trash, tutorial, tutorial_done, starter, warp:hall|street|gym|farm|wild). */
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
    public record TutorialOpen() implements CustomPacketPayload {
        public static final Type<TutorialOpen> TYPE = id("tutorial_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, TutorialOpen> CODEC = StreamCodec.unit(new TutorialOpen());
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }
}
