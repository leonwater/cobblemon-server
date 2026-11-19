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
    @Override
    public void onInitializeClient() {
        ClientPlayNetworking.registerGlobalReceiver(Net.ClaimPopup.TYPE,
                (payload, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ClaimScreen(payload.plot()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.ShopOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ShopScreen(p.json(), p.balance(), p.badges()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.GymOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new GymScreen(p.json()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.Balance.TYPE, (p, ctx) -> ShopScreen.balance = p.balance());
        ClientPlayNetworking.registerGlobalReceiver(Net.MenuOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new MenuScreen(p.balance(), p.notice(), p.tutorialDone()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.TutorialOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new TutorialScreen())));
        // 5. G 키: 메인 메뉴 (설정 → 조작에서 바꿀 수 있음)
        KeyMapping menu = KeyBindingHelper.registerKeyBinding(new KeyMapping("메인 메뉴", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_G, "pokeserver"));
        ClientTickEvents.END_CLIENT_TICK.register(mc -> {
            while (menu.consumeClick()) {
                if (mc.player != null && mc.screen == null) ClientPlayNetworking.send(new Net.MenuAction("open"));
            }
        });
    }
}
