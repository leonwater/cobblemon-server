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
        PayloadTypeRegistry.playS2C().register(Net.Names.TYPE, Net.Names.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.TitlesOpen.TYPE, Net.TitlesOpen.CODEC);
        PayloadTypeRegistry.playS2C().register(Net.Hud.TYPE, Net.Hud.CODEC);
        net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents.JOIN.register((h, s, server) -> {
            Nicknames.join();
            var d = ServerData.get(server);
            if (!h.player.getTags().contains("poke.joined")) { d.resetSeen.put(h.player.getUUID(), d.resetEpoch); d.setDirty(); }   // 처음 온 사람: 초기화할 것 없음
            else Menu.joinCheck(h.player);
        });
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

        ServerLifecycleEvents.SERVER_STARTED.register(server -> {
            Farms.load(); Shop.load(); Menu.load(); Gym.load(); Plaza.start(server);
            // 3. 렉 줄이기: server.properties가 기본값(10)이면 보이는 거리 8·처리 거리 6 (직접 바꿔 두었으면 그대로)
            if (server instanceof net.minecraft.server.dedicated.DedicatedServer ds) {
                var props = ds.getProperties();
                if (props.viewDistance == 10) server.getPlayerList().setViewDistance(8);
                if (props.simulationDistance == 10) server.getPlayerList().setSimulationDistance(6);
            }
        });
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            Plaza.tick(server);
            ItemCleaner.tick(server);
            if (server.getTickCount() % 100 == 0) Farms.refreshLabels(server);
            if (server.getTickCount() % 20 == 0) { Teleport.tick(server); Nicknames.tick(server); }
            if (server.getTickCount() % 200 == 0 && net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.reapply(server);
            if (server.getTickCount() % 20 == 0 && net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) { CobblemonHooks.starterLocks(server); CobblemonHooks.countWild(server); }
            if (server.getTickCount() % CobblemonHooks.LEGEND_TICKS == 0 && net.fabricmc.loader.api.FabricLoader.getInstance().isModLoaded("cobblemon")) CobblemonHooks.spawnLegend(server);
        });
        // 상인(poke.merchant) → 상점, 체육관 안내원(poke.gymguide) → 도전 목록, 오박사(poke.tutor) → 튜토리얼 설명 창 (Cobblemon NPC 스크립트 대신 직접 처리)
        net.fabricmc.fabric.api.event.player.UseEntityCallback.EVENT.register((player, level, hand, entity, hit) -> {
            var tags = entity.getTags();
            if (level.isClientSide() || !(tags.contains("poke.merchant") || tags.contains("poke.gymguide") || tags.contains("poke.tutor")))
                return net.minecraft.world.InteractionResult.PASS;
            if (hit == null && hand == net.minecraft.world.InteractionHand.MAIN_HAND) {   // 우클릭 한 번에 한 번만
                if (tags.contains("poke.merchant")) Shop.open((ServerPlayer) player);
                else if (tags.contains("poke.tutor")) ServerPlayNetworking.send((ServerPlayer) player, Net.TutorialOpen.of((ServerPlayer) player));
                else Gym.open((ServerPlayer) player);
            }
            return net.minecraft.world.InteractionResult.SUCCESS;   // 땅 보호 알림이 뜨지 않게 우리 NPC는 여기서 끝냄
        });
        Protection.register();
        CommandRegistrationCallback.EVENT.register((dispatcher, registries, env) -> {
            dispatcher.register(admin());
            Teleport.register(dispatcher);
            // 4·5. 명령어는 한국어·영어 둘 다 (같은 일)
            for (String name : new String[]{"money", "돈"}) dispatcher.register(Commands.literal(name).executes(PokeServer::balance));
            for (String name : new String[]{"spawn", "광장"}) dispatcher.register(Commands.literal(name).executes(c -> {
                Menu.run(c.getSource().getPlayerOrException(), "function poke:home"); return 1; }));
            for (String name : new String[]{"menu", "메뉴"}) dispatcher.register(Commands.literal(name).executes(c -> {
                Menu.action(c.getSource().getPlayerOrException(), "open"); return 1; }));
            for (String name : new String[]{"commands", "명령어"}) dispatcher.register(Commands.literal(name).executes(c -> {
                for (String line : HELP) c.getSource().sendSystemMessage(Component.literal(line).withStyle(line.startsWith("──") ? ChatFormatting.GOLD : ChatFormatting.WHITE));
                return 1; }));
            // 8. 초기화 (운영자만): /초기화 → 서버의 모든 플레이어 (접속 안 한 사람은 다음 접속 때), /초기화 닉네임 → 그 사람만
            for (String name : new String[]{"초기화", "reset"}) dispatcher.register(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .executes(c -> { int n = Menu.wipeAll(c.getSource().getServer());
                        c.getSource().sendSuccess(() -> Component.literal("전체 초기화: 접속 중 " + n + "명 + 나머지는 다음 접속 때").withStyle(ChatFormatting.RED), true); return n; })
                    .then(Commands.argument("player", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).suggests(Nicknames::suggest).executes(c -> {
                        String who = com.mojang.brigadier.arguments.StringArgumentType.getString(c, "player");
                        ServerPlayer t = Nicknames.find(c.getSource().getServer(), who);
                        if (t == null) { c.getSource().sendFailure(Component.literal("접속 중인 플레이어가 아니에요: " + who)); return 0; }
                        Menu.wipe(t);
                        c.getSource().sendSuccess(() -> Component.literal("초기화: " + Nicknames.nick(t)).withStyle(ChatFormatting.RED), true);
                        return 1;
                    })));
            // 1. /공지 /announce 내용: 운영자(OP)만, 서버 전체 채팅에 공지
            for (String name : new String[]{"announce", "공지"}) dispatcher.register(Commands.literal(name).requires(s -> s.hasPermission(2))
                    .then(Commands.argument("message", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).executes(c -> {
                        String msg = com.mojang.brigadier.arguments.StringArgumentType.getString(c, "message");
                        c.getSource().getServer().getPlayerList().broadcastSystemMessage(Component.literal("[공지] ").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
                                .append(Component.literal(msg).withStyle(ChatFormatting.YELLOW)), false);
                        return 1;
                    })));
            // /송금 닉네임 금액 (닉네임은 한글도 되게 한 덩어리로 받아 마지막 칸을 금액으로)
            for (String name : new String[]{"pay", "송금"}) dispatcher.register(Commands.literal(name)
                    .then(Commands.argument("args", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).suggests(Nicknames::suggest).executes(PokeServer::pay)));
        });
        LOG.info("pokeserver loaded");
    }

    /** /명령어 (/commands) 와 G 메뉴 "명령어" 버튼이 보여 주는 목록. */
    static final String[] HELP = {"── 명령어 (한국어 / English) ──", "G 키: 메인 메뉴  ·  /메뉴 /menu",
            "/돈 /money: 잔액", "/송금 /pay 닉네임 금액: 돈 보내기",
            "/가기 /tpa 닉네임: 그 사람에게 이동 (상대 동의)", "/부르기 /tpahere 닉네임: 내 쪽으로 부르기 (상대 동의)",
            "/수락 /accept · /거절 /deny: 텔레포트 요청에 대답", "/광장 /spawn: 광장으로", "/명령어 /commands: 이 목록",
            "R 키: 포켓몬 꺼내기 · M 키: 상태창 · ↑↓: 파티 선택"};

    static int balance(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        long n = Money.get(p);
        c.getSource().sendSuccess(() -> Component.literal("잔액: " + Money.fmt(n)).withStyle(ChatFormatting.GOLD), false);
        return (int) Math.min(n, Integer.MAX_VALUE);
    }

    static int pay(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer from = c.getSource().getPlayerOrException();
        String args = com.mojang.brigadier.arguments.StringArgumentType.getString(c, "args").trim();
        int sp = args.lastIndexOf(' ');
        long amount;
        try { amount = sp < 0 ? -1 : Long.parseLong(args.substring(sp + 1).replace(",", "")); } catch (NumberFormatException e) { amount = -1; }
        ServerPlayer to = sp < 0 ? null : Nicknames.find(from.server, args.substring(0, sp));
        if (to == null || amount < 1) { from.sendSystemMessage(Component.literal("사용법: /송금 닉네임 금액 (접속 중인 사람에게만)").withStyle(ChatFormatting.RED)); return 0; }
        if (from == to) { from.sendSystemMessage(Component.literal("자기 자신에게는 보낼 수 없습니다.").withStyle(ChatFormatting.RED)); return 0; }
        if (!Money.take(from, amount)) { from.sendSystemMessage(Component.literal("잔액이 부족합니다.").withStyle(ChatFormatting.RED)); return 0; }
        Money.add(from.server, to.getUUID(), amount);
        from.sendSystemMessage(Component.literal(Nicknames.nick(to) + "님에게 " + Money.fmt(amount) + " 보냄").withStyle(ChatFormatting.GREEN));
        to.sendSystemMessage(Component.literal(Nicknames.nick(from) + "님에게서 " + Money.fmt(amount) + " 받음").withStyle(ChatFormatting.GREEN));
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
                                case "give" -> { Money.add(p.server, p.getUUID(), n); Titles.add(p, "earned", n); }
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
                    targets.forEach(p -> ServerPlayNetworking.send(p, Net.TutorialOpen.of(p)));
                    return targets.size();
                })))
                .then(Commands.literal("legend").executes(c -> {   // 6. 전설 출현을 지금 한 번 (관리자·테스트용)
                    String s = CobblemonHooks.spawnLegend(c.getSource().getServer());
                    c.getSource().sendSuccess(() -> Component.literal(s == null ? "전설 출현: 맞는 플레이어·전설 없음" : "전설 출현: " + s), true);
                    return s == null ? 0 : 1;
                }))
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
                .then(Commands.literal("clearitems").executes(c -> {   // 바닥 아이템 지금 정리 (원래 10분마다 자동)
                    int n = ItemCleaner.clear(c.getSource().getServer());
                    c.getSource().sendSuccess(() -> Component.literal("바닥 아이템 " + n + "개 정리"), true);
                    return n;
                }))
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
