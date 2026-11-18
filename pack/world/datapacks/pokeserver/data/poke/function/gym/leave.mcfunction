# 자동 생성: tools/build_league.py
# 경기장·사천왕에서 나가기 (나가기 발판, 승리, 패배, 재접속): 체육관 로비로
execute if score @s poke.gym matches 1.. run function poke:util/tp with storage poke:config gym
function poke:gym/release
