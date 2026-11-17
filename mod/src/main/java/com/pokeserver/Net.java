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
}
