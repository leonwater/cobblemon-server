# ★ 위치·금액은 여기 한 곳에서만 수정합니다. 수정 후 /reload
# dim = 차원, yaw = 바라보는 방향(0 남, 90 서, 180 북, -90 동)
data modify storage poke:config tutorial set value {dim:"poke:hub", x:0, y:65, z:3, yaw:180}
data modify storage poke:config village set value {dim:"poke:hub", x:0, y:65, z:200, yaw:180}

# 바이옴 포탈 목적지 (오버월드, 지면 맨 위로 자동 착지). 명령 블록:  execute as @p run function poke:portal/go {to:"forest"}
data modify storage poke:config portals set value {forest:{x:1000, z:0}, desert:{x:-1000, z:0}, snow:{x:0, z:-1000}}

# 체육관 내부 입장 좌표. 명령 블록:  execute as @p run function poke:gym/enter {id:1}
data modify storage poke:config gyms set value {g1:{dim:"poke:hub", x:30, y:65, z:200, yaw:90}, g2:{dim:"poke:hub", x:-30, y:65, z:200, yaw:-90}}
