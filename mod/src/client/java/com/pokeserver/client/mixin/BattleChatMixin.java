package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 4. 배틀 화면이 열려 있으면 채팅(관장 대사·도구 사용 안내)을 커진 행동 선택 위로 올려 그림. 채팅 입력창(T)을 열면 원래 자리. */
@Mixin(Gui.class)
abstract class BattleChatMixin {
    @Unique private boolean pokeserver$lifted;

    @Inject(method = "renderChat", at = @At("HEAD"))
    private void pokeserver$up(GuiGraphics g, DeltaTracker dt, CallbackInfo ci) {
        var mc = Minecraft.getInstance();
        pokeserver$lifted = mc.screen instanceof com.cobblemon.mod.common.client.gui.battle.BattleGUI;
        if (!pokeserver$lifted) return;
        // 행동 선택 윗변(배틀 좌표로 아래에서 85×배율 + lift) → GUI px, 채팅 아랫변(아래에서 40) 위로 4px 여유
        float up = (85 + 15 + BattleScale.lift()) * BattleScale.f() - 40 + 4;   // +15: 전투 속도 버튼
        g.pose().pushPose();
        g.pose().translate(0, -Math.max(0, up), 0);
    }

    @Inject(method = "renderChat", at = @At("RETURN"))
    private void pokeserver$down(GuiGraphics g, DeltaTracker dt, CallbackInfo ci) {
        if (pokeserver$lifted) g.pose().popPose();
    }
}
