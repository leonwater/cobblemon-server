package com.pokeserver.client;

import com.pokeserver.Net;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
import org.lwjgl.glfw.GLFW;

/** 3. 오박사의 튜토리얼: 쪽마다 실제 게임 화면(textures/gui/tutorial/*.png, 640×360) + 설명. 마지막 쪽 "준비 완료!" → 회의장 + 스타팅 포켓몬. */
public class TutorialScreen extends Screen {
    record Page(String img, String title, String text) {}

    static final List<Page> PAGES = List.of(
            new Page("catch", "포켓몬 잡기", "야생에서 몬스터볼을 들고 우클릭하면 던져서 잡을 수 있다네. HP를 줄이거나 잠듦·마비 상태로 만들면 더 잘 잡히지."),
            new Page("battle", "배틀", "왼쪽의 내 파티에서 ↑↓ 키로 포켓몬을 고르고, 야생 포켓몬을 보며 R 키를 누르면 배틀 시작! 기술을 골라 싸우고 이기면 경험치를 얻는다네."),
            new Page("summary", "상태창 (M 키)", "M 키로 포켓몬의 능력치·기술·성격을 볼 수 있다네. 기술 바꾸기, 도구 들려 주기, 진화도 여기서 하지."),
            new Page("menu", "메인 메뉴 (G 키)", "G 키로 파티·PC·도감을 바로 열 수 있고, 광장·상점가·야생·농장·체육관으로 순간이동할 수도 있다네."),
            new Page("shop", "상점", "상점가 프렌들리 숍의 점원을 우클릭하면 사고팔 수 있지. 상품을 누르고 수량을 정한 뒤 구매하기! 배지를 모을수록 상품이 늘어난다네."),
            new Page("center", "포켓몬센터", "지친 포켓몬은 포켓몬센터의 회복 장치에서 회복시켜 주게. PC에 포켓몬을 맡기거나 꺼낼 수도 있다네."),
            new Page("gym", "체육관", "체육관 안내원에게 말을 걸면 도전할 관장을 고를 수 있다네. 이기면 배지를 받고 레벨 제한이 10씩 오르지. 도전은 한 번에 한 명씩!"),
            new Page("plaza", "서버 규칙", "포켓몬 말고 다른 몬스터·동물은 없고 배고픔도 없다네. 죽어도 아이템은 그대로, 폭발로 블록이 부서지지 않지. 잔액은 /money, 송금은 /pay."),
            new Page("starter", "스타팅 포켓몬", "준비가 되면 아래 버튼을 누르게! 회의장으로 보내 주고, 무작위로 정해진 세대의 스타팅 포켓몬 3마리 중 한 마리를 고르게 해 주지."));
    static final ResourceLocation FACE = ResourceLocation.fromNamespaceAndPath("pokeserver", "textures/npcs/tutorial_guide.png");

    private final Theme.Anim anim = new Theme.Anim();
    private int page;

    public TutorialScreen() {
        super(Component.literal("오박사의 튜토리얼"));
    }

    // ── 배치 (전체 화면 480×270 GUI px, 작은 창 426×240에서도 겹치지 않음) ──
    private int pw() { return Math.max(300, Math.min(width - 16, 400)); }
    private int ph() { return Math.max(200, Math.min(height - 16, 256)); }
    private int px() { return (width - pw()) / 2; }
    private int py() { return (height - ph()) / 2; }
    private int btnY() { return py() + ph() - 26; }
    private List<FormattedCharSequence> lines() { return font.split(Theme.t(PAGES.get(page).text()), pw() - 24); }
    private int imgH() {
        int textTop = btnY() - 6 - 3 * 12;                       // 설명은 최대 3줄
        return Math.min((pw() - 24) * 9 / 16, textTop - 6 - (py() + 40));
    }
    private int imgW() { return imgH() * 16 / 9; }
    private int btnW() { return Math.min(96, (pw() - 40) / 3); }
    private int btnX(int i) { return i == 0 ? px() + 10 : px() + pw() - 10 - btnW(); }

