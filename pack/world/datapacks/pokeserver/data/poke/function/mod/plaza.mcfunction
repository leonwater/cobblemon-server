# 자동 생성: tools/build_world.py. 광장의 Cobblemon 물건·NPC (마커 위치에서 실행)
execute as @e[type=cobblemon:npc,tag=poke.npc,distance=..90] run npcdelete @s
setblock ~33 ~2 ~-3 minecraft:air
setblock ~33 ~1 ~-3 cobblemon:healing_machine[facing=west,natural=false]
setblock ~33 ~2 ~3 minecraft:air
setblock ~33 ~1 ~3 cobblemon:healing_machine[facing=west,natural=false]
setblock ~31 ~1 ~-9 cobblemon:pc[facing=north,part=bottom]
setblock ~31 ~2 ~-9 cobblemon:pc[facing=north,part=top]
setblock ~33 ~1 ~-9 cobblemon:pc[facing=north,part=bottom]
setblock ~33 ~2 ~-9 cobblemon:pc[facing=north,part=top]
summon minecraft:text_display ~32.5 ~3.6 ~-8.2 {Tags:["poke.plaza"],billboard:"center",shadow:1b,background:-1442840576,transformation:{scale:[0.9f,0.9f,0.9f],translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},text:'{"text":"PC 박스","color":"aqua","bold":true,"font":"pokeserver:galmuri","extra":[""]}'}
function poke:mod/spawn_npc {id:"poke:nurse", x:"~35", y:"~1", z:"~0", tag:"poke.nurse", yaw:90}
function poke:mod/spawn_npc {id:"poke:merchant", x:"~-35", y:"~1", z:"~4", tag:"poke.merchant", yaw:-90}
function poke:mod/spawn_npc {id:"poke:merchant", x:"~-35", y:"~1", z:"~10", tag:"poke.merchant", yaw:-90}
function poke:mod/spawn_npc {id:"poke:tip_iv", x:"~-29", y:"~2", z:"~-39", tag:"poke.tip_iv", yaw:0}
function poke:mod/spawn_npc {id:"poke:tip_ev", x:"~-25", y:"~2", z:"~-39", tag:"poke.tip_ev", yaw:0}
function poke:mod/spawn_npc {id:"poke:tip_nature", x:"~-6", y:"~2", z:"~-51", tag:"poke.tip_nature", yaw:0}
function poke:mod/spawn_npc {id:"poke:tip_mint", x:"~-2", y:"~2", z:"~-51", tag:"poke.tip_mint", yaw:0}
function poke:mod/spawn_npc {id:"poke:tip_types", x:"~35", y:"~1", z:"~-40", tag:"poke.tip_types", yaw:0}
function poke:mod/spawn_npc {id:"poke:tip_stab", x:"~39", y:"~1", z:"~-40", tag:"poke.tip_stab", yaw:0}
function poke:mod/spawn_npc {id:"poke:tip_catch", x:"~-42", y:"~2", z:"~35", tag:"poke.tip_catch", yaw:180}
function poke:mod/spawn_npc {id:"poke:tip_cap", x:"~-38", y:"~2", z:"~35", tag:"poke.tip_cap", yaw:180}
function poke:mod/spawn_npc {id:"poke:tip_evolve", x:"~10", y:"~2", z:"~42", tag:"poke.tip_evolve", yaw:180}
function poke:mod/spawn_npc {id:"poke:tip_moves", x:"~31", y:"~2", z:"~30", tag:"poke.tip_moves", yaw:180}
function poke:mod/spawn_npc {id:"poke:tip_items", x:"~35", y:"~2", z:"~30", tag:"poke.tip_items", yaw:180}
