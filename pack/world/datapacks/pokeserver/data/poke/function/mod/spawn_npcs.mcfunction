# 기존 NPC 제거 후 다시 소환
execute as @e[type=cobblemon:npc,tag=poke.npc] run npcdelete @s
# 이전 버전 안내원은 poke.npc 태그가 없음
execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s
kill @e[type=cobbledollars:cobble_merchant,tag=poke.merchant]
# 2. 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게
function poke:mod/spawn_npc {id:"poke:tutorial_guide", x:0, y:65, z:0, tag:"poke.tutor", yaw:0}
# 포켓몬센터 간호사: 접수대 뒤, 입구를 바라보게
function poke:mod/spawn_npc {id:"poke:nurse", x:18, y:65, z:130, tag:"poke.nurse", yaw:0}
# 6. 상인 (상점 건물 안): 우클릭 = 구매, Shift+우클릭 = 판매(은행)
summon cobbledollars:cobble_merchant -17.5 65 130.5 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,Tags:["poke.merchant"],Rotation:[0f,0f],CustomName:'{"text":"상인","color":"gold"}'}
