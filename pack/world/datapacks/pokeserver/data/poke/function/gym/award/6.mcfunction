# 자동 생성: tools/build_league.py
tag @s add poke.badge6
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"그린배지","color":"#46AA50","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 6번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1006,minecraft:custom_data={pokeserver:"badge6"}] 1
give @s mega_showdown:dynamax_band 1
tellraw @s {"text":"다이맥스밴드를 받았어요! 손에 들거나 장신구 칸에 끼면 배틀에서 다이맥스를 쓸 수 있어요.","color":"aqua"}
title @s title {"text":"그린배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 6번째 체육관을 클리어하였습니다! (관장 비주기 · 그린배지)","color":"yellow"}]
function poke:mod/prize/7000
function poke:gym/leave
