# 자동 생성: tools/build_league.py
tag @s add poke.badge3
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"크림슨배지","color":"#D23232","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 3번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1003,minecraft:custom_data={pokeserver:"badge3"}] 1
function poke:mod/reward/3
title @s title {"text":"크림슨배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 3번째 체육관을 클리어하였습니다! (관장 강연 · 크림슨배지)","color":"yellow"}]
function poke:mod/prize/8000
function poke:gym/leave
