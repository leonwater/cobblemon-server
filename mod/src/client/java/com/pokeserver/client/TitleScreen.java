package com.pokeserver.client;

import com.pokeserver.Net;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 7. 칭호 고르기 (G 메뉴 → 간편 메뉴 → 칭호): 5칸씩, 비슷한 칭호(같은 갈래)는 같은 줄에서 시작, 얻은 칭호를 누르면 그 칭호로 보임. 얻는 조건은 마우스를 올리면 말풍선으로. */
public class TitleScreen extends Screen {
    record Row(String id, String name, String how, boolean has, boolean on, int group) {}

    private final List<Row> rows = new ArrayList<>();
    private final List<Integer> col = new ArrayList<>(), line = new ArrayList<>();
    private int lines;
    private final Theme.Anim anim = new Theme.Anim();
    private float k = 1;

    public TitleScreen(String data) {
        super(Component.literal("칭호"));
        for (String line : data.split("\n")) {
            String[] f = line.split("\t");
            if (f.length >= 5) rows.add(new Row(f[0], f[1], f[2], f[3].equals("1"), f[4].equals("1"), f.length > 5 ? Integer.parseInt(f[5]) : 0));
        }
        // 갈래가 바뀌면 새 줄
        int c = 0, r = 0;
        for (int i = 0; i < rows.size(); i++) {
            if (i > 0 && (c == COLS || rows.get(i).group() != rows.get(i - 1).group())) { c = 0; r++; }
            col.add(c++); line.add(r);
        }
        lines = rows.isEmpty() ? 0 : r + 1;
    }

    @Override
    protected void init() {
        k = Math.min(1f, Math.min(width / 640f, height / 360f));
        width = Math.round(width / k);
        height = Math.round(height / k);
    }

    static final int COLS = 5, CW = 116, CH = 20, GAP = 5;   // 640×360 안에 39개 + 갈래별 줄바꿈(12줄)
    private int px() { return (width - (COLS * CW + (COLS - 1) * GAP + 24)) / 2; }
    private int py() { return (height - (40 + lines * (CH + GAP) + 12)) / 2; }
    private int cx(int i) { return px() + 12 + col.get(i) * (CW + GAP); }
    private int cy(int i) { return py() + 40 + line.get(i) * (CH + GAP); }

    @Override
    public void render(GuiGraphics g, int mx, int my, float pt) {
        g.pose().pushPose();
        g.pose().scale(k, k, 1);
        super.render(g, Math.round(mx / k), Math.round(my / k), pt);
        g.pose().popPose();
    }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        g.fillGradient(0, 0, width, height, 0x90000000, 0x70000000);
        int x = px(), y = py(), w = COLS * CW + (COLS - 1) * GAP + 24, h = 40 + lines * (CH + GAP) + 12;
        Theme.panel(g, x, y, x + w, y + h, Theme.PANEL, Theme.BORDER);
        g.fill(x + 12, y + 12, x + 15, y + 26, Theme.ACCENT);
        g.drawString(font, Theme.t("칭호"), x + 20, y + 15, Theme.TEXT, false);
        int sx = x + 20 + font.width(Theme.t("칭호")) + 10;
        g.drawString(font, Theme.t(Theme.fit(font, "눌러서 고르기 · 마우스를 올리면 힌트", x + w - 12 - sx)), sx, y + 15, Theme.SUBTEXT, false);
        int over = -1;
        for (int i = 0; i < rows.size(); i++) {
            card(g, i, mx, my);
            if (mx >= cx(i) && mx < cx(i) + CW && my >= cy(i) && my < cy(i) + CH) over = i;
        }
        if (over >= 0) tip(g, rows.get(over), mx, my);
    }

    /** 힌트 말풍선 (정확한 수치는 안 보여 줌): 마우스 옆, 화면 밖으로 안 나가게. 마우스가 칸을 벗어나면 다음 그림에서 바로 사라짐. */
    private void tip(GuiGraphics g, Row r, int mx, int my) {
        String a = r.how(), b = r.id().equals("none") ? "" : r.has() ? "얻었어요" : "아직 못 얻었어요";
        int w = Math.max(font.width(Theme.t(a)), font.width(Theme.t(b))) + 12, h = b.isEmpty() ? 18 : 30;
        int x = Math.min(mx + 10, width - w - 4), y = Math.min(my + 10, height - h - 4);
        g.pose().pushPose();
        g.pose().translate(0, 0, 400);   // 다른 칸보다 위에
        Theme.panel(g, x, y, x + w, y + h, 0xF0101319, Theme.ACCENT);
        g.drawString(font, Theme.t(a), x + 6, y + 5, Theme.TEXT, false);
        if (!b.isEmpty()) g.drawString(font, Theme.t(b), x + 6, y + 17, r.has() ? Theme.GOLD : Theme.SUBTEXT, false);
        g.pose().popPose();
    }

    private void card(GuiGraphics g, int i, int mx, int my) {
        Row r = rows.get(i);
        int x = cx(i), y = cy(i);
        boolean hov = r.has() && mx >= x && mx < x + CW && my >= y && my < y + CH;
        float h = anim.to(i, hov);
        if (r.has()) {   // 가진 칭호: 밝은 칸 + 칭호 색
            Theme.panel(g, x, y, x + CW, y + CH, r.on() ? Theme.SELECT : Theme.mix(0xE02A303B, 0xF03A4252, h), r.on() ? Theme.ACCENT : Theme.mix(0xFF4A5366, Theme.ACCENT, h));
            String tag = r.on() ? "사용 중" : "";
            int tagW = tag.isEmpty() ? 0 : font.width(Theme.t(tag)) + 6;
            label(g, r.name(), x + 6, y + 6, CW - 12 - tagW, Theme.TEXT);
            if (!tag.isEmpty()) g.drawString(font, Theme.t(tag), x + CW - tagW - 1, y + 6, Theme.GOLD, false);
        } else {         // 없는 칭호: 어두운 칸 + 회색 글자 (색 없이)
            Theme.panel(g, x, y, x + CW, y + CH, 0x80101319, 0xFF23272F);
            String plain = net.minecraft.ChatFormatting.stripFormatting(r.name());
            label(g, plain, x + 6, y + 6, CW - 12, 0xFF5A5F69);
        }
    }

    /** 칸보다 긴 이름은 잘라 내지 않고 살짝 줄여서 다 보이게 (최소 0.8배, 그보다 길면 …). */
    private void label(GuiGraphics g, String s, int x, int y, int w, int color) {
        var t = Theme.t(s);
        float k = Math.max(0.8f, Math.min(1f, w / (float) font.width(t)));
        if (k >= 1f) { g.drawString(font, t, x, y, color, false); return; }
        g.pose().pushPose();
        g.pose().translate(x, y + (1 - k) * 4, 0);
        g.pose().scale(k, k, 1);
        g.drawString(font, Theme.t(Theme.fit(font, s, Math.round(w / k))), 0, 0, color, false);
        g.pose().popPose();
    }

    @Override
    public boolean mouseClicked(double rmx, double rmy, int button) {
        double mx = rmx / k, my = rmy / k;
        for (int i = 0; i < rows.size(); i++) {
            Row r = rows.get(i);
            if (r.has() && !r.on() && mx >= cx(i) && mx < cx(i) + CW && my >= cy(i) && my < cy(i) + CH) {
                ClientPlayNetworking.send(new Net.MenuAction("title:" + r.id()));   // 서버가 바뀐 목록을 다시 보냄
                return true;
            }
        }
        return super.mouseClicked(rmx, rmy, button);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