    private void text(GuiGraphics g, String s, int x, int y, int color) { g.drawString(font, Theme.t(s), x, y, color, false); }
    private int w(String s) { return font.width(Theme.t(s)); }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        anim.frame();
        g.fillGradient(0, 0, width, height, 0x90000000, 0x60000000);
        int px = px(), py = py(), pw = pw(), ph = ph();
        Theme.panel(g, px, py, px + pw, py + ph, Theme.PANEL);
        // 머리: 오박사 얼굴 + 이름, 오른쪽에 쪽 번호
        g.fillGradient(px + 1, py + 1, px + pw - 1, py + 22, 0xFF2A3140, 0xFF181C24);
        g.hLine(px + 1, px + pw - 2, py + 22, Theme.BORDER);
        g.blit(FACE, px + 6, py + 5, 12, 12, 8, 8, 8, 8, 64, 64);
        g.blit(FACE, px + 6, py + 5, 12, 12, 40, 8, 8, 8, 64, 64);
        text(g, "오박사", px + 24, py + 8, Theme.GOLD);
        String num = (page + 1) + " / " + PAGES.size();
        text(g, num, px + pw - 8 - w(num), py + 8, Theme.SUBTEXT);
        // 쪽 제목
        Page p = PAGES.get(page);
        text(g, Theme.fit(font, p.title(), pw - 20), px + 10, py + 28, Theme.TEXT);
        // 실제 게임 화면
        int iw = imgW(), ih = imgH(), ix = (width - iw) / 2, iy = py + 40;
        g.fill(ix - 1, iy - 1, ix + iw + 1, iy + ih + 1, Theme.BORDER);
        g.blit(ResourceLocation.fromNamespaceAndPath("pokeserver", "textures/gui/tutorial/" + p.img() + ".png"),
                ix, iy, iw, ih, 0, 0, 640, 360, 640, 360);
        // 설명 (최대 3줄)
        var ls = lines();
        int ty = iy + ih + 6;
        for (int i = 0; i < Math.min(3, ls.size()); i++) g.drawString(font, ls.get(i), px + 12, ty + i * 12, Theme.TEXT, false);
        // 아래: 이전 · 쪽 점 · 다음/준비 완료
        if (page > 0) button(g, 0, "이전", mx, my, false);
        boolean last = page == PAGES.size() - 1;
        button(g, 1, last ? "준비 완료!" : "다음", mx, my, last);
        int dots = PAGES.size() * 8 - 4, dx = (width - dots) / 2;
        for (int i = 0; i < PAGES.size(); i++) g.fill(dx + i * 8, btnY() + 8, dx + i * 8 + 4, btnY() + 12, i == page ? Theme.ACCENT : 0xFF3A4152);
    }

    private void button(GuiGraphics g, int i, String label, int mx, int my, boolean gold) {
        int x = btnX(i), y = btnY(), bw = btnW();
        boolean hov = mx >= x && mx < x + bw && my >= y && my < y + 20;
        float h = anim.to("b" + i, hov);
        int border = gold ? Theme.GOLD : Theme.mix(Theme.BORDER, Theme.ACCENT, h);
        Theme.panel(g, x, y, x + bw, y + 20, Theme.mix(gold ? 0xE0403418 : 0xE0262C38, gold ? 0xF0584826 : 0xF0384256, h), border);
        String s = Theme.fit(font, label, bw - 8);
        text(g, s, x + (bw - w(s)) / 2, y + 6, gold ? Theme.GOLD : Theme.TEXT);
    }

    private void go(int d) {
        if (d > 0 && page == PAGES.size() - 1) {
            onClose();
            ClientPlayNetworking.send(new Net.MenuAction("tutorial_done"));
            return;
        }
        page = Math.max(0, Math.min(PAGES.size() - 1, page + d));
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        if (my >= btnY() && my < btnY() + 20) {
            if (page > 0 && mx >= btnX(0) && mx < btnX(0) + btnW()) { go(-1); return true; }
            if (mx >= btnX(1) && mx < btnX(1) + btnW()) { go(1); return true; }
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (key == GLFW.GLFW_KEY_RIGHT || key == GLFW.GLFW_KEY_ENTER || key == GLFW.GLFW_KEY_SPACE) { go(1); return true; }
        if (key == GLFW.GLFW_KEY_LEFT) { go(-1); return true; }
        return super.keyPressed(key, scan, mods);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
