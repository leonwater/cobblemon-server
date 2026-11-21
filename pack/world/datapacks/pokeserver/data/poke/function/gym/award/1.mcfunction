# 자동 생성: tools/build_league.py
tag @s add poke.badge1
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"회색배지","color":"#96969B","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 1번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1001,minecraft:custom_data={pokeserver:"badge1"}] 1
function poke:mod/reward/1
title @s title {"text":"회색배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 1번째 체육관을 클리어하였습니다! (관장 웅 · 회색배지)","color":"yellow"}]
function poke:mod/prize/4000
function poke:gym/leave
