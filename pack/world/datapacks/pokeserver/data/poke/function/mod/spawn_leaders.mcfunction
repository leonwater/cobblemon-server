# 자동 생성: tools/build_league.py
# 관장·사천왕 소환 (RCT 소환 명령은 플레이어가 실행해야 해서, 접속한 플레이어로 실행됨)
kill @e[type=rctmod:trainer,tag=poke.leader]
execute in poke:town positioned 3015.5 -59 14.5 run rctmod trainer summon_persistent leader_brock_019e ~ ~ ~
execute in poke:town positioned 3015.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3015.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3065.5 -59 14.5 run rctmod trainer summon_persistent leader_lt_surge_01a0 ~ ~ ~
execute in poke:town positioned 3065.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3065.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3115.5 -59 14.5 run rctmod trainer summon_persistent leader_blaine_01a3 ~ ~ ~
execute in poke:town positioned 3115.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3115.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3165.5 -59 14.5 run rctmod trainer summon_persistent leader_koga_01a2 ~ ~ ~
execute in poke:town positioned 3165.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3165.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3215.5 -59 14.5 run rctmod trainer summon_persistent leader_sabrina_01a4 ~ ~ ~
execute in poke:town positioned 3215.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3215.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3265.5 -59 14.5 run rctmod trainer summon_persistent leader_giovanni_015e ~ ~ ~
execute in poke:town positioned 3265.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3265.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3315.5 -59 14.5 run rctmod trainer summon_persistent leader_erika_01a1 ~ ~ ~
execute in poke:town positioned 3315.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3315.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3365.5 -59 14.5 run rctmod trainer summon_persistent leader_misty_019f ~ ~ ~
execute in poke:town positioned 3365.5 -59 14.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3365.5 -59 14.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 180 0
execute in poke:town positioned 3543.5 -59 -34.5 run rctmod trainer summon_persistent champion_steven_ps ~ ~ ~
execute in poke:town positioned 3543.5 -59 -34.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3543.5 -59 -34.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 90 0
execute in poke:town positioned 3543.5 -59 -12.5 run rctmod trainer summon_persistent champion_cynthia_03a5 ~ ~ ~
execute in poke:town positioned 3543.5 -59 -12.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3543.5 -59 -12.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 90 0
execute in poke:town positioned 3543.5 -59 9.5 run rctmod trainer summon_persistent champion_leon_ps ~ ~ ~
execute in poke:town positioned 3543.5 -59 9.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3543.5 -59 9.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 90 0
execute in poke:town positioned 3543.5 -59 31.5 run rctmod trainer summon_persistent trainer_red_0003 ~ ~ ~
execute in poke:town positioned 3543.5 -59 31.5 run data merge entity @e[type=rctmod:trainer,distance=..1,limit=1,sort=nearest] {NoAI:1b,Invulnerable:1b,Tags:["poke.leader"]}
execute in poke:town positioned 3543.5 -59 31.5 run tp @e[type=rctmod:trainer,tag=poke.leader,distance=..1,limit=1,sort=nearest] ~ ~ ~ 90 0
data modify storage poke:state leaders set value 1
execute in poke:town run forceload remove 2990 -28 3390 22
execute in poke:town run forceload remove 3490 -50 3560 69
