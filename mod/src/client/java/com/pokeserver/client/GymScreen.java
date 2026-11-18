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

/** 3·4·8. 체육관 안내원 화면: 도전 가능(초록 테두리), 클리어(하늘색 테두리 + CLEARED 도장), 다른 사람이 도전 중(주황). 못 가는 곳은 서버가 안 보냄. */
public class GymScreen extends Screen {
    static final int CARD_W = 170, CARD_H = 74, GAP = 8;
    static final int OPEN = 0xFF4CC46A, CLEARED = 0xFF5CD6FF, BUSY = 0xFFF0A040;

    private final List<JsonObject> gyms = new ArrayList<>();
    private final Theme.Anim anim = new Theme.Anim();
    private int pressed = -1, shaking = -1;
    private long pressedAt, shakeAt, popupAt = -10_000;
    private String popup = "";

    public GymScreen(String json) {
        super(Component.literal("체육관 도전"));
        for (var e : JsonParser.parseString(json).getAsJsonArray()) gyms.add(e.getAsJsonObject());
    }

    private int cols() { return Math.max(1, Math.min(3, (width - 32 + GAP) / (CARD_W + GAP))); }
    private int left() { return (width - (cols() * (CARD_W + GAP) - GAP)) / 2; }
    private int cardX(int k) { return left() + (k % cols()) * (CARD_W + GAP); }
    private int cardY(int k) { return 44 + (k / cols()) * (CARD_H + GAP); }
    private String status(int k) { return gyms.get(k).get("status").getAsString(); }
    private String busyBy(int k) { return gyms.get(k).get("busy").getAsString(); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        g.fill(0, 0, width, height, Theme.PANEL);
        long badges = gyms.stream().filter(o -> o.get("n").getAsInt() <= 8 && "cleared".equals(o.get("status").getAsString())).count();
        g.fill(left(), 17, left() + 3, 29, Theme.ACCENT);
        g.drawString(font, Theme.t("체육관 도전"), left() + 8, 19, Theme.TEXT);
        g.drawString(font, Theme.t("배지 " + badges + " / 8"), left() + 14 + font.width(Theme.t("체육관 도전")), 19, Theme.GOLD);
        for (int k = 0; k < gyms.size(); k++) {
            int x = cardX(k), y = cardY(k);
            boolean hov = !"cleared".equals(status(k)) && mx >= x && mx < x + CARD_W && my >= y && my < y + CARD_H;
            card(g, gyms.get(k), k, x, y, anim.to(k, hov));
        }
        g.drawCenteredString(font, Theme.t("앞 체육관을 클리어하면 다음 체육관이 나타나요  ·  ESC: 닫기"), width / 2, height - 14, Theme.SUBTEXT);
        popup(g);
    }

    private void card(GuiGraphics g, JsonObject o, int k, int x, int y, float h) {
        boolean cleared = "cleared".equals(status(k)), busy = !cleared && !busyBy(k).isEmpty();
        int state = cleared ? CLEARED : busy ? BUSY : OPEN;
        float sc = k == pressed ? Theme.press(pressedAt) : 1f;
        long since = System.currentTimeMillis() - shakeAt;
        float shake = k == shaking && since < 400 ? (float) Math.sin(since / 22.0) * 4f * (1 - since / 400f) : 0f;   // 클릭하면 좌우로 살짝 흔들림
        g.pose().pushPose();
        g.pose().translate(x + CARD_W / 2f + shake, y + CARD_H / 2f - h, 0);
        g.pose().scale(sc, sc, 1);
        g.pose().translate(-CARD_W / 2f, -CARD_H / 2f, 0);
        Theme.panel(g, 0, 0, CARD_W, CARD_H, cleared ? 0xE0102030 : Theme.mix(Theme.TILE, Theme.TILE_HOVER, h), state);
        if (cleared) g.renderOutline(1, 1, CARD_W - 2, CARD_H - 2, 0x705CD6FF);   // 하늘색 이중 테두리
        g.fill(1, 1, 4, CARD_H - 1, 0xFF000000 | o.get("color").getAsInt());   // 배지 색 띠
        g.drawString(font, Theme.t(o.get("title").getAsString()), 10, 7, Theme.TEXT);
        g.drawString(font, Theme.t(o.get("type").getAsString() + " · " + o.get("leader").getAsString()), 10, 21, Theme.SUBTEXT);
        g.drawString(font, Theme.t(o.get("badge").getAsString() + " · 권장 레벨 " + o.get("level").getAsInt()), 10, 34, Theme.SUBTEXT);
        if (cleared) {
            g.drawString(font, Theme.t("✔ 클리어"), 10, 55, CLEARED);
            stamp(g);
        } else {
            String chip = busy ? busyBy(k) + "님이 도전 중" : "도전하기 ▶";
            int cw = font.width(Theme.t(chip)) + 10;
            g.fill(10, 52, 10 + cw, 66, state);
            g.drawString(font, Theme.t(chip), 15, 55, 0xFF101319, false);
        }
        g.pose().popPose();
    }

    /** 클리어 도장: 기울어진 하늘색 테두리 상자 + 큰 CLEARED. */
    private void stamp(GuiGraphics g) {
        g.pose().pushPose();
        g.pose().translate(CARD_W - 46, 57, 10);   // 오른쪽 아래 (글자를 가리지 않게)
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

    /** 다른 사람이 도전 중인 곳을 누르면 화면 가운데 3초 알림. */
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
        for (int k = 0; k < gyms.size(); k++) {
            int x = cardX(k), y = cardY(k);
            if (mx < x || mx >= x + CARD_W || my < y || my >= y + CARD_H || "cleared".equals(status(k))) continue;
            if (!busyBy(k).isEmpty()) {
                shaking = k;
                shakeAt = popupAt = System.currentTimeMillis();
                popup = busyBy(k) + "님이 도전 중이에요. 잠시 후 다시 도전해 주세요.";
                return true;
            }
            pressed = k;
            pressedAt = System.currentTimeMillis();
            ClientPlayNetworking.send(new Net.GymPick(gyms.get(k).get("n").getAsInt()));
            onClose();
            return true;
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
