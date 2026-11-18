# 자동 생성: tools/build_league.py
# 모드가 호출: 체육관 안에서 NPC 배틀을 이겼을 때
execute if score @s poke.gym matches 1 run return run function poke:gym/award/1
execute if score @s poke.gym matches 2 run return run function poke:gym/award/2
execute if score @s poke.gym matches 3 run return run function poke:gym/award/3
execute if score @s poke.gym matches 4 run return run function poke:gym/award/4
execute if score @s poke.gym matches 5 run return run function poke:gym/award/5
execute if score @s poke.gym matches 6 run return run function poke:gym/award/6
execute if score @s poke.gym matches 7 run return run function poke:gym/award/7
execute if score @s poke.gym matches 8 run return run function poke:gym/award/8
execute if score @s poke.gym matches 9 run function poke:e4/win
