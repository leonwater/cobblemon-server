package com.pokeserver.mixin;

import com.pokeserver.PokeServer;
import java.util.UUID;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 시험용: 서버를 -Dpokeserver.gimmicklog=true 로 켜면 배틀 엔진(쇼다운) 메시지 중 특수 기믹 줄을 서버 로그에 [기믹]으로 남김
 *  (관장·플레이어가 메가·Z·다이맥스·테라스탈을 실제로 썼는지 근거로 확인). 평소엔 꺼짐. */
@Pseudo
@Mixin(targets = "com.cobblemon.mod.common.battles.ShowdownInterpreter", remap = false)
abstract class GimmickLogMixin {
    private static final boolean ON = Boolean.getBoolean("pokeserver.gimmicklog");

    @Inject(method = "interpretMessage", at = @At("HEAD"), require = 0)   // 시험용이라 Cobblemon이 바뀌어 못 붙어도 서버는 켜지게
    private void pokeserver$log(UUID battle, String message, CallbackInfo ci) {
        if (!ON) return;
        for (String line : message.split("\n")) {
            if (line.startsWith("|request|")) {   // 선택 요청: 이번 턴에 쓸 수 있는 기믹만 (쇼다운이 canMegaEvo 등으로 알려 줌)
                var side = java.util.regex.Pattern.compile("\"id\":\"(p\\d)\"").matcher(line);
                StringBuilder can = new StringBuilder();
                for (String k : new String[]{"canMegaEvo", "canZMove", "canDynamax", "canTerastallize", "canUltraBurst"}) if (line.contains("\"" + k + "\"")) can.append(k).append(' ');
                var mon = java.util.regex.Pattern.compile("\"details\":\"([^\",]+)").matcher(line);   // 나와 있는(첫째) 포켓몬
                if (can.length() > 0) PokeServer.LOG.info("[기믹 가능] {} {} {}", side.find() ? side.group(1) : "?", mon.find() ? mon.group(1) : "?", can);
                continue;
            }
            if (line.contains("|-mega|") || line.contains("|-zpower|") || line.contains("|-burst|") || line.contains("|-terastallize|")
                    || line.contains("Dynamax") || line.contains("Gmax") || line.contains("|-primal|") || line.startsWith("|win|"))
                PokeServer.LOG.info("[기믹] {}", line);
        }
    }
}
