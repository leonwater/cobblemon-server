# 야생 첫 방문: 모든 플레이어가 같은 자리 (처음 간 사람의 착지 지점을 저장해 모두에게 씀)
execute if data storage poke:state wildspawn run return run function poke:warp/last_wild with storage poke:state wildspawn
function poke:warp/first_wild_find
# 실제로 야생에 도착했을 때만 저장 (자리 찾기에 실패하면 다음 사람이 다시 찾음)
execute at @s if dimension poke:wild run function poke:warp/store_wildspawn
execute at @s unless dimension poke:wild run tellraw @s {"text":"야생에서 안전한 자리를 못 찾았어요. 다시 시도해 주세요.","color":"red"}
