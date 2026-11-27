package com.pokeserver.client.mixin;

import com.cobblemon.mod.common.client.battle.SingleActionRequest;
import com.cobblemon.mod.common.client.gui.battle.BattleGUI;
import com.cobblemon.mod.common.client.gui.battle.subscreen.BattleGeneralActionSelection;
import com.cobblemon.mod.common.client.gui.battle.widgets.BattleOptionTile;
import com.pokeserver.client.BagScreen;
import kotlin.Unit;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** 2. 행동 선택 4칸을 원작처럼 2×2: 싸운다(왼쪽 위) · 가방(오른쪽 위) / 포켓몬(왼쪽 아래) · 도망·기권(오른쪽 아래).
 *  코블몬 "잡기"(야생)는 가방 안의 볼로 옮김. */
@Mixin(value = BattleGeneralActionSelection.class, remap = false)
abstract class GeneralActionMixin {
    @Inject(method = "<init>", at = @At("RETURN"))
    private void pokeserver$bag(BattleGUI gui, SingleActionRequest request, CallbackInfo ci) {
        var tiles = ((BattleGeneralActionSelection) (Object) this).getTiles();
        BattleOptionTile fight = null, sw = null, run = null;
        boolean wild = false;
        for (var t : tiles) {
            String path = t.getResource().getPath();
            if (path.contains("fight")) fight = t;
            else if (path.contains("switch")) sw = t;
            else if (path.contains("bag")) wild = true;             // 잡기(야생 배틀에만 있음)
            else run = t;                                            // 도망·기권
        }
        if (fight == null) return;
        int x0 = fight.getX(), y0 = fight.getY(), x1 = x0 + 93, y1 = y0 + 29;   // 코블몬과 같은 칸 간격 (12·105, 26+3)
        final boolean w = wild;
        tiles.clear();
        tiles.add(new BattleOptionTile(gui, x0, y0, fight.getResource(), fight.getText(), fight.getOnClick()));
        tiles.add(new BattleOptionTile(gui, x1, y0, ResourceLocation.fromNamespaceAndPath("cobblemon", "textures/gui/battle/battle_menu_bag.png"),
                Component.literal("가방"), () -> { Minecraft.getInstance().setScreen(new BagScreen(gui, w)); return Unit.INSTANCE; }));
        if (sw != null) tiles.add(new BattleOptionTile(gui, x0, y1, sw.getResource(), sw.getText(), sw.getOnClick()));
        if (run != null) tiles.add(new BattleOptionTile(gui, x1, y1, run.getResource(), run.getText(), run.getOnClick()));
    }
}
