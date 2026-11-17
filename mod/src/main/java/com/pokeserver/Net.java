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
    public record ShopOpen(String json, long balance) implements CustomPacketPayload {
        public static final Type<ShopOpen> TYPE = id("shop_open");
        public static final StreamCodec<RegistryFriendlyByteBuf, ShopOpen> CODEC = StreamCodec.composite(
                ByteBufCodecs.stringUtf8(1 << 20), ShopOpen::json, ByteBufCodecs.VAR_LONG, ShopOpen::balance, ShopOpen::new);
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
}
