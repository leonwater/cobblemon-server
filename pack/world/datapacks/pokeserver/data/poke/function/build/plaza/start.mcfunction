# 자동 생성: tools/build_world.py. 모드(Plaza.java)가 광장 가운데에서 실행
schedule clear poke:build/plaza/run_0
schedule clear poke:build/plaza/run_1
schedule clear poke:build/plaza/run_2
forceload add ~-80 ~-80 ~80 ~80
kill @e[type=minecraft:marker,tag=poke.plaza]
summon minecraft:marker ~ ~ ~ {Tags:["poke.plaza"]}
schedule function poke:build/plaza/run_0 60t
