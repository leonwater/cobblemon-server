# ★ 위치는 여기 한 곳에서만 수정합니다. 수정 후 /reload
# dim = 차원, yaw = 바라보는 방향(0 남, 90 서, 180 북, -90 동)
data modify storage poke:config tutorial set value {dim:"poke:hub", x:0, y:65, z:3, yaw:180}
# 체육관 도착 위치는 tools/build_world.py의 WARPS에서 생성. 광장(hall)은 모드(Plaza.java)가 야생의 광장 자리로 정함
data modify storage poke:config gym set value {dim:"poke:town", x:2000.5, y:-56, z:-11.5, yaw:0}
# 모드가 없을 때(데이터팩 테스트)만: 광장 대신 체육관 로비
execute unless data storage poke:config hall{dim:"poke:wild"} run data modify storage poke:config hall set value {dim:"poke:town", x:2000.5, y:-56, z:-11.5, yaw:0}
# 농장은 처음 갈 때만 여기로, 그다음부터는 마지막 위치로
data modify storage poke:config farm set value {dim:"poke:farm", x:0.5, y:-59, z:-2.5, yaw:0}

# 체육관 경기장·사천왕 방 위치는 tools/build_world.py (gym_geom, e4_geom)에서 정해 함수로 생성됨
# 15. 없어진 상점가 워프 (예전 월드에 남은 값)
data remove storage poke:config street
