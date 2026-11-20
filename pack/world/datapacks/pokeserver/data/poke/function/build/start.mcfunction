# 자동 생성: tools/build_world.py
schedule clear poke:build/run
schedule clear poke:build/finish
schedule clear poke:build/terrain/run_0
schedule clear poke:build/terrain/run_1
schedule clear poke:build/terrain/run_2
schedule clear poke:build/terrain/run_3
schedule clear poke:build/terrain/run_4
schedule clear poke:build/terrain/run_5
execute in poke:hub run forceload add -16 -16 16 16
execute in poke:town run forceload add 1904 -106 2096 88
execute in poke:town run forceload add 2990 -50 3550 22
execute in poke:town run forceload add -106 -162 106 74
execute in poke:town run forceload add 904 -98 1096 98
# 청크가 다 불러와질 때까지 3초 기다렸다가 짓기
schedule function poke:build/run 60t
