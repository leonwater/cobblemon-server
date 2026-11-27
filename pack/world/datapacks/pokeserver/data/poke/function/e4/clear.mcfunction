# 자동 생성: tools/build_league.py
tag @s add poke.e4clear
execute in poke:town run tp @s 3516.5 -59 4.5 -90 0
function poke:mod/prize/30000
function poke:mod/reward/e4
title @s title {"text":"사천왕 클리어!","color":"gold"}
title @s subtitle {"text":"명예의 전당에 이름을 올렸습니다","color":"yellow"}
execute if data storage poke:first e4 run tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕을 클리어하고 챔피언이 되었습니다! 축하합니다!","color":"gold"}]
execute unless data storage poke:first e4 run tellraw @a [{"text":"[퍼스트 클리어] ","color":"light_purple","bold":true},{"selector":"@s"},{"text":"님이 서버 최초로 사천왕을 클리어하고 첫 챔피언이 되었습니다! 모두 축하해 주세요!","color":"aqua"}]
data modify storage poke:first e4 set value 1
