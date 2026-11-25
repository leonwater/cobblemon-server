package com.pokeserver.mixin;

import com.pokeserver.Farms;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.piston.PistonStructureResolver;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 농장: 피스톤(끈끈이·슬라임 장치 포함)은 자기 땅 안의 블록만 밀고 당김. 하나라도 땅 밖을 건드리면 아예 안 움직임. */
@Mixin(PistonStructureResolver.class)
public class PistonMixin {
    @Shadow @Final private Level level;
    @Shadow @Final private BlockPos pistonPos;
    @Shadow @Final private Direction pushDirection;
    @Shadow @Final private List<BlockPos> toPush;
    @Shadow @Final private List<BlockPos> toDestroy;

    @Inject(method = "resolve", at = @At("RETURN"), cancellable = true)
    private void pokeserver$stayInPlot(CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValueZ() || !Farms.isFarm(level)) return;
        for (BlockPos p : toPush)
            if (!Farms.samePlot(pistonPos, p) || !Farms.samePlot(pistonPos, p.relative(pushDirection))) { cir.setReturnValue(false); return; }
        for (BlockPos p : toDestroy)
            if (!Farms.samePlot(pistonPos, p)) { cir.setReturnValue(false); return; }
    }
}
