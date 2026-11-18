# ★ 위치는 여기 한 곳에서만 수정합니다. 수정 후 /reload
# dim = 차원, yaw = 바라보는 방향(0 남, 90 서, 180 북, -90 동)
data modify storage poke:config tutorial set value {dim:"poke:hub", x:0, y:65, z:3, yaw:180}
# 마을(poke:town): 회의장(튜토리얼 후·/trigger home), 상점가, 체육관은 항상 같은 자리로
data modify storage poke:config hall set value {dim:"poke:town", x:0.5, y:-59, z:6.5, yaw:180}
data modify storage poke:config street set value {dim:"poke:town", x:0.5, y:-59, z:-27.5, yaw:180}
data modify storage poke:config gym set value {dim:"poke:town", x:86.5, y:-59, z:-16.5, yaw:-90}
# 농장은 처음 갈 때만 여기로, 그다음부터는 마지막 위치로
data modify storage poke:config farm set value {dim:"poke:farm", x:0.5, y:-59, z:-2.5, yaw:0}

# 체육관 내부 입장 좌표. 명령 블록:  execute as @p run function poke:gym/enter {id:1}
data modify storage poke:config gyms set value {g1:{dim:"poke:town", x:100, y:-59, z:-17, yaw:-90}}
