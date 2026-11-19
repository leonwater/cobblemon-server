# 어디서든  /trigger home  → 회의장
scoreboard players reset @s home
# 튜토리얼을 끝내기 전엔 이동 불가 (G 메뉴 워프와 같게)
execute unless entity @s[tag=poke.tutorial_done] run return run tellraw @s {"text":"튜토리얼을 먼저 끝내 주세요.","color":"red"}
function poke:warp/fixed {key:"hall"}
