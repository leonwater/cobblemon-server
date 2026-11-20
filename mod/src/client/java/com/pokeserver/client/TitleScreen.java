package com.pokeserver.client;

import com.pokeserver.Net;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 7. 별명 고르기 (G 메뉴 → 간편 메뉴 → 별명): 3칸씩, 얻은 별명을 누르면 그 별명으로 보임. 얻는 조건은 마우스를 올리면 말풍선으로. */
public class TitleScreen extends Screen {
    record Row(String id, String name, String how, boolean has, boolean on) {}

    private final List<Row> rows = new ArrayList<>();
    private final Theme.Anim anim = new Theme.Anim();
    private float k = 1;

    public TitleScreen(String data) {
        super(Component.literal("별명"));
        for (String line : data.split("\n")) {
            String[] f = line.split("\t");
            if (f.length == 5) rows.add(new Row(f[0], f[1], f[2], f[3].equals("1"), f[4].equals("1")));
        }
    }

    @Override
    protected void init() {
        k = Math.min(1f, Math.min(width / 640f, height / 360f));
        width = Math.round(width / k);
        height = Math.round(height / k);
    }

    static final int COLS = 3, CW = 168, CH = 22, GAP = 6;
    private int px() { return (width - (COLS * CW + (COLS - 1) * GAP + 24)) / 2; }
    private int py() { return (height - (40 + ((rows.size() + COLS - 1) / COLS) * (CH + GAP) + 12)) / 2; }
    private int cx(int i) { return px() + 12 + (i % COLS) * (CW + GAP); }
    private int cy(int i) { return py() + 40 + (i / COLS) * (CH + GAP); }

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
        int x = px(), y = py(), w = COLS * CW + (COLS - 1) * GAP + 24, h = 40 + ((rows.size() + COLS - 1) / COLS) * (CH + GAP) + 12;
        Theme.panel(g, x, y, x + w, y + h, Theme.PANEL, Theme.BORDER);
        g.fill(x + 12, y + 12, x + 15, y + 26, Theme.ACCENT);
        g.drawString(font, Theme.t("별명"), x + 20, y + 15, Theme.TEXT, false);
        g.drawString(font, Theme.t("얻은 별명을 누르면 이름 앞에 보여요 · 마우스를 올리면 얻는 조건"), x + 20 + font.width(Theme.t("별명")) + 10, y + 15, Theme.SUBTEXT, false);
        int over = -1;
        for (int i = 0; i < rows.size(); i++) {
            card(g, i, mx, my);
            if (mx >= cx(i) && mx < cx(i) + CW && my >= cy(i) && my < cy(i) + CH) over = i;
        }
        if (over >= 0) tip(g, rows.get(over), mx, my);
    }

    /** 얻는 조건 말풍선: 마우스 옆, 화면 밖으로 안 나가게. 마우스가 칸을 벗어나면 다음 그림에서 바로 사라짐. */
    private void tip(GuiGraphics g, Row r, int mx, int my) {
        String a = "얻는 조건: " + r.how(), b = r.id().equals("none") ? "" : r.has() ? "얻었어요" : "아직 못 얻었어요";
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
        int fill = r.on() ? Theme.SELECT : r.has() ? Theme.mix(Theme.TILE, Theme.TILE_HOVER, h) : 0xA0181B22;
        Theme.panel(g, x, y, x + CW, y + CH, fill, r.on() ? Theme.ACCENT : Theme.mix(0xFF2A303C, Theme.BORDER, h));
        String tag = r.on() ? "사용 중" : r.has() ? "" : "잠김";
        int tagW = tag.isEmpty() ? 0 : font.width(Theme.t(tag)) + 6;
        g.drawString(font, Theme.t(Theme.fit(font, r.name(), CW - 14 - tagW)), x + 7, y + 7, r.has() ? Theme.TEXT : 0xFF6A7080, false);
        if (!tag.isEmpty()) g.drawString(font, Theme.t(tag), x + CW - tagW - 1, y + 7, r.on() ? Theme.GOLD : 0xFF6A7080, false);
        if (!r.has()) g.fill(x + 1, y + 1, x + CW - 1, y + CH - 1, 0x40101319);
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
