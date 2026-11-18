# 매크로 줄($)은 실행할 때 검사됨: Cobblemon NPC 목록이 함수보다 늦게 불러와져서 일반 줄로 쓰면 로드 실패함
$spawnnpcat $(x) $(y) $(z) $(id)
$tag @e[type=cobblemon:npc,x=$(x),y=$(y),z=$(z),distance=..1.5,limit=1,sort=nearest] add poke.npc
$tag @e[type=cobblemon:npc,x=$(x),y=$(y),z=$(z),distance=..1.5,limit=1,sort=nearest] add $(tag)
$execute positioned $(x) $(y) $(z) align xz run tp @e[tag=$(tag),limit=1,sort=nearest] ~0.5 ~ ~0.5 $(yaw) 0
