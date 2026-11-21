package com.pokeserver.mixin;

import com.cobblemon.mod.common.api.moves.Moves;
import com.cobblemon.mod.common.api.moves.categories.DamageCategories;
import com.cobblemon.mod.common.battles.InBattleMove;
import com.cobblemon.mod.common.battles.pokemon.BattlePokemon;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import java.lang.reflect.Method;
import net.minecraft.core.registries.BuiltInRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** 관장·사천왕 Z기술: RCT AI는 Z 버전이 있는 기술(크리스탈과 같은 타입)이 그 턴에 가장 좋을 때만 Z를 씀 (실측 2/6).
 *  → Z를 쓸 수 있고 공격 기술이며 상대에게 1배 이상이면 그 기술 점수를 크게 올려 거의 매번 쓰게. 반감·무효면 그대로 (무지성 사용 방지).
 *  메가·다이맥스·테라는 RCT가 고른 기술에 늘 붙여서 따로 손대지 않음. */
@Pseudo
@Mixin(targets = "com.gitlab.srcmc.rctapi.api.ai.RCTBattleAI", remap = false)
abstract class TrainerZMoveMixin {
    private static final double Z_BONUS = 10.0;   // evalMove 점수(높을수록 좋음)에 더함 → 다른 후보보다 앞서게
    private static Method effectiveness;           // RCT TypeChart.getEffectiveness(타입, 상대) = 배수 (1 = 보통)

    @ModifyReturnValue(method = "evalMove", at = @At("RETURN"))
    private double pokeserver$preferZ(double score, BattlePokemon user, BattlePokemon target, InBattleMove move) {
        if (target == null || move.getGimmickMove() == null) return score;   // 이번 턴 Z(또는 맥스) 버전이 없는 기술
        var item = user.getEffectedPokemon().heldItem();
        if (!BuiltInRegistries.ITEM.getKey(item.getItem()).getPath().endsWith("ium_z")) return score;   // Z크리스탈만
        var t = Moves.getByName(move.getId());
        if (t == null || t.getDamageCategory() == DamageCategories.INSTANCE.getSTATUS()) return score;
        try {
            if (effectiveness == null) effectiveness = Class.forName("com.gitlab.srcmc.rctapi.api.ai.utils.TypeChart")
                    .getMethod("getEffectiveness", com.cobblemon.mod.common.api.types.ElementalType.class, BattlePokemon.class);
            double e = (double) effectiveness.invoke(null, t.getElementalType(), target);
            return e >= 1.0 ? score + Z_BONUS : score;
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return score;   // RCT가 바뀌어 못 찾으면 원래 판단대로
        }
    }
}
