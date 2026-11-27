package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 위로 올려 그린 행동 선택(SelectionScaleMixin)의 클릭 좌표도 같은 양만큼. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.subscreen.BattleActionSelection", remap = false)
abstract class SelectionClickMixin {
    @ModifyVariable(method = "method_25402", at = @At("HEAD"), argsOnly = true, ordinal = 1)
    private double pokeserver$my(double my) { return my + BattleScale.lift(); }
}
