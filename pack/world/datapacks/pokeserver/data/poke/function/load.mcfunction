scoreboard objectives add poke.gym dummy
scoreboard objectives add poke.left minecraft.custom:minecraft.leave_game
scoreboard objectives add poke.died deathCount
scoreboard objectives add home trigger
function poke:config
# 4. 포켓몬 외 몹 스폰 끔 (Cobblemon은 자체 규칙 doPokemonSpawning을 따로 씀)
gamerule doMobSpawning false
gamerule doPatrolSpawning false
gamerule doTraderSpawning false
gamerule doInsomnia false
gamerule doWardenSpawning false
gamerule disableRaids true
# 7. 인벤세이브
gamerule keepInventory true
gamerule spawnRadius 0
# 건물 버전이 바뀌면 자동으로 다시 지음 (build/ 수정 시 숫자 +1)
execute unless data storage poke:state {build:1} run function poke:build/start
