package com.pokeserver.client;

import com.pokeserver.Net;
import com.pokeserver.Shop;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/** 4. 상점 화면: 왼쪽 분류, 위 구매/판매 탭·검색·잔액, 가운데 카드 격자. */
public class ShopScreen extends Screen {
    static final int SIDE = 120, CARD_W = 84, CARD_H = 96, GAP = 6, TOP = 44;
    static final int RED = 0xFFC8323C, GREEN = 0xFF3C9650, GOLD = 0xFFF0C040;

    private final Shop.Data data;
    static long balance;
    int category;
    boolean sell;
    private double scroll;
    private EditBox search;
    private final List<int[]> shown = new ArrayList<>();   // {카테고리, 항목}

    public ShopScreen(String json, long balance) {
        super(Component.literal("상점"));
        this.data = Shop.parse(json);
        ShopScreen.balance = balance;
    }

    @Override
    protected void init() {
        search = new EditBox(font, width - 16 - 130, 12, 130, 16, Component.literal("검색"));
        search.setHint(Component.literal("아이템 이름 검색").withColor(Theme.SUBTEXT));
        search.setResponder(s -> refilter());
        addRenderableWidget(search);
        refilter();
    }

    void refilter() {
        shown.clear();
        scroll = 0;
        String q = search == null ? "" : search.getValue().trim();
        for (int c = 0; c < data.categories().size(); c++) {
            if (q.isEmpty() && c != category) continue;   // 검색어가 있으면 모든 분류에서 찾음
            var items = data.categories().get(c).items();
            for (int i = 0; i < items.size(); i++) {
                var e = items.get(i);
                if ((sell ? e.sell() : e.buy()) <= 0 || Shop.stack(e.item()).isEmpty()) continue;  // 없는 아이템 ID는 숨김
                if (!q.isEmpty() && !Shop.stack(e.item()).getHoverName().getString().contains(q)) continue;
                shown.add(new int[]{c, i});
            }
        }
    }

    private int cols() { return Math.max(1, (width - SIDE - 32 + GAP) / (CARD_W + GAP)); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        super.renderBackground(g, mx, my, pt);
        g.fill(0, 0, width, height, Theme.PANEL);
        // 왼쪽 분류
        g.fill(0, 0, SIDE, height, 0xC0080A0E);
        g.fill(12, 12, 15, 28, Theme.ACCENT);
        g.drawString(font, "상점", 20, 16, Theme.TEXT);
        for (int c = 0; c < data.categories().size(); c++) {
            int y = TOP + c * 26;
            boolean sel = c == category, hov = mx < SIDE && my >= y && my < y + 22;
            if (sel || hov) Theme.panel(g, 6, y, SIDE - 6, y + 22, sel ? Theme.TILE_HOVER : Theme.TILE);
            if (sel) g.fill(6, y, 9, y + 22, Theme.ACCENT);
            var cat = data.categories().get(c);
            g.renderItem(Shop.stack(cat.icon()), 14, y + 3);
            g.drawString(font, cat.name(), 36, y + 7, sel ? Theme.TEXT : Theme.SUBTEXT);
        }
        // 구매/판매 탭
        int tx = SIDE + 16;
        Theme.panel(g, tx, 12, tx + 120, 28, 0xE0181B22);
        g.fill(sell ? tx + 60 : tx, 12, sell ? tx + 120 : tx + 60, 28, Theme.TILE_HOVER);
        g.drawCenteredString(font, "구매", tx + 30, 16, sell ? Theme.SUBTEXT : Theme.TEXT);
        g.drawCenteredString(font, "판매", tx + 90, 16, sell ? Theme.TEXT : Theme.SUBTEXT);
        // 잔액
        String bal = String.format("%,d", balance);
        int bw = font.width(bal) + 34, bx = width - 16 - 130 - 10 - bw;
        Theme.panel(g, bx, 12, bx + bw, 28, 0xE0181B22);
        g.renderItem(new ItemStack(Items.GOLD_NUGGET), bx + 4, 12);
        g.drawString(font, bal, bx + 26, 16, GOLD);
        // 카드
        int x0 = SIDE + 16, y0 = TOP, cols = cols();
        g.enableScissor(SIDE, y0, width, height - 18);
        for (int k = 0; k < shown.size(); k++) {
            int x = x0 + (k % cols) * (CARD_W + GAP), y = y0 + (k / cols) * (CARD_H + GAP) - (int) scroll;
            if (y > height || y + CARD_H < y0) continue;
            card(g, shown.get(k), x, y, mx >= x && mx < x + CARD_W && my >= y && my < y + CARD_H && my >= y0);
        }
        g.disableScissor();
        if (shown.isEmpty()) g.drawCenteredString(font, sell ? "판매할 수 있는 상품이 없습니다" : "상품이 없습니다", (SIDE + width) / 2, height / 2, Theme.SUBTEXT);
        g.drawCenteredString(font, "클릭: 1개  ·  Shift+클릭: 16개  ·  ESC: 닫기", (SIDE + width) / 2, height - 13, Theme.SUBTEXT);
    }

