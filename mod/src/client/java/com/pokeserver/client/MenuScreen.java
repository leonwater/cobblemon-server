package com.pokeserver.client;

import com.pokeserver.Net;
import com.pokeserver.Nicknames;
import com.pokeserver.Shop;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 5. 메인 메뉴 (G키), 참고 사진 구성: 왼쪽 분류 탭(포켓몬·간편 메뉴·워프) + 아래 작은 버튼(기본 명령어·휴지통),
 *  오른쪽 위 분류별 칸, 그 아래 내 정보 카드(닉네임·잡은/마주친 포켓몬·잔액·배지), 맨 아래 공지사항. 어두운 반투명 색. */
public class MenuScreen extends Screen {
    record Tile(String label, String icon, String action) {}
    record Cat(String label, String icon, List<Tile> tiles) {}

    static final List<Cat> CATS = List.of(
            new Cat("포켓몬", "cobblemon:poke_ball", List.of(
                    new Tile("파티", "cobblemon:poke_ball", "client:party"),
                    new Tile("PC", "cobblemon:pc", "pc"),
                    new Tile("도감", "cobblemon:pokedex_red", "client:dex"))),
            new Cat("메뉴", "minecraft:book", List.of(
                    new Tile("튜토리얼", "minecraft:book", "tutorial"),
                    new Tile("칭호", "minecraft:name_tag", "titles"),
                    new Tile("명령어", "minecraft:oak_sign", "help"),
                    new Tile("휴지통", "minecraft:lava_bucket", "trash"))),
            new Cat("워프", "minecraft:ender_pearl", List.of(
                    new Tile("야생", "minecraft:grass_block", "warp:hall"),   // 광장 마을은 야생 첫 스폰 자리에 있어 하나로
                    new Tile("농장", "minecraft:wheat", "warp:farm"),
                    new Tile("체육관", "minecraft:red_banner", "warp:gym"))));
    /** 왼쪽 아래 작은 버튼 (참고 사진). */
    static final List<Tile> SMALL = List.of(new Tile("명령어", "minecraft:oak_sign", "help"), new Tile("휴지통", "minecraft:lava_bucket", "trash"));
    static int cat;                       // 마지막으로 고른 분류 (다시 열어도 유지)

    private final long balance;
    private final String notice;
    private final boolean tutorialDone;   // 튜토리얼을 끝내기 전엔 워프 칸 잠금 (서버도 따로 막음)
    private final int caught, seen, total, badges;
    private final Theme.Anim anim = new Theme.Anim();
    private String pressed = "";
    private long pressedAt;
    private float k = 1;
    private final int cap = minecraftCap();

    public MenuScreen(Net.MenuOpen p) {
        super(Component.literal("메인 메뉴"));
        balance = p.balance(); notice = p.notice(); tutorialDone = p.tutorialDone();
        caught = p.caught(); seen = p.seen(); total = p.total(); badges = p.badges();
    }

    /** 포켓몬 레벨 제한 (관장 모드 RCT가 클라이언트에 보내 주는 값). 없으면 -1. */
    static int minecraftCap() {
        try {
            var p = net.minecraft.client.Minecraft.getInstance().player;
            Object st = Class.forName("com.gitlab.srcmc.rctmod.api.data.sync.PlayerState")
                    .getMethod("get", net.minecraft.world.entity.player.Player.class).invoke(null, p);
            return (int) st.getClass().getMethod("getLevelCap").invoke(st);
        } catch (ReflectiveOperationException | RuntimeException ex) {
            return -1;
        }
    }

    /** GUI가 640×360보다 작으면(전체 화면 자동 크기) 전체를 줄여 그림 → 어느 크기에서나 같은 배치. */
    @Override
    protected void init() {
        k = Math.min(1f, Math.min(width / 640f, height / 360f));
        width = Math.round(width / k);
        height = Math.round(height / k);
    }

