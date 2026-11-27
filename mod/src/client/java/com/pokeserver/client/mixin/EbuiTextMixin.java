package com.pokeserver.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 17. Extended Battle UI에 코드로 박힌 영어(언어 파일에 없는 것)만 한국어로: BATTLE INFO, T1, Turn 1, No battle messages, 체력 변화 줄. */
@Pseudo
@Mixin(targets = {"com.cobblemonextendedbattleui.UIUtils", "com.cobblemonextendedbattleui.BattleLogWidget"}, remap = false)
abstract class EbuiTextMixin {
    @ModifyVariable(method = "drawText", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private String pokeserver$koLog(String s) { return pokeserver$tr(s); }

    @Unique private static final java.util.regex.Pattern HP = java.util.regex.Pattern.compile("^(\\s*\\S\\s)(\\+?)([\\d.]+%) to (.+)$");

    @Unique
    private static String pokeserver$tr(String s) {
        if (s == null) return null;
        if (s.equals("BATTLE INFO")) return "배틀 정보";
        if (s.equals("No battle messages")) return "배틀 기록 없음";
        if (s.matches("T\\d+")) return s.substring(1) + "턴";
        if (s.matches("Turn \\d+")) return s.substring(5) + "턴";
        // 체력 변화 줄 "→ 100% to 뿔카노" / "→ +25% to 거북왕" (DamageTracker)
        var m = HP.matcher(s);
        if (m.matches()) return m.group(1) + m.group(4) + " " + m.group(3) + (m.group(2).isEmpty() ? " 피해" : " 회복");
        return s;
    }
}
