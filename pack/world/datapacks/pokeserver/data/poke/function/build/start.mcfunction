# 자동 생성: tools/build_world.py
execute in poke:hub run forceload add -16 -16 16 16
execute in poke:hub run forceload add -40 112 40 236
execute in poke:town run forceload add -40 -48 40 30
execute in poke:town run forceload add 960 -32 1040 32
execute in poke:town run forceload add 1960 -36 2040 36
execute in poke:town run forceload add 3000 -12 3300 12
execute in poke:town run forceload add 3400 -46 3440 12
# 청크가 다 불러와질 때까지 3초 기다렸다가 짓기
schedule function poke:build/run 60t
