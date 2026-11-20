package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/** 행동 버튼(싸운다·포켓몬·포기): 왼쪽에 색 아이콘 칸이 생겨 이름을 x+6 → x+29 로. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.widgets.BattleOptionTile", remap = false)
abstract class OptionTileMixin {
    @ModifyConstant(method = "method_25394", constant = @Constant(intValue = 6))
    private int pokeserver$textX(int v) { return 29; }
}
