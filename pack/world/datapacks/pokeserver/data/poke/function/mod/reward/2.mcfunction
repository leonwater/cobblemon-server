# 자동 생성: tools/build_league.py
give @s mega_showdown:z_ring 1
tellraw @s {"text":"Z링을 받았어요! 손에 들거나 장신구 칸에 끼면 배틀에서 Z기술을 쓸 수 있어요.","color":"aqua"}
give @s cobblemon:exp_candy_s 5
give @s cobblemon:technical_machine[cobblemon:tm_move={move:"thunderbolt"}] 1
tellraw @s {"text":"보상: 경험사탕 5개, 기술머신(thunderbolt) 1장","color":"aqua"}
