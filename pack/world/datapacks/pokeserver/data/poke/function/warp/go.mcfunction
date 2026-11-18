# 8. 농장·야생: 마지막 위치로, 처음이면 기본 위치로.  function poke:warp/go {key:"farm"} / {key:"wild"}
function poke:warp/save_here
execute store result storage poke:tmp g.id int 1 run scoreboard players get @s poke.id
$data modify storage poke:tmp g.key set value "$(key)"
function poke:warp/go_m with storage poke:tmp g
