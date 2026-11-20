# 자동 생성: tools/build_world.py. 기존 NPC 제거 후 다시 소환 (청크는 build/start에서 불러옴)
execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s
execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s
# 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게
execute in poke:hub run function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}
# 간호사(회복), 점원(우클릭 → 상점), 체육관 안내원(우클릭 → 도전 목록; 모드가 태그로 처리)
execute in poke:town run function poke:mod/spawn_npc {id:"poke:gym_guide", x:2000, y:-56, z:12, tag:"poke.gymguide", yaw:180}
