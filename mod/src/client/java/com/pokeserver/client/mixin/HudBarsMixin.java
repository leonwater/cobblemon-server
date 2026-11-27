package com.pokeserver.client.mixin;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** HUD B안: 하트·배고픔·경험치를 칸 나뉜 바로. 바닐라와 같은 자리·길이 (하트·배고픔 81칸 안, 경험치 182).
 *  갑옷·공기·탈것 체력은 바닐라 그대로. 흡수 체력은 바 위 금색 줄, 독·시듦·얼음은 바 색으로. */
@Mixin(Gui.class)
abstract class HudBarsMixin {
    @Shadow @Final private Minecraft minecraft;
    @Shadow protected abstract boolean isExperienceBarVisible();

    private static final int SEG = 10, SW = 7, SH = 4, BORDER = 0xFF101319, EMPTY = 0xFF3A3F4A;

    /** 칸 10개 (한 칸 7px, 틈 1px = 79px). rtl이면 오른쪽부터 참 (바닐라 배고픔과 같은 방향). */
    private static void pokeserver$segs(GuiGraphics g, int x, int y, float frac, int color, int border, boolean rtl) {
        for (int i = 0; i < SEG; i++) {
            int sx = x + i * (SW + 1);
            g.fill(sx, y, sx + SW, y + SH, border);
            g.fill(sx + 1, y + 1, sx + SW - 1, y + SH - 1, EMPTY);
            float f = Math.max(0, Math.min(1, frac * SEG - (rtl ? SEG - 1 - i : i)));
            int w = Math.round((SW - 2) * f);
            if (w > 0) {
                int fx = rtl ? sx + SW - 1 - w : sx + 1;
                g.fill(fx, y + 1, fx + w, y + SH - 1, color);
            }
        }
    }

    @Inject(method = "renderHearts", at = @At("HEAD"), cancellable = true)
    private void pokeserver$hearts(GuiGraphics g, Player p, int x, int y, int rowH, int regen, float max, int hp, int shown, int absorb, boolean blink, CallbackInfo ci) {
        ci.cancel();
        float m = Math.max(1, max), r = hp / m;
        int c = p.hasEffect(MobEffects.POISON) ? 0xFFA040A0 : p.hasEffect(MobEffects.WITHER) ? 0xFF6B5B8A
                : p.isFullyFrozen() ? 0xFF8CC8F0 : r <= .2f ? 0xFFFF7070 : 0xFFE04848;
        int yy = y + 3;   // 하트(9px) 줄 가운데 (참고 사진처럼 얇게 4px)
        pokeserver$segs(g, x + 1, yy, r, c, blink ? 0xFFFFFFFF : BORDER, false);
        if (absorb > 0) g.fill(x + 1, yy - 2, x + 1 + Math.round(79 * Math.min(1, absorb / m)), yy - 1, 0xFFF0C040);
    }

    @Inject(method = "renderFood", at = @At("HEAD"), cancellable = true)
    private void pokeserver$food(GuiGraphics g, Player p, int y, int right, CallbackInfo ci) {
        ci.cancel();
        int c = p.hasEffect(MobEffects.HUNGER) ? 0xFF78A040 : 0xFFF0C040;
        pokeserver$segs(g, right - 80, y + 3, p.getFoodData().getFoodLevel() / 20f, c, BORDER, true);
    }

    @Inject(method = "renderExperienceBar", at = @At("HEAD"), cancellable = true)
    private void pokeserver$xp(GuiGraphics g, int x, CallbackInfo ci) {
        ci.cancel();
        if (minecraft.player.getXpNeededForNextLevel() <= 0) return;
        int y = g.guiHeight() - 29;
        g.fill(x, y, x + 182, y + 5, BORDER);
        g.fill(x + 1, y + 1, x + 181, y + 4, 0xFF2A2F3A);
        int w = Math.round(180 * minecraft.player.experienceProgress);
        if (w > 0) g.fill(x + 1, y + 1, x + 1 + w, y + 4, 0xFF58B8F8);
    }

    @Inject(method = "renderExperienceLevel", at = @At("HEAD"), cancellable = true)
    private void pokeserver$level(GuiGraphics g, DeltaTracker dt, CallbackInfo ci) {
        ci.cancel();
        int lv = minecraft.player.experienceLevel;
        if (!isExperienceBarVisible() || lv <= 0) return;
        var font = minecraft.font;
        String s = String.valueOf(lv);
        int x = (g.guiWidth() - font.width(s)) / 2, y = g.guiHeight() - 31 - 4;
        for (int[] d : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) g.drawString(font, s, x + d[0], y + d[1], 0xFF0B2A40, false);
        g.drawString(font, s, x, y, 0xFF7FD0FF, false);
    }
}
