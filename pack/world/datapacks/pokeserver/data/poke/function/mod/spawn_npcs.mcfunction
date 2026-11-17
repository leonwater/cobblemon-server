# 기존 NPC 제거 후 다시 소환
execute as @e[type=cobblemon:npc,tag=poke.tutor] run npcdelete @s
kill @e[type=cobbledollars:cobble_merchant,tag=poke.merchant]
# 2. 튜토리얼 안내원: 스폰 지점(0,65,3)을 바라보게
function poke:mod/spawn_tutor {id:"poke:tutorial_guide"}
tag @e[type=cobblemon:npc,x=0,y=65,z=0,distance=..1.5,limit=1,sort=nearest] add poke.tutor
tp @e[tag=poke.tutor,limit=1] 0.5 65 0.5 0 0
# 6. 시작 마을 상인: 우클릭 = 구매, Shift+우클릭 = 판매(은행)
summon cobbledollars:cobble_merchant 0.5 65 190.5 {NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,Tags:["poke.merchant"],Rotation:[0f,0f],CustomName:'{"text":"상인","color":"gold"}'}
