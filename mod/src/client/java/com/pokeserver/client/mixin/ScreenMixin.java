package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 배틀 화면(BattleGUI): 줄여서 그림 (말풍선 도움말까지 같은 크기로). */
@Mixin(Screen.class)
abstract class ScreenMixin {
    @Inject(method = "renderWithTooltip", at = @At("HEAD"), cancellable = true)
    private void pokeserver$battleRender(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        if (BattleScale.inside || !BattleScale.isBattle(this)) return;
        float f = BattleScale.f();
        if (f >= 1f) return;
        boolean prev = BattleScale.on;
        BattleScale.inside = true;
        BattleScale.on = true;
        g.pose().pushPose();
        g.pose().scale(f, f, 1);
        try {
            ((Screen) (Object) this).renderWithTooltip(g, Math.round(mx / f), Math.round(my / f), pt);
        } finally {
            g.pose().popPose();
            BattleScale.inside = false;
            BattleScale.on = prev;
        }
        ci.cancel();
    }
}
