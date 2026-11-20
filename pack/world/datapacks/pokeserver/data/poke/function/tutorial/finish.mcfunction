# 튜토리얼 설명 창의 마지막 "준비 완료!"에서 실행됨 (닉네임은 모드가 먼저 저장)
tag @s add poke.tutorial_done
# 기본 물품은 처음 한 번만 (튜토리얼을 다시 해도 안 줌)
execute unless entity @s[tag=poke.kit_given] run function poke:kit
execute unless entity @s[tag=poke.kit_given] run title @s subtitle {"text":"기본 물품을 받았습니다","color":"gray"}
tag @s add poke.kit_given
# 10. 바로 옮기지 않음: 뒤의 철문으로 나가면 광장 (tutorial/leave, bounds가 감지)
title @s title {"text":"튜토리얼 완료!","color":"gold"}
tellraw @s {"text":"뒤의 철문으로 나가면 광장으로 이동해요.","color":"yellow"}
