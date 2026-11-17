# 기존 NPC 제거 후 다시 소환
execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s
# 이전 버전 안내원은 poke.npc 태그가 없음
execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s
# 2. 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게
function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}
# 포켓몬센터 간호사: 접수대 뒤, 입구를 바라보게
function poke:mod/spawn_npc {id:"poke:nurse", x:18, y:65, z:130, tag:"poke.nurse", yaw:0}
# 4. 상인 (상점 건물 안): 우클릭 → 상점 화면 (구매/판매 탭)
function poke:mod/spawn_npc {id:"poke:merchant", x:-18, y:65, z:130, tag:"poke.merchant", yaw:0}
