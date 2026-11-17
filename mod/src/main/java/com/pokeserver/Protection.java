package com.pokeserver;

import net.fabricmc.fabric.api.event.player.AttackBlockCallback;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;

/** 6. 농장: 주인만 편집, 다른 사람은 구경만. */
final class Protection {
    private Protection() {}

    static void deny(Player p) {
        p.displayClientMessage(Component.literal("다른 사람의 땅이거나 주인 없는 땅입니다. 구경만 할 수 있어요.").withStyle(ChatFormatting.RED), true);
    }

    static void register() {
        PlayerBlockBreakEvents.BEFORE.register((level, player, pos, state, be) -> {
            if (Farms.canEdit(player, level, pos)) return true;
            deny(player);
            return false;
        });
        AttackBlockCallback.EVENT.register((player, level, hand, pos, dir) ->
                Farms.canEdit(player, level, pos) ? InteractionResult.PASS : InteractionResult.FAIL);
        UseBlockCallback.EVENT.register((player, level, hand, hit) -> {
            if (!Farms.isFarm(level) || level.isClientSide()) return InteractionResult.PASS;
            // 땅 문서로 빈 땅 우클릭 → 확인 팝업
            if (Farms.isDeed(player.getItemInHand(hand))) {
                Farms.Plot plot = Farms.plotAt(hit.getBlockPos());
                if (plot == null) return InteractionResult.FAIL;
                if (ServerData.get(level.getServer()).plotOwners.containsKey(plot.id())) {
                    player.displayClientMessage(Component.literal("이미 주인이 있는 땅입니다.").withStyle(ChatFormatting.RED), true);
                } else {
                    ServerPlayNetworking.send((ServerPlayer) player, new Net.ClaimPopup(plot.id()));
                }
                return InteractionResult.SUCCESS;
            }
            boolean ok = Farms.canEdit(player, level, hit.getBlockPos());
            // 블록을 놓을 때는 놓이는 자리도 내 땅이어야 함
            if (ok && player.getItemInHand(hand).getItem() instanceof BlockItem) {
                ok = Farms.canEdit(player, level, hit.getBlockPos().relative(hit.getDirection()));
            }
            if (ok) return InteractionResult.PASS;
            deny(player);
            return InteractionResult.FAIL;
        });
        UseItemCallback.EVENT.register((player, level, hand) -> {
            var stack = player.getItemInHand(hand);
            if (!(stack.getItem() instanceof BucketItem) || !Farms.isFarm(level) || level.isClientSide()) {
                return InteractionResultHolder.pass(stack);
            }
            // 물·용암 붓기/뜨기: 바라보는 곳이 내 땅이어야 함
            HitResult hit = player.pick(player.blockInteractionRange(), 0, true);
            if (hit instanceof BlockHitResult b && hit.getType() == HitResult.Type.BLOCK
                    && Farms.canEdit(player, level, b.getBlockPos())
                    && Farms.canEdit(player, level, b.getBlockPos().relative(b.getDirection()))) {
                return InteractionResultHolder.pass(stack);
            }
            deny(player);
            return InteractionResultHolder.fail(stack);
        });
        // 액자·갑옷 거치대 등 (살아있는 몹·포켓몬은 제외)
        AttackEntityCallback.EVENT.register((player, level, hand, entity, hit) ->
                entity instanceof LivingEntity && !(entity instanceof ArmorStand) || Farms.canEdit(player, level, entity.blockPosition())
                        ? InteractionResult.PASS : InteractionResult.FAIL);
        UseEntityCallback.EVENT.register((player, level, hand, entity, hit) ->
                entity instanceof LivingEntity && !(entity instanceof ArmorStand) || Farms.canEdit(player, level, entity.blockPosition())
                        ? InteractionResult.PASS : InteractionResult.FAIL);
    }

}
