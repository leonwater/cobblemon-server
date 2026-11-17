package com.pokeserver;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PokeServer implements ModInitializer {
    public static final String ID = "pokeserver";
    public static final Logger LOG = LoggerFactory.getLogger(ID);

    @Override
    public void onInitialize() {
        PayloadTypeRegistry.playS2C().register(Net.ClaimPopup.TYPE, Net.ClaimPopup.CODEC);
        PayloadTypeRegistry.playC2S().register(Net.ClaimConfirm.TYPE, Net.ClaimConfirm.CODEC);
        ServerPlayNetworking.registerGlobalReceiver(Net.ClaimConfirm.TYPE,
                (payload, ctx) -> ctx.player().server.execute(() -> Farms.claim(ctx.player(), payload.plot())));

        ServerLifecycleEvents.SERVER_STARTED.register(server -> Farms.load());
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 100 == 0) Farms.refreshLabels(server);
        });
        Protection.register();

        CommandRegistrationCallback.EVENT.register((dispatcher, registries, env) -> dispatcher.register(
                Commands.literal(ID).requires(s -> s.hasPermission(2))
                        .then(Commands.literal("deed").then(Commands.argument("targets", EntityArgument.players())
                                .executes(c -> {
                                    var targets = EntityArgument.getPlayers(c, "targets");
                                    targets.forEach(p -> p.getInventory().placeItemBackInInventory(Farms.deed()));
                                    c.getSource().sendSuccess(() -> Component.literal("땅 문서 지급: " + targets.size() + "명"), true);
                                    return targets.size();
                                })))
                        .then(Commands.literal("unclaim").then(Commands.argument("plot", com.mojang.brigadier.arguments.IntegerArgumentType.integer(1))
                                .executes(c -> {
                                    int n = com.mojang.brigadier.arguments.IntegerArgumentType.getInteger(c, "plot");
                                    var data = ServerData.get(c.getSource().getServer());
                                    boolean had = data.plotOwners.remove(n) != null;
                                    data.setDirty();
                                    Farms.refreshLabels(c.getSource().getServer());
                                    c.getSource().sendSuccess(() -> Component.literal("농장 " + n + (had ? " 주인 해제" : ": 주인 없음")), true);
                                    return had ? 1 : 0;
                                })))));
        LOG.info("pokeserver loaded");
    }
}
