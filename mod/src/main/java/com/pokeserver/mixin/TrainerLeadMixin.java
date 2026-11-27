package com.pokeserver.mixin;

import com.cobblemon.mod.common.battles.pokemon.BattlePokemon;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** 관장·사천왕 선봉: RCT는 팀 첫 포켓몬을 먼저 냄 → 스텔스록을 가진 포켓몬(에이스 제외)이 있으면 그중 하나, 없으면 에이스(팀 마지막)를 뺀 나머지 중 무작위 한 마리를 맨 앞으로.
 *  NPC 쪽(toBattleActor(TrainerNPC))만 바꿈. 기믹 지정은 포켓몬 UUID 기준이라 순서를 바꿔도 그대로. */
@Pseudo
@Mixin(targets = "com.gitlab.srcmc.rctapi.api.battle.BattleManager", remap = false)
abstract class TrainerLeadMixin {
    @ModifyExpressionValue(method = "toBattleActor(Lcom/gitlab/srcmc/rctapi/api/trainer/TrainerNPC;)Lcom/cobblemon/mod/common/api/battles/model/actor/BattleActor;",
            at = @At(value = "INVOKE", target = "Lcom/gitlab/srcmc/rctapi/api/battle/BattleManager;toBattlePokemons(Lcom/gitlab/srcmc/rctapi/api/trainer/Trainer;Z)Ljava/util/List;"))
    private static List<BattlePokemon> pokeserver$randomLead(List<BattlePokemon> team) {
        if (team.size() < 2) return team;
        // 스텔스록을 가진 포켓몬이 있으면 그중 하나가 선봉 (에이스 제외), 없으면 에이스 뺀 나머지 중 무작위
        var rock = new java.util.ArrayList<Integer>();
        for (int i = 0; i < team.size() - 1; i++)
            if (team.get(i).getMoveSet().getMoves().stream().anyMatch(m -> m.getName().equals("stealthrock"))) rock.add(i);
        var rnd = ThreadLocalRandom.current();
        int lead = !rock.isEmpty() ? rock.get(rnd.nextInt(rock.size())) : team.size() > 2 ? rnd.nextInt(team.size() - 1) : 0;
        java.util.Collections.swap(team, 0, lead);
        return team;
    }
}
