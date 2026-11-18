execute in poke:hub run function poke:build/tutorial
execute in poke:hub run function poke:build/clear_village
execute in poke:town run function poke:build/town
execute in poke:town run function poke:mod/build_town
execute in poke:hub run function poke:mod/spawn_npcs
execute in poke:hub run forceload remove -40 112 40 236
execute in poke:town run forceload remove all
data modify storage poke:state build set value 3
say [pokeserver] 튜토리얼 방·마을(회의장·상점가·체육관)을 지었습니다.
