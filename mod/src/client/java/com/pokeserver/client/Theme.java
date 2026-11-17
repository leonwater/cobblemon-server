package com.pokeserver.client;

import net.minecraft.client.gui.GuiGraphics;

/** 어두운 반투명 UI 색 (리소스팩 tools/make_ui.py 팔레트와 맞춤). */
public final class Theme {
    private Theme() {}
    public static final int PANEL = 0xD8101319;   // 바탕 (반투명)
    public static final int TILE = 0xE0222630;    // 칸
    public static final int TILE_HOVER = 0xF03A404C;
    public static final int BORDER = 0xFF5A6476;
    public static final int ACCENT = 0xFF88A0C8;
    public static final int TEXT = 0xFFFFFFFF;
    public static final int SUBTEXT = 0xFFA8B0BE;

    public static void panel(GuiGraphics g, int x1, int y1, int x2, int y2, int fill) {
        g.fill(x1, y1, x2, y2, fill);
        g.renderOutline(x1, y1, x2 - x1, y2 - y1, BORDER);
    }
}
