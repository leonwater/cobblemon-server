package com.pokeserver.client;

import com.pokeserver.Net;
import com.pokeserver.Shop;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 5. 메인 메뉴 (G키). ui-ux-pro-max 스킬의 클레이모피즘 구조 (가운데 패널, 둥근 카드, 이중 그림자) + 기존 어두운 반투명 색.
 *  모든 글자는 칸 너비에 맞춰 자르고(…), 잘린 공지는 마우스를 올리면 전체를 보여 줌. 1·2·3 키로 탭 전환. */
public class MenuScreen extends Screen {
    record Tile(String label, String icon, String action) {}
    record Tab(String label, String icon, List<Tile> tiles) {}

    static final List<Tab> TABS = List.of(
            new Tab("포켓몬", "cobblemon:poke_ball", List.of(
                    new Tile("내 파티", "cobblemon:poke_ball", "client:party"),
                    new Tile("PC", "cobblemon:pc", "pc"),
                    new Tile("도감", "cobblemon:pokedex_red", "client:dex"))),
            new Tab("간편 메뉴", "minecraft:book", List.of(
                    new Tile("튜토리얼", "minecraft:book", "tutorial"),
                    new Tile("휴지통", "minecraft:cauldron", "trash"))),
            new Tab("워프", "minecraft:ender_pearl", List.of(
                    new Tile("광장", "minecraft:beacon", "warp:hall"),
                    new Tile("상점가", "minecraft:emerald", "warp:street"),
                    new Tile("야생", "minecraft:grass_block", "warp:wild"),
                    new Tile("농장", "minecraft:wheat", "warp:farm"),
                    new Tile("체육관", "minecraft:red_banner", "warp:gym"))));

    private final long balance;
    private final String notice;
    int tab;
    private final Theme.Anim anim = new Theme.Anim();
    private String pressed = "";
    private long pressedAt;

    public MenuScreen(long balance, String notice) {
        super(Component.literal("메인 메뉴"));
        this.balance = balance;
        this.notice = notice;
    }

    /** RCT 레벨 제한 (RCT가 클라이언트에 보내 주는 값). RCT가 없으면 -1. */
    static int levelCap(net.minecraft.world.entity.player.Player p) {
        try {
            Object st = Class.forName("com.gitlab.srcmc.rctmod.api.data.sync.PlayerState")
                    .getMethod("get", net.minecraft.world.entity.player.Player.class).invoke(null, p);
            return (int) st.getClass().getMethod("getLevelCap").invoke(st);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return -1;
        }
    }

    // ── 배치 (화면 크기에서 계산: 전체 화면 480~640 GUI px 기준, 더 작아도 겹치지 않음) ──
    private int pw() { return Math.max(300, Math.min(width - 24, 520)); }
    private int ph() { return Math.max(214, Math.min(height - 24, 290)); }
    private int px() { return (width - pw()) / 2; }
    private int py() { return (height - ph()) / 2; }
    private int railW() { return Math.max(108, Math.min(124, pw() / 4)); }   // 탭 이름·버튼 글자가 잘리지 않는 최소 폭
    private int cx() { return px() + 12 + railW() + 10; }
    private int cw() { return px() + pw() - 12 - cx(); }
    private int tabY(int i) { return py() + 40 + i * 32; }
    private int tileW(int n) { return Math.min(88, (cw() - 6 * (n - 1)) / n); }
    private int tileX(int i, int n) { return cx() + i * (tileW(n) + 6); }
    private int tileY() { return py() + 58; }
    private int noticeY() { return py() + ph() - 12 - 24; }
    // 남는 높이를 타일과 도감 카드가 나눠 가짐 (빈 공간 없이)
    private int tileH() { return Math.max(56, Math.min(84, noticeY() - 10 - tileY() - 10 - 52)); }
    private int dexH() { return Math.max(52, Math.min(72, noticeY() - 10 - tileY() - tileH() - 10)); }
    private int smallW() { return (railW() - 6) / 2; }
    private int smallX(int i) { return px() + 12 + i * (smallW() + 6); }
    private int smallY() { return py() + ph() - 12 - 40; }

