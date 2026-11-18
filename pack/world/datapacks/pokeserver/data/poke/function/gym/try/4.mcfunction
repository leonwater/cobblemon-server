# 자동 생성: tools/build_league.py
# 4번 체육관 도전 (체육관 안내원 화면에서 고름): 순서·재도전·혼자만 도전 확인 후 경기장으로
execute if score @s poke.gym matches 1.. run return 0
execute unless entity @s[tag=poke.tutorial_done] run return run function poke:gym/deny/4 {msg:"튜토리얼을 먼저 끝내 주세요."}
execute if entity @s[tag=poke.badge4] run return run function poke:gym/deny/4 {msg:"이미 이긴 체육관이에요. 다시 도전할 수 없어요."}
execute unless entity @s[tag=poke.badge3] run return run function poke:gym/deny/4 {msg:"3번 체육관 배지를 먼저 얻어야 도전할 수 있어요."}
execute if entity @a[scores={poke.gym=4}] run return run function poke:gym/deny/4 {msg:"다른 도전자가 관장과 싸우는 중이에요. 잠시 후 다시 와 주세요."}
scoreboard players set @s poke.gym 4
execute in poke:town run tp @s 3130.5 -59 -6.5 0 0
title @s title {"text":"4번 체육관","color":"gold"}
title @s subtitle {"text":"풀 타입 · 관장 민화","color":"white"}
tellraw @s {"text":"관장을 우클릭하면 배틀이 시작돼요. 나가려면 주황 발판을 밟으세요.","color":"gray"}
