package com.pokeserver.mixin;

import com.pokeserver.Nicknames;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 8·9. "[별명] 닉네임": 서버에선 채팅·안내 문구, 클라이언트에선 머리 위 이름표에 쓰임. */
@Mixin(Player.class)
abstract class PlayerNameMixin {
    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void pokeserver$shownName(CallbackInfoReturnable<Component> cir) {
        Component n = Nicknames.SHOWN.get(((Player) (Object) this).getUUID());
        if (n != null) cir.setReturnValue(n);
    }
}
