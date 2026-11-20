package com.pokeserver.mixin;

import com.pokeserver.CobblemonHooks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 2. 다이맥스는 원래 파워 스팟 근처에서만 됨(Mega Showdown). 체육관·사천왕 배틀과 플레이어 배틀 중엔 어디서나 되게. */
@Pseudo
@Mixin(targets = "com.github.yajatkaul.mega_showdown.utils.PlayerUtils", remap = false)
abstract class DynamaxSpotMixin {
    @Inject(method = "isBlockNearby", at = @At("HEAD"), cancellable = true)
    private static void pokeserver$anywhere(ServerPlayer p, TagKey<Block> tag, int range, CallbackInfoReturnable<Boolean> cir) {
        if (CobblemonHooks.dynamaxAnywhere(p)) cir.setReturnValue(true);
    }
}
