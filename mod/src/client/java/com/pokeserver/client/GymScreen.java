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

/** 3·4·8. 체육관 안내원 화면 = 체육관 리그 로드맵: 1~8번 체육관이 지그재그 길로 이어지고 끝에 사천왕(정보 없이 ? 만, 미스터리).
 *  깬 곳(초록 + 배지 그림 + ✔), 지금 도전할 곳(하늘색으로 빛남 + 내 얼굴), 다른 사람이 도전 중(주황), 잠김(어두운 모양 + 자물쇠).
 *  아래 정보창: 관장·타입·권장 레벨·상태·보상(상금·물품) + 체육관 이동 버튼 (깬 곳은 CLEARED 도장). */
public class GymScreen extends Screen {
    static final int W = 470, H = 246, NODE = 30, STEP = 49, E4 = 46, BH = 26, RX = 230;   // 글씨보다 칸을 넉넉하게 (GUI 자동 1920×1080 = 480×270 안에)
    static final int DONE = 0xFF6CC46A, OPEN = 0xFF5CD6FF, BUSY = 0xFFF0A040, LOCKED = 0xFF2A303C, MYST = 0xFFB080F0, DIM = 0xFF6B7383;

    private final List<JsonObject> gyms = new ArrayList<>();   // n 순서 (1~8 체육관, 9 사천왕)
    private final Theme.Anim anim = new Theme.Anim();
    private int sel, shaking = -1;
    private long pressedAt, shakeAt, popupAt = -10_000;
    private String popup = "";

    public GymScreen(String json) {
        super(Component.literal("체육관 리그 로드맵"));
        for (var e : JsonParser.parseString(json).getAsJsonArray()) gyms.add(e.getAsJsonObject());
        gyms.sort((a, b) -> a.get("n").getAsInt() - b.get("n").getAsInt());
        for (int k = 0; k < gyms.size(); k++) if (!"locked".equals(status(k))) sel = k;   // 처음엔 지금 도전할 곳 (없으면 마지막으로 깬 곳)
        for (int k = 0; k < gyms.size(); k++) if ("open".equals(status(k))) { sel = k; break; }
    }

    private int x0() { return (width - W) / 2; }
    private int y0() { return Math.max(4, (height - H) / 2); }
    private int cx(int k) { return k == 8 ? x0() + W - 44 : x0() + 30 + k * STEP; }
    private int cy(int k) { int ry = y0() + 36; return k == 8 ? ry + 48 : k % 2 == 0 ? ry + 68 : ry + 30; }   // 1·3·5·7번은 아래, 2·4·6·8번은 위
    private int half(int k) { return (k == 8 ? E4 : NODE) / 2; }
    private int py() { return y0() + 138; }
    private int btnX() { return x0() + 12 + RX; }
    private int btnW() { return W - 24 - RX - 12; }
    private int btnY() { return py() + 58; }
    private String status(int k) { return gyms.get(k).get("status").getAsString(); }
    private String busyBy(int k) { return gyms.get(k).get("busy").getAsString(); }
    private boolean busy(int k) { return "open".equals(status(k)) && !busyBy(k).isEmpty(); }
    private int color(int k) { return switch (status(k)) { case "cleared" -> DONE; case "open" -> busy(k) ? BUSY : OPEN; default -> LOCKED; }; }
    private boolean onNode(double mx, double my, int k) { return Math.abs(mx - cx(k)) <= half(k) && Math.abs(my - cy(k)) <= half(k); }
    private static boolean in(double mx, double my, int x, int y, int w, int h) { return mx >= x && mx < x + w && my >= y && my < y + h; }
    private static float pulse() { return (float) (Math.sin(System.currentTimeMillis() / 300.0) * 0.5 + 0.5); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        g.fill(0, 0, width, height, Theme.PANEL);
        int x = x0(), y = y0(), n = Math.min(9, gyms.size());
        Theme.panel(g, x, y, x + W, y + H, 0xEC141720, Theme.BORDER);
        // 제목 탭 (가운데) + 배지 칩 (오른쪽)
        Component title = Theme.t("체육관 리그 로드맵");
        int tw = Math.round(font.width(title) * 1.3f) + 40, tx = x + (W - tw) / 2;
        Theme.panel(g, tx, y + 5, tx + tw, y + 27, 0xF01C2029, Theme.ACCENT);
        g.pose().pushPose();
        g.pose().translate(tx + 20, y + 10, 0);
        g.pose().scale(1.3f, 1.3f, 1);
        g.drawString(font, title, 0, 0, Theme.TEXT, true);
        g.pose().popPose();
        long badges = gyms.stream().filter(o -> o.get("n").getAsInt() <= 8 && "cleared".equals(o.get("status").getAsString())).count();
        Component bc = Theme.t("배지 " + badges + " / 8");
        int bw = font.width(bc) + 20;
        Theme.panel(g, x + W - 12 - bw, y + 8, x + W - 12, y + 25, 0xE0201C10, Theme.GOLD);
        g.drawString(font, bc, x + W - 2 - bw, y + 13, Theme.GOLD, false);
        // 길 (먼저 그려서 칸 아래로)
        for (int k = 0; k + 1 < n; k++) {
            int c = "cleared".equals(status(k + 1)) ? DONE : "open".equals(status(k + 1)) ? (k + 1 == 8 ? MYST : color(k + 1)) : 0xFF3A4152;
            line(g, cx(k), cy(k), cx(k + 1), cy(k + 1), c, "locked".equals(status(k + 1)));
        }
        for (int k = 0; k < n; k++) {
            float h = anim.to(k, onNode(mx, my, k));
            if (k == 8) e4Node(g, h); else node(g, k, h);
        }
        if (!gyms.isEmpty()) detail(g, sel, anim.to("btn", in(mx, my, btnX(), btnY(), btnW(), BH)));
        popup(g);
    }

