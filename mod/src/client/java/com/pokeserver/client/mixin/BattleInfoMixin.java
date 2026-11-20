package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Extended Battle UI의 BATTLE INFO 판·배틀 기록(화면 위 HUD)도 배틀 화면과 같은 크기(GUI 2.5배)로 줄여 그림.
 *  안 줄이면 전체 화면(GUI 4배)에서 두 판이 커져 서로 겹침. */
@Pseudo
@Mixin(targets = "com.cobblemonextendedbattleui.BattleInfoRenderer", remap = false)
abstract class BattleInfoMixin {
    @Unique private static boolean pokeserver$scaled, pokeserver$prev;

    @Inject(method = "render(Lnet/minecraft/class_332;)V", at = @At("HEAD"))
    private void pokeserver$head(GuiGraphics g, CallbackInfo ci) {
        float f = BattleScale.f();
        pokeserver$scaled = f < 1f;
        if (!pokeserver$scaled) return;
        pokeserver$prev = BattleScale.on;
        BattleScale.on = true;
        g.pose().pushPose();
        g.pose().scale(f, f, 1);
    }

    @Inject(method = "render(Lnet/minecraft/class_332;)V", at = @At("RETURN"))
    private void pokeserver$end(GuiGraphics g, CallbackInfo ci) {
        if (!pokeserver$scaled) return;
        g.pose().popPose();
        BattleScale.on = pokeserver$prev;
        pokeserver$scaled = false;
    }
}
