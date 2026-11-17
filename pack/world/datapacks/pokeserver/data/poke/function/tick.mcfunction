execute as @a[tag=!poke.joined] run function poke:join/first
execute as @a[scores={poke.left=1..}] run function poke:join/rejoin
execute as @a[scores={poke.died=1..}] run function poke:gym/release
execute as @a[scores={home=1..}] run function poke:home
scoreboard players enable @a home
# 4. 포켓몬 외 몬스터·동물 제거 (스포너·알 등으로 생긴 것까지), 배고픔 없음
execute as @e[type=#poke:blocked_mobs] at @s run tp @s ~ -300 ~
# 허공 아래에서 즉시 제거: 떨어진 아이템도 허공에서 사라짐
kill @e[type=#poke:blocked_mobs]
execute as @a unless predicate poke:has_saturation run effect give @s minecraft:saturation infinite 0 true
