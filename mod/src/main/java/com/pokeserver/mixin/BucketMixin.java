package com.pokeserver.mixin;

import com.pokeserver.Farms;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 농장: 땅 밖(길)에는 물·용암을 못 부음. 사람 손은 Protection에서 막고, 여기선 발사기처럼 사람 없이 붓는 경우까지. */
@Mixin(BucketItem.class)
public class BucketMixin {
    @Inject(method = "emptyContents", at = @At("HEAD"), cancellable = true)
    private void pokeserver$onlyInPlot(Player player, Level level, BlockPos pos, BlockHitResult hit, CallbackInfoReturnable<Boolean> cir) {
        if (!level.isClientSide() && Farms.isFarm(level) && Farms.plotAt(pos) == null) cir.setReturnValue(false);
    }
}
