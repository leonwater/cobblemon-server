package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import com.pokeserver.client.BattleScale;
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

    /** 기술 이름 글자 (PP 숫자는 커지면 아이콘·버튼 끝에 붙어서 그대로): 코블몬은 배율을 기본값(1.0, 2.5픽셀)으로 넘겨 획이 들쭉날쭉 → "기본값 쓰기" 표시(32)를 끄고 정수 픽셀 배율(1080p면 1.2 = 3픽셀)을 넘김. */
    @ModifyArg(method = "render", at = @At(value = "INVOKE", target = "Lcom/cobblemon/mod/common/client/render/RenderHelperKt;drawScaledText$default(Lnet/minecraft/class_332;Lnet/minecraft/class_2960;Lnet/minecraft/class_5250;Ljava/lang/Number;Ljava/lang/Number;FLjava/lang/Number;IIZZLjava/lang/Integer;Ljava/lang/Integer;ILjava/lang/Object;)V", ordinal = 0), index = 5)
    private float pokeserver$crisp(float k) { return BattleScale.crisp(1 - 1e-3f); }

    @ModifyArg(method = "render", at = @At(value = "INVOKE", target = "Lcom/cobblemon/mod/common/client/render/RenderHelperKt;drawScaledText$default(Lnet/minecraft/class_332;Lnet/minecraft/class_2960;Lnet/minecraft/class_5250;Ljava/lang/Number;Ljava/lang/Number;FLjava/lang/Number;IIZZLjava/lang/Integer;Ljava/lang/Integer;ILjava/lang/Object;)V", ordinal = 0), index = 13)
    private int pokeserver$useScale(int mask) { return mask & ~32; }
}