    private void card(GuiGraphics g, int[] ref, int x, int y, boolean hover) {
        var e = data.categories().get(ref[0]).items().get(ref[1]);
        ItemStack st = Shop.stack(e.item());
        long price = sell ? e.sell() : e.buy();
        Theme.panel(g, x, y, x + CARD_W, y + CARD_H, hover ? Theme.TILE_HOVER : Theme.TILE);
        g.fill(x + 4, y + 4, x + CARD_W - 4, y + 44, 0x40FFFFFF);
        g.pose().pushPose();
        g.pose().translate(x + CARD_W / 2f - 16, y + 8, 0);
        g.pose().scale(2, 2, 1);
        g.renderItem(st, 0, 0);
        g.pose().popPose();
        g.drawString(font, "x1", x + CARD_W - 16, y + 34, Theme.SUBTEXT);
        String name = font.plainSubstrByWidth(st.getHoverName().getString(), CARD_W - 6);
        g.drawCenteredString(font, name, x + CARD_W / 2, y + 48, Theme.TEXT);
        // 상태 띠: 판매 탭은 보유 수량, 구매 탭은 잔액 부족만 표시
        var player = minecraft == null ? null : minecraft.player;
        int have = player == null ? 0 : Shop.count(player, e.item());
        String badge = sell ? (have == 0 ? "보유 아이템 없음" : "보유 " + have + "개") : (balance < price ? "잔액 부족" : null);
        if (badge != null) {
            g.fill(x + 3, y + 59, x + CARD_W - 3, y + 70, sell && have > 0 ? GREEN : RED);
            float k = Math.min(1f, (CARD_W - 8f) / font.width(badge));   // 길면 줄여서 다 보이게
            g.pose().pushPose();
            g.pose().translate(x + CARD_W / 2f, y + 65 - 4 * k, 0);
            g.pose().scale(k, k, 1);
            g.drawCenteredString(font, badge, 0, 0, Theme.TEXT);
            g.pose().popPose();
        }
        g.drawCenteredString(font, sell ? "판매" : "구매", x + CARD_W / 2, y + 73, Theme.SUBTEXT);
        g.drawCenteredString(font, String.format("%,d", price), x + CARD_W / 2, y + 84, GOLD);
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (super.mouseClicked(mx, my, button)) return true;
        int tx = SIDE + 16;
        if (my >= 12 && my < 28 && mx >= tx && mx < tx + 120) {
            sell = mx >= tx + 60;
            refilter();
            return true;
        }
        if (mx < SIDE) {
            int c = (int) ((my - TOP) / 26);
            if (my >= TOP && c < data.categories().size()) { category = c; search.setValue(""); refilter(); }
            return true;
        }
        int cols = cols(), x0 = SIDE + 16;
        for (int k = 0; k < shown.size(); k++) {
            int x = x0 + (k % cols) * (CARD_W + GAP), y = TOP + (k / cols) * (CARD_H + GAP) - (int) scroll;
            if (mx >= x && mx < x + CARD_W && my >= y && my < y + CARD_H && my >= TOP) {
                int[] r = shown.get(k);
                ClientPlayNetworking.send(new Net.ShopTrade(sell, r[0], r[1], hasShiftDown() ? 16 : 1));
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double sx, double sy) {
        int rows = (shown.size() + cols() - 1) / cols();
        double max = Math.max(0, rows * (CARD_H + GAP) - (height - TOP - 24));
        scroll = Math.max(0, Math.min(max, scroll - sy * 24));
        return true;
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
