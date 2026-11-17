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
  const rc = await Rcon.connect({ host: 'localhost', port: 25576, password: 'test', timeout: 15000 })  // 채집맵 지형 생성 중엔 서버가 몇 초 느려짐
  const cmd = async c => { const r = await rc.send(c); console.log('>', c, '→', r.slice(0, 300)); return r }
  const ok = async (c, msg) => assert.match(await cmd(c), /passed/, msg)
  const gym = async p => cmd(`scoreboard players get ${p} poke.gym`)
  const pos = async (p, i) => Math.floor(parseFloat((await cmd(`data get entity ${p} Pos[${i}]`)).match(/(-?[\d.]+)d?$/)[1]))
  const dim = async p => (await cmd(`data get entity ${p} Dimension`)).match(/"([^"]+)"$/)[1]
  const at = async (p, d, x, z, msg) => {
    assert.equal(await dim(p), d, msg); assert.equal(await pos(p, 0), x, msg); assert.equal(await pos(p, 2), z, msg)
  }
  const waitFor = async (c, re) => { for (let i = 0; i < 30 && !re.test(await cmd(c)); i++) await sleep(500) }

  // 건물이 지어질 때까지 (load 후 40~60틱)
  await waitFor('data get storage poke:state', /build: 2.*farm: 2|farm: 2.*build: 2/)
  await ok('execute in poke:hub if block 0 64 3 minecraft:polished_deepslate', '튜토리얼 방 바닥')
  await ok('execute in poke:hub if block 0 64 200 minecraft:chiseled_stone_bricks', '마을 중심')
  await ok('execute in poke:hub if block 21 64 200 minecraft:stone_bricks', '2. 마을 반지름 21 (1.5배)')
  await ok('execute in poke:hub if block 22 65 200 minecraft:barrier', '마을 추락 방지 벽')
  await ok('execute in poke:hub if block 0 64 160 minecraft:polished_andesite', '3. 북쪽 길')
  await ok('execute in poke:hub if block -28 66 127 minecraft:stripped_dark_oak_log', '3. 상점 건물')
  await ok('execute in poke:hub if block 8 66 127 minecraft:red_concrete', '3. 포켓몬센터 건물')
  await cmd('execute in poke:farm run forceload add 0 0 80 60'); await sleep(1500)  // 짓고 나면 농장 청크는 풀려 있음
  await ok('execute in poke:farm if block 5 -60 5 minecraft:grass_block', '6. 농장 땅')
  await ok('execute in poke:farm if block 0 -60 20 minecraft:dirt_path', '6. 농장 길')
  await ok('execute in poke:farm if block 73 0 50 minecraft:barrier', '10. 농장 둘레 벽')

  let A = await join('A'), B = await join('B'); await sleep(1500)
  await at('A', 'poke:hub', 0, 3, '튜토리얼 방에서 시작')
  assert.match(await cmd('data get entity A playerGameType'), /: 2$/, '마을(허브)은 모험 모드')

  // 4·7. 규칙
  assert.match(await cmd('gamerule keepInventory'), /true/, '인벤세이브')
  await ok('execute as A if predicate poke:has_saturation', '배고픔 없음')
  await cmd('execute in minecraft:overworld run summon minecraft:zombie 0 -59 0')
  await cmd('execute in minecraft:overworld run summon minecraft:villager 2 -59 0 {NoAI:1b}')
  await sleep(1000)
  assert.match(await cmd('execute in minecraft:overworld if entity @e[type=zombie]'), /failed/, '좀비 제거')
  await ok('execute in minecraft:overworld if entity @e[type=villager]', '주민은 유지')

  // 1. 튜토리얼 보상은 처음 한 번만
  await cmd('execute as A run function poke:tutorial/finish')
  assert.match(await cmd('clear A minecraft:leather_boots 0'), /Found 1 /, '첫 완료: 러닝 슈즈')
  await at('A', 'poke:hub', 0, 200, '8. 마을 정중앙')
  await cmd('execute as A run function poke:admin/reset_me'); await sleep(500)
  await at('A', 'poke:hub', 0, 3, 'reset_me → 튜토리얼 방')
  await cmd('execute as A run function poke:tutorial/finish')
  assert.match(await cmd('clear A minecraft:leather_boots 0'), /Found 1 /, '두 번째 완료: 보상 없음')
  await at('A', 'poke:hub', 0, 200)
  await cmd('item replace entity A armor.feet from entity A container.0'); await sleep(500)
  assert.match(await cmd('attribute A minecraft:generic.movement_speed get'), /0\.13/, '러닝 슈즈 +30%')

  // 6·8. 동쪽 발판 → 농장(처음엔 입구), 마지막 위치 기억
  await cmd('execute in poke:hub run tp A 19.5 65 200.5'); await sleep(500)
  await at('A', 'poke:farm', 0, -3, '동쪽 발판 → 농장 입구')
  assert.match(await cmd('data get entity A playerGameType'), /: 0$/, '농장은 서바이벌')
  await cmd('execute in poke:farm run tp A 20.5 -59 50.5'); await sleep(2500)
  await cmd('execute as A run trigger home'); await sleep(500)
  await at('A', 'poke:hub', 0, 200, '/trigger home → 마을 정중앙')
  await cmd('execute in poke:hub run tp A 19.5 65 200.5'); await sleep(500)
  await at('A', 'poke:farm', 20, 50, '농장: 마지막 위치로')
  await cmd('execute in poke:farm run tp A 0.5 -59 -6.5'); await sleep(500)
  await at('A', 'poke:hub', 0, 200, '농장 "마을로" 발판')
  await cmd('execute in poke:hub run tp A 19.5 65 200.5'); await sleep(500)
  await at('A', 'poke:farm', 20, 50, '발판으로 나와도 마지막 위치 유지 (튕김 없음)')

  // 7·8·10. 서쪽 발판 → 채집맵, 마지막 위치 기억
  await cmd('execute as A run trigger home'); await sleep(500)
  await cmd('execute in poke:hub run tp A -18.5 65 200.5'); await waitFor('data get entity A Dimension', /poke:wild/)  // 처음 가면 지형 생성으로 몇 초 걸림
  assert.equal(await dim('A'), 'poke:wild', '서쪽 발판 → 채집맵')
  assert.ok(Math.abs(await pos('A', 0)) <= 17 && Math.abs(await pos('A', 2)) <= 17, '처음엔 0,0 근처')
  await cmd('execute in poke:wild run spreadplayers 300 300 0 1 false A'); await sleep(2500)
  const wx = await pos('A', 0), wz = await pos('A', 2)
  await cmd('execute as A run trigger home'); await sleep(500)
  await cmd('execute in poke:hub run tp A -18.5 65 200.5'); await waitFor('data get entity A Dimension', /poke:wild/)  // 처음 가면 지형 생성으로 몇 초 걸림
  await at('A', 'poke:wild', wx, wz, '채집맵: 마지막 위치로')
  // 10. 바이옴 바둑판: 256x256 칸마다 목록의 다음 바이옴. 칸 경계(0, 256, ...)는 게임이 몇 칸 흔들어서 칸 한가운데로 확인
  for (const x of [128, 640, 1152]) await cmd(`execute in poke:wild run forceload add ${x} 128`)
  await sleep(6000)
  await ok('execute in poke:wild if biome 128 70 128 minecraft:badlands', '바이옴 1번째 칸')
  await ok('execute in poke:wild if biome 640 70 128 minecraft:beach', '바이옴 3번째 칸 (+512)')
  await ok('execute in poke:wild if biome 1152 70 128 minecraft:cherry_grove', '바이옴 5번째 칸 (+1024) = 256블록 간격')

  // 체육관 1인 제한
  await cmd('execute as A run trigger home'); await sleep(500)
  await cmd('execute as A run function poke:gym/enter {id:1}')
  assert.match(await gym('A'), /has 1 /, 'A 체육관1 입장')
  await cmd('execute as B run function poke:gym/enter {id:1}')
  assert.doesNotMatch(await gym('B'), /has 1 /, 'B는 체육관1 입장 거부')
  A.quit(); await sleep(1500)
  await cmd('execute as B run function poke:gym/enter {id:1}')
  assert.match(await gym('B'), /has 1 /, 'A 로그아웃 → 잠금 해제')
  A = await join('A'); await sleep(1500)
  assert.doesNotMatch(await gym('A'), /has /, 'A 재접속 시 체육관 상태 초기화')
  await cmd('kill B'); await sleep(1500)
  assert.doesNotMatch(await gym('B'), /has /, 'B 사망 시 잠금 해제')

  console.log('ALL PASS'); A.quit(); B.quit(); await rc.end(); process.exit(0)
})().catch(e => { console.error('FAIL', e.message); process.exit(1) })
