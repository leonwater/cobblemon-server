package com.pokeserver.client.mixin;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 17. Extended Battle UI 기술 설명 창에 코드로 박힌 영어 낱말(위력·명중·자속 등)을 한국어로. 설명 글은 이미 한국어라 영어 낱말만 바꿈. */
@Pseudo
@Mixin(targets = "com.cobblemonextendedbattleui.MoveTooltipRenderer", remap = false)
abstract class EbuiTooltipMixin {
    @Unique private static final Map<String, String> KO = Map.ofEntries(
            Map.entry("Power", "위력"), Map.entry("Accuracy", "명중"), Map.entry("Effect", "추가효과"), Map.entry("Priority", "우선도"),
            Map.entry("Crit", "급소"), Map.entry("STAB", "자속"), Map.entry("Status", "변화"), Map.entry("Fast", "빠름"), Map.entry("Slow", "느림"),
            Map.entry("Sheer Force", "우격다짐"), Map.entry("N/A", "없음"), Map.entry("Rain", "비"), Map.entry("Sun", "쾌청"),
            Map.entry("Sandstorm", "모래바람"), Map.entry("Hail", "싸라기눈"), Map.entry("Snow", "설경"));
    @Unique private static final Pattern WORDS = Pattern.compile("Sheer Force|N/A|\\b(Power|Accuracy|Effect|Priority|Crit|STAB|Status|Fast|Slow|Rain|Sun|Sandstorm|Hail|Snow)\\b");

    @ModifyVariable(method = {"draw", "drawRightAligned"}, at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private String pokeserver$ko(String s) {
        if (s == null) return null;
        Matcher m = WORDS.matcher(s);
        return m.find() ? m.reset().replaceAll(r -> KO.get(r.group())) : s;
    }
}