    /** 두 칸을 잇는 길: 2칸 굵기 점을 이어 그림. 잠긴 곳으로 가는 길은 점선. */
    private static void line(GuiGraphics g, int x1, int y1, int x2, int y2, int c, boolean dashed) {
        int steps = Math.max(Math.abs(x2 - x1), Math.abs(y2 - y1));
        for (int i = 0; i <= steps; i++) {
            if (dashed && (i / 3) % 2 == 1) continue;
            int x = x1 + (x2 - x1) * i / Math.max(1, steps), y = y1 + (y2 - y1) * i / Math.max(1, steps);
            g.fill(x - 1, y - 1, x + 1, y + 1, c);
        }
    }

    private static void lock(GuiGraphics g, int cx, int y, int c) {
        g.renderOutline(cx - 2, y, 5, 4, c);
        g.fill(cx - 3, y + 3, cx + 4, y + 8, c);
        g.fill(cx, y + 5, cx + 1, y + 7, 0xFF101319);
    }

    /** 체육관 칸: 번호(위), 배지 그림·실루엣·내 얼굴, 상태 글자(아래). 고른 칸은 흰 테두리, 지금 도전할 곳은 하늘색으로 빛남. */
    private void node(GuiGraphics g, int k, float h) {
        String st = status(k);
        boolean locked = "locked".equals(st), cleared = "cleared".equals(st), now = "open".equals(st) && !busy(k);
        int c = color(k), x = cx(k) - NODE / 2, y = cy(k) - NODE / 2 - Math.round(h * 2);
        g.drawCenteredString(font, Theme.t(String.valueOf(k + 1)), cx(k), y - 12, locked ? DIM : c);
        if (now) for (int r = 1; r <= 3; r++)                                              // 빛 번짐
            g.renderOutline(x - r, y - r, NODE + 2 * r, NODE + 2 * r, Math.round((0x70 - r * 0x18) * pulse()) << 24 | (OPEN & 0xFFFFFF));
        Theme.panel(g, x, y, x + NODE, y + NODE, locked ? 0xE0101319 : cleared ? 0xE0142014 : Theme.mix(0xE0102A33, 0xF0183844, h), c);
        if (k == sel) g.renderOutline(x - 2, y - 2, NODE + 4, NODE + 4, 0xFFE8ECF4);
        if ("open".equals(st) && minecraft != null && minecraft.player != null) {           // 지금 갈 곳 = 내 얼굴
            var skin = minecraft.getSkinManager().getInsecureSkin(minecraft.player.getGameProfile()).texture();
            g.blit(skin, x + 7, y + 7, 16, 16, 8, 8, 8, 8, 64, 64);
            g.blit(skin, x + 7, y + 7, 16, 16, 40, 8, 8, 8, 64, 64);
        } else {
            if (locked) g.setColor(0.1f, 0.11f, 0.14f, 1f);                                // 못 얻은 배지: 모양만
            g.pose().pushPose();
            g.pose().translate(x + 5, y + 5, 0);
            g.pose().scale(1.25f, 1.25f, 1);
            g.blit(ResourceLocation.fromNamespaceAndPath("pokeserver", "textures/item/badge_" + (k + 1) + ".png"), 0, 0, 0, 0, 16, 16, 16, 16);
            g.pose().popPose();
            g.setColor(1f, 1f, 1f, 1f);
        }
        int by = y + NODE + 4;
        if (cleared) {
            g.fill(x + NODE - 8, y + NODE - 8, x + NODE + 1, y + NODE + 1, 0xFF101319);
            g.drawString(font, Theme.t("✔"), x + NODE - 7, y + NODE - 8, DONE, false);
            tag(g, gyms.get(k).get("leader").getAsString().replace("관장 ", ""), cx(k), by, Theme.SUBTEXT);
        } else if (locked) lock(g, cx(k), by, DIM);
        else tag(g, busy(k) ? "도전 중" : "도전 가능", cx(k), by, c);
    }

