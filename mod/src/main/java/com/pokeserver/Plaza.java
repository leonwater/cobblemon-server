package com.pokeserver;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

/** 15·16. 광장(마을)은 야생 첫 스폰 자리에 있음.
 *  1) 서버를 처음 켜면 꽃 숲 칸들 중 땅이 가장 넓고 평평한 자리를 노이즈 높이로 고름 (청크를 만들지 않아 빠름)
 *  2) 반지름 PROTECT 안은 평평하게, 그 밖 BLEND 칸은 자연 지형과 완만하게 이음 (틱마다 청크 하나씩)
 *  3) 끝나면 데이터팩 poke:build/plaza/start 가 그 자리 기준으로 건물·조경을 지음
 *  광장 반지름 PROTECT 안: 블록 수정 금지, 포켓몬 스폰 금지. 그 밖 ~ 200칸: 저레벨 (CobblemonHooks). */
public final class Plaza {
    private Plaza() {}

    public static final int PROTECT = 72, BLEND = 28, BUILD_VERSION = 1;
    static final String DIM = "poke:wild";
    /** 꽃 숲 칸 가운데 (poke:warp/first_wild_find 와 같은 순서, 칸 = 256x256). */
    static final int[][] CELLS = {{1920, 2176}, {2176, 1920}, {1664, 2432}, {2432, 1664}, {1408, 2688}, {2688, 1408},
            {1152, 2944}, {2944, 1152}, {-4736, -4736}, {-4480, -4992}, {-4992, -4480}};

    static BlockPos center;            // 광장 가운데 (땅 블록 높이)
    private static int job = -1;       // 지형 다듬는 중인 청크 순번 (-1: 안 함)

    static CompoundTag state(MinecraftServer s) {
        return s.getCommandStorage().get(ResourceLocation.fromNamespaceAndPath("poke", "state"));
    }

    static void put(MinecraftServer s, CompoundTag st) {
        s.getCommandStorage().set(ResourceLocation.fromNamespaceAndPath("poke", "state"), st);
    }

    static ServerLevel wild(MinecraftServer s) {
        for (ServerLevel l : s.getAllLevels()) if (l.dimension().location().toString().equals(DIM)) return l;
        return null;
    }

    /** 서버 시작: 자리 정하기(처음 한 번) → 지형 → 건물. 광장·야생 스폰·광장 워프(hall) 자리를 저장. */
    static void start(MinecraftServer s) {
        ServerLevel level = wild(s);
        if (level == null) return;
        CompoundTag st = state(s);
        if (!st.contains("plaza")) {
            center = locate(level);
            CompoundTag p = new CompoundTag();
            p.putInt("x", center.getX()); p.putInt("y", center.getY()); p.putInt("z", center.getZ());
            st.put("plaza", p);
            PokeServer.LOG.info("광장 자리: {}", center);
        }
        CompoundTag p = st.getCompound("plaza");
        center = new BlockPos(p.getInt("x"), p.getInt("y"), p.getInt("z"));
        // 도착 지점: 분수 남쪽, 북쪽(분수)을 바라봄. 야생 첫 스폰도 여기
        CompoundTag spawn = new CompoundTag();
        spawn.putDouble("x", center.getX() + 0.5); spawn.putDouble("y", center.getY() + 1); spawn.putDouble("z", center.getZ() + 16.5);
        spawn.putFloat("yaw", 180f);
        st.put("wildspawn", spawn);
        put(s, st);
        CompoundTag hall = spawn.copy();
        hall.putString("dim", DIM);
        hall.putFloat("yaw", 180f);
        CompoundTag cfg = s.getCommandStorage().get(ResourceLocation.fromNamespaceAndPath("poke", "config"));
        cfg.put("hall", hall);
        s.getCommandStorage().set(ResourceLocation.fromNamespaceAndPath("poke", "config"), cfg);
        if (p.getInt("terrain") == 0) job = 0;
        else if (p.getInt("built") != BUILD_VERSION) build(s);
    }

    /** 노이즈 높이로 고름: 바다가 아닌 칸 비율이 높고 높이가 고른 곳. */
    static BlockPos locate(ServerLevel level) {
        var gen = level.getChunkSource().getGenerator();
        var rs = level.getChunkSource().randomState();
        int sea = gen.getSeaLevel();
        double best = -1e9;
        BlockPos pick = new BlockPos(CELLS[0][0], sea + 1, CELLS[0][1]);
        for (int[] c : CELLS) {
            // 칸마다 12칸 간격 높이를 한 번만 계산해 두고 후보 자리들이 같이 씀 (노이즈 계산이 느려서)
            int span = 48 + PROTECT, n0 = span * 2 / 12 + 1;
            int[][] hs = new int[n0][n0];
            for (int i = 0; i < n0; i++) for (int j = 0; j < n0; j++)
                hs[i][j] = gen.getBaseHeight(c[0] - span + i * 12, c[1] - span + j * 12, Heightmap.Types.OCEAN_FLOOR_WG, level, rs);
            for (int ox = -48; ox <= 48; ox += 12) for (int oz = -48; oz <= 48; oz += 12) {
                int n = 0, land = 0;
                double sum = 0, sq = 0;
                for (int dx = -PROTECT; dx <= PROTECT; dx += 12) for (int dz = -PROTECT; dz <= PROTECT; dz += 12) {
                    if (dx * dx + dz * dz > PROTECT * PROTECT) continue;
                    int h = hs[(ox + dx + span) / 12][(oz + dz + span) / 12];
                    n++;
                    if (h >= sea) land++;
                    sum += h; sq += (double) h * h;
                }
                double mean = sum / n, sd = Math.sqrt(Math.max(0, sq / n - mean * mean));
                double score = 100.0 * land / n - sd;
                if (score > best) {
                    best = score;
                    pick = new BlockPos(c[0] + ox, Math.max(sea + 1, (int) Math.round(mean)), c[1] + oz);
                }
            }
            if (best > 90) break;     // 거의 다 땅이고 평평하면 그 칸에서 끝
        }
        return pick;
    }

