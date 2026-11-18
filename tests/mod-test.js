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
  assert.match(await cmd('execute in poke:farm run data get entity @e[tag=poke.plot3,limit=1] text'), /'""'$/, '3. 주인이 생기면 땅 이름표 숨김')
  assert.match(await cmd('execute in poke:farm run data get entity @e[tag=poke.plot4,limit=1] text'), /농장 4/, '빈 땅 이름표는 그대로')

  // 주인은 편집 가능, 다른 사람은 구경만
  await within(A.dig(A.blockAt(grass)), 4000)
  assert.ok(!(await blockName(10, -60, 21)), 'A(주인)는 자기 땅을 부술 수 있음')
  const bars = []
  B.on('actionBar', m => bars.push(m.toString()))
  await within(B.dig(B.blockAt(new Vec3(12, -60, 22))), 3000)
  assert.ok(bars.some(t => t.includes('농장 3번') && t.includes('A님의 땅')), '3. 남의 땅 편집 시 체력바 위에 주인 알림')
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

  // ── 4. 상점·화폐 ──
  const opened = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:shop_open') opened.push(p.data) })
  const trade = (sell, cat, item, qty) => A._client.write('custom_payload', { channel: 'pokeserver:shop_trade', data: Buffer.from([sell ? 1 : 0, cat, item, qty]) })
  const bal = async p => Number((await cmd(`execute as ${p} run money`)).replace(/[^0-9]/g, '') || 0)
  await cmd('pokeserver money set A 1000'); await cmd('pokeserver money set B 0')
  await cmd('pokeserver shop A'); await sleep(800)
  assert.equal(opened.length, 1, '상점 열기 패킷')
  assert.ok(opened[0].toString('utf8').includes('farm_deed'), '상점 목록 JSON 전달')
  await cmd('clear A'); await sleep(300)
  trade(false, 3, 1, 16); await sleep(800)                                     // 밀 씨앗 16개 = 160원
  assert.equal(await bal('A'), 840, '구매: 잔액 차감')
  assert.match(await cmd('clear A minecraft:wheat_seeds 0'), /Found 16 /, '구매: 아이템 받음')
  trade(false, 3, 0, 1); await sleep(800)                                      // 땅 문서 50,000원: 잔액 부족
  assert.equal(await bal('A'), 840, '잔액 부족이면 구매 안 됨')
  assert.match(await cmd('clear A minecraft:paper 0'), /No items/, '잔액 부족: 문서 안 받음')
  trade(true, 3, 1, 10); await sleep(800)                                      // 밀 씨앗 10개 판매 = +10
  assert.equal(await bal('A'), 850, '판매: 잔액 증가')
  assert.match(await cmd('clear A minecraft:wheat_seeds 0'), /Found 6 /, '판매: 아이템 빠짐')
  trade(true, 5, 0, 1); await sleep(800)                                       // 석탄 없음
  assert.equal(await bal('A'), 850, '없는 아이템은 판매 안 됨')
  for (const bad of [[false, 99, 0, 1], [false, 3, 99, 1], [false, 3, 1, 0], [false, 3, 1, 100], [false, 3, 9, 1]]) trade(...bad)
  await sleep(800)                                                             // 9번(물 양동이)은 판매가 0 → 구매만 가능, 여기선 구매라 정상 처리
  assert.equal(await bal('A'), 750, '잘못된 요청은 무시 (마지막 물 양동이 구매 100원만 처리)')
  await cmd('execute as A run pay B 100')
  assert.equal(await bal('A'), 650); assert.equal(await bal('B'), 100, '송금')
  await cmd('execute as A run pay B 99999')
  assert.equal(await bal('A'), 650, '잔액보다 큰 송금은 안 됨')
  assert.match(await cmd('execute as A run pay B -5'), /Invalid|must not be less|least/i, '음수 송금 불가')

  // ── 5. 메인 메뉴 (G키) 서버 동작 ──
  const menus = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:menu_open') menus.push(p.data) })
  const act = a => { const b = Buffer.from(a, 'utf8'); A._client.write('custom_payload', { channel: 'pokeserver:menu_action', data: Buffer.concat([Buffer.from([b.length]), b]) }) }
  const dimOf = async p => (await cmd(`data get entity ${p} Dimension`)).match(/"([^"]+)"$/)[1]
  act('open'); await sleep(800)
  assert.equal(menus.length, 1, '메뉴 열기 패킷'); assert.ok(menus[0].toString('utf8').includes('관리자'), '공지 전달')
  act('warp:hall'); await sleep(800)
  assert.equal(await dimOf('A'), 'poke:town', '메뉴 워프: 회의장')
  act('warp:gym'); await sleep(800)
  assert.match(await cmd('data get entity A Pos[0]'), /86\.5d$/, '메뉴 워프: 체육관')
  act('warp:farm'); await sleep(800)
  assert.equal(await dimOf('A'), 'poke:farm', '메뉴 워프: 농장')
  act('warp:street'); await sleep(500)
  await cmd('tag A remove poke.tutorial_done')
  act('warp:farm'); await sleep(800)
  assert.equal(await dimOf('A'), 'poke:town', '튜토리얼 전에는 워프 막힘')
  await cmd('tag A add poke.tutorial_done')
  act('trash'); await sleep(800)
  assert.ok(A.currentWindow, '휴지통 창 열림'); A.closeWindow(A.currentWindow)
  act('nonsense'); act('warp:../../etc'); await sleep(500)
  assert.equal(await dimOf('A'), 'poke:town', '알 수 없는 동작은 무시')
  // 6. 상점 점원(태그 poke.merchant) 우클릭 → 상점 열림
  await cmd('execute at A run summon minecraft:villager ~1 ~ ~ {NoAI:1b,Tags:["poke.merchant"]}'); await sleep(800)
  const before = opened.length
  await A.activateEntity(Object.values(A.entities).find(e => e.name === 'villager'))
  await sleep(800)
  assert.equal(opened.length, before + 1, '6. 점원 우클릭 → 상점 화면')
  act('tutorial'); await sleep(800)
  assert.match(await cmd('data get entity A Pos[2]'), /3\.5d$/, '튜토리얼 다시 보기 → 튜토리얼 방')

  console.log('ALL PASS'); A.quit(); B.quit(); await rc.end(); process.exit(0)
})().catch(e => { console.error('FAIL', e.message); process.exit(1) })
