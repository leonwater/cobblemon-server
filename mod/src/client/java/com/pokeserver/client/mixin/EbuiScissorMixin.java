package com.pokeserver.client.mixin;

import com.mojang.blaze3d.systems.RenderSystem;
import com.pokeserver.client.BattleScale;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Extended Battle UI는 배틀 기록 칸을 RenderSystem.enableScissor로 직접 잘라 그림:
 *  (x·배율, (창높이 - y - h)·배율, w·배율, h·배율). 창높이는 배틀 중 WindowMixin이 1/f배로 늘려 보여 줌.
 *  BattleInfoMixin이 판을 f배로 줄여 그리므로 네 값 모두 f배 하면 실제 그려진 칸과 맞음
 *  (안 하면 "○○의 나이트헤드" 앞부분처럼 글자가 잘리거나 아예 안 보임). */
@Pseudo
@Mixin(targets = "com.cobblemonextendedbattleui.UIUtils", remap = false)
abstract class EbuiScissorMixin {
    @Redirect(method = "enableScissor", at = @At(value = "INVOKE", target = "Lcom/mojang/blaze3d/systems/RenderSystem;enableScissor(IIII)V"))
    private void pokeserver$scaled(int x, int y, int w, int h) {
        float f = BattleScale.f();
        if (!BattleScale.on || f >= 1f) { RenderSystem.enableScissor(x, y, w, h); return; }
        RenderSystem.enableScissor((int) Math.floor(x * f), (int) Math.floor(y * f), (int) Math.ceil(w * f), (int) Math.ceil(h * f));
    }
}
