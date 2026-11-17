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
                    new Tile("시작 마을", "minecraft:bell", "warp:village"),
                    new Tile("농장", "minecraft:wheat", "warp:farm"),
                    new Tile("채집 맵", "minecraft:grass_block", "warp:wild"))));
    static final int TILE = 58, LEFT = 150, GOLD = 0xFFF0C040;

    private final long balance;
    private final String notice;
    int tab;

    public MenuScreen(long balance, String notice) {
        super(Component.literal("메인 메뉴"));
        this.balance = balance;
        this.notice = notice;
    }

    private int tilesX() { return width - 24 - 5 * (TILE + 8) + 8; }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        // 블러 없이 왼쪽을 어둡게 (사진처럼 뒤에 세상이 보이게)
        g.fillGradient(0, 0, width, height, 0x90000000, 0x60000000);
        g.fill(0, 0, LEFT + 20, height, 0x80080A0E);
        g.drawString(font, "메인 메뉴", 24, 24, Theme.TEXT);
        for (int i = 0; i < TABS.size(); i++) {
            int y = 48 + i * 28;
            boolean sel = i == tab, hov = mx >= 16 && mx < LEFT && my >= y && my < y + 24;
            Theme.panel(g, 16, y, LEFT, y + 24, sel ? 0xE02E4A7A : hov ? Theme.TILE_HOVER : Theme.TILE);
            g.renderItem(Shop.stack(TABS.get(i).icon()), 24, y + 4);
            g.drawString(font, TABS.get(i).label(), 46, y + 8, sel ? Theme.TEXT : Theme.SUBTEXT);
        }
        // 오른쪽 타일
        List<Tile> tiles = TABS.get(tab).tiles();
        for (int i = 0; i < tiles.size(); i++) {
            int x = tilesX() + i * (TILE + 8), y = 24;
            boolean hov = mx >= x && mx < x + TILE && my >= y && my < y + TILE;
            Theme.panel(g, x, y, x + TILE, y + TILE, hov ? 0xE02E4A7A : 0xD0181B22);
            g.pose().pushPose();
            g.pose().translate(x + TILE / 2f - 12, y + 8, 0);
            g.pose().scale(1.5f, 1.5f, 1);
            g.renderItem(Shop.stack(tiles.get(i).icon()), 0, 0);
            g.pose().popPose();
            g.drawCenteredString(font, tiles.get(i).label(), x + TILE / 2, y + TILE - 14, Theme.TEXT);
        }
        // 내 정보
        int px = tilesX(), py = 24 + TILE + 16, pw = width - 24 - px;
        Theme.panel(g, px, py, px + pw, py + 74, 0xD0101319);
        g.drawString(font, minecraft != null && minecraft.player != null ? minecraft.player.getGameProfile().getName() : "플레이어", px + 10, py + 8, Theme.TEXT);
        int[] dex = FabricLoader.getInstance().isModLoaded("cobblemon") ? CobblemonClientHooks.dexCounts() : new int[]{0, 0, 1};
        bar(g, "잡은 포켓몬", dex[0], dex[2], px + 10, py + 24, pw / 2 - 20);
        bar(g, "마주친 포켓몬", dex[1], dex[2], px + 10, py + 46, pw / 2 - 20);
        g.drawString(font, "잔액", px + pw / 2 + 10, py + 24, Theme.SUBTEXT);
        g.drawString(font, String.format("%,d원", balance), px + pw / 2 + 10, py + 36, GOLD);
        // 공지
        int ny = py + 82;
        Theme.panel(g, px, ny, px + pw, ny + 22, 0xD0101319);
        g.drawString(font, "공지사항", px + 10, ny + 7, Theme.TEXT);
        g.drawString(font, font.plainSubstrByWidth(notice, pw - 70), px + 64, ny + 7, GOLD);
        // 왼쪽 아래: 기본 명령어, 휴지통
        small(g, mx, my, 24, height - 52, "minecraft:book", "명령어");
        small(g, mx, my, 84, height - 52, "minecraft:cauldron", "휴지통");
    }

    private void bar(GuiGraphics g, String label, int n, int total, int x, int y, int w) {
        g.drawString(font, label, x, y, Theme.SUBTEXT);
        String pct = String.format("%.2f%%", 100.0 * n / Math.max(1, total));
        g.drawString(font, pct, x + w - font.width(pct), y, Theme.ACCENT);
        g.fill(x, y + 11, x + w, y + 14, 0xFF2A2F3A);
        g.fill(x, y + 11, x + (int) ((long) w * n / Math.max(1, total)), y + 14, Theme.ACCENT);
    }

    private void small(GuiGraphics g, int mx, int my, int x, int y, String icon, String label) {
        boolean hov = mx >= x && mx < x + 52 && my >= y && my < y + 40;
        Theme.panel(g, x, y, x + 52, y + 40, hov ? Theme.TILE_HOVER : Theme.TILE);
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
            if (mx >= x && mx < x + TILE && my >= 24 && my < 24 + TILE) { act(tiles.get(i).action()); return true; }
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
                "/trigger home: 시작 마을로", "R 키: 포켓몬 꺼내기 · M 키: 상태창 · ↑↓: 파티 선택"}) toast(line);
    }

    private void toast(String s) {
        if (minecraft != null && minecraft.player != null) minecraft.player.displayClientMessage(Component.literal(s).withStyle(ChatFormatting.GRAY), false);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
