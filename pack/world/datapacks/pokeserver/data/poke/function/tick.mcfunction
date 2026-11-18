execute as @a[tag=!poke.joined] run function poke:join/first
execute as @a unless score @s poke.id matches 1.. run function poke:join/assign_id
execute as @a[scores={poke.left=1..}] run function poke:join/rejoin
execute as @a[tag=poke.tutorial_done] at @s if dimension poke:hub run function poke:join/migrate
execute as @a[scores={poke.died=1..}] run function poke:gym/release
execute as @a[scores={home=1..}] run function poke:home
scoreboard players enable @a home
# 1. 예전 버전에서 튜토리얼을 끝낸 사람은 이미 보상을 받음
tag @a[tag=poke.tutorial_done] add poke.kit_given
# 튜토리얼 방·마을에서는 블록을 부수거나 놓을 수 없게 모험 모드
execute as @a[gamemode=survival] at @s if dimension poke:hub run gamemode adventure @s
execute as @a[gamemode=survival] at @s if dimension poke:town run gamemode adventure @s
execute as @a[gamemode=adventure] at @s unless dimension poke:hub unless dimension poke:town run gamemode survival @s
# 15. 마을 섬·농장·튜토리얼 방 밖으로 못 나감
function poke:bounds
# 체육관·사천왕 나가기 발판, 관장 소환
function poke:league/pads
execute unless data storage poke:state {leaders:1} if entity @a run function poke:league/spawn_tick
# 농장의 "회의장으로" 발판
execute in poke:farm as @a[x=-1,y=-59,z=-8,dx=2,dy=1,dz=2] run function poke:home
# 8. 농장·야생의 마지막 위치를 1초마다 기억
scoreboard players add #t poke.timer 1
execute if score #t poke.timer matches 20.. run function poke:warp/track
# 4. 포켓몬 외 몬스터·동물 제거 (스포너·알 등으로 생긴 것까지), 배고픔 없음
execute as @e[type=#poke:blocked_mobs] at @s run tp @s ~ -300 ~
# 허공 아래에서 즉시 제거: 떨어진 아이템도 허공에서 사라짐
kill @e[type=#poke:blocked_mobs]
execute as @a unless predicate poke:has_saturation run effect give @s minecraft:saturation infinite 0 true
