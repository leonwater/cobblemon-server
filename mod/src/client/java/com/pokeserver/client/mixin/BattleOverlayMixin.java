package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 배틀 체력 판·기록(화면 위에 늘 보이는 부분)도 같은 크기로 줄여 그림. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.BattleOverlay", remap = false)
abstract class BattleOverlayMixin {
    @Inject(method = "method_1753", at = @At("HEAD"), cancellable = true)
    private void pokeserver$render(GuiGraphics g, DeltaTracker dt, CallbackInfo ci) {
        float f = BattleScale.f();
        if (BattleScale.inside || f >= 1f) return;
        boolean prev = BattleScale.on;
        BattleScale.inside = BattleScale.on = true;
        g.pose().pushPose();
        g.pose().scale(f, f, 1);
        try {
            ((Gui) (Object) this).render(g, dt);
        } finally {
            g.pose().popPose();
            BattleScale.inside = false;
            BattleScale.on = prev;
        }
        ci.cancel();
    }
}
