package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 배틀 화면 왼쪽 아래 행동 선택(싸운다·포켓몬·도망, 기술·교체·대상 고르기)이 HUD(하트·배고픔 줄)를 덮으면 그만큼 위로 올려 그림
 *  (BattleScale.lift, 1080p 기본 화면에선 0). 마우스 좌표도 같은 양만큼 옮겨 눌리는 자리 = 보이는 자리. */
@Mixin(AbstractWidget.class)
abstract class SelectionScaleMixin {
    @Unique private static Class<?> pokeserver$sel;

    @Unique
    private static boolean pokeserver$isSel(Object o) {
        if (pokeserver$sel == null) {
            try { pokeserver$sel = Class.forName("com.cobblemon.mod.common.client.gui.battle.subscreen.BattleActionSelection"); }
            catch (ClassNotFoundException e) { pokeserver$sel = Void.class; }
        }
        return pokeserver$sel.isInstance(o);
    }

    @ModifyVariable(method = "render", at = @At("HEAD"), argsOnly = true, ordinal = 1)
    private int pokeserver$my(int my) { return pokeserver$isSel(this) ? Math.round(my + BattleScale.lift()) : my; }

    @Inject(method = "render", at = @At("HEAD"))
    private void pokeserver$push(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        if (!pokeserver$isSel(this)) return;
        g.pose().pushPose();
        g.pose().translate(0, -BattleScale.lift(), 0);
    }

    @Inject(method = "render", at = @At("RETURN"))
    private void pokeserver$pop(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        if (pokeserver$isSel(this)) g.pose().popPose();
    }
}
