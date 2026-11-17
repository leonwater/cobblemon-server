package com.pokeserver.client;

import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.Screen;

/** 개발용: -Dpokeserver.shot=shop,shop_sell,claim 처럼 실행하면 화면을 차례로 띄워 스크린샷을 찍고 종료 (게임 플레이엔 영향 없음). */
final class DevShot {
    private DevShot() {}
    private static int ticks;

    static void register() {
        String prop = System.getProperty("pokeserver.shot");
        if (prop == null) return;
        String[] shots = prop.split(",");
        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            if (ticks == 0 && (mc.screen == null || mc.getOverlay() != null)) return;  // 리소스 로딩이 끝난 뒤부터
            int i = ticks / 40, t = ticks++ % 40;
            if (i >= shots.length) { mc.stop(); return; }
            if (t == 0) mc.setScreen(screen(shots[i]));
            if (t == 30) Screenshot.grab(mc.gameDirectory, shots[i] + ".png", mc.getMainRenderTarget(), m -> {});
        });
    }

    private static Screen screen(String which) {
        if (which.equals("claim")) return new ClaimScreen(3);
        if (which.startsWith("menu")) {
            MenuScreen m = new MenuScreen(123456, "도움이 필요하면 관리자에게 문의하세요!");
            m.tab = which.equals("menu_warp") ? 2 : 0;
            return m;
        }
        try {
            ShopScreen s = new ShopScreen(Files.readString(Path.of(System.getProperty("pokeserver.shopjson"))), 123456);
            s.category = which.equals("shop_sell") ? 5 : which.equals("shop_balls") ? 0 : 3;
            s.sell = which.equals("shop_sell");
            return s;
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
