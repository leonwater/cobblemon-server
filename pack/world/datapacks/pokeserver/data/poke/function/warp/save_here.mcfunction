# 농장·야생에서 땅을 딛고 있을 때만 위치 저장 (공중에서 저장되면 떨어지므로)
execute unless predicate poke:on_ground run return 0
# 농장의 "마을로" 발판 위는 저장 안 함 (저장되면 농장 오자마자 다시 마을로 튕김)
execute if dimension poke:farm positioned -1 -59 -8 if entity @s[dx=2,dy=1,dz=2] run return 0
execute if dimension poke:farm run function poke:warp/save {key:"farm"}
# 야생: G 메뉴 "야생"은 광장 밖에서 마지막으로 있던 자리로 (광장 안은 저장 안 함: 광장 버튼과 같아지지 않게. 태그는 모드가 1초마다 붙이고, 도착 직후 1초 안에도 막히게 광장 마커 거리도 봄)
execute if dimension poke:wild unless entity @s[tag=poke.in_plaza] unless entity @e[type=minecraft:marker,tag=poke.plaza,distance=..72] run function poke:warp/save {key:"wild"}
