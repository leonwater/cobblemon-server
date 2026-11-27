package com.pokeserver.client;

import com.cobblemon.mod.common.api.item.PokemonSelectingItem;
import com.cobblemon.mod.common.client.CobblemonClient;
import com.cobblemon.mod.common.item.PokeBallItem;
import com.cobblemon.mod.common.pokemon.Pokemon;
import com.pokeserver.Net;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/** 2. 배틀 가방 (배틀 화면의 "가방" 버튼): 회복 도구 → 대상 포켓몬 → 사용, 야생 배틀이면 볼 → 손에 쥐고 던지기.
 *  실제 사용은 서버가 코블몬 규칙(차례·대상·사용 가능)으로 다시 검사함. 닫으면 배틀 화면으로. */
public class BagScreen extends Screen {
    private static final int W = 260, H = 196, ROW = 22;
    private final Screen back;
    private final boolean wild;
    private boolean balls;              // 탭: false = 회복, true = 볼
    private Integer pickSlot;           // 회복 도구를 고른 뒤 대상 고르는 중
    private int scroll;

    record Entry(Item item, int slot, int count, ItemStack stack) {}

    public BagScreen(Screen back, boolean wild) {
        super(Component.literal("가방"));
        this.back = back;
        this.wild = wild;
    }

    /** 가방 속 같은 종류는 한 줄로 (쓸 때는 처음 찾은 칸). */
    private List<Entry> entries() {
        Map<Item, Entry> m = new LinkedHashMap<>();
        var inv = Objects.requireNonNull(minecraft).player.getInventory();
        for (int i = 0; i < inv.items.size(); i++) {
            ItemStack st = inv.items.get(i);
            if (st.isEmpty()) continue;
            boolean ok = balls ? st.getItem() instanceof PokeBallItem
                    : st.getItem() instanceof PokemonSelectingItem psi && psi.getBagItem() != null;
            if (!ok) continue;
            Entry e = m.get(st.getItem());
            m.put(st.getItem(), e == null ? new Entry(st.getItem(), i, st.getCount(), st) : new Entry(e.item(), e.slot(), e.count() + st.getCount(), e.stack()));
        }
        return new ArrayList<>(m.values());
    }

    private List<Pokemon> party() {
        return CobblemonClient.INSTANCE.getStorage().getParty().getSlots().stream().filter(Objects::nonNull).toList();
    }

    private int x0() { return (width - W) / 2; }
    private int y0() { return (height - H) / 2; }

    @Override
    public void render(GuiGraphics g, int mx, int my, float pt) {
        if (CobblemonClient.INSTANCE.getBattle() == null) { onClose(); return; }
        int x = x0(), y = y0();
        Theme.panel(g, x, y, x + W, y + H, 0xF0101319, Theme.ACCENT);
        g.drawString(font, Theme.t(pickSlot == null ? "가방" : "누구에게 쓸까요?"), x + 10, y + 9, Theme.TEXT);
        if (pickSlot == null) {
            tab(g, mx, my, x + W - 118, "회복", !balls, true);
            tab(g, mx, my, x + W - 62, "볼", balls, wild);
            var list = entries();
            if (list.isEmpty()) g.drawCenteredString(font, Theme.t(balls ? "가방에 볼이 없어요" : "배틀에서 쓸 회복 도구가 없어요"), x + W / 2, y + H / 2, Theme.SUBTEXT);
            for (int i = 0; i < list.size(); i++) {
                int ry = y + 28 + (i - scroll) * ROW;
                if (ry < y + 26 || ry + ROW > y + H - 6) continue;
                var e = list.get(i);
                boolean hov = in(mx, my, x + 6, ry, W - 12, ROW - 2);
                Theme.panel(g, x + 6, ry, x + W - 6, ry + ROW - 2, hov ? Theme.TILE_HOVER : Theme.TILE, hov ? Theme.ACCENT : Theme.BORDER);
                g.renderItem(e.stack(), x + 10, ry + 2);
                g.drawString(font, Theme.t(Theme.fit(font, e.stack().getHoverName().getString(), W - 80)), x + 32, ry + 6, Theme.TEXT);
                String c = "x" + e.count();
                g.drawString(font, Theme.t(c), x + W - 12 - font.width(Theme.t(c)), ry + 6, Theme.SUBTEXT);
            }
        } else {
            var mons = party();
            for (int i = 0; i < mons.size(); i++) {
                var p = mons.get(i);
                int ry = y + 28 + i * 26;
                boolean hov = in(mx, my, x + 6, ry, W - 12, 24);
                Theme.panel(g, x + 6, ry, x + W - 6, ry + 24, hov ? Theme.TILE_HOVER : Theme.TILE, hov ? Theme.ACCENT : Theme.BORDER);
                g.drawString(font, Theme.t(Theme.fit(font, p.getDisplayName(false).getString(), 110) + "  Lv." + p.getLevel()), x + 12, ry + 4, Theme.TEXT);
                float r = p.getMaxHealth() == 0 ? 0 : (float) p.getCurrentHealth() / p.getMaxHealth();
                int bw = W - 70, bx = x + 12;
                g.fill(bx, ry + 15, bx + bw, ry + 19, 0xFF2A2F3A);
                g.fill(bx, ry + 15, bx + Math.round(bw * r), ry + 19, r > .5f ? 0xFF58D080 : r > .2f ? 0xFFF8C030 : 0xFFF05848);
                String hp = p.getCurrentHealth() + "/" + p.getMaxHealth();
                g.drawString(font, Theme.t(hp), x + W - 12 - font.width(Theme.t(hp)), ry + 13, Theme.SUBTEXT);
            }
        }
        g.drawCenteredString(font, Theme.t(pickSlot == null ? "클릭: 고르기  ·  ESC: 배틀로" : "ESC: 도구 다시 고르기"), x + W / 2, y + H + 6, Theme.SUBTEXT);
        super.render(g, mx, my, pt);
    }

