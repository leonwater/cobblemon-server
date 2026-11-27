package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import com.cobblemon.mod.common.client.gui.battle.widgets.BattleOptionTile;
import net.minecraft.client.gui.GuiGraphics;
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

    /** 5. 참고 사진처럼 타일 오른쪽 끝에 얇은 색 띠 (싸운다 빨강, 포켓몬 초록, 포기·도망 회색, 잡기 노랑). */
    @Inject(method = "method_25394", at = @At("TAIL"))
    private void pokeserver$strip(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        var t = (BattleOptionTile) (Object) this;
        String p = t.getResource().getPath();
        int c = p.contains("fight") ? 0xFFC8504C : p.contains("switch") ? 0xFF4FAE5A : p.contains("bag") ? 0xFFE0A63A : 0xFF9AA0A8;
        g.fill(t.getX() + 87, t.getY() + 5, t.getX() + 88, t.getY() + 21, c);
    }
}
