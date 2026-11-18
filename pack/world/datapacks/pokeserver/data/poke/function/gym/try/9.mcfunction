# 자동 생성: tools/build_league.py
# 사천왕 도전: 배지 8개, 이미 클리어했으면 불가, 한 번에 한 명
execute if score @s poke.gym matches 1.. run return 0
execute if entity @s[tag=poke.e4clear] run return run function poke:gym/deny/9 {msg:"이미 사천왕을 모두 이겼어요. 다시 도전할 수 없어요."}
execute unless entity @s[tag=poke.badge8] run return run function poke:gym/deny/9 {msg:"배지 8개를 모두 모아야 사천왕에 도전할 수 있어요."}
execute if entity @a[scores={poke.gym=9}] run return run function poke:gym/deny/9 {msg:"다른 도전자가 사천왕에 도전 중이에요. 잠시 후 다시 와 주세요."}
scoreboard players set @s poke.gym 9
scoreboard players set @s poke.e4 0
execute in poke:town run tp @s 3416.5 -59 -39.5 -90 0
title @s title {"text":"사천왕","color":"gold"}
title @s subtitle {"text":"첫 번째: 성호 (강철)","color":"white"}
tellraw @s {"text":"사천왕 4명을 한 번에 모두 이겨야 클리어예요. 한 번이라도 지면 처음부터!","color":"gray"}
