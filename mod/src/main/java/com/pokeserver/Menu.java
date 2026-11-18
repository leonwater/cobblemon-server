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
        switch (a) {
            case "open" -> ServerPlayNetworking.send(p, new Net.MenuOpen(Money.get(p), notice));
            // 휴지통: 넣은 아이템은 창을 닫으면 사라짐 (돌려주지 않음)
            case "trash" -> p.openMenu(new SimpleMenuProvider((id, inv, pl) -> ChestMenu.threeRows(id, inv, new SimpleContainer(27)),
                    Component.literal("휴지통 (닫으면 사라짐)")));
            case "pc" -> run(p, "pc");
            case "tutorial" -> run(p, "function poke:admin/reset_me");
            case "warp:hall", "warp:street", "warp:gym", "warp:farm", "warp:wild" -> {
                // 튜토리얼을 건너뛰지 못하게
                if (!p.getTags().contains("poke.tutorial_done")) {
                    p.displayClientMessage(Component.literal("튜토리얼을 먼저 끝내 주세요.").withStyle(ChatFormatting.RED), true);
                    return;
                }
                String key = a.substring(5);
                // 회의장·상점가·체육관은 항상 같은 자리, 농장·야생은 마지막 위치
                run(p, (key.equals("farm") || key.equals("wild") ? "function poke:warp/go {key:\"" : "function poke:warp/fixed {key:\"") + key + "\"}");
            }
            default -> { }
        }
    }

    /** 플레이어 위치·이름으로, 관리자 권한을 빌려 실행 (함수·/pc는 권한이 필요). */
    static void run(ServerPlayer p, String cmd) {
        p.server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(2).withSuppressedOutput(), cmd);
    }
}
