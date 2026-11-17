package com.pokeserver.client;

import com.pokeserver.Net;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;

public class PokeServerClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientPlayNetworking.registerGlobalReceiver(Net.ClaimPopup.TYPE,
                (payload, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ClaimScreen(payload.plot()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.ShopOpen.TYPE,
                (p, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ShopScreen(p.json(), p.balance()))));
        ClientPlayNetworking.registerGlobalReceiver(Net.Balance.TYPE, (p, ctx) -> ShopScreen.balance = p.balance());
        DevShot.register();
    }
}
