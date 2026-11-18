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
                    new Tile("회의장", "minecraft:lectern", "warp:hall"),
                    new Tile("상점가", "minecraft:emerald", "warp:street"),
                    new Tile("야생", "minecraft:grass_block", "warp:wild"),
                    new Tile("농장", "minecraft:wheat", "warp:farm"),
                    new Tile("체육관", "minecraft:red_banner", "warp:gym"))));
    static final int TILE = 58, LEFT = 150;

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

    private int tilesX() { return width - 24 - 5 * (TILE + 8) + 8; }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        // 블러 없이 왼쪽을 어둡게 (사진처럼 뒤에 세상이 보이게). G키로 자주 여는 화면이라 여는 애니메이션은 없음
        g.fillGradient(0, 0, width, height, 0x90000000, 0x60000000);
        g.fill(0, 0, LEFT + 20, height, 0x80080A0E);
        g.fill(16, 22, 19, 32, Theme.ACCENT);
        g.drawString(font, "메인 메뉴", 24, 24, Theme.TEXT);
        for (int i = 0; i < TABS.size(); i++) {
            int y = 48 + i * 28;
            boolean sel = i == tab, hov = mx >= 16 && mx < LEFT && my >= y && my < y + 24;
            float h = anim.to("tab" + i, hov);
            Theme.panel(g, 16, y, LEFT, y + 24, sel ? Theme.SELECT : Theme.mix(Theme.TILE, Theme.TILE_HOVER, h),
                    sel ? Theme.ACCENT : Theme.mix(Theme.BORDER, Theme.ACCENT, h));
            if (sel) g.fill(16, y + 1, 19, y + 23, Theme.ACCENT);
            g.renderItem(Shop.stack(TABS.get(i).icon()), 26, y + 4);
            g.drawString(font, TABS.get(i).label(), 48, y + 8, sel ? Theme.TEXT : Theme.mix(Theme.SUBTEXT, Theme.TEXT, h));
        }
        // 오른쪽 타일: 마우스를 올리면 떠오르고 테두리가 밝아짐, 누르면 살짝 눌림
        List<Tile> tiles = TABS.get(tab).tiles();
        for (int i = 0; i < tiles.size(); i++) {
            int x = tilesX() + i * (TILE + 8), y = 24;
            boolean hov = mx >= x && mx < x + TILE && my >= y && my < y + TILE;
            float h = anim.to(tab + ":" + i, hov);
            float sc = tiles.get(i).action().equals(pressed) ? Theme.press(pressedAt) : 1f;
            g.pose().pushPose();
            g.pose().translate(x + TILE / 2f, y + TILE / 2f - 2 * h, 0);
            g.pose().scale(sc, sc, 1);
            g.pose().translate(-TILE / 2f, -TILE / 2f, 0);
            Theme.panel(g, 0, 0, TILE, TILE, Theme.mix(0xD0181B22, Theme.SELECT, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
            g.pose().pushPose();
            g.pose().translate(TILE / 2f - 12, 8, 0);
            g.pose().scale(1.5f, 1.5f, 1);
            g.renderItem(Shop.stack(tiles.get(i).icon()), 0, 0);
            g.pose().popPose();
            g.drawCenteredString(font, tiles.get(i).label(), TILE / 2, TILE - 14, Theme.TEXT);
            g.pose().popPose();
        }
        // 내 정보: 얼굴 + 이름, 도감 진행, 잔액
        int px = tilesX(), py = 24 + TILE + 16, pw = width - 24 - px;
        Theme.panel(g, px, py, px + pw, py + 78, 0xD0101319);
        if (minecraft != null && minecraft.player != null) {
            net.minecraft.client.gui.components.PlayerFaceRenderer.draw(g, minecraft.player.getSkin().texture(), px + 10, py + 8, 16);
        }
        g.drawString(font, minecraft != null && minecraft.player != null ? minecraft.player.getGameProfile().getName() : "플레이어", px + 32, py + 12, Theme.TEXT);
        int[] dex = FabricLoader.getInstance().isModLoaded("cobblemon") ? CobblemonClientHooks.dexCounts() : new int[]{0, 0, 1};
        bar(g, "잡은 포켓몬", dex[0], dex[2], px + 10, py + 32, pw / 2 - 20);
        bar(g, "마주친 포켓몬", dex[1], dex[2], px + 10, py + 54, pw / 2 - 20);
        g.vLine(px + pw / 2, py + 10, py + 68, Theme.BORDER);
        g.drawString(font, "잔액", px + pw / 2 + 12, py + 32, Theme.SUBTEXT);
        g.drawString(font, String.format("%,d원", balance), px + pw / 2 + 12, py + 46, Theme.GOLD);
        // 공지
        int ny = py + 86;
        Theme.panel(g, px, ny, px + pw, ny + 22, 0xD0101319);
        g.drawString(font, "공지사항", px + 10, ny + 7, Theme.TEXT);
        g.drawString(font, font.plainSubstrByWidth(notice, pw - 70), px + 64, ny + 7, Theme.GOLD);
        // 왼쪽 아래: 명령어, 휴지통
        small(g, mx, my, 24, height - 52, "minecraft:book", "명령어", "help");
        small(g, mx, my, 84, height - 52, "minecraft:cauldron", "휴지통", "trash");
    }

    private void bar(GuiGraphics g, String label, int n, int total, int x, int y, int w) {
        g.drawString(font, label, x, y, Theme.SUBTEXT);
        String num = n + " / " + total + "  ·  " + String.format("%.1f%%", 100.0 * n / Math.max(1, total));
        g.drawString(font, num, x + w - font.width(num), y, Theme.ACCENT);
        g.fill(x, y + 11, x + w, y + 14, 0xFF2A2F3A);
        int fw = (int) ((long) w * n / Math.max(1, total));
        if (fw > 0) g.fill(x, y + 11, x + Math.max(2, fw), y + 14, Theme.ACCENT);
    }

    private void small(GuiGraphics g, int mx, int my, int x, int y, String icon, String label, String key) {
        boolean hov = mx >= x && mx < x + 52 && my >= y && my < y + 40;
        float h = anim.to(key, hov);
        Theme.panel(g, x, y, x + 52, y + 40, Theme.mix(Theme.TILE, Theme.TILE_HOVER, h), Theme.mix(Theme.BORDER, Theme.ACCENT, h));
        g.renderItem(Shop.stack(icon), x + 18, y + 5);
        g.drawCenteredString(font, label, x + 26, y + 26, Theme.TEXT);  // 픽셀 글꼴은 줄이면 깨져서 원래 크기로
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        for (int i = 0; i < TABS.size(); i++) {
            int y = 48 + i * 28;
            if (mx >= 16 && mx < LEFT && my >= y && my < y + 24) { tab = i; return true; }
        }
        List<Tile> tiles = TABS.get(tab).tiles();
        for (int i = 0; i < tiles.size(); i++) {
            int x = tilesX() + i * (TILE + 8);
            if (mx >= x && mx < x + TILE && my >= 24 && my < 24 + TILE) {
                pressed = tiles.get(i).action();
                pressedAt = System.currentTimeMillis();
                act(pressed);
                return true;
            }
        }
        if (my >= height - 52 && my < height - 12) {
            if (mx >= 24 && mx < 76) { help(); return true; }
            if (mx >= 84 && mx < 136) { act("trash"); return true; }
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
