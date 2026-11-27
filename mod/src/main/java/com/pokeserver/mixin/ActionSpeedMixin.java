package com.pokeserver.mixin;

import com.cobblemon.mod.common.api.moves.animations.ActionEffectContext;
import com.cobblemon.mod.common.api.moves.animations.UsersProvider;
import com.cobblemon.mod.common.battles.BattleRegistry;
import com.cobblemon.mod.common.entity.pokemon.PokemonEntity;
import com.pokeserver.CobblemonHooks;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 5. 배틀 배속: 기술 연출(액션 이펙트) 키프레임이 도는 동안 그 배틀의 배속을 기억 → DelayMixin이 기다림(delayedFuture)을 그만큼 줄임.
 *  키프레임 play 안에서 delayedFuture를 바로 부르므로, play 앞뒤로만 값이 있으면 됨 (중첩 키프레임은 이전 값으로 되돌림). */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.api.moves.animations.keyframes.ConditionalActionEffectKeyframe", remap = false)
abstract class ActionSpeedMixin {
    /** 부모 키프레임(순서·동시)이 자식 play를 안에서 부르므로 겹침 → 이전 값을 쌓아 두고 RETURN에서 하나씩 되돌림. */
    @Unique private static final ThreadLocal<java.util.ArrayDeque<Integer>> PREV = ThreadLocal.withInitial(java.util.ArrayDeque::new);

    @Inject(method = "play", at = @At("HEAD"))
    private void pokeserver$enter(ActionEffectContext ctx, CallbackInfoReturnable<?> cir) {
        PREV.get().push(CobblemonHooks.ACTION_SPEED.get());
        int s = 1;
        for (Object p : ctx.getProviders())
            if (p instanceof UsersProvider u)
                for (var e : u.getEntities())
                    if (e instanceof PokemonEntity pe && pe.getBattleId() != null) {
                        var b = BattleRegistry.INSTANCE.getBattle(pe.getBattleId());
                        if (b != null) s = CobblemonHooks.battleSpeed(b);
                    }
        CobblemonHooks.ACTION_SPEED.set(s);
    }

    @Inject(method = "play", at = @At("RETURN"))
    private void pokeserver$exit(ActionEffectContext ctx, CallbackInfoReturnable<?> cir) {
        Integer p = PREV.get().poll();
        CobblemonHooks.ACTION_SPEED.set(p == null ? 1 : p);
    }
}
