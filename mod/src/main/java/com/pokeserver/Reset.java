package com.pokeserver;

import com.google.gson.JsonParser;
import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import net.fabricmc.api.EnvType;
import net.fabricmc.loader.api.FabricLoader;

/**
 * 8. 월드 초기화: config/pokeserver/reset.json 의 season 이 월드에 적힌 값보다 크면, 서버가 월드를 열기 전에
 * 월드 폴더 내용을 옆의 "world-backup-..." 폴더로 옮김 (지우지 않음 → 되돌리려면 폴더를 다시 옮기면 됨).
 * 데이터팩(datapacks)은 그대로 두어 새 월드에서도 쓰임.
 */
final class Reset {
    private Reset() {}
    static final Set<String> KEEP = Set.of("datapacks", "serverconfig", "session.lock");
    static final String MARK = "pokeserver-season.txt";
    /** 2. /초기화(전체)가 남기는 표시 (서버 폴더). 있으면 시즌과 상관없이 월드를 새로 시작하고 지움. */
    static final String WIPE = "pokeserver-wipe.txt";

    static void run() {
        if (FabricLoader.getInstance().getEnvironmentType() != EnvType.SERVER) return;
        Path root = FabricLoader.getInstance().getGameDir();
        try {
            int want = JsonParser.parseString(Files.readString(FabricLoader.getInstance().getConfigDir().resolve("pokeserver/reset.json")))
                    .getAsJsonObject().get("season").getAsInt();
            Path world = root.resolve(levelName(root));
            Path mark = world.resolve(MARK);
            int have = Files.exists(mark) ? Integer.parseInt(Files.readString(mark).trim()) : 0;
            Path wipe = root.resolve(WIPE);
            if (have >= want && !Files.exists(wipe)) return;
            if (Files.exists(world.resolve("level.dat"))) backup(world, have);
            Files.createDirectories(world);
            Files.writeString(mark, String.valueOf(Math.max(want, have)));
            Files.deleteIfExists(wipe);
        } catch (IllegalStateException ex) {
            throw ex;
        } catch (IOException | RuntimeException ex) {
            // 초기화 설정이 없거나 읽기 실패 → 아무것도 옮기지 않음 (월드 그대로)
            if (!(ex instanceof java.nio.file.NoSuchFileException)) PokeServer.LOG.error("월드 초기화 확인 실패", ex);
        }
    }

    static String levelName(Path root) throws IOException {
        Path f = root.resolve("server.properties");
        if (!Files.exists(f)) return "world";
        Properties p = new Properties();
        try (Reader r = Files.newBufferedReader(f)) { p.load(r); }
        return p.getProperty("level-name", "world");
    }

    /** 월드 내용을 백업 폴더로 옮김. 중간에 실패하면 옮긴 것을 되돌리고 서버 시작을 멈춤 (반쯤 초기화된 월드로 열지 않게). */
    static void backup(Path world, int season) throws IOException {
        String stamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss"));
        Path to = world.resolveSibling(world.getFileName() + "-backup-season" + season + "-" + stamp);
        Files.createDirectories(to);
        List<Path> moved = new ArrayList<>();
        try (var list = Files.list(world)) {
            for (Path p : list.toList()) {
                if (KEEP.contains(p.getFileName().toString())) continue;
                Files.move(p, to.resolve(p.getFileName()));
                moved.add(p);
            }
        } catch (IOException ex) {
            for (Path p : moved) Files.move(to.resolve(p.getFileName()), p);
            throw new IllegalStateException("월드 초기화 실패 (옮긴 파일은 되돌림). 서버를 끄고 다시 켜 보세요: " + ex, ex);
        }
        // 서버장이 고른 초기화 대상 중 월드 밖에 있는 것: 배틀 기록(battle_logs)도 같은 백업 폴더로 (게임에는 영향 없음 → 실패해도 초기화는 계속)
        Path logs = world.resolveSibling("battle_logs");
        try {
            if (Files.isDirectory(logs)) Files.move(logs, to.resolve("battle_logs"));
        } catch (IOException ex) {
            PokeServer.LOG.warn("배틀 기록 폴더를 백업 폴더로 옮기지 못함: {}", ex.toString());
        }
        PokeServer.LOG.warn("월드를 초기화했습니다. 이전 월드는 {} 에 보관됨", to);
    }
}
