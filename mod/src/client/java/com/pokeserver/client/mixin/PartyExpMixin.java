package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** 5. 이상한사탕 등을 연달아 쓸 때 파티 창 레벨업 표시: 코블몬은 앞 표시가 끝나기 전 새 경험치가 오면 처음 레벨(20)을 남기고 경험치를 더해
 *  20→21, 20→22…로 보임. 새로 온 것만 보이게 (21→22). */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.PartyOverlayDataControl", remap = false)
abstract class PartyExpMixin {
    @Redirect(method = "pokemonGainedExp", at = @At(value = "INVOKE",
            target = "Lcom/cobblemon/mod/common/client/gui/PartyOverlayDataControl$ExpGainedData;setOldLevel(Ljava/lang/Integer;)V"))
    private void pokeserver$keepNewLevel(Object data, Integer old) { }

    @Redirect(method = "pokemonGainedExp", at = @At(value = "INVOKE",
            target = "Lcom/cobblemon/mod/common/client/gui/PartyOverlayDataControl$ExpGainedData;setExpGained(I)V"))
    private void pokeserver$keepNewExp(Object data, int exp) { }
}