    /** 칸 아래 글자: 길 위에 겹쳐도 읽히게 어두운 바탕. */
    private void tag(GuiGraphics g, String s, int cx, int y, int c) {
        int w = font.width(Theme.t(s));
        g.fill(cx - w / 2 - 3, y - 2, cx + w / 2 + 3, y + 10, 0xE0141720);
        g.drawCenteredString(font, Theme.t(s), cx, y, c);
    }

    /** 사천왕: 보라 테두리 큰 칸에 ? 하나 (정보는 일부러 안 보여 줌). */
    private void e4Node(GuiGraphics g, float h) {
        String st = status(8);
        boolean locked = "locked".equals(st);
        int x = cx(8) - E4 / 2, y = cy(8) - E4 / 2 - Math.round(h * 2), c = locked ? 0xFF3A2E4A : MYST;
        if (!locked) for (int r = 1; r <= 3; r++)
            g.renderOutline(x - r, y - r, E4 + 2 * r, E4 + 2 * r, Math.round((0x70 - r * 0x18) * pulse()) << 24 | (MYST & 0xFFFFFF));
        Theme.panel(g, x, y, x + E4, y + E4, 0xF0160F22, c);
        g.renderOutline(x + 3, y + 3, E4 - 6, E4 - 6, locked ? 0x603A2E4A : 0x80B080F0);
        if (sel == 8) g.renderOutline(x - 2, y - 2, E4 + 4, E4 + 4, 0xFFE8ECF4);
        g.pose().pushPose();
        g.pose().translate(cx(8), y + 11, 0);
        g.pose().scale(2.6f, 2.6f, 1);
        g.drawCenteredString(font, Theme.t("cleared".equals(st) ? "★" : "?"), 0, 0, locked ? 0xFF5A4A72 : Theme.GOLD);
        g.pose().popPose();
        g.drawCenteredString(font, Theme.t("사천왕"), cx(8), y + E4 + 4, locked ? DIM : MYST);
        if (locked) lock(g, cx(8), y + E4 + 16, DIM);
    }

