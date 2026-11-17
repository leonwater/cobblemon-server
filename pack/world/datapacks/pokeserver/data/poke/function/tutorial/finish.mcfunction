# 튜토리얼 안내원 대화의 마지막 "준비 완료!"에서 실행됨
execute if entity @s[tag=poke.tutorial_done] run return run tellraw @s {"text":"이미 튜토리얼을 완료했습니다.","color":"gray"}
tag @s add poke.tutorial_done
function poke:kit
function poke:util/tp with storage poke:config village
function poke:util/spawnpoint with storage poke:config village
title @s title {"text":"시작 마을","color":"gold"}
title @s subtitle {"text":"기본 물품을 받았습니다","color":"gray"}
