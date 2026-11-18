# 기존 NPC 제거 후 다시 소환 (허브·마을 모두. 마을 청크는 build/start에서 불러옴)
execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s
execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s
# 2. 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게
execute in poke:hub run function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}
# 포켓몬센터 간호사: 접수대 뒤, 입구(서쪽)를 바라보게
execute in poke:town run function poke:mod/spawn_npc {id:"poke:nurse", x:21, y:-59, z:-62, tag:"poke.nurse", yaw:90}
# 4. 프렌들리 숍 점원: 우클릭 → 상점 화면 (모드가 태그 poke.merchant로 처리)
execute in poke:town run function poke:mod/spawn_npc {id:"poke:merchant", x:-11, y:-59, z:-69, tag:"poke.merchant", yaw:0}
