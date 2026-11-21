package com.pokeserver.client.mixin;

import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastComponent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 오른쪽 위 알림(발전 과제·제작법·Cobblemon 안내 등)은 띄우지 않음. 채팅 알림은 그대로. */
@Mixin(ToastComponent.class)
abstract class ToastMixin {
    @Inject(method = "addToast", at = @At("HEAD"), cancellable = true)
    private void pokeserver$noToast(Toast toast, CallbackInfo ci) { ci.cancel(); }
}
