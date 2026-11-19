# 전체 초기화(/초기화 확인, 모드가 아이템·돈·포켓몬을 지운 뒤 호출): 체육관 상태·마지막 위치를 지우고
# poke.* 태그를 모두 지워 다음 틱에 첫 접속처럼 튜토리얼 방으로 (기본 물품도 다시 받음)
function poke:gym/release
execute store result storage poke:tmp w.id int 1 run scoreboard players get @s poke.id
function poke:admin/wipe_last with storage poke:tmp w
function poke:mod/rct_reset
tag @s remove poke.joined
tag @s remove poke.tutorial_done
tag @s remove poke.kit_given
tag @s remove poke.e4clear
tag @s remove poke.badge1
tag @s remove poke.badge2
tag @s remove poke.badge3
tag @s remove poke.badge4
tag @s remove poke.badge5
tag @s remove poke.badge6
tag @s remove poke.badge7
tag @s remove poke.badge8
xp set @s 0 levels
xp set @s 0 points
