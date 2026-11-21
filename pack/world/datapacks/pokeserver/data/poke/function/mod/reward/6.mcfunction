# 자동 생성: tools/build_league.py
give @s mega_showdown:dynamax_band 1
tellraw @s {"text":"다이맥스밴드를 받았어요! 손에 들거나 장신구 칸에 끼면 배틀에서 다이맥스를 쓸 수 있어요.","color":"aqua"}
give @s cobblemon:exp_candy_l 5
give @s cobblemon:technical_machine[cobblemon:tm_move={move:"earthquake"}] 1
tellraw @s {"text":"보상: 경험사탕 5개, 기술머신(earthquake) 1장","color":"aqua"}
