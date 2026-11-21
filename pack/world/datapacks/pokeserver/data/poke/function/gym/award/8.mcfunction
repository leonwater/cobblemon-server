# 자동 생성: tools/build_league.py
tag @s add poke.badge8
give @s minecraft:gold_nugget[minecraft:custom_name='{"text":"블루배지","color":"#3C78E6","italic":false}',minecraft:lore=['{"text":"포켓서버 리그 8번 체육관 배지","color":"gray","italic":false}'],minecraft:custom_model_data=1008,minecraft:custom_data={pokeserver:"badge8"}] 1
give @s mega_showdown:tera_orb 1
tellraw @s {"text":"테라스탈 오브를 받았어요! 손에 들거나 장신구 칸에 끼면 배틀에서 테라스탈을 쓸 수 있어요.","color":"aqua"}
title @s title {"text":"블루배지 획득!","color":"gold"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 8번째 체육관을 클리어하였습니다! (관장 이슬 · 블루배지)","color":"yellow"}]
function poke:mod/prize/9000
function poke:gym/leave
