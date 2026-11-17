package com.pokeserver.client;

import com.pokeserver.Net;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;

public class PokeServerClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientPlayNetworking.registerGlobalReceiver(Net.ClaimPopup.TYPE,
                (payload, ctx) -> ctx.client().execute(() -> ctx.client().setScreen(new ClaimScreen(payload.plot()))));
    }
}
