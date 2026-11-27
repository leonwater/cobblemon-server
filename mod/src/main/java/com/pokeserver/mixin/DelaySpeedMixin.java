package com.pokeserver.mixin;

import com.pokeserver.CobblemonHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 5. 배틀 배속: 기술 연출 키프레임 안에서 부른 기다림만 배속만큼 짧게 (ActionSpeedMixin이 값을 정함, 그 밖에선 1). */
@Mixin(targets = "com.cobblemon.mod.common.api.scheduling.SchedulingFunctionsKt", remap = false)
abstract class DelaySpeedMixin {
    @ModifyVariable(method = "delayedFuture(F)Ljava/util/concurrent/CompletableFuture;", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private static float pokeserver$fast1(float s) { return s / CobblemonHooks.ACTION_SPEED.get(); }

    @ModifyVariable(method = "delayedFuture(IFZ)Ljava/util/concurrent/CompletableFuture;", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private static float pokeserver$fast3(float s) { return s / CobblemonHooks.ACTION_SPEED.get(); }
}
