package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 3. 배틀 화면 왼쪽 아래 행동 선택(싸운다·포켓몬·도망, 기술·교체·대상 고르기)을 왼쪽 아래 모서리 기준으로 키워 그림.
 *  마우스 좌표도 같은 비율로 되돌려 넘겨서 눌리는 자리 = 보이는 자리. */
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

    @Unique
    private static float pokeserver$h() { return Minecraft.getInstance().getWindow().getGuiScaledHeight(); }

    @ModifyVariable(method = "render", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private int pokeserver$mx(int mx) { return pokeserver$isSel(this) ? Math.round(mx / BattleScale.selScale()) : mx; }

    @ModifyVariable(method = "render", at = @At("HEAD"), argsOnly = true, ordinal = 1)
    private int pokeserver$my(int my) {
        if (!pokeserver$isSel(this)) return my;
        float h = pokeserver$h();
        return Math.round(h - (h - BattleScale.lift() - my) / BattleScale.selScale());
    }

    @Inject(method = "render", at = @At("HEAD"))
    private void pokeserver$push(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        if (!pokeserver$isSel(this)) return;
        float s = BattleScale.selScale(), h = pokeserver$h();
        g.pose().pushPose();
        g.pose().translate(0, h - BattleScale.lift(), 0);
        g.pose().scale(s, s, 1);
        g.pose().translate(0, -h, 0);
    }

    @Inject(method = "render", at = @At("RETURN"))
    private void pokeserver$pop(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        if (pokeserver$isSel(this)) g.pose().popPose();
    }
}
