package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 3. 키워 그린 행동 선택의 클릭 좌표를 원래 크기 기준으로 (SelectionScaleMixin과 같은 변환). */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.subscreen.BattleActionSelection", remap = false)
abstract class SelectionClickMixin {
    @ModifyVariable(method = "method_25402", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private double pokeserver$mx(double mx) { return mx / BattleScale.selScale(); }

    @ModifyVariable(method = "method_25402", at = @At("HEAD"), argsOnly = true, ordinal = 1)
    private double pokeserver$my(double my) {
        double h = Minecraft.getInstance().getWindow().getGuiScaledHeight();
        return h - (h - my) / BattleScale.selScale();
    }
}
