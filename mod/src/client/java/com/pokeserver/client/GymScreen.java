package com.pokeserver.client;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.math.Axis;
import com.pokeserver.Net;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

/** 3·4·8. 체육관 안내원 화면 (배지 케이스형 시안 A): 왼쪽 배지 케이스 8칸 + 사천왕 칸, 오른쪽 고른 곳의 정보와 도전하기 버튼.
 *  얻은 배지는 배지 그림, 못 얻은 배지는 모양만. 도전 가능(초록), 클리어(금색 + CLEARED 도장), 다른 사람이 도전 중(주황), 잠김(회색). */
public class GymScreen extends Screen {
    static final int LW = 196, RW = 220, GX = 10, PH = 160, SLOT = 40, SG = 6;
    static final int OPEN = 0xFF4CC46A, CLEARED = 0xFF5CD6FF, BUSY = 0xFFF0A040, EARNED = 0xFF8A7430, LOCKED = 0xFF2A303C;

    private final List<JsonObject> gyms = new ArrayList<>();   // n 순서 (1~8 체육관, 9 사천왕)
    private final Theme.Anim anim = new Theme.Anim();
    private int sel, shaking = -1;
    private long pressedAt, shakeAt, popupAt = -10_000;
    private String popup = "";

    public GymScreen(String json) {
        super(Component.literal("체육관 도전"));
        for (var e : JsonParser.parseString(json).getAsJsonArray()) gyms.add(e.getAsJsonObject());
        gyms.sort((a, b) -> a.get("n").getAsInt() - b.get("n").getAsInt());
        sel = 0;                                                    // 처음엔 지금 도전할 곳 (없으면 마지막으로 깬 곳)
        for (int k = 0; k < gyms.size(); k++) if (!"locked".equals(status(k))) sel = k;
        for (int k = 0; k < gyms.size(); k++) if ("open".equals(status(k))) { sel = k; break; }
    }

