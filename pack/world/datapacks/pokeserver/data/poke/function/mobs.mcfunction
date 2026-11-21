# 포켓몬 외 몬스터·동물 제거 (스포너·알 등으로 생긴 것까지). tick에서 1초마다
execute as @e[type=#poke:blocked_mobs] at @s run tp @s ~ -300 ~
# 허공 아래에서 제거: 떨어진 아이템도 허공에서 사라짐
kill @e[type=#poke:blocked_mobs]
