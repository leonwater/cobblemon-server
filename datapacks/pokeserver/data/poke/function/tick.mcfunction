execute as @a[tag=!poke.joined] run function poke:join/first
execute as @a[scores={poke.left=1..}] run function poke:join/rejoin
execute as @a[scores={poke.died=1..}] run function poke:gym/release
