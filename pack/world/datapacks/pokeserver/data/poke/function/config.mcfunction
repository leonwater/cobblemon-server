# ★ 위치는 여기 한 곳에서만 수정합니다. 수정 후 /reload
# dim = 차원, yaw = 바라보는 방향(0 남, 90 서, 180 북, -90 동)
data modify storage poke:config tutorial set value {dim:"poke:hub", x:0, y:65, z:3, yaw:180}
# 8. 시작 마을은 항상 정중앙으로
data modify storage poke:config village set value {dim:"poke:hub", x:0.5, y:65, z:200.5, yaw:180}
# 농장·채집맵은 처음 갈 때만 여기로, 그다음부터는 마지막 위치로
data modify storage poke:config farm set value {dim:"poke:farm", x:0.5, y:-59, z:-2.5, yaw:0}

# 체육관 내부 입장 좌표. 명령 블록:  execute as @p run function poke:gym/enter {id:1}
data modify storage poke:config gyms set value {g1:{dim:"poke:hub", x:30, y:65, z:200, yaw:90}, g2:{dim:"poke:hub", x:-30, y:65, z:200, yaw:-90}}