    private void tab(GuiGraphics g, int mx, int my, int x, String label, boolean on, boolean enabled) {
        int y = y0() + 6;
        Theme.panel(g, x, y, x + 52, y + 16, on ? Theme.SELECT : enabled && in(mx, my, x, y, 52, 16) ? Theme.TILE_HOVER : Theme.TILE, on ? Theme.ACCENT : Theme.BORDER);
        g.drawCenteredString(font, Theme.t(label), x + 26, y + 4, enabled ? Theme.TEXT : 0xFF6B7280);
    }

    private static boolean in(double mx, double my, int x, int y, int w, int h) { return mx >= x && mx < x + w && my >= y && my < y + h; }

    @Override
    public boolean mouseClicked(double mx, double my, int b) {
        int x = x0(), y = y0();
        if (pickSlot == null) {
            if (in(mx, my, x + W - 118, y + 6, 52, 16)) { balls = false; scroll = 0; return true; }
            if (wild && in(mx, my, x + W - 62, y + 6, 52, 16)) { balls = true; scroll = 0; return true; }
            var list = entries();
            for (int i = 0; i < list.size(); i++) {
                int ry = y + 28 + (i - scroll) * ROW;
                if (ry < y + 26 || ry + ROW > y + H - 6 || !in(mx, my, x + 6, ry, W - 12, ROW - 2)) continue;
                if (balls) {
                    ClientPlayNetworking.send(new Net.BagBall(list.get(i).slot()));
                    Objects.requireNonNull(minecraft).setScreen(null);   // 배틀 화면을 닫아야 볼을 던질 수 있음 (코블몬 "잡기"와 같음)
                } else pickSlot = list.get(i).slot();
                return true;
            }
        } else {
            var mons = party();
            for (int i = 0; i < mons.size(); i++) {
                if (!in(mx, my, x + 6, y + 28 + i * 26, W - 12, 24)) continue;
                ClientPlayNetworking.send(new Net.BagUse(pickSlot, mons.get(i).getUuid()));
                onClose();
                return true;
            }
        }
        return super.mouseClicked(mx, my, b);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double h, double v) {
        scroll = Math.max(0, Math.min(Math.max(0, entries().size() - 7), scroll - (int) Math.signum(v)));
        return true;
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_ESCAPE && pickSlot != null) { pickSlot = null; return true; }
        return super.keyPressed(key, scan, mods);
    }

    @Override
    public void onClose() { Objects.requireNonNull(minecraft).setScreen(CobblemonClient.INSTANCE.getBattle() != null ? back : null); }

    @Override
    public boolean isPauseScreen() { return false; }
}
