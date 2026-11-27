scoreboard objectives add poke.gym dummy
scoreboard objectives add poke.gymcd dummy
scoreboard objectives add poke.left minecraft.custom:minecraft.leave_game
scoreboard objectives add poke.died deathCount
scoreboard objectives add poke.id dummy
scoreboard objectives add poke.timer dummy
scoreboard objectives add poke.e4 dummy
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
# 불이 번지거나 블록을 태우지 않음 (라이터·용암·번개로 건물이 타던 문제)
gamerule doFireTick false
# 건물 버전이 바뀌면 자동으로 다시 지음 (tools/build_world.py 실행 후 숫자 +1)
execute unless data storage poke:state {build:25} run function poke:build/start
# 농장은 다시 지으면 플레이어 건축물을 덮어쓸 수 있어 버전을 따로 둠
execute unless data storage poke:state {farm:3} run function poke:build/farm_start
# 야생 미리 만들기는 광장 지형을 다 다듬은 뒤에 (Plaza.java가 시작). 이미 다듬은 월드면 여기서 이어서
execute if data storage poke:state {plaza:{terrain:1}} unless data storage poke:state {pregen:1} run function poke:mod/pregen
