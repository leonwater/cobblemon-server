// 바닐라 1.21.1 서버 + 봇 2명으로 데이터팩 로직 검증 (모드 전용 명령은 run.sh가 비워둠)
const mineflayer = require('mineflayer')
const { Rcon } = require('rcon-client')
const assert = require('assert')
const sleep = ms => new Promise(r => setTimeout(r, ms))

const join = name => new Promise((res, rej) => {
  const b = mineflayer.createBot({ host: 'localhost', port: 25566, username: name, version: '1.21.1', auth: 'offline' })
  b.once('spawn', () => res(b)); b.once('error', rej); b.once('kicked', r => rej(new Error('kicked ' + r)))
})

;(async () => {
  const rc = await Rcon.connect({ host: 'localhost', port: 25576, password: 'test' })
  const cmd = async c => { const r = await rc.send(c); console.log('>', c, '→', r); return r }
  const gym = async p => cmd(`scoreboard players get ${p} poke.gym`)
  const pos = async (p, i) => Math.floor(parseFloat((await cmd(`data get entity ${p} Pos[${i}]`)).match(/(-?[\d.]+)d?$/)[1]))
  const dim = async p => (await cmd(`data get entity ${p} Dimension`)).match(/"([^"]+)"$/)[1]
  const at = async (p, d, x, z) => { assert.equal(await dim(p), d); assert.equal(await pos(p, 0), x); assert.equal(await pos(p, 2), z) }

  // 건물이 지어질 때까지 (load 후 40틱)
  for (let i = 0; i < 20 && !/build: 1/.test(await cmd('data get storage poke:state')); i++) await sleep(500)
  assert.match(await cmd('execute in poke:hub if block 0 64 3 minecraft:polished_deepslate'), /passed/, '튜토리얼 방 바닥')
  assert.match(await cmd('execute in poke:hub if block 0 64 200 minecraft:chiseled_stone_bricks'), /passed/, '마을 중심 바닥')
  assert.match(await cmd('execute in poke:hub if block 14 64 200 minecraft:stone_bricks'), /passed/, '마을 원형 테두리')
  assert.match(await cmd('execute in poke:hub if block 15 65 200 minecraft:barrier'), /passed/, '마을 추락 방지 벽')

  let A = await join('A'), B = await join('B'); await sleep(1500)
  assert.match(await cmd('tag A list'), /poke\.joined/, '첫 접속 태그')
  await at('A', 'poke:hub', 0, 3)  // 1·2. 튜토리얼 방 바닥 위 (하늘 아님)
  await sleep(1500); await at('A', 'poke:hub', 0, 3)  // 떨어지지 않고 그대로

  // 4. 규칙
  assert.match(await cmd('gamerule keepInventory'), /true/, '7. 인벤세이브')
  assert.match(await cmd('gamerule doMobSpawning'), /false/)
  assert.match(await cmd('execute as A if predicate poke:has_saturation'), /passed/, '배고픔 없음(포화)')
  await cmd('execute in minecraft:overworld run summon minecraft:zombie 0 -59 0')
  await cmd('execute in minecraft:overworld run summon minecraft:cow 1 -59 0')
  await cmd('execute in minecraft:overworld run summon minecraft:villager 2 -59 0 {NoAI:1b}')
  await sleep(1000)
  assert.match(await cmd('execute in minecraft:overworld if entity @e[type=zombie]'), /failed/, '좀비 제거')
  assert.match(await cmd('execute in minecraft:overworld if entity @e[type=cow]'), /failed/, '소 제거')
  assert.match(await cmd('execute in minecraft:overworld if entity @e[type=villager]'), /passed/, '주민은 유지')

  // 5. 튜토리얼 완료 → 마을 + 물품 1회만
  await cmd('execute as A run function poke:tutorial/finish')
  await cmd('execute as A run function poke:tutorial/finish')
  assert.match(await cmd('clear A minecraft:leather_boots 0'), /Found 1 /, '러닝 슈즈 1회만 지급')
  await at('A', 'poke:hub', 0, 200)
  await cmd('item replace entity A armor.feet from entity A container.0'); await sleep(500)
  assert.match(await cmd('attribute A minecraft:generic.movement_speed get'), /0\.13/, '러닝 슈즈 속도 +30%')

  // 체육관 1인 제한
  await cmd('execute as A run function poke:gym/enter {id:1}')
  assert.match(await gym('A'), /has 1 /, 'A 체육관1 입장')
  await at('A', 'poke:hub', 30, 200)
  await cmd('execute as B run function poke:gym/enter {id:1}')
  assert.doesNotMatch(await gym('B'), /has 1 /, 'B는 체육관1 입장 거부')
  await cmd('execute as B run function poke:gym/enter {id:2}')
  assert.match(await gym('B'), /has 2 /, '체육관2는 별도 잠금')
  await cmd('execute as B run function poke:gym/leave')
  assert.doesNotMatch(await gym('B'), /has /, 'B 퇴장 시 잠금 해제')

  A.quit(); await sleep(1500)
  await cmd('execute as B run function poke:gym/enter {id:1}')
  assert.match(await gym('B'), /has 1 /, 'A 로그아웃 → 체육관1 잠금 해제')
  A = await join('A'); await sleep(1500)
  assert.doesNotMatch(await gym('A'), /has /, 'A 재접속 시 체육관 상태 초기화')
  await at('A', 'poke:hub', 0, 200)

  await cmd('kill B'); await sleep(1500)
  assert.doesNotMatch(await gym('B'), /has /, 'B 사망 시 잠금 해제')

  // 1. 포탈: 오버월드 지면 위로 착지
  await cmd('execute as A run function poke:portal/go {to:"forest"}'); await sleep(500)
  assert.equal(await dim('A'), 'minecraft:overworld')
  assert.ok(Math.abs(await pos('A', 0) - 1000) <= 1, '포탈 forest x (±1)')
  assert.equal(await pos('A', 1), -60, '평지 지면(y=-60) 위에 착지')
  // /trigger home → 마을
  await cmd('execute as A run trigger home'); await sleep(500)
  await at('A', 'poke:hub', 0, 200)

  await cmd('execute as A run function poke:admin/reset_me'); await sleep(500)
  assert.match(await cmd('tag A list'), /poke\.joined/, 'reset_me 후 튜토리얼 재시작')
  assert.doesNotMatch(await cmd('tag A list'), /tutorial_done/)
  await at('A', 'poke:hub', 0, 3)

  console.log('ALL PASS'); A.quit(); B.quit(); await rc.end(); process.exit(0)
})().catch(e => { console.error('FAIL', e.message); process.exit(1) })
