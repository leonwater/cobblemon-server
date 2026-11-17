# ★ 좌표는 여기 한 곳에서만 수정합니다. 수정 후 /reload
data modify storage poke:config hub set value {x:0, y:100, z:0}
data modify storage poke:config tutorial set value {x:0, y:100, z:200}

# 포탈 목적지: 명령 블록에서  function poke:portal/go {to:"forest"}
data modify storage poke:config portals set value {forest:{x:1000, y:80, z:0}, desert:{x:-1000, y:80, z:0}, snow:{x:0, y:80, z:-1000}}

# 체육관 내부 입장 좌표: 키는 g + 번호. 명령 블록에서  function poke:gym/enter {id:1}
data modify storage poke:config gyms set value {g1:{x:50, y:100, z:0}, g2:{x:-50, y:100, z:0}}
