# 자동 생성: tools/build_league.py
tag @s add poke.badge2
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"블루배지","color":"#3C78E6","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 2번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1002,minecraft:custom_data={pokeserver:"badge2"}] 1
title @s title {"text":"블루배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 2번 체육관 관장 이슬을(를) 이기고 블루배지를 얻었습니다!","color":"yellow"}]
function poke:gym/leave
