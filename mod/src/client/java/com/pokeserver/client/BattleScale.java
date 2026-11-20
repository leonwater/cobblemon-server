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

    public static boolean isBattle(Object screen) {
        return screen != null && screen.getClass().getName().equals("com.cobblemon.mod.common.client.gui.battle.BattleGUI");
    }
}
