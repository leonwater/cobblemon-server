# 자동 생성: tools/build_world.py
execute in poke:hub run function poke:build/tutorial
execute in poke:town run function poke:mod/build_town
execute in poke:hub run function poke:mod/spawn_npcs
execute in poke:town run forceload remove all
data modify storage poke:state build set value 15
# 관장·사천왕은 플레이어가 접속하면 소환 (RCT 명령이 플레이어를 요구)
data modify storage poke:state leaders set value 0
say [pokeserver] 튜토리얼 방·체육관과 지형을 지었습니다.
