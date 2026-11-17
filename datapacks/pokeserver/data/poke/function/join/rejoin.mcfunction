scoreboard players reset @s poke.left
# 체육관 안에서 나갔다가 다시 들어오면 자리를 비운 것으로 보고 허브로 보냄 (잠금은 로그아웃 순간 이미 풀려 있음)
execute if score @s poke.gym matches 1.. run function poke:gym/leave
