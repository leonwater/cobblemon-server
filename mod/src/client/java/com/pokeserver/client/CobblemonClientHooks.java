package com.pokeserver.client;

import com.cobblemon.mod.common.api.pokedex.PokedexEntryProgress;
import com.cobblemon.mod.common.api.pokemon.PokemonSpecies;
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

    static int partySize() {
        return (int) CobblemonClient.INSTANCE.getStorage().getParty().getSlots().stream().filter(Objects::nonNull).count();
    }

    static void openDex() {
        PokedexGUI.Companion.open(CobblemonClient.INSTANCE.getClientPokedexData(), PokedexType.RED, null, null);
    }

    /** {잡은 수, 마주친 수, 전체 종 수} */
    static int[] dexCounts() {
        int caught = 0, seen = 0;
        for (var r : CobblemonClient.INSTANCE.getClientPokedexData().getSpeciesRecords().values()) {
            if (r.getKnowledge() == PokedexEntryProgress.OWNED) caught++;
            if (r.getKnowledge() != PokedexEntryProgress.UNREGISTERED) seen++;
        }
        return new int[]{caught, seen, PokemonSpecies.getImplemented().size()};
    }
}
