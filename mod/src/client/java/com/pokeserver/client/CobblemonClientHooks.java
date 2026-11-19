package com.pokeserver.client;

import com.cobblemon.mod.common.client.CobblemonClient;
import com.cobblemon.mod.common.client.gui.pokedex.PokedexGUI;
import com.cobblemon.mod.common.client.gui.summary.Summary;
import com.cobblemon.mod.common.client.pokedex.PokedexType;
import java.util.Objects;

/** Cobblemon이 있을 때만 불림. */
final class CobblemonClientHooks {
    private CobblemonClientHooks() {}

    /** @return 파티가 비어 있으면 false */
    static boolean openParty() {
        var party = CobblemonClient.INSTANCE.getStorage().getParty().getSlots().stream().filter(Objects::nonNull).toList();
        if (party.isEmpty()) return false;
        Summary.Companion.open(party, true, 0);
        return true;
    }

    static void openDex() {
        PokedexGUI.Companion.open(CobblemonClient.INSTANCE.getClientPokedexData(), PokedexType.RED, null, null);
    }

}
