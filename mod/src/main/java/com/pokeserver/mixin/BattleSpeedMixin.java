package com.pokeserver.mixin;

import com.cobblemon.mod.common.api.battles.model.PokemonBattle;
import com.pokeserver.CobblemonHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 5. 배틀 배속: 코블몬이 배틀 메시지 사이에 두는 기다림(dispatchWaiting 초)을 배속만큼 줄임.
 *  shortcut: 기술 연출(액션 이펙트)·교체·특성 알림처럼 따로 기다리는 몇 곳은 그대로, 더 빨라야 하면 WaitDispatch 생성자도 줄이기. */
@Mixin(value = PokemonBattle.class, remap = false)
abstract class BattleSpeedMixin {
    @ModifyVariable(method = {"dispatchWaiting", "dispatchWaitingToFront"}, at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private float pokeserver$fast(float seconds) {
        return seconds / CobblemonHooks.battleSpeed((PokemonBattle) (Object) this);
    }
}
