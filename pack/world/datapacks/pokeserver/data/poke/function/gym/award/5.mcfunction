# 자동 생성: tools/build_league.py
tag @s add poke.badge5
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"핑크배지","color":"#F078B4","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 5번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1005,minecraft:custom_data={pokeserver:"badge5"}] 1
title @s title {"text":"핑크배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 5번째 체육관을 클리어하였습니다! (관장 독수 · 핑크배지)","color":"yellow"}]
function poke:mod/prize/6000
function poke:gym/leave
