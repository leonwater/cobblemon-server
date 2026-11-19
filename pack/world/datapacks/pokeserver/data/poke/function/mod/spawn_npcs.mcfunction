# 자동 생성: tools/build_world.py. 기존 NPC 제거 후 다시 소환 (청크는 build/start에서 불러옴)
execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s
execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s
# 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게
execute in poke:hub run function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}
# 간호사(회복), 점원(우클릭 → 상점), 체육관 안내원(우클릭 → 도전 목록; 모드가 태그로 처리)
execute in poke:town run function poke:mod/spawn_npc {id:"poke:nurse", x:1031, y:-59, z:0, tag:"poke.nurse", yaw:90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:merchant", x:967, y:-59, z:-3, tag:"poke.merchant", yaw:-90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:merchant", x:967, y:-59, z:3, tag:"poke.merchant", yaw:-90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:gym_guide", x:2000, y:-56, z:12, tag:"poke.gymguide", yaw:180}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_iv", x:-43, y:-59, z:-68, tag:"poke.tip_iv", yaw:-90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_ev", x:-43, y:-59, z:-64, tag:"poke.tip_ev", yaw:-90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_nature", x:-43, y:-59, z:-44, tag:"poke.tip_nature", yaw:-90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_mint", x:-43, y:-59, z:-40, tag:"poke.tip_mint", yaw:-90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_types", x:43, y:-59, z:-68, tag:"poke.tip_types", yaw:90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_stab", x:43, y:-59, z:-64, tag:"poke.tip_stab", yaw:90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_catch", x:43, y:-59, z:-44, tag:"poke.tip_catch", yaw:90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_cap", x:43, y:-59, z:-40, tag:"poke.tip_cap", yaw:90}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_evolve", x:-26, y:-58, z:-95, tag:"poke.tip_evolve", yaw:0}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_moves", x:22, y:-58, z:-95, tag:"poke.tip_moves", yaw:0}
execute in poke:town run function poke:mod/spawn_npc {id:"poke:tip_items", x:26, y:-58, z:-95, tag:"poke.tip_items", yaw:0}
