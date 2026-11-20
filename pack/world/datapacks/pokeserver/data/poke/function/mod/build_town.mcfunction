# 자동 생성: tools/build_world.py. Cobblemon 물건
execute as @e[type=cobblemon:pokemon] at @s if dimension poke:town run kill @s
execute in poke:town as @e[type=cobblemon:npc,tag=poke.npc,x=-106,y=-70,z=-162,dx=212,dy=80,dz=236] run npcdelete @s
execute in poke:town as @e[type=cobblemon:npc,tag=poke.npc,x=904,y=-70,z=-98,dx=192,dy=80,dz=196] run npcdelete @s
execute in poke:hub run kill @e[type=minecraft:item_display,tag=poke.lab]
execute in poke:hub run setblock -6 65 -8 cobblemon:healing_machine[facing=east,natural=false]
execute in poke:hub run summon minecraft:item_display -0.5 66.2 -1.5 {Tags:["poke.lab"],item:{id:"cobblemon:poke_ball",count:1},transformation:{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}
execute in poke:hub run summon minecraft:item_display 0.5 66.2 -1.5 {Tags:["poke.lab"],item:{id:"cobblemon:poke_ball",count:1},transformation:{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}
execute in poke:hub run summon minecraft:item_display 1.5 66.2 -1.5 {Tags:["poke.lab"],item:{id:"cobblemon:poke_ball",count:1},transformation:{scale:[0.6f,0.6f,0.6f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]}}
