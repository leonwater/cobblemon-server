execute store result storage poke:tmp p.id int 1 run scoreboard players get @s poke.id
$data modify storage poke:tmp p.key set value "$(key)"
data modify storage poke:tmp p.x set from entity @s Pos[0]
data modify storage poke:tmp p.y set from entity @s Pos[1]
data modify storage poke:tmp p.z set from entity @s Pos[2]
data modify storage poke:tmp p.yaw set from entity @s Rotation[0]
function poke:warp/save_m with storage poke:tmp p