    /** 아래 정보창: 왼쪽 정보(제목·관장·권장 레벨·상태), 오른쪽 보상(배지·상금·물품) + 체육관 이동 버튼. 사천왕은 제목만 두고 나머지는 ? (미스터리). */
    private void detail(GuiGraphics g, int k, float h) {
        JsonObject o = gyms.get(k);
        String st = status(k);
        boolean e4 = k == 8, locked = "locked".equals(st);
        int px = x0() + 12, py = py(), pw = W - 24, ph = 96, rx = px + RX, rw = btnW();
        Theme.panel(g, px, py, px + pw, py + ph, 0xF0181B22, e4 ? 0xFF3A2E4A : 0xFF2A303C);
        g.fill(px + 1, py + 1, px + 4, py + ph - 1, e4 ? MYST : 0xFF000000 | o.get("color").getAsInt());
        g.fill(rx - 12, py + 12, rx - 11, py + ph - 12, 0x604A5366);                       // 가운데 나눔 줄
        g.pose().pushPose();
        g.pose().translate(px + 14, py + 12, 0);
        g.pose().scale(1.25f, 1.25f, 1);
        g.drawString(font, Theme.t(e4 ? "사천왕" : Theme.fit(font, o.get("title").getAsString() + " · " + o.get("type").getAsString(), (int) ((RX - 40) / 1.25f))), 0, 0, e4 ? MYST : OPEN, false);
        g.pose().popPose();
        String now = switch (st) { case "cleared" -> "클리어"; case "open" -> busy(k) ? busyBy(k) + "님이 도전 중" : "도전 가능"; default -> "잠김"; };
        String[][] rows = e4 ? new String[][]{{"?", "? ? ?"}, {"?", "? ? ?"}, {"?", "? ? ?"}}
                : new String[][]{{"관장", o.get("leader").getAsString().replace("관장 ", "")}, {"권장 레벨", "Lv. " + o.get("level").getAsInt()}, {"상태", now}};
        for (int i = 0; i < 3; i++) {
            int ry = py + 40 + i * 16;
            g.drawString(font, Theme.t(rows[i][0]), px + 14, ry, e4 ? DIM : Theme.SUBTEXT, false);
            int vc = e4 ? DIM : i == 2 ? (locked ? DIM : color(k)) : Theme.TEXT;
            g.drawString(font, Theme.t(Theme.fit(font, rows[i][1], RX - 100)), px + 84, ry, vc, false);
        }
        // 보상: 배지 그림 + 상금(+ 기믹 도구) + 물품 (사천왕은 ?)
        g.drawString(font, Theme.t("보상"), rx, py + 12, e4 ? DIM : Theme.SUBTEXT, false);
        Theme.panel(g, rx, py + 26, rx + 28, py + 54, 0xE0101319, e4 ? 0xFF3A2E4A : 0xFF4A5366);
        if (e4) g.drawCenteredString(font, Theme.t("?"), rx + 14, py + 36, 0xFF5A4A72);
        else {
            g.blit(ResourceLocation.fromNamespaceAndPath("pokeserver", "textures/item/badge_" + (k + 1) + ".png"), rx + 6, py + 32, 0, 0, 16, 16, 16, 16);
            List<String> r = new ArrayList<>();                                              // [경험사탕, 기술머신, (기믹 도구)]
            if (o.has("reward")) o.getAsJsonArray("reward").forEach(e -> r.add(e.getAsString()));
            int tx = rx + 38, tw = rw - 38;
            if (o.has("prize")) {
                String m = Theme.money(font, o.get("prize").getAsLong(), "원", tw);
                g.drawString(font, Theme.t(m), tx, py + 29, Theme.GOLD, false);
                if (r.size() > 2) g.drawString(font, Theme.t(Theme.fit(font, " + " + r.get(2), tw - font.width(Theme.t(m)))), tx + font.width(Theme.t(m)), py + 29, Theme.TEXT, false);
            }
            g.drawString(font, Theme.t(Theme.fit(font, String.join(" · ", r.subList(0, Math.min(2, r.size()))), tw)), tx, py + 43, Theme.SUBTEXT, false);
        }
        if ("cleared".equals(st)) { stamp(g, btnX() + rw / 2, btnY() + BH / 2); return; }
        long since = System.currentTimeMillis() - shakeAt;
        float shake = k == shaking && since < 400 ? (float) Math.sin(since / 22.0) * 4f * (1 - since / 400f) : 0f;   // 막혔을 때 좌우로 살짝
        float s = Theme.press(pressedAt);
        int c = locked ? LOCKED : busy(k) ? BUSY : e4 ? MYST : OPEN;
        g.pose().pushPose();
        g.pose().translate(btnX() + rw / 2f + shake, btnY() + BH / 2f, 0);
        g.pose().scale(s, s, 1);
        g.pose().translate(-rw / 2f, -BH / 2f, 0);
        g.fill(0, 0, rw, BH, locked ? 0xE0181B22 : Theme.mix(0xF0102A33, 0xF0183C48, h));
        g.renderOutline(0, 0, rw, BH, c);
        if (!locked) g.renderOutline(2, 2, rw - 4, BH - 4, (c & 0xFFFFFF) | 0x50000000);
        String b = locked ? "잠김" : busy(k) ? "도전 중" : "체육관 이동 ▶";
        g.drawCenteredString(font, Theme.t(b), rw / 2, (BH - 8) / 2, locked ? DIM : Theme.TEXT);
        g.pose().popPose();
    }

    /** 클리어 도장: 기울어진 초록 테두리 상자 + 큰 CLEARED. */
    private void stamp(GuiGraphics g, int cx, int cy) {
        g.pose().pushPose();
        g.pose().translate(cx, cy, 10);
        g.pose().mulPose(Axis.ZP.rotationDegrees(-8));
        int w = 80, hgt = 20;
        g.fill(-w / 2 - 2, -hgt / 2 - 2, w / 2 + 2, hgt / 2 + 2, 0x406CC46A);
        g.fill(-w / 2, -hgt / 2, w / 2, hgt / 2, 0xD00A1A10);
        g.renderOutline(-w / 2, -hgt / 2, w, hgt, DONE);
        g.renderOutline(-w / 2 + 2, -hgt / 2 + 2, w - 4, hgt - 4, 0xA06CC46A);
        g.pose().scale(1.4f, 1.4f, 1);
        g.drawCenteredString(font, Theme.t("CLEARED"), 0, -4, DONE);
        g.pose().popPose();
    }

    /** 다른 사람이 도전 중인 곳에 가려 하면 화면 가운데 3초 알림. */
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
        for (int k = 0; k < Math.min(9, gyms.size()); k++)
            if (onNode(mx, my, k)) { sel = k; return true; }
        if (!gyms.isEmpty() && "open".equals(status(sel)) && in(mx, my, btnX(), btnY(), btnW(), BH)) {
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
