// 모드 서버 테스트: 6. 땅 문서 → 팝업 → 확인 → 내 땅, 다른 사람은 구경만
const mineflayer = require('mineflayer')
const { Vec3 } = require('vec3')
const { Rcon } = require('rcon-client')
const assert = require('assert')
const sleep = ms => new Promise(r => setTimeout(r, ms))
const join = name => new Promise((res, rej) => {
  const b = mineflayer.createBot({ host: 'localhost', port: 25567, username: name, version: '1.21.1', auth: 'offline' })
  b.once('spawn', () => res(b)); b.once('error', rej); b.once('kicked', r => rej(new Error('kicked ' + JSON.stringify(r))))
})
const within = (p, ms) => Promise.race([p, sleep(ms).then(() => 'timeout')]).catch(e => 'error: ' + e.message)

;(async () => {
  const rc = await Rcon.connect({ host: 'localhost', port: 25577, password: 'test', timeout: 15000 })
  const cmd = async c => { const r = await rc.send(c); console.log('>', c, '→', r.slice(0, 200)); return r }
  for (let i = 0; i < 30 && !/farm: 2/.test(await cmd('data get storage poke:state')); i++) await sleep(500)

  const A = await join('A'), B = await join('B'); await sleep(1000)
  const popups = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:claim_popup') popups.push(p.data[0]) })
  B._client.on('custom_payload', p => { if (p.channel === 'pokeserver:claim_popup') popups.push('B' + p.data[0]) })
  for (const p of ['A', 'B']) await cmd(`execute as ${p} run function poke:tutorial/finish`)
  await cmd('execute in poke:farm run tp A 10.5 -59 20.5 0 90')   // 농장 3번 땅 (x4~35, z3~34), 발밑 보기
  await cmd('execute in poke:farm run tp B 12.5 -59 20.5 0 90')
  await sleep(1500)
  const grass = new Vec3(10, -60, 21), road = new Vec3(0, -60, 20)
  const blockName = async (x, y, z) => (await cmd(`execute in poke:farm if block ${x} ${y} ${z} minecraft:grass_block`)).includes('passed')

  // 주인 없는 땅: 아무도 못 부숨
  await within(A.dig(A.blockAt(grass)), 3000)
  assert.ok(await blockName(10, -60, 21), '주인 없는 땅은 못 부숨')

  // 땅 문서 → 우클릭 → 팝업 → 확인
  await cmd('pokeserver deed A'); await sleep(500)
  const deed = A.inventory.items().find(i => i.name === 'paper')
  assert.ok(deed, '땅 문서 받음'); await A.equip(deed, 'hand')
  await within(A.activateBlock(A.blockAt(grass)), 2000); await sleep(800)
  assert.deepEqual(popups, [3], '농장 3번 팝업이 A에게만 옴')
  A._client.write('custom_payload', { channel: 'pokeserver:claim_confirm', data: Buffer.from([3]) })
  await sleep(1000)
  assert.match(await cmd('clear A minecraft:paper 0'), /No items|0 matching/, '땅 문서 1장 사용됨')
  await sleep(5500)  // 이름표 갱신 주기 100틱
  assert.match(await cmd('execute in poke:farm run data get entity @e[tag=poke.plot3,limit=1] text'), /농장 3 · A/, '이름표에 주인 이름')

  // 주인은 편집 가능, 다른 사람은 구경만
  await within(A.dig(A.blockAt(grass)), 4000)
  assert.ok(!(await blockName(10, -60, 21)), 'A(주인)는 자기 땅을 부술 수 있음')
  await within(B.dig(B.blockAt(new Vec3(12, -60, 22))), 3000)
  assert.ok(await blockName(12, -60, 22), 'B는 남의 땅을 못 부숨')
  await cmd('execute in poke:farm run setblock 12 -59 23 minecraft:chest')
  await sleep(300)
  await within(B.openContainer(B.blockAt(new Vec3(12, -59, 23))), 2000)
  assert.ok(!B.currentWindow, 'B는 남의 땅 상자를 못 엶')
  await within(A.openContainer(A.blockAt(new Vec3(12, -59, 23))), 3000)
  assert.ok(A.currentWindow, 'A는 자기 상자를 엶'); A.closeWindow(A.currentWindow)
  await within(B.dig(B.blockAt(road)), 3000)
  assert.ok(!(await cmd('execute in poke:farm if block 0 -60 20 minecraft:air')).includes('passed'), '길은 아무도 못 부숨')

  // 이미 주인 있는 땅에 문서를 써도 팝업 없음, 가짜 확인 패킷도 무시
  await cmd('pokeserver deed B'); await sleep(500)
  await B.equip(B.inventory.items().find(i => i.name === 'paper'), 'hand')
  await within(B.activateBlock(B.blockAt(new Vec3(14, -60, 24))), 2000); await sleep(800)
  assert.deepEqual(popups, [3], '주인 있는 땅은 팝업 없음')
  B._client.write('custom_payload', { channel: 'pokeserver:claim_confirm', data: Buffer.from([3]) })
  await sleep(800)
  assert.match(await cmd('clear B minecraft:paper 0'), /Found 1 /, 'B 문서는 안 쓰임')
  // 멀리서 보낸 가짜 확인 패킷 (농장 16번)도 무시
  B._client.write('custom_payload', { channel: 'pokeserver:claim_confirm', data: Buffer.from([16]) })
  await sleep(800)
  assert.match(await cmd('clear B minecraft:paper 0'), /Found 1 /, '멀리 있는 땅은 등록 안 됨')

  console.log('ALL PASS'); A.quit(); B.quit(); await rc.end(); process.exit(0)
})().catch(e => { console.error('FAIL', e.message); process.exit(1) })
