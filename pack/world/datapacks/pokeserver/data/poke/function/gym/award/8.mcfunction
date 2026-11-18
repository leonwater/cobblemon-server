# 자동 생성: tools/build_league.py
tag @s add poke.badge8
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"그린배지","color":"#46AA50","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 8번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1008,minecraft:custom_data={pokeserver:"badge8"}] 1
title @s title {"text":"그린배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 8번 체육관 관장 비주기을(를) 이기고 그린배지를 얻었습니다!","color":"yellow"}]
function poke:gym/leave