    // ── 배치 (가상 화면 기준) ──
    private int side() { return Math.max(170, width * 30 / 100); }          // 왼쪽 분류 칸 폭
    private int catY(int i) { return 52 + i * 38; }
    private int cx() { return side() + 22; }                                 // 오른쪽 내용 시작
    private int cw() { return Math.min(width - cx() - 22, 460); }
    static final int TILE = 78, GAP = 8, SW = 58;   // SW: 왼쪽 아래 작은 버튼 폭
    private int perRow() { return Math.max(1, (cw() + GAP) / (TILE + GAP)); }
    private List<Tile> tiles() { return CATS.get(cat).tiles(); }
    private int tileX(int i) { return cx() + (i % perRow()) * (TILE + GAP); }
    private int tileY(int i) { return 26 + (i / perRow()) * (TILE + GAP); }
    private int cardY() { return 26 + TILE + 14; }                           // 분류마다 칸은 한 줄 (가장 많은 워프 4칸)
    private int noticeY() { return height - 40; }                         // 공지사항은 맨 아래 (왼쪽 아래 작은 버튼과 나란히)
    static final int CARD_H = 122;
    private int smallX(int i) { return 18 + i * 66; }
    private int smallY() { return height - 64; }

    private void text(GuiGraphics g, String s, int x, int y, int color) { g.drawString(font, Theme.t(s), x, y, color, false); }
    private void center(GuiGraphics g, String s, int cx, int y, int color) { text(g, s, cx - font.width(Theme.t(s)) / 2, y, color); }
    private int w(String s) { return font.width(Theme.t(s)); }

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
        // 자주 여는 화면이라 여는 애니메이션은 없음
        g.fillGradient(0, 0, width, height, 0x90000000, 0x70000000);
        g.fill(0, 0, side(), height, 0xB0080A0E);                            // 왼쪽 판
        g.fill(18, 22, 21, 36, Theme.ACCENT);
        g.pose().pushPose();
        g.pose().translate(26, 23, 0);
        g.pose().scale(1.3f, 1.3f, 1);
        text(g, "메인 메뉴", 0, 0, Theme.TEXT);
        g.pose().popPose();
        for (int i = 0; i < CATS.size(); i++) catButton(g, i, mx, my);
        for (int i = 0; i < SMALL.size(); i++) small(g, i, mx, my);
        for (int i = 0; i < tiles().size(); i++) tile(g, i, mx, my);
        card(g);
        // 공지사항 (잘리면 마우스를 올려 전체 보기)
        int ny = noticeY(), x = cx(), cw = cw();
        Theme.panel(g, x, ny, x + cw, ny + 24, 0xD0181B22, 0xFF2A303C);
        text(g, "공지사항", x + 10, ny + 8, Theme.TEXT);
        String shown = Theme.fit(font, notice, cw - w("공지사항") - 30);
        text(g, shown, x + 22 + w("공지사항"), ny + 8, Theme.GOLD);
        if (!shown.equals(notice) && mx >= x && mx < x + cw && my >= ny && my < ny + 24) {
            g.renderComponentTooltip(font, Theme.wrap(font, notice, 220, 99).stream().map(l -> (Component) Theme.t(l)).toList(), mx, my);
        }
    }

    private void catButton(GuiGraphics g, int i, int mx, int my) {
        int x1 = 16, x2 = side() - 16, y = catY(i);
        boolean hov = mx >= x1 && mx < x2 && my >= y && my < y + 30, sel = i == cat;
        float h = anim.to("c" + i, hov || sel);
        Theme.panel(g, x1, y, x2, y + 30, sel ? 0xF02E4A7A : Theme.mix(0xC0181B22, 0xE0262C38, h), sel ? Theme.ACCENT : Theme.mix(0xFF2A303C, Theme.BORDER, h));
        g.renderItem(Shop.stack(CATS.get(i).icon()), x1 + 8, y + 7);
        g.fill(x1 + 30, y + 6, x1 + 31, y + 24, sel ? 0x80FFFFFF : 0x604A5366);
        text(g, CATS.get(i).label(), x1 + 40, y + 11, sel ? Theme.TEXT : Theme.mix(Theme.SUBTEXT, Theme.TEXT, h));
    }

    /** 왼쪽 아래 작은 버튼: 위에 이름, 아래 아이콘 (참고 사진). */
    private void small(GuiGraphics g, int i, int mx, int my) {
        int x = smallX(i), y = smallY();
        boolean hov = mx >= x && mx < x + SW && my >= y && my < y + 46;
        float h = anim.to("s" + i, hov);
        Theme.panel(g, x, y, x + SW, y + 46, Theme.mix(0xC0181B22, 0xF0343A47, h), Theme.mix(0xFF2A303C, Theme.ACCENT, h));
        center(g, SMALL.get(i).label(), x + SW / 2, y + 7, Theme.mix(Theme.SUBTEXT, Theme.TEXT, h));
        g.renderItem(Shop.stack(SMALL.get(i).icon()), x + SW / 2 - 8, y + 22);
    }

    private void tile(GuiGraphics g, int i, int mx, int my) {
        Tile t = tiles().get(i);
        int x = tileX(i), y = tileY(i);
        boolean hov = mx >= x && mx < x + TILE && my >= y && my < y + TILE;
        float h = anim.to(cat * 10 + i, hov);
        float sc = t.action().equals(pressed) ? Theme.press(pressedAt) : 1f;
        g.pose().pushPose();
        g.pose().translate(x + TILE / 2f, y + TILE / 2f, 0);   // 누르면 0.97배 (배치는 그대로)
        g.pose().scale(sc, sc, 1);
        g.pose().translate(-TILE / 2f, -TILE / 2f, 0);
        Theme.panel(g, 0, 0, TILE, TILE, Theme.mix(0xE01C2029, 0xF0363D4C, h), Theme.mix(0xFF3A4152, Theme.ACCENT, h));
        boolean locked = !tutorialDone && t.action().startsWith("warp:");
        g.pose().pushPose();
        g.pose().translate(TILE / 2f - 12, 8, 0);
        g.pose().scale(1.5f, 1.5f, 1);
        g.renderItem(Shop.stack(t.icon()), 0, 0);
        g.pose().popPose();
        g.hLine(8, TILE - 9, 40, 0x604A5366);
        center(g, Theme.fit(font, t.label(), TILE - 6), TILE / 2, 47, locked ? Theme.SUBTEXT : Theme.TEXT);
        if (locked) g.fill(1, 1, TILE - 1, TILE - 1, 0x90101319);
        g.pose().popPose();
    }

    /** 내 정보: 얼굴·[칭호] 닉네임, 잡은/마주친 포켓몬 막대 | 잔액·배지. */
    private void card(GuiGraphics g) {
        int x = cx(), y = cardY(), cw = cw(), split = x + cw * 62 / 100;
        Theme.panel(g, x, y, x + cw, y + CARD_H, 0xD0181B22, 0xFF2A303C);
        if (minecraft != null && minecraft.player != null) {
            var skin = minecraft.getSkinManager().getInsecureSkin(minecraft.player.getGameProfile()).texture();
            g.blit(skin, x + 10, y + 8, 14, 14, 8, 8, 8, 8, 64, 64);
            g.blit(skin, x + 10, y + 8, 14, 14, 40, 8, 8, 8, 64, 64);
            Component name = Nicknames.SHOWN.getOrDefault(minecraft.player.getUUID(), Component.literal(minecraft.player.getGameProfile().getName()));
            g.pose().pushPose();
            g.pose().translate(x + 30, y + 10, 0);
            g.pose().scale(1.4f, 1.4f, 1);   // 닉네임은 크게
            g.drawString(font, name, 0, 0, Theme.TEXT, false);
            g.pose().popPose();
        }
        bar(g, x + 10, y + 30, split - x - 22, "잡은 포켓몬", caught);
        badgeCase(g, x + 10, y + 50, split - x - 22);
        bar(g, x + 10, y + 96, split - x - 22, "마주친 포켓몬", seen);   // 배지 칸(y+61~87) 아래로 띄움
        g.fill(split, y + 10, split + 1, y + CARD_H - 10, 0x604A5366);
        int rx = split + 12;
        text(g, "잔액", rx, y + 14, Theme.SUBTEXT);
        text(g, Theme.money(font, balance, "원", x + cw - rx - 10), rx, y + 26, Theme.GOLD);
        text(g, "레벨 제한", rx, y + 50, Theme.SUBTEXT);
        text(g, cap > 0 ? "Lv. " + cap : "-", rx, y + 62, Theme.TEXT);
    }

    /** 배지 칸 8개: 얻은 배지는 배지 그림, 못 얻은 배지는 모양만(어두운 실루엣). 배지는 순서대로만 얻으므로 개수로 판단. */
    private void badgeCase(GuiGraphics g, int x, int y, int w) {
        text(g, "배지", x, y, Theme.SUBTEXT);
        text(g, badges + " / 8", x + w - w(badges + " / 8"), y, Theme.TEXT);
        int slot = Math.min(26, (w + 4) / 8 - 4), step = (w - slot) / 7;
        for (int i = 0; i < 8; i++) {
            int sx = x + i * step, sy = y + 11;
            Theme.panel(g, sx, sy, sx + slot, sy + slot, 0xC0101319, i < badges ? 0xFF6A5A2A : 0xFF2A303C);
            var tex = net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("pokeserver", "textures/item/badge_" + (i + 1) + ".png");
            if (i >= badges) g.setColor(0.1f, 0.11f, 0.14f, 1f);   // 못 얻은 배지: 색 없이 모양만 (거의 검은 실루엣)
            int ix = sx + (slot - 16) / 2, iy = sy + (slot - 16) / 2;
            g.blit(tex, ix, iy, 0, 0, 16, 16, 16, 16);
            g.setColor(1f, 1f, 1f, 1f);
        }
    }

    private void bar(GuiGraphics g, int x, int y, int w, String label, int n) {
        String v = total > 0 ? n + " / " + total + " · " + String.format("%.1f%%", 100.0 * n / total) : "-";
        text(g, label, x, y, Theme.SUBTEXT);
        text(g, v, x + w - w(v), y, Theme.TEXT);
        g.fill(x, y + 11, x + w, y + 14, 0xFF2A303C);
        if (total > 0) g.fill(x, y + 11, x + Math.max(n > 0 ? 1 : 0, w * n / total), y + 14, Theme.ACCENT);
    }

    @Override
    public boolean mouseClicked(double rmx, double rmy, int button) {
        double mx = rmx / k, my = rmy / k;
        for (int i = 0; i < CATS.size(); i++) {
            if (mx >= 16 && mx < side() - 16 && my >= catY(i) && my < catY(i) + 30) { cat = i; return true; }
        }
        for (int i = 0; i < SMALL.size(); i++) {
            if (mx >= smallX(i) && mx < smallX(i) + SW && my >= smallY() && my < smallY() + 46) { act(SMALL.get(i).action()); return true; }
        }
        for (int i = 0; i < tiles().size(); i++) {
            int x = tileX(i), y = tileY(i);
            if (mx >= x && mx < x + TILE && my >= y && my < y + TILE) {
                Tile t = tiles().get(i);
                if (!tutorialDone && t.action().startsWith("warp:")) { toast("튜토리얼을 끝낸 뒤에 이동할 수 있어요."); return true; }
                pressed = t.action();
                pressedAt = System.currentTimeMillis();
                act(pressed);
                return true;
            }
        }
        return super.mouseClicked(rmx, rmy, button);
    }

    private void act(String a) {
        boolean cobble = FabricLoader.getInstance().isModLoaded("cobblemon");
        if (a.equals("client:party")) {
            if (cobble && !CobblemonClientHooks.openParty()) {   // 파티가 비었으면 스타팅 포켓몬 고르기 (서버가 튜토리얼·선택 여부 확인)
                onClose();
                ClientPlayNetworking.send(new Net.MenuAction("starter"));
            }
        } else if (a.equals("client:dex")) {
            if (cobble) CobblemonClientHooks.openDex();
        } else if (a.equals("help")) {
            onClose();
            if (minecraft != null && minecraft.player != null) minecraft.player.connection.sendCommand("명령어");   // 목록은 서버(PokeServer.HELP) 한 곳에서
        } else {
            onClose();
            ClientPlayNetworking.send(new Net.MenuAction(a));
        }
    }

    private void toast(String s) {
        if (minecraft != null && minecraft.player != null) minecraft.player.displayClientMessage(Component.literal(s).withStyle(ChatFormatting.GRAY), false);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
