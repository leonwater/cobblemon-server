package com.pokeserver.client;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

/** 어두운 반투명 UI 색·패널·짧은 상태 애니메이션 (마우스 올림 120ms, 누름 100ms). */
public final class Theme {
    private Theme() {}
    public static final int PANEL = 0xD8101319;   // 바탕 (반투명)
    public static final int TILE = 0xE0222630;    // 칸
    public static final int TILE_HOVER = 0xF0343A47;
    public static final int BORDER = 0xFF4A5366;
    public static final int ACCENT = 0xFF88A0C8;
    public static final int SELECT = 0xE02E4A7A;
    public static final int TEXT = 0xFFFFFFFF;
    public static final int SUBTEXT = 0xFFA8B0BE;
    public static final int GOLD = 0xFFF0C040;
    public static final int SHADOW = 0x70000000;
    /** 갈무리9: 닌텐도 DS 글꼴에서 영감을 받은 한글 픽셀 글꼴 (SIL OFL). 없는 글자는 기본 글꼴로. */
    public static final ResourceLocation FONT = ResourceLocation.fromNamespaceAndPath("pokeserver", "galmuri");

    /** 우리 화면의 글자는 모두 이 글꼴로. */
    public static Component t(String s) {
        return Component.literal(s).withStyle(st -> st.withFont(FONT));
    }

    /** 너비 w에 맞게 뒤를 자르고 잘렸으면 "…"를 붙임 (글자가 칸 밖으로 나가지 않게). */
    public static String fit(Font f, String s, int w) {
        if (f.width(t(s)) <= w) return s;
        while (!s.isEmpty() && f.width(t(s + "…")) > w) s = s.substring(0, s.length() - 1);
        return s + "…";
    }

    // ── 둥근 카드 스타일 (ui-ux-pro-max 클레이모피즘의 구조: 둥근 모서리·굵은 테두리·이중 그림자) — 색은 기존 어두운 반투명 계열 ──
    public static final int C_PRIMARY = SELECT, C_SECONDARY = 0xFF9B86D6, C_ACCENT = GOLD;
    public static final int C_BG = PANEL, C_CARD = TILE, C_MUTED = 0xD0181B22, C_BORDER = BORDER;
    public static final int C_TEXT = TEXT, C_SUB = SUBTEXT, C_TRACK = 0xFF3A4152;

    /** 둥근 사각형 채우기 (모서리 r픽셀을 계단처럼 깎음). */
    public static void round(GuiGraphics g, int x1, int y1, int x2, int y2, int r, int color) {
        for (int i = 0; i < r; i++) {
            int inset = r - (int) Math.round(Math.sqrt(r * r - (r - i - 0.5) * (r - i - 0.5)));
            g.fill(x1 + inset, y1 + i, x2 - inset, y1 + i + 1, color);
            g.fill(x1 + inset, y2 - i - 1, x2 - inset, y2 - i, color);
        }
        g.fill(x1, y1 + r, x2, y2 - r, color);
    }

    /** 클레이 카드: 아래 그림자 + 테두리 + 몸통 + 위 하이라이트 + 아래 음영. */
    public static void clay(GuiGraphics g, int x1, int y1, int x2, int y2, int fill, int border) {
        round(g, x1 + 1, y1 + 3, x2 + 1, y2 + 3, 5, SHADOW);
        round(g, x1, y1, x2, y2, 5, border);
        round(g, x1 + 2, y1 + 2, x2 - 2, y2 - 2, 4, fill);
        g.fill(x1 + 6, y1 + 3, x2 - 6, y1 + 4, mix(fill, 0xFFFFFFFF, 0.10f));   // 위쪽 은은한 하이라이트
        g.fill(x1 + 6, y2 - 4, x2 - 6, y2 - 3, mix(fill, 0xFF000000, 0.25f));
    }


    /** 모서리 1픽셀을 깎은 패널 + 아래쪽 그림자. */
    public static void panel(GuiGraphics g, int x1, int y1, int x2, int y2, int fill) {
        panel(g, x1, y1, x2, y2, fill, BORDER);
    }

    public static void panel(GuiGraphics g, int x1, int y1, int x2, int y2, int fill, int border) {
        g.fill(x1 + 1, y2, x2 + 1, y2 + 2, SHADOW);
        g.fill(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill);
        g.hLine(x1 + 1, x2 - 2, y1, border);
        g.hLine(x1 + 1, x2 - 2, y2 - 1, border);
        g.vLine(x1, y1, y2 - 1, border);
        g.vLine(x2 - 1, y1, y2 - 1, border);
    }

    /** ARGB 색 섞기 (t=0 → a, t=1 → b). */
    public static int mix(int a, int b, float t) {
        int r = 0;
        for (int s = 0; s < 32; s += 8) {
            int ca = a >>> s & 0xFF, cb = b >>> s & 0xFF;
            r |= Math.round(ca + (cb - ca) * t) << s;
        }
        return r;
    }

    /** 키별로 0↔1 사이를 부드럽게 따라가는 값 (빠르게 시작해 감속, 약 120ms에 90%). */
    public static final class Anim {
        private final Map<Object, Float> values = new HashMap<>();
        private long last = System.nanoTime();
        private float dt;

        public void frame() {
            long now = System.nanoTime();
            dt = Math.min(0.1f, (now - last) / 1e9f);
            last = now;
        }

        public float to(Object key, boolean on) {
            float v = values.getOrDefault(key, 0f);
            v += ((on ? 1f : 0f) - v) * (1f - (float) Math.exp(-dt / 0.05f));
            values.put(key, v);
            return v;
        }
    }

    /** 누른 직후 100ms 동안 0.97배로 살짝 눌림. */
    public static float press(long pressedAt) {
        return System.currentTimeMillis() - pressedAt < 100 ? 0.97f : 1f;
    }
}
