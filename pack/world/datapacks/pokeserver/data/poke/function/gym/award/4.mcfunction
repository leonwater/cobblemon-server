# 자동 생성: tools/build_league.py
tag @s add poke.badge4
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"핑크배지","color":"#F078B4","italic":false}',minecraft:lore=['{"text":"잡켓몬 리그 4번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1004,minecraft:custom_data={pokeserver:"badge4"}] 1
function poke:mod/reward/4
title @s title {"text":"핑크배지 획득!","color":"gold"}
execute if data storage poke:first g4 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 4번째 체육관을 클리어하였습니다! (관장 독수 · 핑크배지) 축하합니다!","color":"yellow"}]
execute unless data storage poke:first g4 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 4번째 체육관을 클리어하였습니다! (관장 독수 · 핑크배지) 모두 축하해 주세요!","color":"aqua"}]
execute unless data storage poke:first g4 run tag @s add poke.firstclear
data modify storage poke:first g4 set value 1
function poke:mod/prize/10000
function poke:gym/leave
