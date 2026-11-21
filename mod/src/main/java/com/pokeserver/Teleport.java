package com.pokeserver;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/** 텔레포트: /가기 /tp <플레이어> (그 사람에게 감), /부르기 /tpa <플레이어> (데려옴), /수락 /accept · /거절 /deny.
 *  OP는 바로 이동. 일반 사용자는 상대가 채팅의 [예]를 눌러야 이동, 10초 안에 안 고르면 취소. */
final class Teleport {
    private Teleport() {}

    static final int TIMEOUT_TICKS = 200;
    /** 대답할 사람 → 요청 */
    record Req(UUID from, UUID mover, UUID dest, long until) {}
    static final Map<UUID, Req> PENDING = new HashMap<>();

    static void register(CommandDispatcher<CommandSourceStack> d) {
        // 가기 = /tp (일반 사용자 /tp는 TpAliasMixin이 가기로 바꿈), 부르기 = /tpa
        for (String name : new String[]{"가기"}) d.register(Commands.literal(name)
                .then(Commands.argument("player", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).suggests(Nicknames::suggest).executes(c -> request(c, false))));
        for (String name : new String[]{"부르기", "tpa"}) d.register(Commands.literal(name)
                .then(Commands.argument("player", com.mojang.brigadier.arguments.StringArgumentType.greedyString()).suggests(Nicknames::suggest).executes(c -> request(c, true))));
        for (String name : new String[]{"수락", "accept"}) d.register(Commands.literal(name).executes(c -> answer(c, true)));
        for (String name : new String[]{"거절", "deny"}) d.register(Commands.literal(name).executes(c -> answer(c, false)));
    }

    static int request(CommandContext<CommandSourceStack> c, boolean here) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer me = c.getSource().getPlayerOrException(), other = Nicknames.find(me.server, com.mojang.brigadier.arguments.StringArgumentType.getString(c, "player"));
        if (other == null) return fail(me, "접속 중인 사람의 닉네임을 적어 주세요.");
        if (me == other) return fail(me, "자기 자신에게는 쓸 수 없어요.");
        ServerPlayer mover = here ? other : me, dest = here ? me : other;
        if (c.getSource().hasPermission(2)) { move(mover, dest); return 1; }
        String why = blocked(me, other);
        if (why != null) return fail(me, why);
        if (PENDING.containsKey(other.getUUID())) return fail(me, Nicknames.nick(other) + "님이 다른 요청에 대답하는 중이에요. 잠시 후 다시 해 주세요.");
        PENDING.put(other.getUUID(), new Req(me.getUUID(), mover.getUUID(), dest.getUUID(), me.server.getTickCount() + TIMEOUT_TICKS));
        String ask = here ? Nicknames.nick(me) + "님이 당신을 데려가려고 해요." : Nicknames.nick(me) + "님이 당신에게 오려고 해요.";
        other.sendSystemMessage(Component.literal("[텔레포트] " + ask + " ").withStyle(ChatFormatting.AQUA)
                .append(button("[예]", ChatFormatting.GREEN, "/수락")).append(" ")
                .append(button("[아니요]", ChatFormatting.RED, "/거절"))
                .append(Component.literal(" (10초)").withStyle(ChatFormatting.GRAY)));
        me.sendSystemMessage(Component.literal("[텔레포트] " + Nicknames.nick(other) + "님에게 요청을 보냈어요. (10초 안에 대답이 없으면 취소)").withStyle(ChatFormatting.GRAY));
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
            from.sendSystemMessage(Component.literal("[텔레포트] " + Nicknames.nick(me) + "님이 거절했어요.").withStyle(ChatFormatting.RED));
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
            String n = Nicknames.nick(p);
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
        mover.sendSystemMessage(Component.literal("[텔레포트] " + Nicknames.nick(dest) + "님에게 이동했어요.").withStyle(ChatFormatting.AQUA));
        dest.sendSystemMessage(Component.literal("[텔레포트] " + Nicknames.nick(mover) + "님이 왔어요.").withStyle(ChatFormatting.AQUA));
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
