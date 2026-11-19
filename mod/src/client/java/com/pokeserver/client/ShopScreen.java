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
    static final int SIDE = 128, CARD_H = 98, GAP = 8, TOP = 52;
    static final int RED = 0xFFC8323C, GREEN = 0xFF3C9650;

    private final Shop.Data data;
    static long balance;
    private long shownBalance = -1, balanceChangedAt;
    static int category;      // 다시 열려도(땅 문서 가격 갱신 등) 보던 분류·탭 유지
    static boolean sell;
    private double scroll;
    private EditBox search;
    private final List<int[]> shown = new ArrayList<>();   // {카테고리, 항목}
    private final Theme.Anim anim = new Theme.Anim();
    private int pressedKey = -1, hoverKey = -1;
    // 2. 수량 선택 창: 카드를 누르면 열리고, 확인을 눌러야 거래
    private int[] modal;
    private boolean modalSell;
    private int qty = 1;
    static final int MW = 230, MH = 152;
    static final int[] PRESETS = {1, 8, 16, 32, 64};
    private long pressedAt, hoverSince, lastTooltip;

    private final int badges;

    public ShopScreen(String json, long balance, int badges) {
        super(Component.literal("상점"));
        this.data = Shop.parse(json);
        this.badges = badges;
        if (category >= data.categories().size()) category = 0;
        ShopScreen.balance = balance;
    }

    /** 화면(GUI)이 640×360보다 작으면 전체를 줄여 그림 → GUI 크기 4(전체 화면)에서도 분류·안내 글이 잘리지 않음. */
    private float k = 1;

    @Override
    protected void init() {
        k = Math.min(1f, Math.min(width / 640f, height / 360f));
        width = Math.round(width / k);
        height = Math.round(height / k);
        search = new EditBox(font, width - 16 - 130, 14, 130, 16, Component.literal("검색"));
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
                if (!sell && e.badges() > badges) continue;   // 배지를 더 모으면 풀리는 상품
                if (!q.isEmpty() && !Shop.stack(e.item()).getHoverName().getString().contains(q)) continue;
                shown.add(new int[]{c, i});
            }
        }
    }

    private int cols() { return 5; }   // 가로 5칸 고정: 화면이 좁으면 카드 폭을 줄임
    private int cardW() { return Math.max(44, Math.min(84, (width - SIDE - 32 + GAP) / 5 - GAP)); }
    private int cardX(int k) { return SIDE + 16 + (k % cols()) * (cardW() + GAP); }
    private int cardY(int k) { return TOP + 14 + (k / cols()) * (CARD_H + GAP) - (int) scroll; }

    @Override
    public void render(GuiGraphics g, int mx, int my, float pt) {
        g.pose().pushPose();
        g.pose().scale(k, k, 1);
        super.render(g, Math.round(mx / k), Math.round(my / k), pt);
        g.pose().popPose();
    }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        super.renderBackground(g, mx, my, pt);
        anim.frame();
        if (shownBalance != balance) { if (shownBalance >= 0) balanceChangedAt = System.currentTimeMillis(); shownBalance = balance; }
        g.fill(0, 0, width, height, Theme.PANEL);
        sidebar(g, mx, my);
        topBar(g, mx, my);
        // 분류 제목 (위계: 제목 흰색, 개수 회색)
        String title = search.getValue().isBlank() ? data.categories().get(category).name() : "검색 결과";
        g.drawString(font, Theme.t(title), SIDE + 16, TOP, Theme.TEXT);
        g.drawString(font, Theme.t(shown.size() + "개"), SIDE + 22 + font.width(Theme.t(title)), TOP, Theme.SUBTEXT);
        // 카드
        int hovered = -1;
        g.enableScissor(Math.round(SIDE * k), Math.round((TOP + 10) * k), Math.round(width * k), Math.round((height - 20) * k));   // 가위 영역은 화면 축소(k)를 따르지 않아 직접 곱함
        for (int k = 0; k < shown.size(); k++) {
            int x = cardX(k), y = cardY(k);
            boolean hov = mx >= x && mx < x + cardW() && my >= y && my < y + CARD_H && my >= TOP + 10 && my < height - 20;
            if (hov) hovered = k;
            float h = anim.to(k, hov);
            if (y > height || y + CARD_H < TOP) continue;
            card(g, shown.get(k), k, x, y, h);
        }
        g.disableScissor();
        if (shown.isEmpty()) g.drawCenteredString(font, Theme.t(sell ? "판매할 수 있는 상품이 없습니다" : "상품이 없습니다"), (SIDE + width) / 2, height / 2, Theme.SUBTEXT);
        g.drawCenteredString(font, Theme.t(Theme.fit(font, (sell ? "" : "배지 " + badges + "개 · 배지를 모으면 상품이 늘어나요  ·  ") + "클릭: 수량 고르기  ·  ESC: 닫기", width - SIDE - 16)),
                (SIDE + width) / 2, height - 13, Theme.SUBTEXT);
        if (modal == null) tooltip(g, hovered, mx, my);
        else modal(g, mx, my);
    }

    private Shop.Entry modalEntry() { return data.categories().get(modal[0]).items().get(modal[1]); }
    private long unit() { return modalSell ? modalEntry().sell() : modalEntry().buy(); }

    /** 고를 수 있는 최대 수량: 구매는 잔액·64개, 판매는 보유 수량·64개. 땅 문서는 살 때마다 값이 올라 1장씩. */
    private int maxQty() {
        if (modalSell) return Math.min(64, minecraft == null || minecraft.player == null ? 0 : Shop.count(minecraft.player, modalEntry().item()));
        if ("pokeserver:farm_deed".equals(modalEntry().item())) return balance >= unit() ? 1 : 0;
        return (int) Math.min(64, balance / Math.max(1, unit()));
    }

    private int mx0() { return (width - MW) / 2; }
    private int my0() { return (height - MH) / 2; }

    private void modal(GuiGraphics g, int mx, int my) {
        g.pose().pushPose();
        g.pose().translate(0, 0, 400);
        g.fill(0, 0, width, height, 0xA0000000);
        int x = mx0(), y = my0(), max = maxQty();
        qty = Math.max(max == 0 ? 0 : 1, Math.min(qty, max));
        Theme.panel(g, x, y, x + MW, y + MH, 0xF8181B22, Theme.ACCENT);
        ItemStack st = Shop.stack(modalEntry().item());
        g.pose().pushPose();
        g.pose().translate(x + 12, y + 10, 0);
        g.pose().scale(1.5f, 1.5f, 1);
        g.renderItem(st, 0, 0);
        g.pose().popPose();
        String verb = modalSell ? "판매" : "구매";
        int chipW = font.width(Theme.t(verb)) + 10;
        g.fill(x + MW - 12 - chipW, y + 12, x + MW - 12, y + 24, modalSell ? GREEN : Theme.SELECT);
        g.drawString(font, Theme.t(verb), x + MW - 7 - chipW, y + 14, Theme.TEXT, false);
        g.drawString(font, Theme.t(Theme.fit(font, st.getHoverName().getString(), MW - 50 - chipW - 16)), x + 42, y + 12, Theme.TEXT, false);
        g.drawString(font, Theme.t("개당 " + Theme.money(font, unit(), "원", MW - 54 - font.width(Theme.t("개당 ")))), x + 42, y + 24, Theme.SUBTEXT, false);
        // 수량: [-] 숫자 [+]
        int ry = y + 44;
        button(g, mx, my, x + 12, ry, 24, 20, "-", qty > 1, false);
        Theme.panel(g, x + 40, ry, x + 100, ry + 20, 0xE0101319);
        String q = String.valueOf(qty);
        g.drawString(font, Theme.t(q), x + 70 - font.width(Theme.t(q)) / 2, ry + 6, Theme.TEXT, false);
        button(g, mx, my, x + 104, ry, 24, 20, "+", qty < max, false);
        String maxText = "최대 " + max + "개";
        g.drawString(font, Theme.t(maxText), x + MW - 12 - font.width(Theme.t(maxText)), ry + 6, Theme.SUBTEXT, false);
        // 빠른 선택
        for (int i = 0; i < PRESETS.length; i++) {
            button(g, mx, my, x + 12 + i * 42, y + 72, 36, 18, String.valueOf(PRESETS[i]), PRESETS[i] <= max, PRESETS[i] == qty);
        }
        // 합계 + 이유
        int ty = y + 100;
        g.drawString(font, Theme.t("합계"), x + 12, ty, Theme.SUBTEXT, false);
        if (max == 0) {
            String why = modalSell ? "보유 아이템 없음" : "잔액 부족";
            g.drawString(font, Theme.t(why), x + MW - 12 - font.width(Theme.t(why)), ty, 0xFFFF6B6B, false);
        } else {
            String total = Theme.money(font, unit() * qty, "원", MW - 60);
            g.drawString(font, Theme.t(total), x + MW - 12 - font.width(Theme.t(total)), ty, Theme.GOLD, false);
        }
        button(g, mx, my, x + 12, y + MH - 30, 98, 20, "취소", true, false);
        button(g, mx, my, x + MW - 110, y + MH - 30, 98, 20, verb + "하기", max > 0, true);
        g.pose().popPose();
    }

    private void button(GuiGraphics g, int mx, int my, int x, int y, int w, int h, String label, boolean enabled, boolean primary) {
        boolean hov = enabled && mx >= x && mx < x + w && my >= y && my < y + h;
        int fill = !enabled ? 0x80222630 : primary ? (hov ? 0xFF3E66A8 : Theme.SELECT) : (hov ? Theme.TILE_HOVER : Theme.TILE);
        Theme.panel(g, x, y, x + w, y + h, fill, enabled ? (primary || hov ? Theme.ACCENT : Theme.BORDER) : 0x604A5366);
        String l = Theme.fit(font, label, w - 6);
        g.drawString(font, Theme.t(l), x + w / 2 - font.width(Theme.t(l)) / 2, y + (h - 8) / 2, enabled ? Theme.TEXT : 0xFF6B7280, false);
    }

    private static boolean in(double mx, double my, int x, int y, int w, int h) { return mx >= x && mx < x + w && my >= y && my < y + h; }

    private void confirm() {
        if (modal == null || qty < 1 || qty > maxQty()) return;
        pressedAt = System.currentTimeMillis();
        ClientPlayNetworking.send(new Net.ShopTrade(modalSell, modal[0], modal[1], qty));
        modal = null;
    }

    private boolean modalClick(double mx, double my) {
        int x = mx0(), y = my0(), max = maxQty();
        if (!in(mx, my, x, y, MW, MH) || in(mx, my, x + 12, y + MH - 30, 98, 20)) { modal = null; return true; }   // 바깥·취소
        if (in(mx, my, x + MW - 110, y + MH - 30, 98, 20)) { confirm(); return true; }
        if (in(mx, my, x + 12, y + 44, 24, 20)) qty = Math.max(1, qty - (hasShiftDown() ? 10 : 1));
        if (in(mx, my, x + 104, y + 44, 24, 20)) qty = Math.min(max, qty + (hasShiftDown() ? 10 : 1));
        for (int i = 0; i < PRESETS.length; i++) if (in(mx, my, x + 12 + i * 42, y + 72, 36, 18) && PRESETS[i] <= max) qty = PRESETS[i];
        return true;
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (modal != null) {
            if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_ESCAPE) { modal = null; return true; }           // 창만 닫고 상점은 그대로
            if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_ENTER || key == org.lwjgl.glfw.GLFW.GLFW_KEY_KP_ENTER) { confirm(); return true; }
            if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_UP || key == org.lwjgl.glfw.GLFW.GLFW_KEY_RIGHT) qty = Math.min(maxQty(), qty + 1);
            if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_DOWN || key == org.lwjgl.glfw.GLFW.GLFW_KEY_LEFT) qty = Math.max(1, qty - 1);
            return true;
        }
        return super.keyPressed(key, scan, mods);
    }

    private void sidebar(GuiGraphics g, int mx, int my) {
        g.fill(0, 0, SIDE, height, 0xC0080A0E);
        g.fill(14, 15, 17, 27, Theme.ACCENT);
        g.drawString(font, Theme.t("상점"), 22, 17, Theme.TEXT);
        for (int c = 0; c < data.categories().size(); c++) {
            int y = TOP + c * 26;
            boolean sel = c == category, hov = mx < SIDE && my >= y && my < y + 22;
            float h = anim.to("cat" + c, hov || sel);
            if (h > 0.01f) Theme.panel(g, 8, y, SIDE - 8, y + 22, Theme.mix(0x00222630, sel ? Theme.SELECT : Theme.TILE_HOVER, h),
                    Theme.mix(0x004A5366, sel ? Theme.ACCENT : Theme.BORDER, h));
            var cat = data.categories().get(c);
            g.renderItem(Shop.stack(cat.icon()), 15, y + 3);
            g.drawString(font, Theme.t(cat.name()), 37, y + 7, sel ? Theme.TEXT : Theme.mix(Theme.SUBTEXT, Theme.TEXT, h));
        }
    }

    private void topBar(GuiGraphics g, int mx, int my) {
        // 구매/판매 탭: 선택 표시가 미끄러지듯 이동
        int tx = SIDE + 16;
        Theme.panel(g, tx, 14, tx + 124, 30, 0xE0181B22);
        float s = anim.to("tab", sell);
        int ix = tx + 2 + Math.round(60 * s);
        g.fill(ix, 16, ix + 60, 28, Theme.SELECT);
        g.drawCenteredString(font, Theme.t("구매"), tx + 32, 18, Theme.mix(Theme.TEXT, Theme.SUBTEXT, s));
        g.drawCenteredString(font, Theme.t("판매"), tx + 92, 18, Theme.mix(Theme.SUBTEXT, Theme.TEXT, s));
        // 잔액: 거래하면 0.4초간 밝게 빛남
        int room = width - 16 - 130 - 10 - (SIDE + 16 + 124 + 8);                     // 탭과 검색창 사이
        String bal = Theme.money(font, balance, "", room - 34);
        int bw = font.width(Theme.t(bal)) + 34, bx = width - 16 - 130 - 10 - bw;
        float flash = Math.max(0, 1 - (System.currentTimeMillis() - balanceChangedAt) / 400f);
        Theme.panel(g, bx, 14, bx + bw, 30, 0xE0181B22, Theme.mix(Theme.BORDER, Theme.GOLD, flash));
        g.renderItem(new ItemStack(Items.GOLD_NUGGET), bx + 4, 14);
        g.drawString(font, Theme.t(bal), bx + 26, 18, Theme.mix(Theme.GOLD, Theme.TEXT, flash));
    }

    private void card(GuiGraphics g, int[] ref, int k, int x, int y, float h) {
        var e = data.categories().get(ref[0]).items().get(ref[1]);
        ItemStack st = Shop.stack(e.item());
        long price = sell ? e.sell() : e.buy();
        var player = minecraft == null ? null : minecraft.player;
        int have = player == null ? 0 : Shop.count(player, e.item());
        boolean blocked = sell ? have == 0 : balance < price;
        float sc = k == pressedKey ? Theme.press(pressedAt) : 1f;
        g.pose().pushPose();
        g.pose().translate(x + cardW() / 2f, y + CARD_H / 2f - h, 0);   // 마우스를 올리면 1픽셀 떠오름
        g.pose().scale(sc, sc, 1);
        g.pose().translate(-cardW() / 2f, -CARD_H / 2f, 0);
        Theme.panel(g, 0, 0, cardW(), CARD_H, Theme.mix(Theme.TILE, Theme.TILE_HOVER, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
        g.fill(5, 5, cardW() - 5, 44, Theme.mix(0x30FFFFFF, 0x48FFFFFF, h));
        g.pose().pushPose();
        g.pose().translate(cardW() / 2f - 16, 8, 0);
        g.pose().scale(2, 2, 1);
        g.renderItem(st, 0, 0);
        g.pose().popPose();
        g.drawString(font, Theme.t("x1"), cardW() - 16, 34, Theme.SUBTEXT);
        g.drawCenteredString(font, Theme.t(Theme.fit(font, st.getHoverName().getString(), cardW() - 8)), cardW() / 2, 49, Theme.TEXT);
        // 상태 띠: 판매 탭은 보유 수량, 구매 탭은 잔액 부족만
        String badge = sell ? (have == 0 ? "보유 아이템 없음" : "보유 " + have + "개") : (blocked ? "잔액 부족" : null);
        if (badge != null) {
            g.fill(4, 60, cardW() - 4, 71, sell && have > 0 ? GREEN : RED);
            g.drawCenteredString(font, Theme.t(Theme.fit(font, badge, cardW() - 8)), cardW() / 2, 62, Theme.TEXT);
        }
        g.drawCenteredString(font, Theme.t(sell ? "판매가" : "구매가"), cardW() / 2, 75, Theme.SUBTEXT);
        g.drawCenteredString(font, Theme.t(Theme.money(font, price, "", cardW() - 8)), cardW() / 2, 86, blocked ? Theme.SUBTEXT : Theme.GOLD);
        g.pose().popPose();
    }

    /** 아이템 설명: 처음엔 0.4초 머문 뒤, 바로 다음 카드부터는 즉시. */
    private void tooltip(GuiGraphics g, int hovered, int mx, int my) {
        long now = System.currentTimeMillis();
        if (hovered != hoverKey) { hoverKey = hovered; hoverSince = now; }
        if (hovered < 0) return;
        if (now - hoverSince < 400 && now - lastTooltip > 300) return;
        lastTooltip = now;
        int[] r = shown.get(hovered);
        g.renderTooltip(font, Shop.stack(data.categories().get(r[0]).items().get(r[1]).item()), mx, my);
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        mx /= k; my /= k;
        if (modal != null) return modalClick(mx, my);
        if (super.mouseClicked(mx, my, button)) return true;
        int tx = SIDE + 16;
        if (my >= 14 && my < 30 && mx >= tx && mx < tx + 124) {
            sell = mx >= tx + 62;
            refilter();
            return true;
        }
        if (mx < SIDE) {
            int c = (int) ((my - TOP) / 26);
            if (my >= TOP && c < data.categories().size()) { category = c; search.setValue(""); refilter(); }
            return true;
        }
        if (my < TOP + 10 || my >= height - 20) return false;
        for (int k = 0; k < shown.size(); k++) {
            int x = cardX(k), y = cardY(k);
            if (mx >= x && mx < x + cardW() && my >= y && my < y + CARD_H) {
                int[] r = shown.get(k);
                pressedKey = k;
                pressedAt = System.currentTimeMillis();
                modal = r;
                modalSell = sell;
                qty = 1;
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double sx, double sy) {
        mx /= k; my /= k;
        if (modal != null) {                                       // 수량 창에서는 휠로 수량 조절
            qty = (int) Math.max(1, Math.min(maxQty(), qty + Math.signum(sy) * (hasShiftDown() ? 10 : 1)));
            return true;
        }
        int rows = (shown.size() + cols() - 1) / cols();
        double max = Math.max(0, rows * (CARD_H + GAP) - (height - TOP - 34));
        scroll = Math.max(0, Math.min(max, scroll - sy * 24));
        return true;
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
