# 농장·야생에서 땅을 딛고 있을 때만 위치 저장 (공중에서 저장되면 떨어지므로)
execute unless predicate poke:on_ground run return 0
# 농장의 "마을로" 발판 위는 저장 안 함 (저장되면 농장 오자마자 다시 마을로 튕김)
execute if dimension poke:farm positioned -1 -59 -8 if entity @s[dx=2,dy=1,dz=2] run return 0
execute if dimension poke:farm run function poke:warp/save {key:"farm"}
execute if dimension poke:wild run function poke:warp/save {key:"wild"}
