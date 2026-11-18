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
fill 1021 -59 -9 1023 -59 -9 minecraft:light_blue_concrete
setblock 1022 -58 -9 minecraft:light_blue_stained_glass
setblock 1021 -58 -9 minecraft:light_gray_concrete
setblock 1023 -58 -9 minecraft:light_gray_concrete
setblock 1022 -57 -9 minecraft:sea_lantern
summon minecraft:interaction 1022.5 -59 -8.5 {Tags:["poke.trade"],width:3.2f,height:2.5f,response:1b}
summon minecraft:text_display 1022.5 -55.8 -8.2 {Tags:["poke.deco"],billboard:"center",shadow:1b,background:-1442840576,transformation:{scale:[1.1f,1.1f,1.1f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},text:'{"text":"교환 장치","color":"aqua","bold":true,"extra":[{"text":"\\n두 사람이 차례로 우클릭하면 교환 시작","color":"gray","bold":false}]}'}