    private void text(GuiGraphics g, String s, int x, int y, int color) { g.drawString(font, Theme.t(s), x, y, color, false); }
    private void center(GuiGraphics g, String s, int cx, int y, int color) { text(g, s, cx - font.width(Theme.t(s)) / 2, y, color); }
    private int w(String s) { return font.width(Theme.t(s)); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        // 자주 여는 화면이라 여는 애니메이션은 없음 (emil-design-eng: 자주 쓰는 키 동작은 애니메이션 X)
        g.fillGradient(0, 0, width, height, 0x90000000, 0x60000000);   // 기존처럼 뒤 세상이 비치는 어두운 반투명
        int px = px(), py = py(), pw = pw(), ph = ph();
        Theme.clay(g, px, py, px + pw, py + ph, Theme.C_BG, Theme.C_BORDER);
        header(g, px, py, pw);
        for (int i = 0; i < TABS.size(); i++) tab(g, i, mx, my);
        content(g, mx, my);
        small(g, mx, my, 0, "minecraft:book", "명령어", "help");
        small(g, mx, my, 1, "minecraft:cauldron", "휴지통", "trash");
    }

    private void header(GuiGraphics g, int px, int py, int pw) {
        g.renderItem(Shop.stack("cobblemon:poke_ball"), px + 12, py + 9);
        text(g, "메인 메뉴", px + 32, py + 13, Theme.C_TEXT);
        // 오른쪽 칩: 레벨 제한, 잔액 (글자 길이에 맞춰 폭 계산)
        int cap = minecraft != null && minecraft.player != null ? levelCap(minecraft.player) : -1;
        String money = String.format("%,d원", balance), capText = "레벨 제한 " + (cap > 0 ? "Lv" + cap : "-");
        int x = px + pw - 12;
        x = chip(g, x, py + 8, "minecraft:gold_nugget", money, 0xE0181B22, Theme.GOLD, Theme.GOLD);
        chip(g, x - 6, py + 8, "minecraft:experience_bottle", capText, 0xE0181B22, Theme.ACCENT, Theme.TEXT);
        g.fill(px + 12, py + 31, px + pw - 12, py + 32, Theme.C_BORDER);
    }

    /** 오른쪽 끝(right)에서 왼쪽으로 칩을 그리고, 칩 왼쪽 끝 x를 돌려줌. */
    private int chip(GuiGraphics g, int right, int y, String icon, String label, int fill, int border, int textColor) {
        int cw = w(label) + 28, x = right - cw;
        Theme.round(g, x, y, right, y + 18, 5, border);
        Theme.round(g, x + 1, y + 1, right - 1, y + 17, 4, fill);
        g.renderItem(Shop.stack(icon), x + 2, y + 1);
        text(g, label, x + 20, y + 5, textColor);
        return x;
    }

    private void tab(GuiGraphics g, int i, int mx, int my) {
        int x = px() + 12, y = tabY(i), wdt = railW();
        boolean sel = i == tab, hov = mx >= x && mx < x + wdt && my >= y && my < y + 26;
        float h = anim.to("tab" + i, hov && !sel);
        Theme.clay(g, x, y, x + wdt, y + 26, sel ? Theme.SELECT : Theme.mix(Theme.TILE, Theme.TILE_HOVER, h),
                sel ? Theme.ACCENT : Theme.mix(Theme.BORDER, Theme.ACCENT, h));
        if (sel) g.fill(x + 2, y + 5, x + 4, y + 21, Theme.ACCENT);
        g.renderItem(Shop.stack(TABS.get(i).icon()), x + 6, y + 5);
        text(g, Theme.fit(font, TABS.get(i).label(), wdt - 26 - 16), x + 26, y + 9, sel ? Theme.C_TEXT : Theme.mix(Theme.C_SUB, Theme.C_TEXT, h));
        text(g, String.valueOf(i + 1), x + wdt - 10, y + 9, sel ? Theme.ACCENT : 0xFF6B7385);   // 키보드 단축키 표시
    }

