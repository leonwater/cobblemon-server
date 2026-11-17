package com.pokeserver.client;

import com.pokeserver.Net;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** 6. 땅 문서 확인 팝업. */
public class ClaimScreen extends Screen {
    private static final int W = 220, H = 96;
    private final int plot;

    public ClaimScreen(int plot) {
        super(Component.literal("땅 등록"));
        this.plot = plot;
    }

    @Override
    protected void init() {
        int x = (width - W) / 2, y = (height - H) / 2;
        addRenderableWidget(Button.builder(Component.literal("확인"), b -> {
            ClientPlayNetworking.send(new Net.ClaimConfirm(plot));
            onClose();
        }).bounds(x + 16, y + H - 30, 88, 20).build());
        addRenderableWidget(Button.builder(Component.literal("취소"), b -> onClose())
                .bounds(x + W - 104, y + H - 30, 88, 20).build());
    }

    @Override
    public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
        super.renderBackground(g, mx, my, pt);
        int x = (width - W) / 2, y = (height - H) / 2;
        Theme.panel(g, x, y, x + W, y + H, Theme.PANEL);
        g.fill(x, y, x + W, y + 18, Theme.TILE);
        g.drawCenteredString(font, "땅 등록", width / 2, y + 5, Theme.TEXT);
        g.drawCenteredString(font, "농장 " + plot + "번 땅을 내 땅으로 등록할까요?", width / 2, y + 30, Theme.TEXT);
        g.drawCenteredString(font, "땅 문서 1장이 사용됩니다.", width / 2, y + 44, Theme.SUBTEXT);
    }

    @Override
    public boolean isPauseScreen() { return false; }
}
