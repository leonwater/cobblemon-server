package com.pokeserver;

import com.google.gson.JsonParser;
import java.nio.file.Files;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.inventory.ChestMenu;

/** 5. 메인 메뉴의 서버 쪽 동작. 공지는 config/pokeserver/menu.json 의 "notice". */
final class Menu {
    private Menu() {}
    static String notice = "";

    static void load() {
        try {
            notice = JsonParser.parseString(Files.readString(FabricLoader.getInstance().getConfigDir().resolve("pokeserver/menu.json")))
                    .getAsJsonObject().get("notice").getAsString();
        } catch (Exception ex) {
            PokeServer.LOG.warn("메뉴 공지를 못 읽음 ({})", ex.toString());
        }
    }

    static void action(ServerPlayer p, String a) {
        if (a.startsWith("tutorial_done:")) {                     // 8. 튜토리얼 마지막 쪽에서 정한 닉네임 (아직 없을 때만; 광장 이동은 튜토리얼 방에서만)
            // 3. 닉네임은 첫 튜토리얼에서만: 이미 있으면 새로 적은 것은 무시
            String why = ServerData.get(p.server).nicks.containsKey(p.getUUID()) ? null : Nicknames.set(p, a.substring("tutorial_done:".length()));
            if (why != null) {
                p.sendSystemMessage(Component.literal(why + " 다시 정해 주세요.").withStyle(ChatFormatting.RED));
                ServerPlayNetworking.send(p, Net.TutorialOpen.of(p, why));   // 1. 닉네임 쪽에 바로 "겹친다" 등 이유를 보여 줌
                return;
            }
            a = "tutorial_done";
        }
        if (a.startsWith("title:")) {                              // 7. 칭호 고르기
            Titles.pick(p, a.substring(6));
            a = "titles";
        }
        switch (a) {
            case "titles" -> ServerPlayNetworking.send(p, new Net.TitlesOpen(Titles.list(p)));
            case "open" -> {
                var st = new java.util.ArrayList<>(net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon") ? CobblemonHooks.dex(p) : java.util.List.of(0, 0, 0));
                st.add(Nicknames.badges(p));
                ServerPlayNetworking.send(p, new Net.MenuOpen(Money.get(p), notice, p.getTags().contains("poke.tutorial_done"), st));
            }
            // 휴지통: 넣은 아이템은 창을 닫으면 사라짐 (돌려주지 않음)
            case "trash" -> p.openMenu(new SimpleMenuProvider((id, inv, pl) -> ChestMenu.threeRows(id, inv, new SimpleContainer(27)),
                    Component.literal("휴지통 (닫으면 사라짐)")));
            case "pc" -> run(p, "pc");
            case "tutorial" -> ServerPlayNetworking.send(p, Net.TutorialOpen.of(p));   // 7. 다시 보기: 오박사에게 가지 않고 설명 창만
            // 튜토리얼 설명 창의 "준비 완료!" (튜토리얼 방에서만) → 보상 → 바로 광장 → 스타팅 포켓몬 고르기
            case "tutorial_done" -> {
                if (!p.level().dimension().location().toString().equals("poke:hub")) return;
                if (!ServerData.get(p.server).nicks.containsKey(p.getUUID())) { ServerPlayNetworking.send(p, Net.TutorialOpen.of(p)); return; }
                run(p, "function poke:tutorial/finish");   // 2. 기본 물품 → 바로 광장으로
                // 광장으로 옮긴 뒤 2초쯤 있다가 스타팅 고르기 창 (먼저 열면 차원 이동 화면에 닫힘)
                if (FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.STARTER_AT.put(p.getUUID(), p.server.getTickCount() + 40);
            }
            case "starter" -> { if (FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.offerStarter(p); }
            case "warp:hall", "warp:gym", "warp:farm" -> {
                // 튜토리얼을 건너뛰지 못하게
                if (!p.getTags().contains("poke.tutorial_done")) {
                    p.displayClientMessage(Component.literal("튜토리얼을 먼저 끝내 주세요.").withStyle(ChatFormatting.RED), true);
                    return;
                }
                String key = a.substring(5);
                // 광장·체육관은 항상 같은 자리, 농장은 마지막 위치
                run(p, (key.equals("farm") ? "function poke:warp/go {key:\"" : "function poke:warp/fixed {key:\"") + key + "\"}");
            }
            default -> { }
        }
    }

    /** 2. 서버 전체 초기화: 표시 파일을 남기고 모두 내보낸 뒤 서버를 끔 → 다음 시작 때 Reset이 월드(맵·플레이어·포켓몬·돈)를
     *  통째로 백업 폴더로 옮기고 새 월드로 시작. start.bat은 표시 파일이 있으면 서버를 바로 다시 켬. */
    static void wipeAll(net.minecraft.server.MinecraftServer server) {
        try {
            java.nio.file.Files.writeString(FabricLoader.getInstance().getGameDir().resolve(Reset.WIPE), "운영자가 /초기화를 실행함");
        } catch (java.io.IOException ex) {
            PokeServer.LOG.error("전체 초기화 표시 파일을 못 씀", ex);
            server.getPlayerList().broadcastSystemMessage(Component.literal("[서버] 전체 초기화 실패: 서버 폴더에 파일을 쓸 수 없습니다.").withStyle(ChatFormatting.RED), false);
            return;
        }
        for (ServerPlayer p : java.util.List.copyOf(server.getPlayerList().getPlayers()))
            p.connection.disconnect(Component.literal("서버 전체를 초기화합니다. 1~2분 뒤 다시 접속해 주세요."));
        server.halt(false);
    }

    static void wipe(ServerPlayer p) {
        p.getInventory().clearContent();
        p.getEnderChestInventory().clearContent();
        var data = ServerData.get(p.server);
        data.money.put(p.getUUID(), 0L);
        data.deedsBought.remove(p.getUUID());
        data.nicks.remove(p.getUUID());
        data.stats.remove(p.getUUID());
        data.plotOwners.values().removeIf(o -> o.id().equals(p.getUUID()));
        data.setDirty();
        Farms.refreshLabels(p.server);
        if (FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.wipe(p);
        run(p, "function poke:admin/wipe_me");   // 체육관 상태·마지막 위치·RCT 진행도·태그 → 다음 틱에 튜토리얼 방으로
        ServerPlayNetworking.send(p, new Net.Balance(0));
        p.sendSystemMessage(Component.literal("모든 진행을 초기화했습니다. 튜토리얼부터 다시 시작합니다.").withStyle(ChatFormatting.YELLOW));
    }

    /** 플레이어 위치·이름으로, 관리자 권한을 빌려 실행 (함수·/pc는 권한이 필요). */
    static void run(ServerPlayer p, String cmd) {
        p.server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(2).withSuppressedOutput(), cmd);
    }
}
