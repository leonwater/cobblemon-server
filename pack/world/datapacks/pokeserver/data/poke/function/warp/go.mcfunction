# 농장: 마지막 위치로, 처음이면 기본 위치로.  function poke:warp/go {key:"farm"}
function poke:warp/save_here
# 체육관 도전 중 떠나면 잠금 해제 (warp/fixed와 같게)
function poke:gym/release
execute store result storage poke:tmp g.id int 1 run scoreboard players get @s poke.id
$data modify storage poke:tmp g.key set value "$(key)"
function poke:warp/go_m with storage poke:tmp g
