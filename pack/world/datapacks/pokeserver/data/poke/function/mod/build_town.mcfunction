# 자동 생성: tools/build_world.py. Cobblemon 블록
kill @e[type=cobblemon:pokemon]
kill @e[type=minecraft:interaction,tag=poke.trade]
setblock 1029 -58 -3 minecraft:air
setblock 1029 -59 -3 cobblemon:healing_machine[facing=west,natural=false]
setblock 1029 -58 3 minecraft:air
setblock 1029 -59 3 cobblemon:healing_machine[facing=west,natural=false]
setblock 1016 -59 -10 cobblemon:pc[facing=north,part=bottom]
setblock 1016 -58 -10 cobblemon:pc[facing=north,part=top]
setblock 1018 -59 -10 cobblemon:pc[facing=north,part=bottom]
setblock 1018 -58 -10 cobblemon:pc[facing=north,part=top]
summon minecraft:text_display 1017.5 -56.4 -9.2 {Tags:["poke.deco"],billboard:"center",shadow:1b,background:-1442840576,transformation:{scale:[0.9f,0.9f,0.9f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},text:'{"text":"PC 박스","color":"aqua","bold":true,"font":"pokeserver:galmuri","extra":[""]}'}
