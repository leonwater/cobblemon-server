# 튜토리얼 끝 지점의 명령 블록:  execute as @p run function poke:tutorial/finish
execute if entity @s[tag=poke.tutorial_done] run return run tellraw @s {"text":"이미 튜토리얼을 완료했습니다.","color":"gray"}
tag @s add poke.tutorial_done
function poke:kit
function poke:util/tp with storage poke:config hub
tellraw @s {"text":"튜토리얼 완료! 기본 물자를 지급했습니다. 이제 자유롭게 모험하세요.","color":"green"}
