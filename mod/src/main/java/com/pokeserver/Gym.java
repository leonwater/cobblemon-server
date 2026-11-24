package com.pokeserver;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.server.level.ServerPlayer;

/** 3·4. 체육관 안내원 → 도전 목록. 목록 정보는 config/pokeserver/league.json (tools/build_league.py가 만듦). */
final class Gym {
    private Gym() {}
    static JsonArray info = new JsonArray();

    static void load() {
        try {
            info = JsonParser.parseString(Files.readString(FabricLoader.getInstance().getConfigDir().resolve("pokeserver/league.json"))).getAsJsonArray();
        } catch (Exception ex) {
            PokeServer.LOG.warn("리그 정보를 못 읽음 ({})", ex.toString());
        }
    }

    /** n(1~8 체육관, 9 사천왕)의 상태: cleared(클리어), open(도전 가능), null(아직 못 감 → 목록에 안 보임). */
    static String status(ServerPlayer p, int n) {
        var t = p.getTags();
        if (t.contains(n == 9 ? "poke.e4clear" : "poke.badge" + n)) return "cleared";
        return n == 1 || t.contains("poke.badge" + (n - 1)) ? "open" : null;
    }

    /** 도전 중인 체육관 번호 (1~8, 사천왕 9, 아니면 0). */
    static int score(ServerPlayer p) {
        var sb = p.server.getScoreboard();
        var obj = sb.getObjective("poke.gym");
        var s = obj == null ? null : sb.getPlayerScoreInfo(p, obj);
        return s == null ? 0 : s.value();
    }

    /** 지금 그 체육관에서 싸우는 다른 사람의 이름 (없으면 ""). */
    static String busyBy(ServerPlayer me, int n) {
        var sb = me.server.getScoreboard();
        var obj = sb.getObjective("poke.gym");
        if (obj == null) return "";
        for (ServerPlayer o : me.server.getPlayerList().getPlayers()) {
            var s = sb.getPlayerScoreInfo(o, obj);
            if (o != me && s != null && s.value() == n) return o.getGameProfile().getName();
        }
        return "";
    }

    static void open(ServerPlayer p) {
        JsonArray out = new JsonArray();
        for (var e : info) {
            JsonObject g = e.getAsJsonObject().deepCopy();
            String st = status(p, g.get("n").getAsInt());
            g.addProperty("status", st == null ? "locked" : st);   // 배지 케이스 화면은 잠긴 칸도 모양으로 보여 줌 (고르기는 pick에서 다시 검사)
            g.addProperty("busy", busyBy(p, g.get("n").getAsInt()));
            out.add(g);
        }
        ServerPlayNetworking.send(p, new Net.GymOpen(out.toString()));
    }

    /** 클라이언트가 고른 체육관: 다시 확인 후 입장 함수 실행 (순서·혼자·재도전 검사는 함수에서 한 번 더). */
    static void pick(ServerPlayer p, int n) {
        if (n < 1 || n > 9 || !"open".equals(status(p, n))) return;
        Menu.run(p, "function poke:gym/try/" + n);
    }
}
