# 자동 생성: tools/build_league.py
# 관장 소환 준비: 경기장 청크를 불러오고 3초 뒤 접속한 플레이어 한 명으로 소환
execute unless data storage poke:state {leaders:2} run scoreboard players set #lead poke.timer 0
execute unless data storage poke:state {leaders:2} in poke:town run forceload add 3000 -46 3540 18
data modify storage poke:state leaders set value 2
scoreboard players add #lead poke.timer 1
execute if score #lead poke.timer matches 60.. as @a[limit=1] run function poke:mod/spawn_leaders
