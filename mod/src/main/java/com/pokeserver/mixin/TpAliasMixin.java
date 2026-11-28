package com.pokeserver.mixin;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 일반 사용자의 "/tp 닉네임" = "/가기 닉네임" (상대 동의 후 이동). /tp는 바닐라 명령이라(OP·데이터팩이 씀) 등록하지 않고
 *  OP가 아닌 사람이 채팅으로 칠 때만 바꿔 줌. OP는 그대로 바닐라 /tp (바로 이동)이되 닉네임을 마크 아이디로 바꿔 줌. */
@Mixin(ServerGamePacketListenerImpl.class)
abstract class TpAliasMixin {
    @Shadow public ServerPlayer player;

    @ModifyVariable(method = "performUnsignedChatCommand", at = @At("HEAD"), argsOnly = true)
    private String pokeserver$tpToRequest(String command) {
        if (!player.hasPermissions(2) && command.matches("tp \\S+")) return "가기 " + command.substring(3);
        if (command.startsWith("tp ") || command.startsWith("teleport ")) return com.pokeserver.Nicknames.tpNames(player.server, command);   // OP: 닉네임도 받음
        return command;
    }
}
