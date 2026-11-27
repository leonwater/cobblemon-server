package com.pokeserver.client;

import net.minecraft.client.Minecraft;

/** 배틀 화면 크기: 참고 사진처럼 GUI 2.5배 크기로 그림 (전체 화면 자동 크기 4배보다 작게).
 *  Cobblemon 배틀 화면은 창 크기(Window.getGuiScaledWidth)를 직접 읽어 배치하므로,
 *  배틀 화면을 그리거나 마우스를 처리하는 동안만 창 크기를 1/f 로 보이게 하고 그림을 f배로 줄임 (믹스인). */
public final class BattleScale {
    private BattleScale() {}

    static final double TARGET = 2.5;
    /** 배틀 화면 코드 안: 창 크기를 늘려 보이게 (WindowMixin). */
    public static boolean on;
    public static boolean inside;

    public static float f() {
        double s = Minecraft.getInstance().getWindow().getGuiScale();
        return s > TARGET ? (float) (TARGET / s) : 1f;
    }

    /** 화면 1 GUI 픽셀이 실제 몇 픽셀인지 (배틀 화면 안 = GUI 크기 × 줄임 비율). */
    public static float pixels() { return (float) Minecraft.getInstance().getWindow().getGuiScale() * f(); }

    /** 2. 화면 아래 HUD(핫바·체력·배고픔·경험치) 배율: 참고 사진처럼 1080p에서 1 GUI 픽셀 = 3 픽셀 (GUI 크기 3과 같은 비율).
     *  창 높이에 비례하므로 화면이 커져도 같은 비율. GUI 크기를 더 작게 골랐으면 그대로. */
    public static float hudScale() {
        var w = Minecraft.getInstance().getWindow();
        return (float) Math.min(1, 3.0 * w.getHeight() / 1080 / w.getGuiScale());
    }

    /** 7. 배틀 기록 글자 배율: 원래보다 한 단계 크고, 한 점이 정수 픽셀 (2.5배 화면이면 1.0 → 1.2 = 3픽셀). 소수 픽셀이면 픽셀 글꼴 획이 들쭉날쭉 깨짐. */
    public static float crisp(float k) {
        float px = pixels();
        return (float) (Math.floor(k * px + 1e-3) + 1) / px;
    }

    /** 배틀 중 (배틀 화면을 닫아 둔 동안도): 미니맵·오른쪽 정보창을 숨김 (배틀 체력 판·기록과 겹쳐서). */
    public static boolean inBattle() {
        return net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon") && CobblemonClientHooks.inBattle();
    }

    public static boolean isBattle(Object screen) {
        return screen != null && screen.getClass().getName().equals("com.cobblemon.mod.common.client.gui.battle.BattleGUI");
    }
    /** 행동 선택이 HUD(하트·배고픔 줄)를 덮으면 위로 올리는 양 (배틀 좌표). 타일 오른쪽 끝(배틀 좌표 12+93+90)이 하트 줄 왼쪽 끝보다 왼쪽이면 0. */
    public static float lift() {
        var w = Minecraft.getInstance().getWindow();
        double guiW = w.getWidth() / w.getGuiScale(), hud = hudScale();
        if (195 * f() < guiW / 2 - 91 * hud - 2) return 0;
        return (float) Math.max(0, (39 * hud + 3) / f() - 30);
    }

    /** 5. 배틀 배속 (1·2·4). 서버가 기억, 배틀 화면을 열 때마다 다시 보냄 (다시 접속해도 맞게). */
    public static int speed = 1;
}
