package com.pokeserver;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/** 텔레포트: /텔포 <플레이어> (그 사람에게 감), /텔포 <플레이어> 여기로 (데려옴).
 *  OP는 바로 이동. 일반 사용자는 상대가 채팅의 [예]를 눌러야 이동, 10초 안에 안 고르면 취소. */
final class Teleport {
    private Teleport() {}

    static final int TIMEOUT_TICKS = 200;
    /** 대답할 사람 → 요청 */
    record Req(UUID from, UUID mover, UUID dest, long until) {}
    static final Map<UUID, Req> PENDING = new HashMap<>();

    static void register(CommandDispatcher<CommandSourceStack> d) {
        for (String name : new String[]{"텔포", "tpa"}) d.register(Commands.literal(name)
                .then(Commands.literal("예").executes(c -> answer(c, true)))
                .then(Commands.literal("아니요").executes(c -> answer(c, false)))
                .then(Commands.argument("player", EntityArgument.player())
                        .executes(c -> request(c, false))
                        .then(Commands.literal("여기로").executes(c -> request(c, true)))));
    }

    static int request(CommandContext<CommandSourceStack> c, boolean here) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer me = c.getSource().getPlayerOrException(), other = EntityArgument.getPlayer(c, "player");
        if (me == other) return fail(me, "자기 자신에게는 쓸 수 없어요.");
        ServerPlayer mover = here ? other : me, dest = here ? me : other;
        if (c.getSource().hasPermission(2)) { move(mover, dest); return 1; }
        String why = blocked(me, other);
        if (why != null) return fail(me, why);
        if (PENDING.containsKey(other.getUUID())) return fail(me, other.getGameProfile().getName() + "님이 다른 요청에 대답하는 중이에요. 잠시 후 다시 해 주세요.");
        PENDING.put(other.getUUID(), new Req(me.getUUID(), mover.getUUID(), dest.getUUID(), me.server.getTickCount() + TIMEOUT_TICKS));
        String ask = here ? me.getGameProfile().getName() + "님이 당신을 데려가려고 해요." : me.getGameProfile().getName() + "님이 당신에게 오려고 해요.";
        other.sendSystemMessage(Component.literal("[텔레포트] " + ask + " ").withStyle(ChatFormatting.AQUA)
                .append(button("[예]", ChatFormatting.GREEN, "/텔포 예")).append(" ")
                .append(button("[아니요]", ChatFormatting.RED, "/텔포 아니요"))
                .append(Component.literal(" (10초)").withStyle(ChatFormatting.GRAY)));
        me.sendSystemMessage(Component.literal("[텔레포트] " + other.getGameProfile().getName() + "님에게 요청을 보냈어요. (10초 안에 대답이 없으면 취소)").withStyle(ChatFormatting.GRAY));
        return 1;
    }

    static int answer(CommandContext<CommandSourceStack> c, boolean yes) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer me = c.getSource().getPlayerOrException();
        Req r = PENDING.remove(me.getUUID());
        if (r == null) return fail(me, "대답할 텔레포트 요청이 없어요. (10초가 지나면 취소돼요)");
        var list = me.server.getPlayerList();
        ServerPlayer from = list.getPlayer(r.from()), mover = list.getPlayer(r.mover()), dest = list.getPlayer(r.dest());
        if (from == null || mover == null || dest == null) return fail(me, "상대가 나가서 취소됐어요.");
        if (!yes) {
            me.sendSystemMessage(Component.literal("[텔레포트] 거절했어요.").withStyle(ChatFormatting.GRAY));
            from.sendSystemMessage(Component.literal("[텔레포트] " + me.getGameProfile().getName() + "님이 거절했어요.").withStyle(ChatFormatting.RED));
            return 1;
        }
        String why = blocked(from, me);
        if (why != null) { fail(from, why); return fail(me, why); }
        move(mover, dest);
        return 1;
    }

    /** 일반 사용자가 못 쓰는 경우: 튜토리얼 전, 튜토리얼 방, 체육관·사천왕 경기 중. */
    static String blocked(ServerPlayer a, ServerPlayer b) {
        for (ServerPlayer p : new ServerPlayer[]{a, b}) {
            String n = p.getGameProfile().getName();
            if (!p.getTags().contains("poke.tutorial_done") || p.level().dimension().location().toString().equals("poke:hub"))
                return n + "님이 아직 튜토리얼 중이에요.";
            var obj = p.server.getScoreboard().getObjective("poke.gym");
            var score = obj == null ? null : p.server.getScoreboard().getPlayerScoreInfo(p, obj);
            if (score != null && score.value() > 0) return n + "님이 체육관 경기 중이에요.";
        }
        return null;
    }

    static void move(ServerPlayer mover, ServerPlayer dest) {
        mover.teleportTo(dest.serverLevel(), dest.getX(), dest.getY(), dest.getZ(), dest.getYRot(), dest.getXRot());
        mover.sendSystemMessage(Component.literal("[텔레포트] " + dest.getGameProfile().getName() + "님에게 이동했어요.").withStyle(ChatFormatting.AQUA));
        dest.sendSystemMessage(Component.literal("[텔레포트] " + mover.getGameProfile().getName() + "님이 왔어요.").withStyle(ChatFormatting.AQUA));
    }

    /** 10초 지난 요청 취소 (1초마다). */
    static void tick(MinecraftServer server) {
        long now = server.getTickCount();
        PENDING.entrySet().removeIf(e -> {
            if (e.getValue().until() > now) return false;
            for (UUID id : new UUID[]{e.getKey(), e.getValue().from()}) {
                ServerPlayer p = server.getPlayerList().getPlayer(id);
                if (p != null) p.sendSystemMessage(Component.literal("[텔레포트] 10초 동안 대답이 없어 취소됐어요.").withStyle(ChatFormatting.GRAY));
            }
            return true;
        });
    }

    static MutableComponent button(String label, ChatFormatting color, String cmd) {
        return Component.literal(label).withStyle(s -> s.withColor(color).withBold(true)
                .withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, cmd))
                .withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.literal("눌러서 " + label.substring(1, label.length() - 1)))));
    }

    static int fail(ServerPlayer p, String msg) {
        p.sendSystemMessage(Component.literal("[텔레포트] " + msg).withStyle(ChatFormatting.RED));
        return 0;
    }
}
