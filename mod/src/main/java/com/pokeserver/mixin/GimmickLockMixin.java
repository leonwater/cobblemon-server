package com.pokeserver.mixin;

import com.cobblemon.mod.common.battles.ShowdownMoveset;
import com.pokeserver.CobblemonHooks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Mega Showdown이 배틀 턴마다 기믹 가능 여부(팔찌·Z링·밴드·오브)를 보는 곳: 진행도가 모자라면 없는 것으로 (플레이어만, 배틀 중만). */
@Pseudo
@Mixin(targets = "com.github.yajatkaul.mega_showdown.gimmick.GimmickTurnCheck", remap = false)
abstract class GimmickLockMixin {
    @Inject(method = "hasGimmick", at = @At("HEAD"), cancellable = true)
    private static void pokeserver$lock(ShowdownMoveset.Gimmick gimmick, LivingEntity e, CallbackInfoReturnable<Boolean> cir) {
        if (e instanceof ServerPlayer p && CobblemonHooks.gimmickLocked(p, gimmick.name())) cir.setReturnValue(false);
    }
}
