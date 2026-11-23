package com.pokeserver.client.mixin;

import com.pokeserver.client.Bgm;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.Music;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 지금 틀 음악: 공간 BGM이 있는 자리면 그 곡 (Bgm.AT, 메인 화면은 Bgm.TITLE). */
@Mixin(Minecraft.class)
public class MusicMixin {
    @Inject(method = "getSituationalMusic", at = @At("HEAD"), cancellable = true)
    private void pokeserver$bgm(CallbackInfoReturnable<Music> cir) {
        Music m = Bgm.situational((Minecraft) (Object) this);
        if (m != null) cir.setReturnValue(m);
    }
}
