package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 배틀 중엔 Xaero 미니맵을 그리지 않음: 왼쪽 위 내 포켓몬 체력 판과 겹침 (배틀이 끝나면 다시 보임). */
@Pseudo
@Mixin(targets = "xaero.hud.minimap.module.MinimapRenderer", remap = false)
abstract class MinimapMixin {
    @Inject(method = "render(Lxaero/hud/minimap/module/MinimapSession;Lxaero/hud/render/module/ModuleRenderContext;Lnet/minecraft/class_332;F)V",
            at = @At("HEAD"), cancellable = true)
    private void pokeserver$hideInBattle(CallbackInfo ci) {
        if (BattleScale.inBattle()) ci.cancel();
    }
}
