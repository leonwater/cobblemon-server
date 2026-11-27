# 자동 생성: tools/build_league.py
tag @s add poke.badge3
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"크림슨배지","color":"#D23232","italic":false}',minecraft:lore=['{"text":"잡켓몬 리그 3번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1003,minecraft:custom_data={pokeserver:"badge3"}] 1
function poke:mod/reward/3
title @s title {"text":"크림슨배지 획득!","color":"gold"}
execute if data storage poke:first g3 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 3번째 체육관을 클리어하였습니다! (관장 강연 · 크림슨배지) 축하합니다!","color":"yellow"}]
execute unless data storage poke:first g3 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 3번째 체육관을 클리어하였습니다! (관장 강연 · 크림슨배지) 모두 축하해 주세요!","color":"aqua"}]
execute unless data storage poke:first g3 run tag @s add poke.firstclear
data modify storage poke:first g3 set value 1
function poke:mod/prize/8000
function poke:gym/leave
