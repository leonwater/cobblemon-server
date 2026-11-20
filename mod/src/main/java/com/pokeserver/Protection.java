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

    /** 체력바 위 가운데 알림: 누구 땅인지. */
    static void deny(Player p, net.minecraft.world.level.Level level, net.minecraft.core.BlockPos pos) {
        if (!level.isClientSide()) p.displayClientMessage(Farms.denyReason(level, pos), true);
    }

    static InteractionResult entityRule(Player player, net.minecraft.world.level.Level level, net.minecraft.world.entity.Entity entity) {
        if (entity instanceof LivingEntity && !(entity instanceof ArmorStand) || Farms.canEdit(player, level, entity.blockPosition())) return InteractionResult.PASS;
        deny(player, level, entity.blockPosition());
        return InteractionResult.FAIL;
    }

    static void register() {
        // 9. 블록을 못 고치는 곳(광장·마을·연구소·남의 농장 땅)에선 플레이어끼리 때릴 수 없음 (화살 등 포함)
        net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents.ALLOW_DAMAGE.register((victim, source, amount) -> {
            if (!(victim instanceof Player) || !(source.getEntity() instanceof Player attacker) || attacker == victim) return true;
            if (Farms.canEdit(attacker, victim.level(), victim.blockPosition())) return true;
            attacker.displayClientMessage(Component.literal("여기서는 다른 플레이어를 공격할 수 없어요.").withStyle(ChatFormatting.RED), true);
            return false;
        });
        PlayerBlockBreakEvents.BEFORE.register((level, player, pos, state, be) -> {
            if (Farms.canEdit(player, level, pos)) return true;
            deny(player, level, pos);
            return false;
        });
        AttackBlockCallback.EVENT.register((player, level, hand, pos, dir) -> {
            if (Farms.canEdit(player, level, pos)) return InteractionResult.PASS;
            deny(player, level, pos);   // 부수기 시작하는 순간 막히므로 알림도 여기서
            return InteractionResult.FAIL;
        });
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
            deny(player, level, hit.getBlockPos());
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
            deny(player, level, hit instanceof BlockHitResult b ? b.getBlockPos() : player.blockPosition());
            return InteractionResultHolder.fail(stack);
        });
        // 액자·갑옷 거치대 등 (살아있는 몹·포켓몬은 제외)
        AttackEntityCallback.EVENT.register((player, level, hand, entity, hit) -> entityRule(player, level, entity));
        UseEntityCallback.EVENT.register((player, level, hand, entity, hit) -> entityRule(player, level, entity));
    }

}
