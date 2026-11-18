execute in poke:hub run forceload add -16 -16 16 16
execute in poke:hub run forceload add -40 112 40 236
execute in poke:town run forceload add -40 -125 250 20
# 청크가 다 불러와질 때까지 3초 기다렸다가 짓기
schedule function poke:build/run 60t
