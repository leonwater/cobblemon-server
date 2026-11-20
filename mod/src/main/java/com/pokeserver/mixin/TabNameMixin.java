package com.pokeserver.mixin;

import com.pokeserver.Nicknames;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 탭 목록(Tab 키)에도 "[칭호] 닉네임". */
@Mixin(ServerPlayer.class)
abstract class TabNameMixin {
    @Inject(method = "getTabListDisplayName", at = @At("HEAD"), cancellable = true)
    private void pokeserver$tabName(CallbackInfoReturnable<Component> cir) {
        Component n = Nicknames.SHOWN.get(((ServerPlayer) (Object) this).getUUID());
        if (n != null) cir.setReturnValue(n);
    }
}