    private int x0() { return (width - LW - GX - RW) / 2; }
    private int y0() { return Math.max(30, (height - PH) / 2 + 4); }
    private int slotX(int k) { return k == 8 ? x0() + (LW - 4 * SLOT - 3 * SG) / 2 : x0() + (LW - 4 * SLOT - 3 * SG) / 2 + (k % 4) * (SLOT + SG); }
    private int slotY(int k) { return y0() + 22 + (k / 4) * (SLOT + SG); }
    private int slotW(int k) { return k == 8 ? 4 * SLOT + 3 * SG : SLOT; }
    private int slotH(int k) { return k == 8 ? 22 : SLOT; }
    private int btnX() { return x0() + LW + GX + 10; }
    private int btnY() { return y0() + PH - 30; }
    private String status(int k) { return gyms.get(k).get("status").getAsString(); }
    private String busyBy(int k) { return gyms.get(k).get("busy").getAsString(); }
    private boolean busy(int k) { return "open".equals(status(k)) && !busyBy(k).isEmpty(); }
    private int stateColor(int k) { return switch (status(k)) { case "cleared" -> EARNED; case "open" -> busy(k) ? BUSY : OPEN; default -> LOCKED; }; }
    private static boolean in(double mx, double my, int x, int y, int w, int h) { return mx >= x && mx < x + w && my >= y && my < y + h; }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        g.fill(0, 0, width, height, Theme.PANEL);
        int x = x0(), y = y0();
        long badges = gyms.stream().filter(o -> o.get("n").getAsInt() <= 8 && "cleared".equals(o.get("status").getAsString())).count();
        g.fill(x, y - 18, x + 3, y - 6, Theme.ACCENT);
        g.drawString(font, Theme.t("체육관 도전"), x + 8, y - 16, Theme.TEXT);
        g.drawString(font, Theme.t("배지 " + badges + " / 8"), x + 14 + font.width(Theme.t("체육관 도전")), y - 16, Theme.GOLD);
        // 왼쪽: 배지 케이스
        Theme.panel(g, x, y, x + LW, y + PH, 0xE0181B22, 0xFF2A303C);
        g.drawString(font, Theme.t(Theme.fit(font, "배지 케이스 · 칸을 눌러 보기", LW - 20)), x + 10, y + 8, Theme.SUBTEXT);
        for (int k = 0; k < gyms.size() && k < 9; k++) slot(g, k, anim.to(k, in(mx, my, slotX(k), slotY(k), slotW(k), slotH(k))));
        g.drawString(font, Theme.t(Theme.fit(font, "못 얻은 배지는 모양만", LW - 20)), x + 10, y + PH - 14, Theme.SUBTEXT);
        if (!gyms.isEmpty()) detail(g, sel, anim.to("btn", in(mx, my, btnX(), btnY(), RW - 20, 20)));
        g.drawCenteredString(font, Theme.t("앞 체육관을 클리어하면 다음 칸이 열려요  ·  ESC: 닫기"), width / 2, Math.min(height - 14, y + PH + 10), Theme.SUBTEXT);
        popup(g);
    }

    /** 케이스 한 칸: 배지 그림(얻은 것) / 실루엣(못 얻은 것) + 아래 짧은 상태 글자. 고른 칸은 파란 바탕. */
    private void slot(GuiGraphics g, int k, float h) {
        int x = slotX(k), y = slotY(k), w = slotW(k), sh = slotH(k);
        String st = status(k);
        boolean locked = "locked".equals(st), cleared = "cleared".equals(st);
        int fill = k == sel ? Theme.SELECT : locked ? 0xC0101319 : Theme.mix(Theme.TILE, Theme.TILE_HOVER, h);
        Theme.panel(g, x, y, x + w, y + sh, fill, k == sel ? Theme.ACCENT : stateColor(k));
        String label = cleared ? "✔" : locked ? "잠김" : busy(k) ? "도전 중" : "도전!";
        int lc = cleared ? Theme.GOLD : locked ? 0xFF6B7383 : stateColor(k);
        if (k == 8) {                                                   // 사천왕: 넓은 한 줄
            g.drawString(font, Theme.t("★ 사천왕"), x + 8, y + 7, locked ? 0xFF6B7383 : Theme.GOLD);
            String r = cleared ? "명예의 전당 ✔" : label;
            g.drawString(font, Theme.t(r), x + w - 8 - font.width(Theme.t(r)), y + 7, lc);
            return;
        }
        if (locked) g.setColor(0.1f, 0.11f, 0.14f, 1f);                 // 못 얻은 배지: 색 없이 모양만
        g.pose().pushPose();
        g.pose().translate(x + (w - 24) / 2f, y + 4, 0);
        g.pose().scale(1.5f, 1.5f, 1);
        g.blit(ResourceLocation.fromNamespaceAndPath("pokeserver", "textures/item/badge_" + (k + 1) + ".png"), 0, 0, 0, 0, 16, 16, 16, 16);
        g.pose().popPose();
        g.setColor(1f, 1f, 1f, 1f);
        g.drawCenteredString(font, Theme.t(label), x + w / 2, y + sh - 10, lc);
    }

    /** 오른쪽: 고른 곳의 관장·타입·배지·권장 레벨, 맨 아래 상태별 버튼 (클리어면 도장). */
    private void detail(GuiGraphics g, int k, float h) {
        JsonObject o = gyms.get(k);
        String st = status(k);
        int x = x0() + LW + GX, y = y0(), iw = RW - 20;
        Theme.panel(g, x, y, x + RW, y + PH, 0xE8181B22, stateColor(k));
        g.fill(x + 1, y + 1, x + 4, y + PH - 1, 0xFF000000 | o.get("color").getAsInt());   // 배지 색 띠
        g.drawString(font, Theme.t(o.get("title").getAsString()), x + 10, y + 9, Theme.SUBTEXT);
        g.pose().pushPose();
        g.pose().translate(x + 10, y + 24, 0);
        g.pose().scale(1.6f, 1.6f, 1);
        g.drawString(font, Theme.t(Theme.fit(font, o.get("leader").getAsString(), (int) (iw / 1.6f))), 0, 0, Theme.TEXT);
        g.pose().popPose();
        int cx = x + 10, cy = y + 46;                                   // 칩: 타입(배지 색) · 배지 이름
        for (String[] c : new String[][]{{o.get("type").getAsString(), "type"}, {o.get("badge").getAsString(), "badge"}}) {
            int cw = Math.min(iw, font.width(Theme.t(c[0])) + 8);
            if (cx + cw > x + 10 + iw) { cx = x + 10; cy += 15; }
            g.fill(cx, cy, cx + cw, cy + 12, c[1].equals("type") ? Theme.mix(0xFF101319, 0xFF000000 | o.get("color").getAsInt(), 0.55f) : Theme.SELECT);
            g.drawString(font, Theme.t(Theme.fit(font, c[0], cw - 8)), cx + 4, cy + 2, Theme.TEXT);
            cx += cw + 5;
        }
        int ry = cy + 22;
        g.drawString(font, Theme.t("권장 레벨"), x + 10, ry, Theme.SUBTEXT);
        g.drawString(font, Theme.t("Lv. " + o.get("level").getAsInt()), x + 70, ry, Theme.TEXT);
        g.drawString(font, Theme.t("상태"), x + 10, ry + 14, Theme.SUBTEXT);
        String now = switch (st) { case "cleared" -> "클리어"; case "open" -> busy(k) ? busyBy(k) + "님이 도전 중" : "도전 가능"; default -> "잠김"; };
        g.drawString(font, Theme.t(Theme.fit(font, now, iw - 60)), x + 70, ry + 14, stateColor(k) == LOCKED ? 0xFF6B7383 : stateColor(k));
        if ("cleared".equals(st)) { stamp(g, x + RW - 50, y + PH - 22); return; }
        long since = System.currentTimeMillis() - shakeAt;
        float shake = k == shaking && since < 400 ? (float) Math.sin(since / 22.0) * 4f * (1 - since / 400f) : 0f;   // 막혔을 때 좌우로 살짝
        float sc = Theme.press(pressedAt);
        int bx = btnX(), by = btnY();
        g.pose().pushPose();
        g.pose().translate(bx + iw / 2f + shake, by + 10, 0);
        g.pose().scale(sc, sc, 1);
        g.pose().translate(-iw / 2f, -10, 0);
        boolean locked = "locked".equals(st);
        int bc = locked ? LOCKED : busy(k) ? BUSY : Theme.mix(0xFF3CB46A, 0xFF4CD07A, h);
        g.fill(0, 0, iw, 20, bc);
        String b = locked ? "앞 체육관을 먼저 클리어" : busy(k) ? "다른 사람이 도전 중" : "도전하기 ▶";
        g.drawCenteredString(font, Theme.t(b), iw / 2, 6, locked ? Theme.SUBTEXT : 0xFFFFFFFF);
        g.pose().popPose();
    }

    /** 클리어 도장: 기울어진 하늘색 테두리 상자 + 큰 CLEARED. */
    private void stamp(GuiGraphics g, int cx, int cy) {
        g.pose().pushPose();
        g.pose().translate(cx, cy, 10);
        g.pose().mulPose(Axis.ZP.rotationDegrees(-10));
        int w = 74, hgt = 20;
        g.fill(-w / 2 - 2, -hgt / 2 - 2, w / 2 + 2, hgt / 2 + 2, 0x405CD6FF);   // 은은한 빛
        g.fill(-w / 2, -hgt / 2, w / 2, hgt / 2, 0xD00A1A28);
        g.renderOutline(-w / 2, -hgt / 2, w, hgt, CLEARED);
        g.renderOutline(-w / 2 + 2, -hgt / 2 + 2, w - 4, hgt - 4, 0xA05CD6FF);
        g.pose().scale(1.4f, 1.4f, 1);
        g.drawCenteredString(font, Theme.t("CLEARED"), 0, -4, CLEARED);
        g.pose().popPose();
    }

    /** 다른 사람이 도전 중인 곳에 도전하면 화면 가운데 3초 알림. */
    private void popup(GuiGraphics g) {
        long since = System.currentTimeMillis() - popupAt;
        if (since > 3000) return;
        float a = since > 2700 ? (3000 - since) / 300f : 1f;
        int w = font.width(Theme.t(popup)) + 32, x = (width - w) / 2, y = height / 2 - 14;
        g.pose().pushPose();
        g.pose().translate(0, 0, 300);
        Theme.panel(g, x, y, x + w, y + 28, Theme.mix(0x00181B22, 0xF0181B22, a), Theme.mix(0x00F0A040, BUSY, a));
        g.drawCenteredString(font, Theme.t(popup), width / 2, y + 10, Theme.mix(0x00FFFFFF, Theme.TEXT, a));
        g.pose().popPose();
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        for (int k = 0; k < gyms.size() && k < 9; k++)
            if (in(mx, my, slotX(k), slotY(k), slotW(k), slotH(k))) { sel = k; return true; }
        if (!gyms.isEmpty() && "open".equals(status(sel)) && in(mx, my, btnX(), btnY(), RW - 20, 20)) {
            pressedAt = System.currentTimeMillis();
            if (busy(sel)) {
                shaking = sel;
                shakeAt = popupAt = System.currentTimeMillis();
                popup = busyBy(sel) + "님이 도전 중이에요. 잠시 후 다시 도전해 주세요.";
                return true;
            }
            ClientPlayNetworking.send(new Net.GymPick(gyms.get(sel).get("n").getAsInt()));
            onClose();
            return true;
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
