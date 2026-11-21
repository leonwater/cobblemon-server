execute as @a[tag=!poke.joined] run function poke:join/first
execute as @a unless score @s poke.id matches 1.. run function poke:join/assign_id
execute as @a[scores={poke.left=1..}] run function poke:join/rejoin
# 튜토리얼을 끝낸 사람이 튜토리얼 차원에 남아 있으면(접속이 끊겼다 다시 들어오는 등) 광장으로
execute as @a[tag=poke.tutorial_done] at @s if dimension poke:hub run function poke:join/migrate
execute as @a[scores={poke.died=1..}] run function poke:gym/release
execute as @a[scores={home=1..}] run function poke:home
scoreboard players enable @a home
# 1. 예전 버전에서 튜토리얼을 끝낸 사람은 이미 보상을 받음
tag @a[tag=poke.tutorial_done] add poke.kit_given
# 튜토리얼 방·마을에서는 블록을 부수거나 놓을 수 없게 모험 모드
execute as @a[gamemode=survival] at @s if dimension poke:hub run gamemode adventure @s
execute as @a[gamemode=survival] at @s if dimension poke:town run gamemode adventure @s
# 야생(광장 안은 모험 모드)은 모드가 정함 (Plaza.modes)
execute as @a[gamemode=adventure] at @s unless dimension poke:hub unless dimension poke:town unless dimension poke:wild run gamemode survival @s
# 15. 마을 섬·농장·튜토리얼 방 밖으로 못 나감
function poke:bounds
# 체육관·사천왕 나가기 발판, 관장 소환
function poke:league/pads
execute unless data storage poke:state {leaders:1} if entity @a run function poke:league/spawn_tick
# 농장의 "광장으로" 발판
execute in poke:farm as @a[x=-1,y=-59,z=-8,dx=2,dy=1,dz=2] run function poke:home
# 8. 농장·야생의 마지막 위치를 1초마다 기억
scoreboard players add #t poke.timer 1
# 4. 포켓몬 외 몬스터·동물 제거는 1초마다 (모든 엔티티를 훑어서 매 틱은 비쌈). track이 타이머를 0으로 돌리므로 먼저
execute if score #t poke.timer matches 20.. run function poke:mobs
execute if score #t poke.timer matches 20.. run function poke:warp/track
# 배고픔 없음
execute as @a unless predicate poke:has_saturation run effect give @s minecraft:saturation infinite 0 true
