# 자동 생성: tools/build_league.py
tag @s add poke.badge6
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"그린배지","color":"#46AA50","italic":false}',minecraft:lore=['{"text":"잡켓몬 리그 6번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1006,minecraft:custom_data={pokeserver:"badge6"}] 1
function poke:mod/reward/6
title @s title {"text":"그린배지 획득!","color":"gold"}
execute if data storage poke:first g6 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 6번째 체육관을 클리어하였습니다! (관장 비주기 · 그린배지) 축하합니다!","color":"yellow"}]
execute unless data storage poke:first g6 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 6번째 체육관을 클리어하였습니다! (관장 비주기 · 그린배지) 모두 축하해 주세요!","color":"aqua"}]
data modify storage poke:first g6 set value 1
function poke:mod/prize/14000
function poke:gym/leave
