# 자동 생성: tools/build_world.py
execute in poke:wild at @e[type=minecraft:marker,tag=poke.plaza,limit=1] run function poke:mod/plaza
function poke:mod/clear_items
schedule function poke:build/plaza/unload_0 20t
schedule function poke:build/plaza/unload_1 40t
schedule function poke:build/plaza/unload_2 60t
schedule function poke:build/plaza/unload_3 80t
schedule function poke:build/plaza/unload_4 100t
schedule function poke:build/plaza/unload_6 120t
schedule function poke:build/plaza/unload_7 140t
schedule function poke:build/plaza/unload_8 160t
schedule function poke:build/plaza/unload_9 180t
schedule function poke:build/plaza/unload_5 200t
say [잡켓몬] 광장 마을을 지었습니다.
