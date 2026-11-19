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

/** 5. 메인 메뉴 (G키). 처음 방향(평평한 어두운 반투명 칸, 1픽셀 테두리), 참고 사진처럼 같은 크기 칸.
 *  위: 제목 + 레벨 제한·잔액, 가운데: 주요 메뉴 4×2 (파티·PC·도감 + 워프 5곳), 아래: 공지 + 작은 버튼(튜토리얼·휴지통·명령어 / 닫기). */
public class MenuScreen extends Screen {
    record Tile(String label, String icon, String action) {}

    static final List<Tile> TILES = List.of(
            new Tile("내 파티", "cobblemon:poke_ball", "client:party"),
            new Tile("PC", "cobblemon:pc", "pc"),
            new Tile("도감", "cobblemon:pokedex_red", "client:dex"),
            new Tile("체육관", "minecraft:red_banner", "warp:gym"),
            new Tile("광장", "minecraft:beacon", "warp:hall"),
            new Tile("상점가", "minecraft:emerald", "warp:street"),
            new Tile("야생", "minecraft:grass_block", "warp:wild"),
            new Tile("농장", "minecraft:wheat", "warp:farm"));
    /** 자주 안 쓰는 것: 아래 줄 작은 버튼 (닫기는 오른쪽 끝). */
    static final List<Tile> SMALL = List.of(
            new Tile("튜토리얼", "minecraft:book", "tutorial"),
            new Tile("휴지통", "minecraft:cauldron", "trash"),
            new Tile("명령어", "minecraft:paper", "help"),
            new Tile("닫기", "minecraft:barrier", "close"));
    static final int COLS = 4, GAP = 3;

    private final long balance;
    private final String notice;
    private final boolean tutorialDone;   // 튜토리얼을 끝내기 전엔 워프 칸 잠금 (서버도 따로 막음)
    private final Theme.Anim anim = new Theme.Anim();
    private String pressed = "";
    private long pressedAt;

