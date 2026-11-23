# 야생에 처음 가면: 광장 도착 자리에서 110칸 밖(광장 가운데에서 약 94칸 이상, 광장 둘레 72칸 밖)의 안전한 땅으로
# 그쪽이 물이라 내릴 곳이 없으면 동 → 남 → 서 순서로 다시 (모두 실패하면 광장에 그대로)
function poke:util/tp with storage poke:config hall
execute store success score #ok poke.timer at @s run spreadplayers ~ ~-110 0 20 false @s
execute if score #ok poke.timer matches 0 store success score #ok poke.timer at @s run spreadplayers ~110 ~ 0 20 false @s
execute if score #ok poke.timer matches 0 store success score #ok poke.timer at @s run spreadplayers ~ ~110 0 20 false @s
execute if score #ok poke.timer matches 0 at @s run spreadplayers ~-110 ~ 0 20 false @s
