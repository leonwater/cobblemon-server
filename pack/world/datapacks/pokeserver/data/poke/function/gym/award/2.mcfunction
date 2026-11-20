# 자동 생성: tools/build_league.py
tag @s add poke.badge2
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"블루배지","color":"#3C78E6","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 2번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1002,minecraft:custom_data={pokeserver:"badge2"}] 1
title @s title {"text":"블루배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 2번째 체육관을 클리어하였습니다! (관장 이슬 · 블루배지)","color":"yellow"}]
function poke:mod/prize/3000
function poke:gym/leave
