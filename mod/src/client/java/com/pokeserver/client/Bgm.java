package com.pokeserver.client;

import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.Music;
import net.minecraft.sounds.SoundEvent;

/** 공간별 BGM: 그 자리에 있을 때만 (마인크래프트 "음악" 소리 크기로 조절). 자리는 서버가 보내는 정보창 "위치" 값으로 고름.
 *  마인크래프트 음악 관리(MusicManager)에 그대로 맡김: MusicMixin이 지금 틀 곡을 바꿔 주고, 자리를 벗어나면 tick()이 끔. */
public final class Bgm {
    private Bgm() {}

    static final Music TITLE = music("bgm_1");                      // 마인크래프트 메인 화면
    static final Map<String, Music> AT = Map.of(
            "광장 마을", music("bgm_2"),
            "포켓몬 센터", music("bgm_10"),
            "체육관", music("bgm_20"),                              // 로비만 (관장을 고르면 가는 경기장은 "경기장"이라 없음)
            "오박사 연구소", music("bgm_13"));                       // 튜토리얼 공간

    /** 같은 곡이 끝나면 쉬지 않고 다시 (delay 0), 다른 음악이 나오던 중이면 바로 바꿈. */
    static Music music(String id) {
        return new Music(Holder.direct(SoundEvent.createVariableRangeEvent(ResourceLocation.fromNamespaceAndPath("pokeserver", "bgm." + id))), 0, 0, true);
    }

    /** 지금 자리의 곡 (없으면 null = 마인크래프트 기본 음악). MusicMixin이 부름. */
    public static Music situational(Minecraft mc) { return now(mc); }

    static Music now(Minecraft mc) {
        if (mc.player == null) return TITLE;
        return AT.get(InfoHud.place);
    }

    /** 매 틱: 우리 곡이 나오는데 그 자리를 벗어났으면 끔 (마인크래프트는 기본 음악으로 바뀔 때 앞 곡을 끝까지 틀기 때문). */
    static void tick(Minecraft mc) {
        Music want = now(mc);
        var mm = mc.getMusicManager();
        if (want != TITLE && mm.isPlayingMusic(TITLE)) mm.stopPlaying(TITLE);
        for (Music m : AT.values()) if (m != want && mm.isPlayingMusic(m)) mm.stopPlaying(m);
    }
}
