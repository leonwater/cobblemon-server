# 튜토리얼 안내원 대화의 마지막 "준비 완료!"에서 실행됨
tag @s add poke.tutorial_done
# 기본 물품은 처음 한 번만 (튜토리얼을 다시 해도 안 줌)
execute unless entity @s[tag=poke.kit_given] run function poke:kit
execute unless entity @s[tag=poke.kit_given] run title @s subtitle {"text":"기본 물품을 받았습니다","color":"gray"}
tag @s add poke.kit_given
function poke:util/tp with storage poke:config hall
function poke:util/spawnpoint with storage poke:config hall
title @s title {"text":"회의장","color":"gold"}
