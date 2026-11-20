package com.pokeserver.client.mixin;

import com.mojang.blaze3d.platform.Window;
import com.pokeserver.client.BattleScale;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 배틀 화면 코드 안에서만 창 크기를 1/f 배로 (BattleScale). */
@Mixin(Window.class)
abstract class WindowMixin {
    @Inject(method = {"getGuiScaledWidth", "getGuiScaledHeight"}, at = @At("RETURN"), cancellable = true)
    private void pokeserver$battleSize(CallbackInfoReturnable<Integer> cir) {
        if (BattleScale.on) cir.setReturnValue(Math.round(cir.getReturnValueI() / BattleScale.f()));
    }
}
