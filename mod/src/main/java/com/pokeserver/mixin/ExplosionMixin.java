package com.pokeserver.mixin;

import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Explosion;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 서버 전체: 폭발(TNT·크리퍼·가스트·침대 등)이 블록을 부수거나 불을 놓지 않음. 엔티티 피해·넉백은 그대로. */
@Mixin(Explosion.class)
public class ExplosionMixin {
    @Shadow @Final private ObjectArrayList<BlockPos> toBlow;

    @Inject(method = "finalizeExplosion", at = @At("HEAD"))
    private void pokeserver$keepBlocks(boolean particles, CallbackInfo ci) {
        toBlow.clear();
    }
}
