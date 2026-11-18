# 자동 생성: tools/build_world.py. Cobblemon 블록
kill @e[type=cobblemon:pokemon]
setblock 1026 -59 -2 cobblemon:healing_machine[facing=west,natural=false]
setblock 1026 -59 2 cobblemon:healing_machine[facing=west,natural=false]
setblock 1015 -59 -9 cobblemon:pc[facing=north,part=bottom]
setblock 1015 -58 -9 cobblemon:pc[facing=north,part=top]
setblock 1017 -59 -9 cobblemon:pc[facing=north,part=bottom]
setblock 1017 -58 -9 cobblemon:pc[facing=north,part=top]
summon minecraft:text_display 1016.5 -56.4 -8.2 {Tags:["poke.deco"],billboard:"center",shadow:1b,background:-1442840576,transformation:{scale:[0.9f,0.9f,0.9f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},text:'{"text":"PC 박스","color":"aqua","bold":true,"extra":[""]}'}
kill @e[type=minecraft:interaction,tag=poke.trade]
