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

    /** 돈 표시: 너비 w 안에 "1,234,567원"이 안 들어가면 "123.4억원"처럼 줄이고, 그래도 길면 "…" (큰 금액에도 UI가 깨지지 않게). */
    public static String money(Font f, long n, String unit, int w) {
        String full = String.format("%,d", n) + unit;
        if (f.width(t(full)) <= w) return full;
        double a = Math.abs((double) n);
        String c = a >= 1e16 ? String.format("%,.0f경", n / 1e16) : a >= 1e12 ? String.format("%.1f조", n / 1e12)
                : a >= 1e8 ? String.format("%.1f억", n / 1e8) : String.format("%.1f만", n / 1e4);
        return fit(f, c + unit, w);
    }

    /** 줄바꿈: 단어 사이(띄어쓰기)에서만 끊음. 문장 끝(. ! ?)에서 끊어도 maxLines 안에 들고, 마지막 줄을 뺀 줄 길이가 비슷하면 문장 끝을 우선.
     *  §색 코드가 줄을 넘어가면 다음 줄 앞에 다시 붙임. 그리기는 Theme.t(줄). */
    public static java.util.List<String> wrap(Font f, String s, int w, int maxLines) {
        var bySentence = new java.util.ArrayList<String>();
        for (String sentence : s.split("(?<=[.!?])\\s+")) bySentence.addAll(words(f, sentence, w));
        var lines = bySentence.size() <= maxLines && similar(f, bySentence) ? bySentence : words(f, s, w);
        String code = "";
        for (int i = 0; i < lines.size(); i++) {
            String line = code + lines.get(i);
            lines.set(i, line);
            for (int k = line.indexOf('§'); k >= 0 && k + 1 < line.length(); k = line.indexOf('§', k + 1))
                code = line.charAt(k + 1) == 'r' ? "" : "§" + line.charAt(k + 1);
        }
        return lines;
    }

    /** 단어 단위로 채움. 한 단어가 줄보다 길 때만 글자 단위로 자름. */
    static java.util.List<String> words(Font f, String s, int w) {
        var out = new java.util.ArrayList<String>();
        String line = "";
        for (String word : s.trim().split(" +")) {
            String next = line.isEmpty() ? word : line + " " + word;
            if (f.width(t(next)) <= w) { line = next; continue; }
            if (!line.isEmpty()) out.add(line);
            line = word;
            while (f.width(t(line)) > w && line.length() > 1) {
                int k = line.length() - 1;
                while (k > 1 && f.width(t(line.substring(0, k))) > w) k--;
                out.add(line.substring(0, k));
                line = line.substring(k);
            }
        }
        if (!line.isEmpty()) out.add(line);
        return out;
    }

    /** 마지막 줄을 뺀 줄들의 길이가 비슷한지 (가장 짧은 줄 ≥ 가장 긴 줄의 70%). */
    static boolean similar(Font f, java.util.List<String> lines) {
        if (lines.size() <= 2) return true;
        int min = Integer.MAX_VALUE, max = 0;
        for (String l : lines.subList(0, lines.size() - 1)) { int x = f.width(t(l)); min = Math.min(min, x); max = Math.max(max, x); }
        return min >= max * 0.7;
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
