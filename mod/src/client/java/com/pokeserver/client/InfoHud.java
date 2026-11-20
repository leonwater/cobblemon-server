package com.pokeserver.client;

import com.pokeserver.Nicknames;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;

/** 7. 오른쪽 가운데 간략 정보 (참고 사진처럼): 닉네임, 그 아래 두 묶음 "이름 ∥ 값" — 위치·소지금·배지 / 시간·바이옴·좌표.
 *  줄 간격은 모두 같게, 묶음 왼쪽에 세로 줄. */
public final class InfoHud {
    private InfoHud() {}

    static long balance = -1;
    static int badges;
    static String place = "";

    static void render(GuiGraphics g, DeltaTracker dt) {
        Minecraft mc = Minecraft.getInstance();
        // 화면(배틀·메뉴)이 열려 있으면 숨김: 배틀 확장 UI의 정보창과 같은 자리라서
        if (mc.player == null || mc.level == null || mc.screen != null || BattleScale.inBattle() || mc.options.hideGui || mc.getDebugOverlay().showDebugScreen()) return;
        var font = mc.font;
        var p = mc.player;
        Component name = Nicknames.SHOWN.getOrDefault(p.getUUID(), Component.literal(p.getGameProfile().getName()));
        long day = mc.level.getDayTime() % 24000;
        var pos = p.blockPosition();
        var biome = mc.level.getBiome(pos).unwrapKey().map(k -> Component.translatable("biome." + k.location().getNamespace() + "." + k.location().getPath()))
                .orElse(Component.literal("-"));
        String[][][] groups = {
                {{"위치", place.isEmpty() ? "-" : place}, {"소지금", balance < 0 ? "-" : Theme.money(font, balance, "원", 90)}, {"배지", badges + " / 8"}},
                {{"시간", String.format("%02d:%02d", (day / 1000 + 6) % 24, day % 1000 * 60 / 1000)}, {"바이옴", biome.getString()},
                        {"좌표", pos.getX() + " " + pos.getY() + " " + pos.getZ()}}};
        float s = Math.min(1f, 2f / (float) mc.getWindow().getGuiScale());   // 참고 사진 크기: 전체 화면에서 GUI 2배 크기로
        int lw = 0, vw = 0;
        for (String[][] gr : groups) for (String[] r : gr) { lw = Math.max(lw, font.width(Theme.t(r[0]))); vw = Math.max(vw, font.width(Theme.t(r[1]))); }
        int row = font.lineHeight + 6, gap = 8, sep = font.width(Theme.t(" ∥ "));
        int w = Math.max(lw + sep + vw, font.width(name)) + 18, h = font.lineHeight + 10 + 6 * row + gap + 6;
        int sw = (int) (g.guiWidth() / s), sh = (int) (g.guiHeight() / s);
        int x = sw - w - 6, y = (sh - h) / 2;
        g.pose().pushPose();
        g.pose().scale(s, s, 1);
        g.fill(x, y, x + w, y + h, 0x70101319);
        g.drawString(font, name, x + (w - font.width(name)) / 2, y + 5, Theme.TEXT, true);
        int ry = y + font.lineHeight + 12;
        for (String[][] gr : groups) {
            g.fill(x + 6, ry - 2, x + 7, ry + gr.length * row - 4, 0xFFD0D4DC);            // 묶음 왼쪽 세로 줄
            for (String[] r : gr) {
                g.drawString(font, Theme.t(r[0]), x + 11, ry, Theme.TEXT, true);
                g.drawString(font, Theme.t(" ∥ "), x + 11 + lw, ry, Theme.SUBTEXT, true);
                g.drawString(font, Theme.t(r[1]), x + 11 + lw + sep, ry, r[0].equals("소지금") ? Theme.GOLD : Theme.TEXT, true);
                ry += row;
            }
            ry += gap;
        }
        g.pose().popPose();
    }
}
