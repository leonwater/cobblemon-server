package com.pokeserver.mixin;

import com.pokeserver.Protection;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.FireBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 광장·마을·튜토리얼 방(고정 구역)과 농장의 불은 붙고 1~2초 뒤 저절로 꺼짐 (불은 놓일 때 틱이 예약됨 → 번지거나 태우기 전에 꺼짐). 야생은 그대로. */
@Mixin(FireBlock.class)
public class FireMixin {
    @Inject(method = "tick", at = @At("HEAD"), cancellable = true)
    private void pokeserver$out(BlockState state, ServerLevel level, BlockPos pos, RandomSource random, CallbackInfo ci) {
        if (!Protection.frozen(level, pos) && !com.pokeserver.Farms.isFarm(level)) return;
        level.removeBlock(pos, false);
        ci.cancel();
    }
}
