# 자동 생성: tools/build_world.py. Cobblemon 블록
kill @e[type=cobblemon:pokemon]
kill @e[type=minecraft:interaction,tag=poke.trade]
setblock 1029 -58 -3 minecraft:air
setblock 1029 -59 -3 cobblemon:healing_machine[facing=west,natural=false]
setblock 1029 -58 3 minecraft:air
setblock 1029 -59 3 cobblemon:healing_machine[facing=west,natural=false]
setblock 1027 -59 -9 cobblemon:pc[facing=north,part=bottom]
setblock 1027 -58 -9 cobblemon:pc[facing=north,part=top]
setblock 1029 -59 -9 cobblemon:pc[facing=north,part=bottom]
setblock 1029 -58 -9 cobblemon:pc[facing=north,part=top]
summon minecraft:text_display 1028.5 -56.4 -8.2 {Tags:["poke.deco"],billboard:"center",shadow:1b,background:-1442840576,transformation:{scale:[0.9f,0.9f,0.9f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},text:'{"text":"PC 박스","color":"aqua","bold":true,"font":"pokeserver:galmuri","extra":[""]}'}
execute in poke:hub run kill @e[type=minecraft:item_display,tag=poke.lab]
execute in poke:hub run setblock -6 65 -8 cobblemon:healing_machine[facing=east,natural=false]
execute in poke:hub run summon minecraft:item_display -0.5 66.2 -1.5 {Tags:["poke.lab"],item:{id:"cobblemon:poke_ball",count:1},transformation:{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}
execute in poke:hub run summon minecraft:item_display 0.5 66.2 -1.5 {Tags:["poke.lab"],item:{id:"cobblemon:poke_ball",count:1},transformation:{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}
execute in poke:hub run summon minecraft:item_display 1.5 66.2 -1.5 {Tags:["poke.lab"],item:{id:"cobblemon:poke_ball",count:1},transformation:{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}
