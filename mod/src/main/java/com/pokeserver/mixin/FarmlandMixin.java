package com.pokeserver.mixin;

import com.pokeserver.Farms;
import com.pokeserver.Protection;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 밭이 흙으로 바뀌는 것(밟기·마름)을 막음: 광장 등 고정 구역은 항상, 농장은 땅 주인이 밟을 때만 허용. */
@Mixin(FarmBlock.class)
public class FarmlandMixin {
    @Inject(method = "turnToDirt", at = @At("HEAD"), cancellable = true)
    private static void pokeserver$keep(Entity entity, BlockState state, Level level, BlockPos pos, CallbackInfo ci) {
        if (level.isClientSide()) return;
        if (Protection.frozen(level, pos)) { ci.cancel(); return; }
        if (Farms.isFarm(level) && entity != null && !(entity instanceof Player p && Farms.canEdit(p, level, pos))) ci.cancel();
    }
}
