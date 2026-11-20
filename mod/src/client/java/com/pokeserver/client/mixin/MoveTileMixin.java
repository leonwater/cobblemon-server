package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/** 기술 버튼: 타입 아이콘을 버튼 밖(x-9) → 왼쪽 칸 안(x+3), 기술 이름 x+17 → x+25. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.subscreen.BattleMoveSelection$MoveTile", remap = false)
abstract class MoveTileMixin {
    @ModifyConstant(method = "render", constant = @Constant(intValue = 9))
    private int pokeserver$iconX(int v) { return -3; }

    @ModifyConstant(method = "render", constant = @Constant(intValue = 17))
    private int pokeserver$nameX(int v) { return 25; }
}
