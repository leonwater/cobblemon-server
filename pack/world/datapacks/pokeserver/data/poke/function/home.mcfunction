# 어디서든  /광장 (/spawn, /trigger home)  → 광장
scoreboard players reset @s home
# 튜토리얼을 끝내기 전엔 이동 불가 (G 메뉴 워프와 같게)
execute unless entity @s[tag=poke.tutorial_done] run return run tellraw @s {"text":"튜토리얼을 먼저 끝내 주세요.","color":"red"}
# 체육관·사천왕 도전 중엔 못 씀 (예전엔 여기로 빠져나가 도전 점수가 남고 G 메뉴 이동이 계속 막혔음)
execute if score @s poke.gym matches 1.. run return run tellraw @s {"text":"도전 중엔 이동할 수 없어요. 포기하려면 관장 맞은편 주황 발판을 밟으세요.","color":"red"}
function poke:warp/fixed {key:"hall"}
