# 자동 생성: tools/build_league.py
tag @s add poke.badge7
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"크림슨배지","color":"#D23232","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 7번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1007,minecraft:custom_data={pokeserver:"badge7"}] 1
title @s title {"text":"크림슨배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 7번 체육관 관장 강연을(를) 이기고 크림슨배지를 얻었습니다!","color":"yellow"}]
function poke:gym/leave
