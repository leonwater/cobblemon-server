# 야생 첫 스폰 찾기: 포켓몬 평균 레벨이 가장 낮은 바이옴(꽃 숲) 칸들을 차례로, 땅이 있는 첫 칸에 착지
# (바둑판 지형은 바이옴과 무관해서 칸 전체가 바다일 수 있음). 칸 = 256x256, 계산은 tools/spawn_levels.py
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 1920 2176 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 2176 1920 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 1664 2432 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 2432 1664 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 1408 2688 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 2688 1408 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 1152 2944 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers 2944 1152 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers -4736 -4736 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers -4480 -4992 0 120 false @s
execute at @s unless dimension poke:wild in poke:wild run spreadplayers -4992 -4480 0 120 false @s
