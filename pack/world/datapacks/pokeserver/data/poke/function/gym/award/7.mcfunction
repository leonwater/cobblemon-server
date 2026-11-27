# 자동 생성: tools/build_league.py
tag @s add poke.badge7
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"무지개배지","color":"#78C85A","italic":false}',minecraft:lore=['{"text":"잡켓몬 리그 7번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1007,minecraft:custom_data={pokeserver:"badge7"}] 1
function poke:mod/reward/7
title @s title {"text":"무지개배지 획득!","color":"gold"}
execute if data storage poke:first g7 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 7번째 체육관을 클리어하였습니다! (관장 민화 · 무지개배지) 축하합니다!","color":"yellow"}]
execute unless data storage poke:first g7 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 7번째 체육관을 클리어하였습니다! (관장 민화 · 무지개배지) 모두 축하해 주세요!","color":"aqua"}]
data modify storage poke:first g7 set value 1
function poke:mod/prize/16000
function poke:gym/leave
