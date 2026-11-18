# 자동 생성: tools/build_league.py
tag @s add poke.e4clear
execute in poke:town run tp @s 3416.5 -59 4.5 -90 0
title @s title {"text":"사천왕 클리어!","color":"gold"}
title @s subtitle {"text":"명예의 전당에 이름을 올렸습니다","color":"yellow"}
tellraw @a [{"text":"[리그] ","color":"gold"},{"selector":"@s"},{"text":"님이 사천왕을 모두 이기고 명예의 전당에 올랐습니다!","color":"yellow"}]
