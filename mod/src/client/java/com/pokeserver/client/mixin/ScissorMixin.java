package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 줄여 그리는 배틀 화면 안의 잘라 그리기(초상화 칸 등)도 같은 비율로 (1.21.1은 잘라 그리기에 크기 변환을 안 씀). */
@Mixin(GuiGraphics.class)
abstract class ScissorMixin {
    @Unique private static boolean pokeserver$inside;

    @Inject(method = "enableScissor", at = @At("HEAD"), cancellable = true)
    private void pokeserver$scale(int x1, int y1, int x2, int y2, CallbackInfo ci) {
        if (!BattleScale.on || pokeserver$inside) return;
        float f = BattleScale.f();
        if (f >= 1f) return;
        pokeserver$inside = true;
        try {
            ((GuiGraphics) (Object) this).enableScissor((int) Math.floor(x1 * f), (int) Math.floor(y1 * f), (int) Math.ceil(x2 * f), (int) Math.ceil(y2 * f));
        } finally {
            pokeserver$inside = false;
        }
        ci.cancel();
    }
}
