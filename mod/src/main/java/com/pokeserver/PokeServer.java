package com.pokeserver;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.LongArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PokeServer implements ModInitializer {
    public static final String ID = "pokeserver";
    public static final Logger LOG = LoggerFactory.getLogger(ID);

    @Override
    public void onInitialize() {
        Reset.run();   // 월드를 열기 전에 (데이터팩·월드 로딩보다 먼저 실행됨)
        PayloadTypeRegistry.playS2C().register(Net.ClaimPopup.TYPE, Net.ClaimPopup.CODEC);
        PayloadTypeRegistry.playC2S().register(Net.ClaimConfirm.TYPE, Net.ClaimConfirm.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.ShopOpen.TYPE, Net.ShopOpen.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.Balance.TYPE, Net.Balance.CODEC);
        PayloadTypeRegistry.playC2S().register(Net.ShopTrade.TYPE, Net.ShopTrade.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.MenuOpen.TYPE, Net.MenuOpen.CODEC);
        PayloadTypeRegistry.playC2S().register(Net.MenuAction.TYPE, Net.MenuAction.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.GymOpen.TYPE, Net.GymOpen.CODEC);
        PayloadTypeRegistry.playC2S().register(Net.GymPick.TYPE, Net.GymPick.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.TutorialOpen.TYPE, Net.TutorialOpen.CODEC);
        ServerPlayNetworking.registerGlobalReceiver(Net.GymPick.TYPE,
                (m, ctx) -> ctx.player().server.execute(() -> Gym.pick(ctx.player(), m.n())));
        ServerPlayNetworking.registerGlobalReceiver(Net.MenuAction.TYPE,
                (m, ctx) -> ctx.player().server.execute(() -> Menu.action(ctx.player(), m.action())));
        if (net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.register();
        ServerPlayNetworking.registerGlobalReceiver(Net.ClaimConfirm.TYPE,
                (payload, ctx) -> ctx.player().server.execute(() -> Farms.claim(ctx.player(), payload.plot())));
        ServerPlayNetworking.registerGlobalReceiver(Net.ShopTrade.TYPE, (t, ctx) -> ctx.player().server.execute(
                () -> Shop.trade(ctx.player(), t.sell(), t.category(), t.item(), t.qty())));

        ServerLifecycleEvents.SERVER_STARTED.register(server -> { Farms.load(); Shop.load(); Menu.load(); Gym.load(); });
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTickCount() % 100 == 0) Farms.refreshLabels(server);
            if (server.getTickCount() % 200 == 0 && net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.reapply(server);
            if (server.getTickCount() % 20 == 0 && net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.starterLocks(server);
        });
        // 상인(poke.merchant) → 상점, 체육관 안내원(poke.gymguide) → 도전 목록, 오박사(poke.tutor) → 튜토리얼 설명 창 (Cobblemon NPC 스크립트 대신 직접 처리)
        net.fabricmc.fabric.api.event.player.UseEntityCallback.EVENT.register((player, level, hand, entity, hit) -> {
            var tags = entity.getTags();
            if (level.isClientSide() || !(tags.contains("poke.merchant") || tags.contains("poke.gymguide") || tags.contains("poke.tutor")))
                return net.minecraft.world.InteractionResult.PASS;
            if (hit == null && hand == net.minecraft.world.InteractionHand.MAIN_HAND) {   // 우클릭 한 번에 한 번만
                if (tags.contains("poke.merchant")) Shop.open((ServerPlayer) player);
                else if (tags.contains("poke.tutor")) ServerPlayNetworking.send((ServerPlayer) player, new Net.TutorialOpen());
                else Gym.open((ServerPlayer) player);
            }
            return net.minecraft.world.InteractionResult.SUCCESS;   // 땅 보호 알림이 뜨지 않게 우리 NPC는 여기서 끝냄
        });
        Protection.register();
        CommandRegistrationCallback.EVENT.register((dispatcher, registries, env) -> {
            dispatcher.register(admin());
            for (String name : new String[]{"money", "돈"}) dispatcher.register(Commands.literal(name).executes(PokeServer::balance));
            // 전체 초기화 (자기 자신만): /초기화 → 안내, /초기화 확인 → 실행
            dispatcher.register(Commands.literal("초기화").executes(c -> {
                c.getSource().sendSuccess(() -> Component.literal("가진 아이템·돈·농장 땅·포켓몬·배지가 모두 사라지고 튜토리얼부터 다시 시작합니다. "
                        + "정말 하려면  /초기화 확인  을 입력하세요.").withStyle(ChatFormatting.RED), false);
                return 0;
            }).then(Commands.literal("확인").executes(c -> { Menu.wipe(c.getSource().getPlayerOrException()); return 1; })));
            for (String name : new String[]{"pay", "송금"}) dispatcher.register(Commands.literal(name)
                    .then(Commands.argument("player", EntityArgument.player())
                            .then(Commands.argument("amount", LongArgumentType.longArg(1)).executes(PokeServer::pay))));
        });
        LOG.info("pokeserver loaded");
    }

    static int balance(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        long n = Money.get(p);
        c.getSource().sendSuccess(() -> Component.literal("잔액: " + Money.fmt(n)).withStyle(ChatFormatting.GOLD), false);
        return (int) Math.min(n, Integer.MAX_VALUE);
    }

    static int pay(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer from = c.getSource().getPlayerOrException();
        ServerPlayer to = EntityArgument.getPlayer(c, "player");
        long amount = LongArgumentType.getLong(c, "amount");
        if (from == to) { from.sendSystemMessage(Component.literal("자기 자신에게는 보낼 수 없습니다.").withStyle(ChatFormatting.RED)); return 0; }
        if (!Money.take(from, amount)) { from.sendSystemMessage(Component.literal("잔액이 부족합니다.").withStyle(ChatFormatting.RED)); return 0; }
        Money.add(from.server, to.getUUID(), amount);
        from.sendSystemMessage(Component.literal(to.getGameProfile().getName() + "님에게 " + Money.fmt(amount) + " 보냄").withStyle(ChatFormatting.GREEN));
        to.sendSystemMessage(Component.literal(from.getGameProfile().getName() + "님에게서 " + Money.fmt(amount) + " 받음").withStyle(ChatFormatting.GREEN));
        return 1;
    }

    static LiteralArgumentBuilder<CommandSourceStack> admin() {
        var money = Commands.literal("money");
        for (String op : new String[]{"give", "take", "set"}) {
            money.then(Commands.literal(op).then(Commands.argument("targets", EntityArgument.players())
                    .then(Commands.argument("amount", LongArgumentType.longArg(0)).executes(c -> {
                        long n = LongArgumentType.getLong(c, "amount");
                        var targets = EntityArgument.getPlayers(c, "targets");
                        for (ServerPlayer p : targets) {
                            switch (op) {
                                case "give" -> Money.add(p.server, p.getUUID(), n);
                                case "take" -> Money.add(p.server, p.getUUID(), -Math.min(n, Money.get(p)));
                                default -> Money.set(p.server, p.getUUID(), n);
                            }
                            ServerPlayNetworking.send(p, new Net.Balance(Money.get(p)));
                        }
                        c.getSource().sendSuccess(() -> Component.literal("잔액 변경(" + op + " " + n + "): " + targets.size() + "명"), true);
                        return targets.size();
                    }))));
        }
        return Commands.literal(ID).requires(s -> s.hasPermission(2))
                .then(money)
                .then(Commands.literal("shop").then(Commands.argument("targets", EntityArgument.players()).executes(c -> {
                    var targets = EntityArgument.getPlayers(c, "targets");
                    targets.forEach(Shop::open);
                    return targets.size();
                })))
                // 7. NPC 스킨: /pokeserver npc skin poke.nurse <플레이어이름|이미지URL|reset>
                .then(Commands.literal("npc").then(Commands.literal("skin")
                        .then(Commands.argument("tag", com.mojang.brigadier.arguments.StringArgumentType.word())
                                .then(Commands.argument("skin", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).executes(c -> {
                                    if (!net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) return 0;
                                    String tag = com.mojang.brigadier.arguments.StringArgumentType.getString(c, "tag");
                                    String skin = com.mojang.brigadier.arguments.StringArgumentType.getString(c, "skin");
                                    int n = CobblemonHooks.setSkin(c.getSource().getServer(), tag, skin);
                                    c.getSource().sendSuccess(() -> Component.literal("NPC 스킨 " + (skin.equals("reset") ? "기본으로" : "→ " + skin) + ": " + n + "명 (저장됨)"), true);
                                    return n;
                                })))))
                .then(Commands.literal("tutorial").then(Commands.argument("targets", EntityArgument.players()).executes(c -> {
                    var targets = EntityArgument.getPlayers(c, "targets");
                    targets.forEach(p -> ServerPlayNetworking.send(p, new Net.TutorialOpen()));
                    return targets.size();
                })))
                .then(Commands.literal("reset").then(Commands.argument("targets", EntityArgument.players()).executes(c -> {
                    var targets = EntityArgument.getPlayers(c, "targets");
                    targets.forEach(Menu::wipe);
                    c.getSource().sendSuccess(() -> Component.literal("전체 초기화: " + targets.size() + "명"), true);
                    return targets.size();
                })))
                .then(Commands.literal("menu").then(Commands.argument("targets", EntityArgument.players()).executes(c -> {
                    var targets = EntityArgument.getPlayers(c, "targets");
                    targets.forEach(p -> Menu.action(p, "open"));
                    return targets.size();
                })))
                .then(Commands.literal("reload").executes(c -> {
                    Farms.load(); Shop.load(); Menu.load();
                    c.getSource().sendSuccess(() -> Component.literal("농장·상점·메뉴 설정을 다시 불러왔습니다."), true);
                    return 1;
                }))
                .then(Commands.literal("deed").then(Commands.argument("targets", EntityArgument.players()).executes(c -> {
                    var targets = EntityArgument.getPlayers(c, "targets");
                    targets.forEach(p -> p.getInventory().placeItemBackInInventory(Farms.deed()));
                    c.getSource().sendSuccess(() -> Component.literal("땅 문서 지급: " + targets.size() + "명"), true);
                    return targets.size();
                })))
                .then(Commands.literal("unclaim").then(Commands.argument("plot", IntegerArgumentType.integer(1)).executes(c -> {
                    int n = IntegerArgumentType.getInteger(c, "plot");
                    var data = ServerData.get(c.getSource().getServer());
                    boolean had = data.plotOwners.remove(n) != null;
                    data.setDirty();
                    Farms.refreshLabels(c.getSource().getServer());
                    c.getSource().sendSuccess(() -> Component.literal("농장 " + n + (had ? " 주인 해제" : ": 주인 없음")), true);
                    return had ? 1 : 0;
                })));
    }
}
