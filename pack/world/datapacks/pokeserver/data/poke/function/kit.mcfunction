# 5. 기본 물품: 돈·몬스터볼은 mod/kit, 러닝 슈즈는 여기
function poke:mod/kit
give @s minecraft:leather_boots[minecraft:custom_name='{"text":"러닝 슈즈","color":"aqua","italic":false}',minecraft:lore=['{"text":"신으면 이동 속도 +30%","color":"gray","italic":false}'],minecraft:dyed_color={rgb:3355647,show_in_tooltip:false},minecraft:unbreakable={show_in_tooltip:false},minecraft:attribute_modifiers={modifiers:[{type:"minecraft:generic.movement_speed",id:"poke:running_shoes",amount:0.3,operation:"add_multiplied_base",slot:"feet"}],show_in_tooltip:false}] 1
