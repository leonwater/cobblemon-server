package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.At;
import com.pokeserver.client.BattleScale;

/** 행동 버튼(싸운다·포켓몬·포기): 왼쪽에 색 아이콘 칸이 생겨 이름을 x+6 → x+29 로. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.widgets.BattleOptionTile", remap = false)
abstract class OptionTileMixin {
    @ModifyConstant(method = "method_25394", constant = @Constant(intValue = 6))
    private int pokeserver$textX(int v) { return 29; }

    /** 2. 타일 이름 글자 배율 1.0 → 한 점이 정수 픽셀인 가장 가까운 큰 값 (1080p면 1.2 = 3픽셀). 타일 크기는 그대로. */
    @ModifyArg(method = "method_25394", at = @At(value = "INVOKE", target = "Lcom/cobblemon/mod/common/client/render/RenderHelperKt;drawScaledText$default(Lnet/minecraft/class_332;Lnet/minecraft/class_2960;Lnet/minecraft/class_5250;Ljava/lang/Number;Ljava/lang/Number;FLjava/lang/Number;IIZZLjava/lang/Integer;Ljava/lang/Integer;ILjava/lang/Object;)V"), index = 5)
    private float pokeserver$crispText(float k) { return BattleScale.crisp(k * BattleScale.selScale() - 1e-3f) / BattleScale.selScale(); }
}
