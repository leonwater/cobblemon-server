# 관장 소환 준비: 체육관 거리 청크를 불러오고 3초 뒤 접속한 플레이어 한 명으로 소환
execute unless data storage poke:state {leaders:2} run scoreboard players set #lead poke.timer 0
execute unless data storage poke:state {leaders:2} in poke:town run forceload add 30 -50 250 15
data modify storage poke:state leaders set value 2
scoreboard players add #lead poke.timer 1
execute if score #lead poke.timer matches 60.. as @a[limit=1] run function poke:mod/spawn_leaders
