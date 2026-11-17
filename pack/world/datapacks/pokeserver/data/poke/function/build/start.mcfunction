execute in poke:hub run forceload add -16 -16 16 16
execute in poke:hub run forceload add -20 180 20 220
# 청크가 다 불러와질 때까지 2초 기다렸다가 짓기
schedule function poke:build/run 40t
