# 매크로 줄($)은 실행할 때 검사됨: Cobblemon NPC 목록이 함수보다 늦게 불러와져서 일반 줄로 쓰면 로드 실패함
# x·y·z는 절대값 또는 "~상대값" (광장은 마커 기준 상대 좌표)
$spawnnpcat $(x) $(y) $(z) $(id)
$execute positioned $(x) $(y) $(z) run tag @e[type=cobblemon:npc,distance=..1.5,limit=1,sort=nearest] add poke.npc
$execute positioned $(x) $(y) $(z) run tag @e[type=cobblemon:npc,distance=..1.5,limit=1,sort=nearest] add $(tag)
$execute positioned $(x) $(y) $(z) align xz run tp @e[tag=$(tag),limit=1,sort=nearest] ~0.5 ~ ~0.5 $(yaw) 0
