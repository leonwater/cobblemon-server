package com.pokeserver.client.mixin;

import com.pokeserver.client.BattleScale;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Cobblemon 배틀 화면: 배치(init)와 마우스 좌표를 줄인 화면 기준으로. 이름은 실행 환경(intermediary) 이름. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.client.gui.battle.BattleGUI", remap = false)
abstract class BattleGuiMixin extends Screen {
    protected BattleGuiMixin() { super(Component.empty()); }

    @Inject(method = "method_25426", at = @At("HEAD"))
    private void pokeserver$initHead(CallbackInfo ci) {
        float f = BattleScale.f();
        width = Math.round(width / f);
        height = Math.round(height / f);
        BattleScale.on = true;
    }

    @Inject(method = "method_25426", at = @At("RETURN"))
    private void pokeserver$initEnd(CallbackInfo ci) { BattleScale.on = false; }

    @Inject(method = "method_25402", at = @At("HEAD"), cancellable = true)
    private void pokeserver$click(double mx, double my, int b, CallbackInfoReturnable<Boolean> cir) {
        if (BattleScale.inside) return;
        float f = BattleScale.f();
        BattleScale.inside = BattleScale.on = true;
        try { cir.setReturnValue(mouseClicked(mx / f, my / f, b)); } finally { BattleScale.inside = BattleScale.on = false; }
    }

    @Inject(method = "method_25403", at = @At("HEAD"), cancellable = true)
    private void pokeserver$drag(double mx, double my, int b, double dx, double dy, CallbackInfoReturnable<Boolean> cir) {
        if (BattleScale.inside) return;
        float f = BattleScale.f();
        BattleScale.inside = BattleScale.on = true;
        try { cir.setReturnValue(mouseDragged(mx / f, my / f, b, dx / f, dy / f)); } finally { BattleScale.inside = BattleScale.on = false; }
    }

    @Inject(method = "method_25400", at = @At("HEAD"))
    private void pokeserver$typeHead(char c, int m, CallbackInfoReturnable<Boolean> cir) { BattleScale.on = true; }

    @Inject(method = "method_25400", at = @At("RETURN"))
    private void pokeserver$typeEnd(char c, int m, CallbackInfoReturnable<Boolean> cir) { BattleScale.on = false; }

    @Override
    public boolean mouseScrolled(double mx, double my, double h, double v) {
        float f = BattleScale.f();
        BattleScale.on = true;
        try { return super.mouseScrolled(mx / f, my / f, h, v); } finally { BattleScale.on = false; }
    }

    @Override
    public boolean mouseReleased(double mx, double my, int b) {
        float f = BattleScale.f();
        BattleScale.on = true;
        try { return super.mouseReleased(mx / f, my / f, b); } finally { BattleScale.on = false; }
    }
}
