# 자동 생성: tools/build_league.py
tag @s add poke.badge2
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"오렌지배지","color":"#F09628","italic":false}',minecraft:lore=['{"text":"잡켓몬 리그 2번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1002,minecraft:custom_data={pokeserver:"badge2"}] 1
function poke:mod/reward/2
title @s title {"text":"오렌지배지 획득!","color":"gold"}
execute if data storage poke:first g2 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 2번째 체육관을 클리어하였습니다! (관장 마티스 · 오렌지배지) 축하합니다!","color":"yellow"}]
execute unless data storage poke:first g2 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 2번째 체육관을 클리어하였습니다! (관장 마티스 · 오렌지배지) 모두 축하해 주세요!","color":"aqua"}]
data modify storage poke:first g2 set value 1
function poke:mod/prize/6000
function poke:gym/leave
