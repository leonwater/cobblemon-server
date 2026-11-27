package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 2. 화면 아래 HUD(핫바·체력·배고픔·경험치 바·든 물건 이름 + 레벨 숫자)를 화면 아래 가운데 기준으로 줄여 그림 (BattleScale.hudScale). */
@Mixin(Gui.class)
abstract class HudScaleMixin {
    @Inject(method = {"renderHotbarAndDecorations", "renderExperienceLevel"}, at = @At("HEAD"))
    private void pokeserver$push(GuiGraphics g, DeltaTracker dt, CallbackInfo ci) {
        float k = BattleScale.hudScale();
        g.pose().pushPose();
        g.pose().translate(g.guiWidth() / 2f, g.guiHeight(), 0);
        g.pose().scale(k, k, 1);
        g.pose().translate(-g.guiWidth() / 2f, -g.guiHeight(), 0);
    }

    @Inject(method = {"renderHotbarAndDecorations", "renderExperienceLevel"}, at = @At("RETURN"))
    private void pokeserver$pop(GuiGraphics g, DeltaTracker dt, CallbackInfo ci) { g.pose().popPose(); }
}
