# 자동 생성: tools/build_league.py
# 1번 체육관 도전 (체육관 안내원 화면에서 고름): 순서·재도전·혼자만 도전 확인 후 경기장으로
execute if score @s poke.gym matches 1.. run return 0
execute unless entity @s[tag=poke.tutorial_done] run return run function poke:gym/deny/1 {msg:"튜토리얼을 먼저 끝내 주세요."}
execute if entity @s[tag=poke.badge1] run return run function poke:gym/deny/1 {msg:"이미 이긴 체육관이에요. 다시 도전할 수 없어요."}
execute store result score #now poke.gymcd run time query gametime
execute if score @s poke.gymcd > #now poke.gymcd run return run function poke:gym/deny/1 {msg:"관장에게 진 뒤 5분 동안은 다시 도전할 수 없어요."}
execute if entity @a[scores={poke.gym=1}] run return run function poke:gym/deny/1 {msg:"다른 도전자가 관장과 싸우는 중이에요. 잠시 후 다시 와 주세요."}
scoreboard players set @s poke.gym 1
execute in poke:town run tp @s 3015.5 -59 -13.5 0 0
title @s title {"text":"1번 체육관","color":"gold"}
title @s subtitle {"text":"바위 타입 · 관장 웅","color":"white"}
tellraw @s {"text":"관장을 우클릭하면 배틀이 시작돼요. 나가려면 주황 발판을 밟으세요.","color":"gray"}
