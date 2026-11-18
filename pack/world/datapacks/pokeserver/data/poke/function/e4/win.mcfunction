# 자동 생성: tools/build_league.py
# 사천왕 한 명을 이기면 다음 방, 네 명 모두 이기면 클리어
scoreboard players add @s poke.e4 1
execute if score @s poke.e4 matches 4.. run return run function poke:e4/clear
execute if score @s poke.e4 matches 1 run execute in poke:town run tp @s 206.5 -59 -28.5 -90 0
execute if score @s poke.e4 matches 1 run title @s subtitle {"text":"2번째: 시바 (격투)","color":"white"}
execute if score @s poke.e4 matches 1 run title @s title {"text":"다음 방으로","color":"gold"}
execute if score @s poke.e4 matches 2 run execute in poke:town run tp @s 206.5 -59 -17.5 -90 0
execute if score @s poke.e4 matches 2 run title @s subtitle {"text":"3번째: 국화 (고스트)","color":"white"}
execute if score @s poke.e4 matches 2 run title @s title {"text":"다음 방으로","color":"gold"}
execute if score @s poke.e4 matches 3 run execute in poke:town run tp @s 206.5 -59 -6.5 -90 0
execute if score @s poke.e4 matches 3 run title @s subtitle {"text":"4번째: 목호 (드래곤)","color":"white"}
execute if score @s poke.e4 matches 3 run title @s title {"text":"다음 방으로","color":"gold"}
