package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Extended Battle UI 설정: 7. 배틀 기록 글자는 한 단계 크고 정수 픽셀로 (깨짐 방지), 11. 기록 판 왼쪽 끝 = BATTLE INFO 판 왼쪽 끝. */
@Pseudo
@Mixin(targets = "com.cobblemonextendedbattleui.PanelConfig", remap = false)
abstract class EbuiConfigMixin {
    @Shadow public abstract Integer getPanelX();

    @Inject(method = "getLogFontScale", at = @At("RETURN"), cancellable = true)
    private void pokeserver$crisp(CallbackInfoReturnable<Float> cir) { cir.setReturnValue(BattleScale.crisp(cir.getReturnValueF())); }

    @Inject(method = "getLogX", at = @At("RETURN"), cancellable = true)
    private void pokeserver$alignX(CallbackInfoReturnable<Integer> cir) {
        Integer px = getPanelX();
        if (px != null) cir.setReturnValue(px);
    }
}
