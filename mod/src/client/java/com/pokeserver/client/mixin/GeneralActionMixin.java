package com.pokeserver.client.mixin;

import com.cobblemon.mod.common.client.battle.SingleActionRequest;
import com.cobblemon.mod.common.client.gui.battle.BattleGUI;
import com.cobblemon.mod.common.client.gui.battle.subscreen.BattleGeneralActionSelection;
import com.cobblemon.mod.common.client.gui.battle.widgets.BattleOptionTile;
import com.pokeserver.Net;
import com.pokeserver.client.BattleScale;
import com.pokeserver.client.Theme;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.sounds.SoundEvents;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 5. 행동 선택 (참고 사진 배치): 싸운다 | 포켓몬 / 포기(도망) 아래 왼쪽, 야생이면 잡기 아래 오른쪽.
 *  그 위에 작은 "전투 속도 1x·2x·4x" 버튼 (누를 때마다 바뀜, 서버가 배틀 기다림을 줄임). */
@Mixin(value = BattleGeneralActionSelection.class, remap = false)
abstract class GeneralActionMixin {
    @Unique private static final int SW = 66, SH = 12, HALF = 48;   // 속도 버튼 크기 (배틀 좌표)

    @Inject(method = "<init>", at = @At("RETURN"))
    private void pokeserver$layout(BattleGUI gui, SingleActionRequest request, CallbackInfo ci) {
        var tiles = ((BattleGeneralActionSelection) (Object) this).getTiles();
        BattleOptionTile fight = null, sw = null, run = null, ball = null;
        for (var t : tiles) {
            String path = t.getResource().getPath();
            if (path.contains("fight")) fight = t;
            else if (path.contains("switch")) sw = t;
            else if (path.contains("bag")) ball = t;   // 잡기 (야생 배틀에만)
            else run = t;                              // 도망·기권
        }
        if (fight == null) return;
        int x0 = fight.getX(), y0 = fight.getY(), x1 = x0 + 93, y1 = y0 + 29;   // 코블몬과 같은 칸 간격
        tiles.clear();
        tiles.add(fight);
        if (sw != null) tiles.add(new BattleOptionTile(gui, x1, y0, sw.getResource(), sw.getText(), sw.getOnClick()));
        if (run != null) tiles.add(new BattleOptionTile(gui, x0, y1, run.getResource(), run.getText(), run.getOnClick()));
        if (ball != null) tiles.add(new BattleOptionTile(gui, x1, y1, ball.getResource(), ball.getText(), ball.getOnClick()));
        ClientPlayNetworking.send(new Net.BattleSpeed(BattleScale.speed));   // 다시 접속해도 서버 값 = 화면 값
    }

    @Unique
    private int[] pokeserver$box() {
        var tiles = ((BattleGeneralActionSelection) (Object) this).getTiles();
        if (tiles.isEmpty()) return null;
        var t = tiles.get(0);
        return new int[]{t.getX(), t.getY() - SH - 3};
    }

    @Inject(method = "method_48579", at = @At("TAIL"))
    private void pokeserver$drawSpeed(GuiGraphics g, int mx, int my, float pt, CallbackInfo ci) {
        int[] b = pokeserver$box();
        if (b == null) return;
        int x = b[0], y = b[1], half = HALF;
        boolean hov = mx >= x && mx < x + SW && my >= y && my < y + SH;
        g.fill(x, y, x + SW, y + SH, hov ? 0xF0262B36 : 0xE0101319);
        g.renderOutline(x, y, SW, SH, hov ? Theme.ACCENT : 0xFF3A4152);
        g.fill(x + half, y + 1, x + half + 1, y + SH - 1, 0xFF3A4152);
        var font = Minecraft.getInstance().font;
        float k = BattleScale.crisp(0.6f);   // 작은 글자, 한 점 = 정수 픽셀
        g.pose().pushPose();
        g.pose().translate(x, y + (SH - 8 * k) / 2f + 0.5f, 0);
        g.pose().scale(k, k, 1);
        String label = "전투 속도", val = BattleScale.speed + "x";
        g.drawString(font, Theme.t(label), Math.round((half / k - font.width(Theme.t(label))) / 2), 0, Theme.SUBTEXT, false);
        g.drawString(font, Theme.t(val), Math.round(half / k + ((SW - half) / k - font.width(Theme.t(val))) / 2), 0,
                BattleScale.speed > 1 ? Theme.GOLD : Theme.TEXT, false);
        g.pose().popPose();
    }

    @Inject(method = "mousePrimaryClicked", at = @At("HEAD"), cancellable = true)
    private void pokeserver$clickSpeed(double mx, double my, CallbackInfoReturnable<Boolean> cir) {
        int[] b = pokeserver$box();
        if (b == null || mx < b[0] || mx >= b[0] + SW || my < b[1] || my >= b[1] + SH) return;
        BattleScale.speed = BattleScale.speed >= 4 ? 1 : BattleScale.speed * 2;
        ClientPlayNetworking.send(new Net.BattleSpeed(BattleScale.speed));
        Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1f));
        cir.setReturnValue(true);
    }
}
