# 튜토리얼 설명 창의 마지막 "준비 완료!"에서 실행됨 (닉네임은 모드가 먼저 저장)
tag @s add poke.tutorial_done
# 기본 물품은 처음 한 번만 (튜토리얼을 다시 해도 안 줌)
execute unless entity @s[tag=poke.kit_given] run function poke:kit
execute unless entity @s[tag=poke.kit_given] run title @s subtitle {"text":"기본 물품을 받았습니다","color":"gray"}
tag @s add poke.kit_given
# 2. 끝나면 바로 광장으로 (스타팅 포켓몬 고르기 창은 도착하고 2초 뒤 모드가 띄움)
tellraw @s {"text":"튜토리얼 완료! 광장으로 이동합니다.","color":"yellow"}
function poke:tutorial/leave
