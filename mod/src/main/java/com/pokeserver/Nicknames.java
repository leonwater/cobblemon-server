package com.pokeserver;

import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.suggestion.Suggestions;
import com.mojang.brigadier.suggestion.SuggestionsBuilder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Pattern;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundPlayerInfoUpdatePacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/** 8·9. 닉네임(튜토리얼에서 직접 입력) + 업적 칭호. 화면에는 "[칭호] 닉네임"으로 보임 (채팅·머리 위·탭 목록). */
public final class Nicknames {
    private Nicknames() {}

    /** 보이는 이름 (서버·클라이언트 공통, 믹스인이 읽음). 클라이언트는 Net.Names 패킷으로 채움. */
    public static final Map<UUID, Component> SHOWN = new java.util.concurrent.ConcurrentHashMap<>();
    static final Pattern VALID = Pattern.compile("[가-힣A-Za-z0-9_]{2,12}");
    private static String last = "";

    static int badges(ServerPlayer p) {
        int n = 0;
        for (int i = 1; i <= 8; i++) if (p.getTags().contains("poke.badge" + i)) n++;
        return n;
    }

    /** 닉네임 (없으면 마인크래프트 이름). */
    public static String nick(ServerPlayer p) {
        String n = ServerData.get(p.server).nicks.get(p.getUUID());
        return n != null ? n : p.getGameProfile().getName();
    }

    static String shown(ServerPlayer p) {
        String t = Titles.shown(p);
        return (t.isEmpty() ? "" : t + "§r ") + nick(p);
    }

    /** 바꾸면 null, 안 되면 이유. */
    static String set(ServerPlayer p, String nick) {
        nick = nick.trim();
        if (!VALID.matcher(nick).matches()) return "닉네임은 한글·영어·숫자·_ 로 2~12글자예요.";
        var d = ServerData.get(p.server);
        for (var e : d.nicks.entrySet())
            if (!e.getKey().equals(p.getUUID()) && e.getValue().equalsIgnoreCase(nick)) return "이미 다른 사람이 쓰는 닉네임이에요.";
        for (ServerPlayer o : p.server.getPlayerList().getPlayers())
            if (o != p && o.getGameProfile().getName().equalsIgnoreCase(nick)) return "다른 사람의 아이디와 같은 닉네임은 쓸 수 없어요.";
        d.nicks.put(p.getUUID(), nick);
        d.setDirty();
        return null;
    }

    /** 닉네임 또는 마인크래프트 이름으로 접속 중인 플레이어 찾기. */
    static ServerPlayer find(MinecraftServer server, String name) {
        for (ServerPlayer p : server.getPlayerList().getPlayers())
            if (nick(p).equalsIgnoreCase(name.trim()) || p.getGameProfile().getName().equalsIgnoreCase(name.trim())) return p;
        return null;
    }

    static CompletableFuture<Suggestions> suggest(CommandContext<CommandSourceStack> c, SuggestionsBuilder b) {
        for (ServerPlayer p : c.getSource().getServer().getPlayerList().getPlayers()) b.suggest(nick(p));
        return b.buildFuture();
    }

    static final Map<UUID, Net.Hud> LAST_HUD = new HashMap<>();
    static void join() { last = ""; LAST_HUD.clear(); }   // 새로 들어온 사람에게도 보내게

    /** 1초마다: 보이는 이름이 바뀌었으면 모두에게 보내고 탭 목록 갱신. HUD 정보(돈·배지·도감)도 보냄. */
    static void tick(MinecraftServer server) {
        var players = server.getPlayerList().getPlayers();
        Titles.DEX.clear();
        Map<UUID, String> now = new HashMap<>();
        for (ServerPlayer p : players) { Titles.check(p); now.put(p.getUUID(), shown(p)); }
        StringBuilder sb = new StringBuilder();
        now.forEach((id, s) -> sb.append(id).append('\t').append(s).append('\n'));
        String data = sb.toString();
        if (!data.equals(last)) {
            last = data;
            SHOWN.clear();
            now.forEach((id, s) -> SHOWN.put(id, Component.literal(s)));
            for (ServerPlayer p : players) ServerPlayNetworking.send(p, new Net.Names(data));
            server.getPlayerList().broadcastAll(new ClientboundPlayerInfoUpdatePacket(
                    java.util.EnumSet.of(ClientboundPlayerInfoUpdatePacket.Action.UPDATE_DISPLAY_NAME), new ArrayList<>(players)));
        }
        for (ServerPlayer p : players) {   // 정보창: 바뀐 사람에게만 보냄
            var hud = new Net.Hud(Money.get(p), badges(p), place(p));
            if (!hud.equals(LAST_HUD.put(p.getUUID(), hud))) ServerPlayNetworking.send(p, hud);
        }
    }

    /** 정보창 "위치" (BGM도 이 값으로 고름): 광장 마을 / 포켓몬 센터 / 야생 / 농장 / 체육관(로비) / 경기장 / 오박사 연구소. */
    static String place(ServerPlayer p) {
        String d = p.level().dimension().location().toString();
        return switch (d) {
            case "poke:wild" -> Plaza.inCenter(p.level(), p.blockPosition()) ? "포켓몬 센터" : Plaza.protects(p.level(), p.blockPosition()) ? "광장 마을" : "야생";
            case "poke:farm" -> "농장";
            case "poke:town" -> p.getX() >= 2990 ? "경기장" : "체육관";   // 경기장·사천왕 본부는 x 3000~ (tools/build_world.py ARENA_X), 로비는 2000 근처
            case "poke:hub" -> "오박사 연구소";
            default -> "-";
        };
    }

    /** 클라이언트: 패킷 내용 → 보이는 이름. */
    public static void read(String data) {
        SHOWN.clear();
        for (String line : data.split("\n")) {
            int t = line.indexOf('\t');
            if (t > 0) SHOWN.put(UUID.fromString(line.substring(0, t)), Component.literal(line.substring(t + 1)));
        }
    }
}
