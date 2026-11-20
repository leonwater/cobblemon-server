package com.pokeserver.client;

import com.pokeserver.Nicknames;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;

/** 7. 오른쪽 가운데 간략 정보: [별명] 닉네임, 소지금, 배지, 레벨 제한, 도감, 시간, 바이옴, 좌표 (참고 사진처럼). */
public final class InfoHud {
    private InfoHud() {}

    static long balance = -1;
    static int badges, dex = -1;

    static void render(GuiGraphics g, DeltaTracker dt) {
        Minecraft mc = Minecraft.getInstance();
        // 화면(배틀·메뉴)이 열려 있으면 숨김: 배틀 확장 UI의 정보창과 같은 자리라서
        if (mc.player == null || mc.level == null || mc.screen != null || mc.options.hideGui || mc.getDebugOverlay().showDebugScreen()) return;
        var font = mc.font;
        var p = mc.player;
        Component name = Nicknames.SHOWN.getOrDefault(p.getUUID(), Component.literal(p.getGameProfile().getName()));
        long day = mc.level.getDayTime() % 24000;
        int cap = MenuScreen.levelCap(p);
        var pos = p.blockPosition();
        var biome = mc.level.getBiome(pos).unwrapKey().map(k -> Component.translatable("biome." + k.location().getNamespace() + "." + k.location().getPath()))
                .orElse(Component.literal("-"));
        String[][] rows = {
                {"소지금", balance < 0 ? "-" : Theme.money(font, balance, "원", 90)},
                {"배지", badges + " / 8"},
                {"레벨 제한", cap > 0 ? "Lv" + cap : "-"},
                {"도감", dex < 0 ? "-" : dex + "종"},
                {"시간", String.format("%02d:%02d", (day / 1000 + 6) % 24, day % 1000 * 60 / 1000)},
                {"바이옴", biome.getString()},
                {"좌표", pos.getX() + " " + pos.getY() + " " + pos.getZ()}};
        float s = Math.min(1f, 3f / (float) mc.getWindow().getGuiScale());   // 전체 화면(GUI 4)에서도 너무 크지 않게
        int lw = 0, vw = 0;
        for (String[] r : rows) { lw = Math.max(lw, font.width(Theme.t(r[0]))); vw = Math.max(vw, font.width(Theme.t(r[1]))); }
        int row = font.lineHeight + 4, w = Math.max(lw + 10 + vw, font.width(name)) + 12, h = 18 + rows.length * row + 4;
        int sw = (int) (g.guiWidth() / s), sh = (int) (g.guiHeight() / s);
        int x = sw - w - 4, y = (sh - h) / 2;
        g.pose().pushPose();
        g.pose().scale(s, s, 1);
        g.fill(x, y, x + w, y + h, 0x90101319);
        g.fill(x, y, x + 2, y + h, Theme.ACCENT);
        g.drawString(font, name, x + 6, y + 4, Theme.TEXT, true);
        g.hLine(x + 6, x + w - 6, y + font.lineHeight + 6, 0x804A5366);
        for (int i = 0; i < rows.length; i++) {
            int ry = y + font.lineHeight + 10 + i * row;
            g.drawString(font, Theme.t(rows[i][0]), x + 6, ry, Theme.SUBTEXT, false);
            g.drawString(font, Theme.t(rows[i][1]), x + w - 6 - font.width(Theme.t(rows[i][1])), ry, i == 0 ? Theme.GOLD : Theme.TEXT, false);
        }
        g.pose().popPose();
    }
}
