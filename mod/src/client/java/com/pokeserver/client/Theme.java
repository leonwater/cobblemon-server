package com.pokeserver.client;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.gui.GuiGraphics;

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