    private void content(GuiGraphics g, int mx, int my) {
        int cx = cx(), cw = cw(), py = py();
        String[] hints = {"파티·PC·도감을 바로 열어요", "튜토리얼 다시 보기, 아이템 버리기", "농장·야생은 마지막 위치로 이동"};
        text(g, TABS.get(tab).label(), cx, py + 42, Theme.C_TEXT);
        text(g, Theme.fit(font, hints[tab], cw - w(TABS.get(tab).label()) - 10), cx + w(TABS.get(tab).label()) + 8, py + 42, Theme.C_SUB);
        List<Tile> tiles = TABS.get(tab).tiles();
        int n = tiles.size(), tw = tileW(n), ty = tileY();
        for (int i = 0; i < n; i++) {
            int x = tileX(i, n);
            boolean hov = mx >= x && mx < x + tw && my >= ty && my < ty + tileH();
            float h = anim.to(tab + ":" + i, hov);
            float sc = tiles.get(i).action().equals(pressed) ? Theme.press(pressedAt) : 1f;
            g.pose().pushPose();
            g.pose().translate(x + tw / 2f, ty + tileH() / 2f - h, 0);   // 올리면 1픽셀 떠오름, 누르면 0.97배 (배치는 그대로)
            g.pose().scale(sc, sc, 1);
            g.pose().translate(-tw / 2f, -tileH() / 2f, 0);
            Theme.clay(g, 0, 0, tw, tileH(), Theme.mix(Theme.TILE, Theme.SELECT, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
            g.pose().pushPose();
            g.pose().translate(tw / 2f - 12, (tileH() - 17) / 2f - 13, 0);
            g.pose().scale(1.5f, 1.5f, 1);
            g.renderItem(Shop.stack(tiles.get(i).icon()), 0, 0);
            g.pose().popPose();
            String label = Theme.fit(font, tiles.get(i).label(), tw - 8);
            center(g, label, tw / 2, tileH() - 17, Theme.C_TEXT);
            g.pose().popPose();
        }
        // 내 도감 카드
        int dy = ty + tileH() + 10, dh = dexH();
        Theme.clay(g, cx, dy, cx + cw, dy + dh, Theme.C_CARD, Theme.C_BORDER);
        String name = minecraft != null && minecraft.player != null ? minecraft.player.getGameProfile().getName() : "플레이어";
        if (minecraft != null && minecraft.player != null) {
            net.minecraft.client.gui.components.PlayerFaceRenderer.draw(g, minecraft.player.getSkin().texture(), cx + 8, dy + 7, 12);
        }
        text(g, Theme.fit(font, name + "의 도감", cw - 34), cx + 26, dy + 9, Theme.C_TEXT);
        int[] dex = FabricLoader.getInstance().isModLoaded("cobblemon") ? CobblemonClientHooks.dexCounts() : new int[]{0, 0, 1};
        int bw = (cw - 30) / 2;
        bar(g, "잡은 포켓몬", dex[0], dex[2], cx + 10, dy + dh - 27, bw, Theme.ACCENT);
        bar(g, "마주친 포켓몬", dex[1], dex[2], cx + 20 + bw, dy + dh - 27, bw, Theme.C_SECONDARY);
        // 공지 (잘리면 마우스를 올려 전체 보기)
        int ny = noticeY();
        Theme.clay(g, cx, ny, cx + cw, ny + 24, Theme.C_MUTED, Theme.C_BORDER);
        int lw = w("공지") + 12;
        Theme.round(g, cx + 6, ny + 5, cx + 6 + lw, ny + 19, 4, Theme.C_ACCENT);
        text(g, "공지", cx + 12, ny + 8, 0xFF101319);
        String shown = Theme.fit(font, notice, cw - lw - 22);
        text(g, shown, cx + lw + 14, ny + 8, Theme.GOLD);
        if (!shown.equals(notice) && mx >= cx && mx < cx + cw && my >= ny && my < ny + 24) {
            g.renderComponentTooltip(font, font.getSplitter().splitLines(Theme.t(notice), 220, net.minecraft.network.chat.Style.EMPTY).stream()
                    .map(l -> (Component) Theme.t(l.getString())).toList(), mx, my);
        }
    }

    private void bar(GuiGraphics g, String label, int n, int total, int x, int y, int w, int color) {
        String num = n + " / " + total;
        String lab = Theme.fit(font, label, w - w(num) - 6);
        text(g, lab, x, y, Theme.C_SUB);
        text(g, num, x + w - w(num), y, Theme.C_TEXT);
        Theme.round(g, x, y + 12, x + w, y + 18, 3, Theme.C_TRACK);
        int fw = (int) ((long) w * n / Math.max(1, total));
        if (fw > 0) Theme.round(g, x, y + 12, x + Math.max(6, fw), y + 18, 3, color);
    }

    private void small(GuiGraphics g, int mx, int my, int i, String icon, String label, String key) {
        int x = smallX(i), y = smallY(), sw = smallW();
        boolean hov = mx >= x && mx < x + sw && my >= y && my < y + 40;
        float h = anim.to(key, hov);
        Theme.clay(g, x, y, x + sw, y + 40, Theme.mix(Theme.TILE, Theme.TILE_HOVER, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
        g.renderItem(Shop.stack(icon), x + sw / 2 - 8, y + 5);
        center(g, Theme.fit(font, label, sw - 8), x + sw / 2, y + 25, Theme.C_TEXT);
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (key >= org.lwjgl.glfw.GLFW.GLFW_KEY_1 && key < org.lwjgl.glfw.GLFW.GLFW_KEY_1 + TABS.size()) {
            tab = key - org.lwjgl.glfw.GLFW.GLFW_KEY_1;
            return true;
        }
        return super.keyPressed(key, scan, mods);
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        for (int i = 0; i < TABS.size(); i++) {
            int x = px() + 12, y = tabY(i);
            if (mx >= x && mx < x + railW() && my >= y && my < y + 26) { tab = i; return true; }
        }
        List<Tile> tiles = TABS.get(tab).tiles();
        int n = tiles.size();
        for (int i = 0; i < n; i++) {
            int x = tileX(i, n);
            if (mx >= x && mx < x + tileW(n) && my >= tileY() && my < tileY() + tileH()) {
                pressed = tiles.get(i).action();
                pressedAt = System.currentTimeMillis();
                act(pressed);
                return true;
            }
        }
        if (my >= smallY() && my < smallY() + 40) {
            if (mx >= smallX(0) && mx < smallX(0) + smallW()) { help(); return true; }
            if (mx >= smallX(1) && mx < smallX(1) + smallW()) { act("trash"); return true; }
        }
        return super.mouseClicked(mx, my, button);
    }

    private void act(String a) {
        boolean cobble = FabricLoader.getInstance().isModLoaded("cobblemon");
        if (a.equals("client:party")) {
            if (!cobble || !CobblemonClientHooks.openParty()) toast("파티에 포켓몬이 없어요.");
        } else if (a.equals("client:dex")) {
            if (cobble) CobblemonClientHooks.openDex();
        } else {
            onClose();
            ClientPlayNetworking.send(new Net.MenuAction(a));
        }
    }

    private void help() {
        onClose();
        for (String line : new String[]{"── 기본 명령어 ──", "G 키: 메인 메뉴", "/money (/돈): 잔액", "/pay 닉네임 금액 (/송금): 돈 보내기",
                "/trigger home: 회의장으로", "R 키: 포켓몬 꺼내기 · M 키: 상태창 · ↑↓: 파티 선택"}) toast(line);
    }

    private void toast(String s) {
        if (minecraft != null && minecraft.player != null) minecraft.player.displayClientMessage(Component.literal(s).withStyle(ChatFormatting.GRAY), false);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
