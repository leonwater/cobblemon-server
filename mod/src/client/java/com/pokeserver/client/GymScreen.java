package com.pokeserver.client;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.pokeserver.Net;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 3·4. 체육관 안내원 화면: 클리어한 곳(금색)과 도전 가능한 곳(초록)만 보임. 아직 못 가는 곳은 서버가 보내지 않음. */
public class GymScreen extends Screen {
    static final int CARD_W = 150, CARD_H = 64, GAP = 8;
    static final int OPEN = 0xFF4CC46A, CLEARED = Theme.GOLD, BUSY = 0xFF8A8F99;

    private final List<JsonObject> gyms = new ArrayList<>();
    private final Theme.Anim anim = new Theme.Anim();
    private int pressed = -1;
    private long pressedAt;

    public GymScreen(String json) {
        super(Component.literal("체육관 도전"));
        for (var e : JsonParser.parseString(json).getAsJsonArray()) gyms.add(e.getAsJsonObject());
    }

    private int cols() { return Math.max(1, Math.min(3, (width - 32 + GAP) / (CARD_W + GAP))); }
    private int left() { return (width - (cols() * (CARD_W + GAP) - GAP)) / 2; }
    private int cardX(int k) { return left() + (k % cols()) * (CARD_W + GAP); }
    private int cardY(int k) { return 58 + (k / cols()) * (CARD_H + GAP); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        g.fill(0, 0, width, height, Theme.PANEL);
        int badges = (int) gyms.stream().filter(o -> o.get("n").getAsInt() <= 8 && "cleared".equals(o.get("status").getAsString())).count();
        g.fill(left(), 17, left() + 3, 29, Theme.ACCENT);
        g.drawString(font, "체육관 도전", left() + 8, 19, Theme.TEXT);
        g.drawString(font, "배지 " + badges + " / 8", left() + 8 + font.width("체육관 도전") + 8, 19, Theme.GOLD);
        // 범례: 색만으로 구분하지 않도록 글자도 함께
        int lx = left();
        lx = legend(g, lx, 38, OPEN, "도전 가능");
        lx = legend(g, lx, 38, CLEARED, "클리어 (다시 도전 불가)");
        legend(g, lx, 38, BUSY, "다른 도전자 배틀 중");
        for (int k = 0; k < gyms.size(); k++) {
            int x = cardX(k), y = cardY(k);
            card(g, gyms.get(k), k, x, y, anim.to(k, clickable(k) && mx >= x && mx < x + CARD_W && my >= y && my < y + CARD_H));
        }
        g.drawCenteredString(font, "아직 갈 수 없는 체육관은 앞 체육관을 클리어하면 나타나요  ·  ESC: 닫기", width / 2, height - 14, Theme.SUBTEXT);
    }

    private int legend(GuiGraphics g, int x, int y, int color, String label) {
        g.fill(x, y + 1, x + 7, y + 8, color);
        g.drawString(font, label, x + 11, y, Theme.SUBTEXT);
        return x + 11 + font.width(label) + 14;
    }

    private boolean clickable(int k) { return "open".equals(gyms.get(k).get("status").getAsString()); }

    private void card(GuiGraphics g, JsonObject o, int k, int x, int y, float h) {
        boolean cleared = "cleared".equals(o.get("status").getAsString()), busy = !cleared && o.get("busy").getAsBoolean();
        int state = cleared ? CLEARED : busy ? BUSY : OPEN;
        float sc = k == pressed ? Theme.press(pressedAt) : 1f;
        g.pose().pushPose();
        g.pose().translate(x + CARD_W / 2f, y + CARD_H / 2f - h, 0);
        g.pose().scale(sc, sc, 1);
        g.pose().translate(-CARD_W / 2f, -CARD_H / 2f, 0);
        int fill = cleared ? 0xE02A2614 : Theme.mix(Theme.TILE, Theme.TILE_HOVER, h);
        Theme.panel(g, 0, 0, CARD_W, CARD_H, fill, Theme.mix(state, Theme.TEXT, h * 0.5f));
        g.fill(1, 1, 4, CARD_H - 1, 0xFF000000 | o.get("color").getAsInt());   // 배지 색 띠
        g.drawString(font, o.get("title").getAsString(), 10, 7, Theme.TEXT);
        g.drawString(font, o.get("type").getAsString() + " · " + o.get("leader").getAsString(), 10, 20, Theme.SUBTEXT);
        g.drawString(font, o.get("badge").getAsString() + " · 최고 Lv" + o.get("level").getAsInt(), 10, 32, Theme.SUBTEXT);
        String chip = cleared ? "클리어 ✔" : busy ? "배틀 중 · 잠시 후" : "도전하기 ▶";
        int cw = font.width(chip) + 10;
        g.fill(10, 45, 10 + cw, 57, state);
        g.drawString(font, chip, 15, 47, cleared || !busy ? 0xFF101319 : Theme.TEXT, false);
        g.pose().popPose();
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        for (int k = 0; k < gyms.size(); k++) {
            int x = cardX(k), y = cardY(k);
            if (clickable(k) && mx >= x && mx < x + CARD_W && my >= y && my < y + CARD_H) {
                pressed = k;
                pressedAt = System.currentTimeMillis();
                ClientPlayNetworking.send(new Net.GymPick(gyms.get(k).get("n").getAsInt()));
                onClose();
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
