# 체육관 입구 명령 블록:  execute as @p run function poke:gym/enter {id:1}
# 잠금 = "그 체육관 번호를 가진 접속 중인 플레이어가 있는가". 로그아웃하면 자동으로 풀림.
execute if score @s poke.gym matches 1.. run return run tellraw @s {"text":"이미 다른 체육관에 도전 중입니다.","color":"red"}
$execute if entity @a[scores={poke.gym=$(id)}] run return run tellraw @s {"text":"다른 도전자가 도전 중입니다. 끝나면 다시 시도하세요.","color":"red"}
$scoreboard players set @s poke.gym $(id)
$function poke:util/tp with storage poke:config gyms.g$(id)
$tellraw @a [{"text":"[체육관 $(id)] ","color":"gold"},{"selector":"@s"},{"text":" 도전 시작!","color":"white"}]
