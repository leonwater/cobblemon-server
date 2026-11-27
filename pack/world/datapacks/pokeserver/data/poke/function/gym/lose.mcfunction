# 자동 생성: tools/build_league.py
# 모드가 호출: 체육관 안에서 NPC 배틀을 지거나 도망쳤을 때
execute unless score @s poke.gym matches 1.. run return 0
execute if score @s poke.gym matches 9 run tellraw @s {"text":"사천왕 도전 실패... 1분 뒤에 처음(첫 번째 사천왕)부터 다시 도전해요.","color":"red"}
execute if score @s poke.gym matches 1..8 run tellraw @s {"text":"관장에게 졌어요. 포켓몬을 회복하고 1분 뒤에 다시 도전하세요!","color":"red"}
execute store result score @s poke.gymcd run time query gametime
scoreboard players add @s poke.gymcd 1200
function poke:gym/leave
