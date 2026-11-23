package com.pokeserver.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.pokeserver.Net;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.KeyMapping;
import org.lwjgl.glfw.GLFW;

public class PokeServerClient implements ClientModInitializer {
    /** G 키 (메뉴 창에서 한 번 더 누르면 닫힘: MenuScreen.keyPressed). */
    static KeyMapping menu;

    @Override
    public void onInitializeClient() {
        ClientPlayNetworking.registerGlobalReceiver(Net.ClaimPopup.TYPE,
                (payload, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ClaimScreen(payload.plot()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.ShopOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ShopScreen(p.json(), p.balance(), p.badges()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.GymOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new GymScreen(p.json()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.Balance.TYPE, (p, ctx) -> ShopScreen.balance = p.balance());
        ClientPlayNetworking.registerGlobalReceiver(Net.Names.TYPE, (p, ctx) -> com.pokeserver.Nicknames.read(p.data()));
        ClientPlayNetworking.registerGlobalReceiver(Net.Hud.TYPE, (p, ctx) -> { InfoHud.balance = p.balance(); InfoHud.badges = p.badges(); InfoHud.place = p.place(); });
        net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback.EVENT.register(InfoHud::render);
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents.JOIN.register((h, s, mc) -> { InfoHud.joinedAt = System.currentTimeMillis(); InfoHud.keepW = 0; });
        // 3. 관장·챔피언 원작풍 스킨 (RCT 기본 스킨보다 위에 오도록 항상 켜진 내장 리소스팩)
        net.fabricmc.fabric.api.resource.ResourceManagerHelper.registerBuiltinResourcePack(
                net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("pokeserver", "leaders"),
                net.fabricmc.loader.api.FabricLoader.getInstance().getModContainer("pokeserver").orElseThrow(),
                net.minecraft.network.chat.Component.literal("잡켓몬 서버 관장 스킨"),
                net.fabricmc.fabric.api.resource.ResourcePackActivationType.ALWAYS_ENABLED);
        ClientPlayNetworking.registerGlobalReceiver(Net.MenuOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new MenuScreen(p))));
        ClientPlayNetworking.registerGlobalReceiver(Net.TitlesOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new TitleScreen(p.data()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.TutorialOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new TutorialScreen(p.nick(), p.error()))));
        // 5. G 키: 메인 메뉴 (설정 → 조작에서 바꿀 수 있음)
        menu = KeyBindingHelper.registerKeyBinding(new KeyMapping("메인 메뉴", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_G, "pokeserver"));
        // 키 겹침: Iris(셰이더)의 "셰이더 다시 불러오기"도 기본 R이라 코블몬 R(포켓몬 내보내기·상호작용 휠·관전·배틀 화면)이 안 먹음
        // (마인크래프트는 같은 키에 하나만 연결) → 다른 키와 겹치면 Iris 쪽을 비움. 바꾸고 싶으면 설정 → 조작에서 다시 지정
        net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientLifecycleEvents.CLIENT_STARTED.register(mc -> {
            for (KeyMapping k : mc.options.keyMappings) {
                if (!k.getName().equals("iris.keybind.reload") || k.isUnbound()) continue;
                if (java.util.Arrays.stream(mc.options.keyMappings).noneMatch(o -> o != k && o.same(k))) continue;
                k.setKey(InputConstants.UNKNOWN);
                KeyMapping.resetMapping();
                mc.options.save();
            }
        });
        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            Bgm.tick(mc);
            while (menu.consumeClick()) {
                if (mc.player != null && mc.screen == null) ClientPlayNetworking.send(new Net.MenuAction("open"));
            }
        });
    }
}
