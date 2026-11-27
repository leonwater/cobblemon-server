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

    /** 4. 배틀 정보 판 오른쪽 끝을 SHRINK만큼 왼쪽으로 (오른쪽 상대 파티 볼 줄을 안 가리게). 펼침·접힘 모두. 왼쪽 끝은 그대로 (기본 자리 = 화면 폭 - 200 - 10). 직접 옮긴 값이 있으면 그대로. */
    @Inject(method = {"getPanelWidth", "getCollapsedWidth"}, at = @At("RETURN"), cancellable = true)
    private void pokeserver$width(CallbackInfoReturnable<Integer> cir) { if (cir.getReturnValue() == null) cir.setReturnValue(200 - pokeserver$SHRINK); }

    @Inject(method = "getPanelX", at = @At("RETURN"), cancellable = true)
    private void pokeserver$x(CallbackInfoReturnable<Integer> cir) {
        if (cir.getReturnValue() == null) cir.setReturnValue(net.minecraft.client.Minecraft.getInstance().getWindow().getGuiScaledWidth() - 200 - 10);
    }

    @org.spongepowered.asm.mixin.Unique private static final int pokeserver$SHRINK = 24;
}
