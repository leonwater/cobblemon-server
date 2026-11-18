# 자동 생성: tools/build_league.py
tag @s add poke.badge6
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"골드배지","color":"#F0C83C","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 6번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1006,minecraft:custom_data={pokeserver:"badge6"}] 1
title @s title {"text":"골드배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 6번 체육관 관장 초련을(를) 이기고 골드배지를 얻었습니다!","color":"yellow"}]
function poke:gym/leave
