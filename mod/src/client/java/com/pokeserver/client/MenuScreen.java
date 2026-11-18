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

/** 5. 메인 메뉴 (G키): 왼쪽 탭, 오른쪽 타일, 내 정보, 공지. */
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
                    new Tile("스폰 광장", "minecraft:beacon", "warp:hall"),
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

    // 화면이 좁으면(UI 크기를 키웠거나 창이 작으면) 탭·타일을 줄이고 내 정보를 위아래로 쌓음 → 어떤 크기에서도 겹치거나 잘리지 않게
    private boolean compact() { return width < 480 || height < 300; }
    private int left() { return compact() ? 104 : 150; }                 // 왼쪽 탭 오른쪽 끝
    private int tile() { return compact() ? 40 : 58; }
    private int gap() { return compact() ? 6 : 8; }
    private int tilesX() { return left() + (compact() ? 12 : 28); }
    private int right() { return width - (compact() ? 10 : 24); }
    private int perRow() { return Math.max(1, (right() - tilesX() + gap()) / (tile() + gap())); }
    private int tileX(int i) { return tilesX() + i % perRow() * (tile() + gap()); }
    private int tileY(int i) { return (compact() ? 14 : 24) + i / perRow() * (tile() + gap()); }

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

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        // 블러 없이 왼쪽을 어둡게 (사진처럼 뒤에 세상이 보이게). G키로 자주 여는 화면이라 여는 애니메이션은 없음
        g.fillGradient(0, 0, width, height, 0x90000000, 0x60000000);
        g.fill(0, 0, left() + 20, height, 0x80080A0E);
        g.fill(16, 22, 19, 32, Theme.ACCENT);
        g.drawString(font, Theme.t("메인 메뉴"), 24, 24, Theme.TEXT);
        for (int i = 0; i < TABS.size(); i++) {
            int y = 48 + i * 28;
            boolean sel = i == tab, hov = mx >= 16 && mx < left() && my >= y && my < y + 24;
            float h = anim.to("tab" + i, hov);
            Theme.panel(g, 16, y, left(), y + 24, sel ? Theme.SELECT : Theme.mix(Theme.TILE, Theme.TILE_HOVER, h),
                    sel ? Theme.ACCENT : Theme.mix(Theme.BORDER, Theme.ACCENT, h));
            if (sel) g.fill(16, y + 1, 19, y + 23, Theme.ACCENT);
            g.renderItem(Shop.stack(TABS.get(i).icon()), 26, y + 4);
            g.drawString(font, Theme.t(TABS.get(i).label()), 48, y + 8, sel ? Theme.TEXT : Theme.mix(Theme.SUBTEXT, Theme.TEXT, h));
        }
        // 오른쪽 타일: 마우스를 올리면 떠오르고 테두리가 밝아짐, 누르면 살짝 눌림
        List<Tile> tiles = TABS.get(tab).tiles();
        for (int i = 0; i < tiles.size(); i++) {
            int x = tileX(i), y = tileY(i);
            int T = tile();
            boolean hov = mx >= x && mx < x + T && my >= y && my < y + T;
            float h = anim.to(tab + ":" + i, hov);
            float sc = tiles.get(i).action().equals(pressed) ? Theme.press(pressedAt) : 1f;
            g.pose().pushPose();
            g.pose().translate(x + T / 2f, y + T / 2f - 2 * h, 0);
            g.pose().scale(sc, sc, 1);
            g.pose().translate(-T / 2f, -T / 2f, 0);
            Theme.panel(g, 0, 0, T, T, Theme.mix(0xD0181B22, Theme.SELECT, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
            float is = compact() ? 1f : 1.5f;
            g.pose().pushPose();
            g.pose().translate(T / 2f - 8 * is, compact() ? 5 : 8, 0);
            g.pose().scale(is, is, 1);
            g.renderItem(Shop.stack(tiles.get(i).icon()), 0, 0);
            g.pose().popPose();
            g.drawCenteredString(font, Theme.t(tiles.get(i).label()), T / 2, T - 13, Theme.TEXT);
            g.pose().popPose();
        }
        // 내 정보: 얼굴 + 이름, 도감 진행, 잔액·레벨 제한. 칸이 좁으면(360 미만) 위아래로 쌓음
        int px = tilesX(), py = tileY(tiles.size() - 1) + tile() + (compact() ? 8 : 16), pw = right() - px;
        boolean stack = pw < 360;
        int ph = stack ? 92 : 78;
        Theme.panel(g, px, py, px + pw, py + ph, 0xD0101319);
        if (minecraft != null && minecraft.player != null) {
            net.minecraft.client.gui.components.PlayerFaceRenderer.draw(g, minecraft.player.getSkin().texture(), px + 10, py + 6, 16);
        }
        g.drawString(font, Theme.t(minecraft != null && minecraft.player != null ? minecraft.player.getGameProfile().getName() : "플레이어"), px + 32, py + 10, Theme.TEXT);
        int[] dex = FabricLoader.getInstance().isModLoaded("cobblemon") ? CobblemonClientHooks.dexCounts() : new int[]{0, 0, 1};
        int cap = minecraft != null && minecraft.player != null ? levelCap(minecraft.player) : -1;
        String capText = cap > 0 ? "Lv" + cap : "-", money = String.format("%,d원", balance);
        if (stack) {
            bar(g, "잡은 포켓몬", dex[0], dex[2], px + 10, py + 28, pw - 20);
            bar(g, "마주친 포켓몬", dex[1], dex[2], px + 10, py + 48, pw - 20);
            int ry = py + 72;
            g.drawString(font, Theme.t("잔액"), px + 10, ry, Theme.SUBTEXT);
            g.drawString(font, Theme.t(money), px + 16 + font.width(Theme.t("잔액")), ry, Theme.GOLD);
            int cx = px + pw - 10 - font.width(Theme.t(capText));
            g.drawString(font, Theme.t(capText), cx, ry, Theme.ACCENT);
            g.drawString(font, Theme.t("레벨 제한"), cx - 6 - font.width(Theme.t("레벨 제한")), ry, Theme.SUBTEXT);
        } else {
            bar(g, "잡은 포켓몬", dex[0], dex[2], px + 10, py + 32, pw / 2 - 20);
            bar(g, "마주친 포켓몬", dex[1], dex[2], px + 10, py + 54, pw / 2 - 20);
            g.vLine(px + pw / 2, py + 10, py + 68, Theme.BORDER);
            g.drawString(font, Theme.t("잔액"), px + pw / 2 + 12, py + 30, Theme.SUBTEXT);
            g.drawString(font, Theme.t(money), px + pw / 2 + 12, py + 44, Theme.GOLD);
            g.drawString(font, Theme.t("레벨 제한"), px + pw / 2 + 12, py + 58, Theme.SUBTEXT);
            g.drawString(font, Theme.t(capText), px + pw / 2 + 12 + font.width(Theme.t("레벨 제한")) + 8, py + 58, Theme.ACCENT);
        }
        // 공지
        int ny = py + ph + (compact() ? 6 : 8);
        Theme.panel(g, px, ny, px + pw, ny + 22, 0xD0101319);
        g.drawString(font, Theme.t("공지사항"), px + 10, ny + 7, Theme.TEXT);
        g.drawString(font, Theme.t(Theme.fit(font, notice, pw - 74)), px + 64, ny + 7, Theme.GOLD);
        // 왼쪽 아래: 명령어, 휴지통
        small(g, mx, my, smallX(0), height - 52, "minecraft:book", "명령어", "help");
        small(g, mx, my, smallX(1), height - 52, "minecraft:cauldron", "휴지통", "trash");
    }

    private void bar(GuiGraphics g, String label, int n, int total, int x, int y, int w) {
        g.drawString(font, Theme.t(label), x, y, Theme.SUBTEXT);
        String num = n + " / " + total + "  ·  " + String.format("%.1f%%", 100.0 * n / Math.max(1, total));
        if (font.width(Theme.t(label)) + font.width(Theme.t(num)) + 8 > w) num = n + " / " + total;   // 좁으면 퍼센트 생략
        g.drawString(font, Theme.t(num), x + w - font.width(Theme.t(num)), y, Theme.ACCENT);
        g.fill(x, y + 11, x + w, y + 14, 0xFF2A2F3A);
        int fw = (int) ((long) w * n / Math.max(1, total));
        if (fw > 0) g.fill(x, y + 11, x + Math.max(2, fw), y + 14, Theme.ACCENT);
    }

    private int smallW() { return compact() ? 42 : 52; }
    private int smallX(int i) { return compact() ? 16 + i * (smallW() + 4) : 24 + i * 60; }

    private void small(GuiGraphics g, int mx, int my, int x, int y, String icon, String label, String key) {
        int w = smallW();
        boolean hov = mx >= x && mx < x + w && my >= y && my < y + 40;
        float h = anim.to(key, hov);
        Theme.panel(g, x, y, x + w, y + 40, Theme.mix(Theme.TILE, Theme.TILE_HOVER, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
        g.renderItem(Shop.stack(icon), x + w / 2 - 8, y + 5);
        g.drawCenteredString(font, Theme.t(label), x + w / 2, y + 26, Theme.TEXT);  // 픽셀 글꼴은 줄이면 깨져서 원래 크기로
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        for (int i = 0; i < TABS.size(); i++) {
            int y = 48 + i * 28;
            if (mx >= 16 && mx < left() && my >= y && my < y + 24) { tab = i; return true; }
        }
        List<Tile> tiles = TABS.get(tab).tiles();
        for (int i = 0; i < tiles.size(); i++) {
            int x = tileX(i), y = tileY(i);
            if (mx >= x && mx < x + tile() && my >= y && my < y + tile()) {
                pressed = tiles.get(i).action();
                pressedAt = System.currentTimeMillis();
                act(pressed);
                return true;
            }
        }
        if (my >= height - 52 && my < height - 12) {
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
