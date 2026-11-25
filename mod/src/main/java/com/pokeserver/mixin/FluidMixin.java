package com.pokeserver.mixin;

import com.pokeserver.Farms;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.FluidState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 농장: 물·용암은 같은 땅 안에서만 흐름 (내 땅 끝에 부은 물이 길·이웃 땅으로 넘쳐 밭을 쓸지 못하게). */
@Mixin(FlowingFluid.class)
public class FluidMixin {
    @Inject(method = "canSpreadTo", at = @At("HEAD"), cancellable = true)
    private void pokeserver$stayInPlot(BlockGetter getter, BlockPos from, BlockState fromState, Direction dir, BlockPos to, BlockState toState,
                                       FluidState toFluid, Fluid fluid, CallbackInfoReturnable<Boolean> cir) {
        if (getter instanceof Level level && Farms.isFarm(level) && !Farms.samePlot(from, to)) cir.setReturnValue(false);
    }
}