    public MenuScreen(long balance, String notice, boolean tutorialDone) {
        super(Component.literal("메인 메뉴"));
        this.balance = balance;
        this.notice = notice;
        this.tutorialDone = tutorialDone;
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

    // ── 배치: 화면 크기에서 계산 (전체 화면 480×270 GUI px, 작은 창 426×240에서도 겹치지 않음) ──
    private int pw() { return Math.max(300, Math.min(width - 16, 380)); }
    private int ph() { return Math.max(200, Math.min(height - 16, 250)); }
    private int px() { return (width - pw()) / 2; }
    private int py() { return (height - ph()) / 2; }
    private int gx() { return px() + 10; }                      // 격자 틀 안쪽 시작
    private int gy() { return py() + 30; }
    private int gw() { return pw() - 20; }
    private int btnY() { return py() + ph() - 26; }
    private int noticeY() { return btnY() - 23; }
    private int tileW() { return (gw() - 8 - GAP * (COLS - 1)) / COLS; }
    private int tileH() { return Math.min(tileW(), (noticeY() - 6 - gy() - 8 - GAP) / 2); }   // 참고 사진처럼 거의 정사각형
    private int gh() { return tileH() * 2 + GAP + 8; }
    private int tileX(int i) { return gx() + 4 + (i % COLS) * (tileW() + GAP) + (gw() - 8 - COLS * tileW() - GAP * (COLS - 1)) / 2; }
    private int tileY(int i) { return gy() + 4 + (i / COLS) * (tileH() + GAP); }
    private int btnW(int i) { return w(SMALL.get(i).label()) + 26; }
    private int btnX(int i) {                                  // 왼쪽부터 차례로, 마지막(닫기)만 오른쪽 끝
        if (i == SMALL.size() - 1) return gx() + gw() - btnW(i);
        int x = gx();
        for (int k = 0; k < i; k++) x += btnW(k) + 4;
        return x;
    }

    private void text(GuiGraphics g, String s, int x, int y, int color) { g.drawString(font, Theme.t(s), x, y, color, false); }
    private void center(GuiGraphics g, String s, int cx, int y, int color) { text(g, s, cx - font.width(Theme.t(s)) / 2, y, color); }
    private int w(String s) { return font.width(Theme.t(s)); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        // 자주 여는 화면이라 여는 애니메이션은 없음
        g.fillGradient(0, 0, width, height, 0x90000000, 0x60000000);
        int px = px(), py = py(), pw = pw(), ph = ph();
        Theme.panel(g, px, py, px + pw, py + ph, Theme.PANEL);
        // 제목 줄: 가운데 제목, 왼쪽 레벨 제한, 오른쪽 잔액
        g.fillGradient(px + 1, py + 1, px + pw - 1, py + 22, 0xFF2A3140, 0xFF181C24);
        g.hLine(px + 1, px + pw - 2, py + 22, Theme.BORDER);
        center(g, "메인 메뉴", width / 2, py + 8, Theme.TEXT);
        int cap = minecraft != null && minecraft.player != null ? levelCap(minecraft.player) : -1;
        g.renderItem(Shop.stack("cobblemon:poke_ball"), px + 5, py + 3);   // 포켓몬 레벨 제한
        text(g, "포켓몬 레벨 제한 " + (cap > 0 ? "Lv" + cap : "-"), px + 23, py + 8, Theme.ACCENT);
        String money = String.format("%,d원", balance);
        text(g, money, px + pw - 8 - w(money), py + 8, Theme.GOLD);
        g.renderItem(Shop.stack("minecraft:gold_nugget"), px + pw - 26 - w(money), py + 3);
        // 격자 틀 (참고 사진처럼 한 단계 어두운 판 위에 칸)
        Theme.panel(g, gx(), gy(), gx() + gw(), gy() + gh(), 0xC00A0C10, 0xFF2A303C);
        for (int i = 0; i < TILES.size(); i++) tile(g, i, mx, my);
        // 공지 (잘리면 마우스를 올려 전체 보기)
        int ny = noticeY();
        Theme.panel(g, gx(), ny, gx() + gw(), ny + 18, 0xC0181B22, 0xFF2A303C);
        text(g, "공지", gx() + 6, ny + 5, Theme.ACCENT);
        String shown = Theme.fit(font, notice, gw() - w("공지") - 18);
        text(g, shown, gx() + 12 + w("공지"), ny + 5, Theme.GOLD);
        if (!shown.equals(notice) && mx >= gx() && mx < gx() + gw() && my >= ny && my < ny + 18) {
            g.renderComponentTooltip(font, font.getSplitter().splitLines(Theme.t(notice), 220, net.minecraft.network.chat.Style.EMPTY).stream()
                    .map(l -> (Component) Theme.t(l.getString())).toList(), mx, my);
        }
        for (int i = 0; i < SMALL.size(); i++) button(g, i, mx, my);
    }

    private void tile(GuiGraphics g, int i, int mx, int my) {
        int x = tileX(i), y = tileY(i), tw = tileW(), th = tileH();
        boolean hov = mx >= x && mx < x + tw && my >= y && my < y + th;
        float h = anim.to(i, hov);
        float sc = TILES.get(i).action().equals(pressed) ? Theme.press(pressedAt) : 1f;
        g.pose().pushPose();
        g.pose().translate(x + tw / 2f, y + th / 2f, 0);   // 누르면 0.97배 (배치는 그대로)
        g.pose().scale(sc, sc, 1);
        g.pose().translate(-tw / 2f, -th / 2f, 0);
        Theme.panel(g, 0, 0, tw, th, Theme.mix(0xE01C2029, 0xF0363D4C, h), Theme.mix(0xFF2E3442, Theme.ACCENT, h));
        // 아이콘 · 이름을 세로 가운데로. 튜토리얼 전엔 워프 칸을 흐리게 (누르면 안내만)
        boolean locked = !tutorialDone && TILES.get(i).action().startsWith("warp:");
        int block = 24 + 4 + 9, top = Math.max(3, (th - block) / 2);
        g.pose().pushPose();
        g.pose().translate(tw / 2f - 12, top, 0);
        g.pose().scale(1.5f, 1.5f, 1);
        g.renderItem(Shop.stack(TILES.get(i).icon()), 0, 0);
        g.pose().popPose();
        center(g, Theme.fit(font, TILES.get(i).label(), tw - 6), tw / 2, top + 28, locked ? Theme.SUBTEXT : Theme.TEXT);
        if (locked) g.fill(1, 1, tw - 1, th - 1, 0x90101319);
        g.pose().popPose();
    }

    /** 작은 버튼: 아이콘 + 이름, 높이 18 (주요 칸보다 눈에 덜 띄게 흐린 글씨). */
    private void button(GuiGraphics g, int i, int mx, int my) {
        int x = btnX(i), y = btnY(), bw = btnW(i);
        boolean hov = mx >= x && mx < x + bw && my >= y && my < y + 18;
        float h = anim.to("b" + i, hov);
        Theme.panel(g, x, y, x + bw, y + 18, Theme.mix(0xC0181B22, 0xF0343A47, h), Theme.mix(0xFF2A303C, Theme.ACCENT, h));
        g.renderItem(Shop.stack(SMALL.get(i).icon()), x + 3, y + 1);
        text(g, SMALL.get(i).label(), x + 21, y + 5, Theme.mix(Theme.SUBTEXT, Theme.TEXT, h));
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        for (int i = 0; i < TILES.size(); i++) {
            int x = tileX(i), y = tileY(i);
            if (mx >= x && mx < x + tileW() && my >= y && my < y + tileH()) {
                if (!tutorialDone && TILES.get(i).action().startsWith("warp:")) { toast("튜토리얼을 끝낸 뒤에 이동할 수 있어요."); return true; }
                pressed = TILES.get(i).action();
                pressedAt = System.currentTimeMillis();
                act(pressed);
                return true;
            }
        }
        if (my >= btnY() && my < btnY() + 18) {
            for (int i = 0; i < SMALL.size(); i++) {
                if (mx < btnX(i) || mx >= btnX(i) + btnW(i)) continue;
                switch (SMALL.get(i).action()) {
                    case "help" -> help();
                    case "close" -> onClose();
                    default -> act(SMALL.get(i).action());
                }
                return true;
            }
        }
        return super.mouseClicked(mx, my, button);
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
        } else {
            onClose();
            ClientPlayNetworking.send(new Net.MenuAction(a));
        }
    }

    private void help() {
        onClose();
        for (String line : new String[]{"── 기본 명령어 ──", "G 키: 메인 메뉴", "/money (/돈): 잔액", "/pay 닉네임 금액 (/송금): 돈 보내기",
                "/trigger home: 회의장으로", "/초기화: 모든 진행 삭제 (확인 필요)", "R 키: 포켓몬 꺼내기 · M 키: 상태창 · ↑↓: 파티 선택"}) toast(line);
    }

    private void toast(String s) {
        if (minecraft != null && minecraft.player != null) minecraft.player.displayClientMessage(Component.literal(s).withStyle(ChatFormatting.GRAY), false);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
