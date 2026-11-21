# 자동 생성: tools/build_league.py
# 사천왕 한 명을 이기면 다음 방, 네 명 모두 이기면 클리어
scoreboard players add @s poke.e4 1
execute if score @s poke.e4 matches 4.. run return run function poke:e4/clear
execute if score @s poke.e4 matches 1 run execute in poke:town run tp @s 3516.5 -59 -28.5 -90 0
execute if score @s poke.e4 matches 1 run title @s subtitle {"text":"2번째: 단델 (불꽃 · 가라르 챔피언)","color":"white"}
execute if score @s poke.e4 matches 1 run title @s title {"text":"다음 방으로","color":"gold"}
execute if score @s poke.e4 matches 1 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕 1번째(성호)를 클리어하였습니다!","color":"yellow"}]
execute if score @s poke.e4 matches 2 run execute in poke:town run tp @s 3516.5 -59 -17.5 -90 0
execute if score @s poke.e4 matches 2 run title @s subtitle {"text":"3번째: 난천 (드래곤 · 신오 챔피언)","color":"white"}
execute if score @s poke.e4 matches 2 run title @s title {"text":"다음 방으로","color":"gold"}
execute if score @s poke.e4 matches 2 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕 2번째(단델)을 클리어하였습니다!","color":"yellow"}]
execute if score @s poke.e4 matches 3 run execute in poke:town run tp @s 3516.5 -59 -6.5 -90 0
execute if score @s poke.e4 matches 3 run title @s subtitle {"text":"4번째: 레드 (관동 전설의 챔피언)","color":"white"}
execute if score @s poke.e4 matches 3 run title @s title {"text":"다음 방으로","color":"gold"}
execute if score @s poke.e4 matches 3 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕 3번째(난천)을 클리어하였습니다!","color":"yellow"}]
