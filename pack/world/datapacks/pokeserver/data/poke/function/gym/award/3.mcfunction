# 자동 생성: tools/build_league.py
tag @s add poke.badge3
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"오렌지배지","color":"#F09628","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 3번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1003,minecraft:custom_data={pokeserver:"badge3"}] 1
title @s title {"text":"오렌지배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 3번 체육관 관장 마티스을(를) 이기고 오렌지배지를 얻었습니다!","color":"yellow"}]
function poke:mod/prize/4000
function poke:gym/leave