    /** 지형 다듬기: 틱마다 청크 하나 (반지름 PROTECT+BLEND 둘레). 끝나면 건물을 지음. */
    static void tick(MinecraftServer s) {
        if (job < 0 || center == null) return;
        ServerLevel level = wild(s);
        int r = PROTECT + BLEND, side = (2 * r) / 16 + 2;
        int cx0 = (center.getX() - r) >> 4, cz0 = (center.getZ() - r) >> 4;
        if (job >= side * side) {
            job = -1;
            CompoundTag st = state(s);
            st.getCompound("plaza").putInt("terrain", 1);
            put(s, st);
            PokeServer.LOG.info("광장 지형 다듬기 끝");
            build(s);
            return;
        }
        int ccx = cx0 + job % side, ccz = cz0 + job / side;
        job++;
        level.getChunk(ccx, ccz);   // 없으면 만들어 불러옴
        for (int x = ccx * 16; x < ccx * 16 + 16; x++) for (int z = ccz * 16; z < ccz * 16 + 16; z++) column(level, x, z);
    }

    static void column(ServerLevel level, int x, int z) {
        double d = Math.sqrt(Math.pow(x - center.getX(), 2) + Math.pow(z - center.getZ(), 2));
        if (d > PROTECT + BLEND) return;
        int y0 = center.getY();
        int h = ground(level, x, z);
        double t01 = d <= PROTECT ? 0 : Math.min(1, (d - PROTECT) / BLEND);
        double sm = t01 * t01 * (3 - 2 * t01);
        int t = (int) Math.round(y0 + (h - y0) * sm);
        var pos = new BlockPos.MutableBlockPos();
        // 위쪽 비우기: 광장 안은 나무까지 모두, 둘레는 깎는 만큼 + 그 위 나무
        int top = d <= PROTECT ? y0 + 40 : (t < h ? h + 12 : t);
        for (int y = t + 1; y <= top; y++) {
            pos.set(x, y, z);
            if (!level.getBlockState(pos).isAir()) level.setBlock(pos, Blocks.AIR.defaultBlockState(), 2);
        }
        // 아래 채우기: 빈칸·물을 흙·돌로 (바다 쪽이면 섬처럼 이어짐)
        for (int y = t - 14; y <= t; y++) {
            pos.set(x, y, z);
            BlockState b = level.getBlockState(pos);
            boolean soft = b.isAir() || !b.getFluidState().isEmpty() || b.canBeReplaced() || b.is(BlockTags.LOGS) || b.is(BlockTags.LEAVES);
            if (y == t) level.setBlock(pos, Blocks.GRASS_BLOCK.defaultBlockState(), 2);
            else if (soft || y >= t - 3) level.setBlock(pos, (y >= t - 3 ? Blocks.DIRT : Blocks.STONE).defaultBlockState(), 2);
        }
    }

    /** 자연 땅 높이 (나무·풀·물 아래의 흙·돌). */
    static int ground(ServerLevel level, int x, int z) {
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z) - 1;
        var pos = new BlockPos.MutableBlockPos(x, y, z);
        while (y > level.getMinBuildHeight()) {
            BlockState b = level.getBlockState(pos.setY(y));
            if (!b.isAir() && b.getFluidState().isEmpty() && !b.canBeReplaced() && !b.is(BlockTags.LOGS) && !b.is(BlockTags.LEAVES)) break;
            y--;
        }
        return y;
    }

    /** 건물·조경 (데이터팩): 광장 가운데 기준 상대 좌표로 지음. */
    static void build(MinecraftServer s) {
        CompoundTag st = state(s);
        st.getCompound("plaza").putInt("built", BUILD_VERSION);
        put(s, st);
        s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput(),
                "execute in " + DIM + " positioned " + center.getX() + " " + center.getY() + " " + center.getZ() + " run function poke:build/plaza/start");
    }

    /** 광장 둘레: 블록 수정 금지 (관리자 크리에이티브 제외는 Farms.canEdit). */
    public static boolean protects(net.minecraft.world.level.Level level, BlockPos pos) {
        if (center == null || !level.dimension().location().toString().equals(DIM)) return false;
        double dx = pos.getX() - center.getX(), dz = pos.getZ() - center.getZ();
        return dx * dx + dz * dz <= PROTECT * PROTECT;
    }
}
