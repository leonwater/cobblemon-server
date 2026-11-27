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

    /** 3. 왼쪽 아래 행동 선택(싸운다·가방·포켓몬·도망)을 키우는 배율: 원하는 1.5배에 가장 가까우면서 글자 한 점이 정수 픽셀이 되게
     *  (2.5배 화면이면 1.6배 = 4픽셀. 1.5배면 3.75픽셀이라 픽셀 글꼴이 깨짐). */
    public static float selScale() {
        float px = pixels();
        return Math.max(1, Math.round(1.5f * px)) / px;
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
}
