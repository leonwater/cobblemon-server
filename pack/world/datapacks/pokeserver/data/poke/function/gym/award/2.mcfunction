# 자동 생성: tools/build_league.py
tag @s add poke.badge2
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"골드배지","color":"#F0C83C","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 2번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1002,minecraft:custom_data={pokeserver:"badge2"}] 1
give @s mega_showdown:z_ring 1
tellraw @s {"text":"Z링을 받았어요! 손에 들거나 장신구 칸에 끼면 배틀에서 Z기술을 쓸 수 있어요.","color":"aqua"}
title @s title {"text":"골드배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 2번째 체육관을 클리어하였습니다! (관장 초련 · 골드배지)","color":"yellow"}]
function poke:mod/prize/3000
function poke:gym/leave
