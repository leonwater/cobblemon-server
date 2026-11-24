// 모드 서버 테스트: 6. 땅 문서 → 팝업 → 확인 → 내 땅, 다른 사람은 구경만
const mineflayer = require('mineflayer')
const BUILD = require('fs').readFileSync(__dirname + '/../pack/world/datapacks/pokeserver/data/poke/function/load.mcfunction', 'utf8').match(/\{build:(\d+)\}/)[1]   // 건물 번호 (load.mcfunction 한 곳에서만 정함)
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
  const rc = await Rcon.connect({ host: 'localhost', port: 25577, password: 'test', timeout: 60000 })
  const cmd = async c => { const r = await rc.send(c); console.log('>', c, '→', r.slice(0, 200)); return r }
  // 게임 시간을 기다리는 곳은 실제 시간 대신 /tick sprint로 빨리 돌림 (끝날 때까지 확인)
  const ff = async t => { await rc.send(`tick sprint ${t}`); for (let i = 0; i < 100 && /sprint/i.test(await rc.send('tick query')); i++) await sleep(100) }
  // 농장·마을 짓기가 끝날 때까지 (짓는 동안엔 서버가 바빠 응답이 늦음): 그동안 게임 시간을 빨리
  await rc.send('tick sprint 12000')
  for (let i = 0; i < 240 && !new RegExp(`build: ${BUILD}\\b.*farm: 3|farm: 3.*build: ${BUILD}\\b`).test(await cmd('data get storage poke:state')); i++) await sleep(500)
  assert.match(await cmd('data get storage poke:state'), new RegExp(`build: ${BUILD}\\b`), '건물 번호가 load와 같아야 함 (기다리다 시간만 버리지 않게 바로 실패)')
  await rc.send('tick sprint stop')

  const A = await join('A'), B = await join('B'); await sleep(450)
  const popups = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:claim_popup') popups.push(p.data[0]) })
  B._client.on('custom_payload', p => { if (p.channel === 'pokeserver:claim_popup') popups.push('B' + p.data[0]) })
  for (const p of ['A', 'B']) await cmd(`execute as ${p} run function poke:tutorial/finish`)
  await cmd('execute in poke:farm run tp A 10.5 -59 20.5 0 90')   // 농장 3번 땅 (x4~35, z3~34), 발밑 보기
  await cmd('execute in poke:farm run tp B 12.5 -59 20.5 0 90')
  await sleep(700)
  const grass = new Vec3(10, -60, 21), road = new Vec3(0, -60, 20)
  const blockName = async (x, y, z) => (await cmd(`execute in poke:farm if block ${x} ${y} ${z} minecraft:grass_block`)).includes('passed')

  // 주인 없는 땅: 아무도 못 부숨
  await within(A.dig(A.blockAt(grass)), 3000)
  assert.ok(await blockName(10, -60, 21), '주인 없는 땅은 못 부숨')

  // 땅 문서 → 우클릭 → 팝업 → 확인
  await cmd('pokeserver deed A'); await sleep(500)
  const deed = A.inventory.items().find(i => i.name === 'paper')
  assert.ok(deed, '땅 문서 받음'); await A.equip(deed, 'hand')
  await within(A.activateBlock(A.blockAt(grass)), 2000); await sleep(350)
  assert.deepEqual(popups, [3], '농장 3번 팝업이 A에게만 옴')
  A._client.write('custom_payload', { channel: 'pokeserver:claim_confirm', data: Buffer.from([3]) })
  await sleep(450)
  assert.match(await cmd('clear A minecraft:paper 0'), /No items|0 matching/, '땅 문서 1장 사용됨')
  await ff(110)  // 이름표 갱신 주기 100틱
  assert.match(await cmd('execute in poke:farm run data get entity @e[tag=poke.plot3,limit=1] text'), /'""'$/, '3. 주인이 생기면 땅 이름표 숨김')
  assert.match(await cmd('execute in poke:farm run data get entity @e[tag=poke.plot4,limit=1] text'), /농장 4/, '빈 땅 이름표는 그대로')

  // 주인은 편집 가능, 다른 사람은 구경만
  await within(A.dig(A.blockAt(grass)), 4000)
  if (await blockName(10, -60, 21)) { await sleep(450); await within(A.dig(A.blockAt(grass)), 4000) }   // 봇 캐기가 가끔 첫 시도에 씹힘
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
  await within(B.activateBlock(B.blockAt(new Vec3(14, -60, 24))), 2000); await sleep(350)
  assert.deepEqual(popups, [3], '주인 있는 땅은 팝업 없음')
  B._client.write('custom_payload', { channel: 'pokeserver:claim_confirm', data: Buffer.from([3]) })
  await sleep(350)
  assert.match(await cmd('clear B minecraft:paper 0'), /Found 1 /, 'B 문서는 안 쓰임')
  // 멀리서 보낸 가짜 확인 패킷 (농장 16번)도 무시
  B._client.write('custom_payload', { channel: 'pokeserver:claim_confirm', data: Buffer.from([16]) })
  await sleep(350)
  assert.match(await cmd('clear B minecraft:paper 0'), /Found 1 /, '멀리 있는 땅은 등록 안 됨')

  // ── 4. 상점·화폐 ──
  const opened = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:shop_open') opened.push(p.data) })
  const trade = (sell, cat, item, qty) => A._client.write('custom_payload', { channel: 'pokeserver:shop_trade', data: Buffer.from([sell ? 1 : 0, cat, item, qty]) })
  const bal = async p => Number((await cmd(`execute as ${p} run money`)).replace(/[^0-9]/g, '') || 0)
  await cmd('pokeserver money set A 1000'); await cmd('pokeserver money set B 0')
  await cmd('pokeserver shop A'); await sleep(350)
  assert.equal(opened.length, 1, '상점 열기 패킷')
  assert.ok(opened[0].toString('utf8').includes('farm_deed'), '상점 목록 JSON 전달')
  await cmd('clear A'); await sleep(300)
  // 분류 6 = 농장·작물 (0 땅 문서, 1 밀 씨앗 10원·판매 2원), 7 = 광물·블록 (0 석탄), 8 = 도구·기타 (3 철 괭이 300원) — tools/build_shop.py 순서
  trade(false, 6, 1, 16); await sleep(350)                                     // 밀 씨앗 16개 = 160원
  assert.equal(await bal('A'), 840, '구매: 잔액 차감')
  assert.match(await cmd('clear A minecraft:wheat_seeds 0'), /Found 16 /, '구매: 아이템 받음')
  trade(false, 6, 0, 1); await sleep(350)                                      // 땅 문서 50,000원: 잔액 부족
  assert.equal(await bal('A'), 840, '잔액 부족이면 구매 안 됨')
  assert.match(await cmd('clear A minecraft:paper 0'), /No items/, '잔액 부족: 문서 안 받음')
  trade(true, 6, 1, 10); await sleep(350)                                      // 밀 씨앗 10개 판매 = +20 (구매가 ÷ 4)
  assert.equal(await bal('A'), 860, '판매: 잔액 증가')
  assert.match(await cmd('clear A minecraft:wheat_seeds 0'), /Found 6 /, '판매: 아이템 빠짐')
  trade(true, 7, 0, 1); await sleep(350)                                       // 석탄 없음
  assert.equal(await bal('A'), 860, '없는 아이템은 판매 안 됨')
  for (const bad of [[false, 99, 0, 1], [false, 6, 99, 1], [false, 6, 1, 0], [false, 6, 1, 100], [false, 8, 3, 1]]) trade(...bad)
  await sleep(350)                                                             // 마지막(철 괭이 300원)만 정상 구매
  assert.equal(await bal('A'), 560, '잘못된 요청은 무시 (마지막 철 괭이 구매 300원만 처리)')
  await cmd('execute as A run pay B 100')
  assert.equal(await bal('A'), 460); assert.equal(await bal('B'), 100, '송금')
  await cmd('execute as A run pay B 99999')
  assert.equal(await bal('A'), 460, '잔액보다 큰 송금은 안 됨')
  await cmd('execute as A run pay B -5')
  assert.equal(await bal('A'), 460, '음수 송금 불가'); assert.equal(await bal('B'), 100)

  // ── 5. 메인 메뉴 (G키) 서버 동작 ──
  const menus = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:menu_open') menus.push(p.data) })
  const act = a => { const b = Buffer.from(a, 'utf8'); A._client.write('custom_payload', { channel: 'pokeserver:menu_action', data: Buffer.concat([Buffer.from([b.length]), b]) }) }
  const dimOf = async p => (await cmd(`data get entity ${p} Dimension`)).match(/"([^"]+)"$/)[1]
  act('open'); await sleep(350)
  assert.equal(menus.length, 1, '메뉴 열기 패킷'); assert.ok(menus[0].toString('utf8').includes('관리자'), '공지 전달')
  act('warp:hall'); await sleep(350)
  assert.equal(await dimOf('A'), 'poke:wild', '15. 메뉴 워프: 광장 (야생)')
  // 초기화·다시 짓기 뒤 바닥 아이템 정리 (build/finish·plaza/finish가 부르는 함수)
  await cmd('execute in minecraft:overworld run summon minecraft:item 0 -55 0 {NoGravity:1b,PickupDelay:32767,Tags:["poke.testitem"],Item:{id:"minecraft:dandelion",count:1}}')   // 늘 불러와진 스폰 청크
  await sleep(300)   // 소환 직후엔 선택자에 안 잡힐 때가 있음
  assert.match(await cmd('execute if entity @e[type=minecraft:item,tag=poke.testitem]'), /passed/, '아이템 하나 떨어뜨림')
  await cmd('function poke:mod/clear_items')
  assert.doesNotMatch(await cmd('execute if entity @e[type=minecraft:item,tag=poke.testitem]'), /passed/, '2. 짓기 끝 → 바닥 아이템 정리')   // A 근처만 셈 (다른 차원·다른 시험이 떨군 아이템과 섞이지 않게)
  // 야생 버튼: 광장 밖에서 마지막으로 있던 자리로 (처음이면 광장 북쪽 출구 밖, 광장 안은 저장 안 함)
  const posX = async () => (await cmd('data get entity A Pos[0]')).match(/(-?[\d.]+)d$/)[1]
  const posZ = async () => +(await cmd('data get entity A Pos[2]')).match(/(-?[\d.]+)d$/)[1]
  const hallZ = await posZ()
  await ff(25)   // 광장 태그(1초마다) 붙을 때까지
  const aid = (await cmd('scoreboard players get A poke.id')).match(/has (\d+)/)[1]
  await cmd(`data remove storage poke:last p${aid}.wild`)   // 앞 시험에서 저장된 야생 위치 지움 → "처음"
  act('warp:wild'); await sleep(500)
  assert.equal(await dimOf('A'), 'poke:wild', '메뉴 워프: 야생')
  const hallX = +(await cmd('data get storage poke:config hall.x')).match(/(-?[\d.]+)d$/)[1]
  assert.ok(Math.hypot(+(await posX()) - hallX, await posZ() - hallZ) > 72, '야생 처음 → 광장 밖 (북·동·남·서 중 땅이 있는 쪽)')
  for (let i = 0; i < 10 && !/wild/.test(await cmd(`data get storage poke:last p${aid}`)); i++) {   // 땅에 내려설 때까지 (공중이면 저장 안 함)
    await ff(20); await cmd('execute as A run function poke:warp/save_here')
  }
  const wildX = await posX()
  act('warp:hall'); await sleep(350); await ff(25)
  await cmd('execute as A run function poke:warp/save_here')   // 광장 안에서 저장해도 무시
  act('warp:gym'); await sleep(350)
  act('warp:wild'); await sleep(350)
  for (let i = 0; i < 10 && await posX() !== wildX; i++) await sleep(300)   // 체육관도 야생 차원이라 워프가 처리될 때까지 기다림 (3초 안에 안 오면 실패)
  assert.equal(await posX(), wildX, '야생 → 광장이 아니라 광장 밖 마지막 위치로')
  act('warp:hall'); await sleep(350)
  assert.ok(Math.abs(await posZ() - hallZ) < 3, '광장 → 광장 자리로')
  act('warp:gym'); await sleep(350)
  assert.match(await cmd('data get entity A Pos[0]'), /2000\.5d$/, '메뉴 워프: 체육관 로비')
  act('warp:farm'); await sleep(350)
  assert.equal(await dimOf('A'), 'poke:farm', '메뉴 워프: 농장')
  act('warp:gym'); await sleep(350)
  // 1. 체육관 도전 중엔 G 메뉴 이동이 막힘 (나가기는 포기 발판·승패로만)
  await cmd('scoreboard players set A poke.gym 1'); act('warp:farm'); await sleep(350)
  assert.equal(await dimOf('A'), 'poke:town', '도전 중 워프 막힘')
  assert.match(await cmd('scoreboard players get A poke.gym'), /has 1 /, '도전 상태 그대로')
  await cmd('scoreboard players reset A poke.gym')
  await cmd('tag A remove poke.tutorial_done')
  act('warp:farm'); await sleep(350)
  assert.equal(await dimOf('A'), 'poke:town', '튜토리얼 전에는 워프 막힘')
  await cmd('tag A add poke.tutorial_done')
  act('trash'); await sleep(350)
  assert.ok(A.currentWindow, '휴지통 창 열림'); A.closeWindow(A.currentWindow)
  act('nonsense'); act('warp:../../etc'); await sleep(500)
  assert.equal(await dimOf('A'), 'poke:town', '알 수 없는 동작은 무시')
  // 6. 상인 우클릭 → 그 상인의 상점만 열림 (포켓몬 상인 = shop:poke 분류만)
  await cmd('execute at A run summon minecraft:villager ~1 ~ ~ {NoAI:1b,Tags:["poke.merchant_poke"]}'); await sleep(350)
  const before = opened.length
  let vil; for (let i = 0; i < 20 && !(vil = Object.values(A.entities).find(e => e.name === 'villager')); i++) await sleep(150)   // 봇이 주민을 볼 때까지
  await A.activateEntity(vil)
  await sleep(350)
  assert.equal(opened.length, before + 1, '6. 상인 우클릭 → 상점 화면')
  const pokeTxt = opened[opened.length - 1].toString('utf8')
  assert.ok(pokeTxt.includes('"shop":"poke"') && !pokeTxt.includes('"shop":"mc"'), '포켓몬 상인은 포켓몬 물품만')
  await cmd('kill @e[type=minecraft:villager]'); await cmd('pokeserver shop A'); await sleep(350)   // 아래 거래 시험은 전체 목록 기준
  // 7. 튜토리얼 다시 보기: 설명 창만 열고 자리는 그대로
  let tut = 0; A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:tutorial_open') tut++ })
  const posBefore = await cmd('data get entity A Pos')
  act('tutorial'); await sleep(350)
  assert.equal(tut, 1, '7. 튜토리얼 다시 보기 → 설명 창 패킷')
  assert.equal(await cmd('data get entity A Pos'), posBefore, '7. 튜토리얼 다시 보기 → 오박사에게 이동하지 않음')


  // 3·4. 체육관 안내원(태그 poke.gymguide) → 배지 케이스: 9칸 모두(잠긴 곳은 locked), 열린 곳만 고를 수 있고 고르면 경기장으로
  const gyms = []
  A._client.on('custom_payload', p => { if (p.channel === 'pokeserver:gym_open') gyms.push(p.data.toString('utf8')) })
  await cmd('execute as A run function poke:tutorial/finish')   // 바로 위에서 튜토리얼을 다시 시작했으므로
  await cmd('execute as A run function poke:warp/fixed {key:"gym"}'); await sleep(500)
  await cmd('execute at A run summon minecraft:villager ~ ~ ~2 {NoAI:1b,Tags:["poke.gymguide"]}'); await sleep(350)
  const guide = () => Object.values(A.entities).find(e => e.name === 'villager' && e.position.z > A.entity.position.z + 1)
  const listOf = j => JSON.parse(j.slice(j.indexOf('['))).map(g => [g.n, g.status]).filter(([, st]) => st !== 'locked')
  const countOf = j => JSON.parse(j.slice(j.indexOf('['))).length
  await A.activateEntity(guide()); await sleep(350)
  assert.deepEqual(listOf(gyms[0]), [[1, 'open']], '배지 0개: 1번 체육관만 열림')
  assert.equal(countOf(gyms[0]), 9, '배지 케이스: 잠긴 칸(2~8번·사천왕)도 locked로 옴')
  await cmd('tag A add poke.badge1'); await A.activateEntity(guide()); await sleep(350)
  assert.deepEqual(listOf(gyms[1]), [[1, 'cleared'], [2, 'open']], '클리어한 1번(금색) + 도전 가능한 2번만')
  const pick = n => A._client.write('custom_payload', { channel: 'pokeserver:gym_pick', data: Buffer.from([n]) })
  const gymOf = async () => cmd('scoreboard players get A poke.gym')
  pick(5); pick(9); pick(1); await sleep(600)
  assert.doesNotMatch(await gymOf(), /has /, '못 가는 곳·클리어한 곳은 고를 수 없음')
  pick(2); await sleep(600)
  assert.match(await gymOf(), /has 2 /, '고른 2번 체육관 경기장으로')
  await cmd('execute as A run function poke:gym/leave')
  // 상금: 1번 관장을 이기면 레벨 제한 20 × 200 = 4,000원 (+ 보상 물품: 경험사탕·기술머신)
  await cmd('pokeserver money set A 0'); await cmd('tag A remove poke.badge1'); await cmd('scoreboard players set A poke.gym 1')
  await cmd('execute as A run function poke:gym/win'); await sleep(400)
  assert.equal(await bal('A'), 4000, '1번 관장 승리 상금 4,000원')
  // 12. 배지가 있어야 사는 상품: 시험용 철 블록(1,200원, 배지 1개, mod-test.sh가 생활 상점 마지막 분류 끝에 붙임 → 번호가 128 아래라 한 바이트로 보냄), 판매는 제한 없음
  const shopTxt = opened[0].toString('utf8'), shopCats = JSON.parse(shopTxt.slice(shopTxt.indexOf('{'), shopTxt.lastIndexOf('}') + 1)).categories
  const ic = shopCats.findIndex(c => c.items.some(x => x.item === 'minecraft:iron_block')), ii = shopCats[ic].items.findIndex(x => x.item === 'minecraft:iron_block')
  await cmd('tag A remove poke.badge1'); await cmd('pokeserver money set A 5000')
  trade(false, ic, ii, 1); await sleep(600)
  assert.equal(await bal('A'), 5000, '배지 없으면 철 블록 못 삼')
  await cmd('tag A add poke.badge1'); trade(false, ic, ii, 1); await sleep(600)
  assert.equal(await bal('A'), 3800, '배지 1개 → 철 블록 구매')
  await cmd('tag A remove poke.badge1'); trade(true, ic, ii, 1); await sleep(600)
  assert.equal(await bal('A'), 4100, '판매는 배지와 상관없음')
  // 3. 땅 문서는 한 사람이 살수록 비싸짐 (기본가 × (산 개수 + 1)), 사람마다 따로
  await cmd('pokeserver money set A 300000'); await cmd('pokeserver money set B 300000')
  trade(false, 6, 0, 1); await sleep(600)
  assert.equal(await bal('A'), 250000, '첫 땅 문서 50,000')
  trade(false, 6, 0, 1); await sleep(600)
  assert.equal(await bal('A'), 150000, '두 번째 땅 문서 100,000')
  B._client.write('custom_payload', { channel: 'pokeserver:shop_trade', data: Buffer.from([0, 6, 0, 1]) }); await sleep(600)
  assert.equal(await bal('B'), 250000, '다른 사람은 따로 셈: B의 첫 문서는 50,000')
  // 10. 마을(야생·농장 밖)은 아무도 못 부숨
  await cmd('execute in poke:town run tp A 2000.5 -59 -11.5 0 90'); await sleep(350)
  await within(A.dig(A.blockAt(new Vec3(2000, -60, -12))), 3000)
  assert.ok(!(await cmd('execute in poke:town if block 2000 -60 -12 minecraft:air')).includes('passed'), '마을 블록은 못 부숨')

  // 새 2. 텔레포트: 일반 사용자는 상대가 [예]를 눌러야 이동, 10초 지나면 취소
  const msgs = []; B.on('message', m => msgs.push(m.toString()))
  await cmd('execute in poke:town run tp A 2000.5 -56 -11.5'); await cmd('execute in poke:town run tp B 2006.5 -56 -11.5'); await sleep(500)
  A.chat('/tp B'); await sleep(350)   // 일반 사용자 /tp = /가기
  assert.ok(msgs.some(m => m.includes('A님이 당신에게 오려고 해요') && m.includes('[예]') && m.includes('[아니요]')), '2. 상대에게 예/아니요가 뜸')
  assert.match(await cmd('data get entity A Pos[0]'), /: 2000\.5d/, '2. 동의 전엔 이동 안 함')
  B.chat('/수락'); await sleep(350)
  assert.match(await cmd('data get entity A Pos[0]'), /2006\.5d/, '2. [예]를 누르면 상대에게 이동')
  await cmd('execute in poke:town run tp A 2000.5 -56 -11.5'); await sleep(300)
  A.chat('/tpa B'); await sleep(300); await ff(220)   // /tpa = /부르기   // 10초(200틱) 시간 초과
  assert.ok(msgs.some(m => m.includes('10초 동안 대답이 없어 취소')), '2. 10초가 지나면 자동 취소')
  B.chat('/수락'); await sleep(350)
  assert.match(await cmd('data get entity B Pos[0]'), /2006\.5d/, '2. 취소된 요청은 수락해도 이동 안 함')
  console.log('> 새 2. 텔레포트 동의·10초 취소')
  // 7. /초기화는 OP만: 일반 사용자에겐 명령어가 없음 → 돈이 그대로
  const aMsgs = []; A.on('message', m => aMsgs.push(m.toString()))
  const balA = await bal('A'); A.chat('/초기화 확인'); await sleep(350)
  assert.equal(await bal('A'), balA, '7. 일반 사용자는 /초기화 불가')
  assert.ok(aMsgs.some(m => /Unknown|unknown|알 수 없/.test(m)), '7. 알 수 없는 명령어 안내')
  await cmd('pokeserver money set B 777'); await cmd('초기화 B'); await sleep(350)
  assert.equal(await bal('B'), 0, '8. /초기화 이름 → 그 사람만')
  assert.ok(await bal('A') > 0, '8. 다른 사람은 그대로')
  await cmd('tag B add poke.tutorial_done')
  console.log('> 7·8. 초기화는 OP만, 이름을 붙이면 그 사람만')

  // 15. 광장 마을: 모드가 자리·지형을 정하고 지음, 둘레 72칸은 수정 금지
  await rc.send('tick sprint 4800')
  for (let i = 0; i < 120 && !/built: 6/.test(await cmd('data get storage poke:state plaza')); i++) await sleep(450)
  await rc.send('tick sprint stop')
  assert.match(await cmd('data get storage poke:state plaza'), /built: 6/, '광장 짓기 끝')
  const pz = (await cmd('data get storage poke:state plaza')).match(/x: (-?\d+), y: (-?\d+), z: (-?\d+)/)
  assert.ok(pz, '15. 광장 자리 저장'); const [px, py, pzz] = pz.slice(1).map(Number)
  await cmd(`execute in poke:wild run forceload add ${px} ${pzz}`); await sleep(700)
  assert.ok((await cmd(`execute in poke:wild if block ${px} ${py + 1} ${pzz} minecraft:quartz_pillar`)).includes('passed'), '15. 광장 분수 기둥')
  await cmd(`execute in poke:wild run tp A ${px + 5}.5 ${py + 1} ${pzz + 20}.5 0 90`); await sleep(300); await ff(25)   // 게임 모드는 1초(20틱)마다
  await within(A.dig(A.blockAt(new Vec3(px + 5, py, pzz + 21))), 3000)
  assert.ok(!(await cmd(`execute in poke:wild if block ${px + 5} ${py} ${pzz + 21} minecraft:air`)).includes('passed'), '15. 광장 둘레 블록은 못 부숨')
  // 5. 광장 안: 모험 모드 + 블록 놓기 금지 (예전엔 놓기만 안 막혔음)
  assert.ok((await cmd('execute if entity @a[name=A,gamemode=adventure]')).includes('passed'), '5. 광장 안은 모험 모드')
  await cmd('give A minecraft:stone 1'); await sleep(500)
  await A.equip(A.inventory.items().find(i => i.name === 'stone'), 'hand')
  await within(A.placeBlock(A.blockAt(new Vec3(px + 5, py, pzz + 21)), new Vec3(0, 1, 0)), 2000); await sleep(500)
  assert.ok((await cmd(`execute in poke:wild if block ${px + 5} ${py + 1} ${pzz + 21} minecraft:air`)).includes('passed'), '5. 광장에 블록을 못 놓음')
  // 정보창 "위치" (공간 BGM도 이 값으로 고름): 포켓몬 센터·체육관 로비·경기장을 나눔
  let place = ''
  const varint = (b, o) => { let v = 0, k = 0, c; do { c = b[o++]; v |= (c & 0x7f) << (7 * k++) } while (c & 0x80); return [v, o] }
  A._client.on('custom_payload', p => {
    if (p.channel !== 'pokeserver:hud') return
    let o = varint(p.data, 0)[1]; o = varint(p.data, o)[1]; const [n, s] = varint(p.data, o); place = p.data.slice(s, s + n).toString('utf8')
  })
  const placeAt = async (tp, want, msg) => { await cmd(tp); await sleep(300); await ff(25); await sleep(300); assert.equal(place, want, msg) }
  await placeAt(`execute in poke:wild run tp A ${px + 27}.5 ${py + 1} ${pzz}.5`, '포켓몬 센터', 'BGM 위치: 광장의 포켓몬 센터 안')
  await placeAt(`execute in poke:wild run tp A ${px + 5}.5 ${py + 1} ${pzz + 20}.5`, '광장 마을', 'BGM 위치: 광장')
  await placeAt('execute in poke:town run tp A 2000.5 -56 0.5', '체육관', 'BGM 위치: 체육관 로비')
  await placeAt('execute in poke:town run tp A 3015.5 -59 0.5', '경기장', 'BGM 위치: 경기장 (체육관 BGM 없음)')
  await placeAt(`execute in poke:wild run tp A ${px - 29}.5 ${py + 1} ${pzz + 7}.5`, '상점', 'BGM 위치: 광장의 상점 안')
  await placeAt('execute in poke:town run tp A 3520.5 -59 0.5', '사천왕 본부', 'BGM 위치: 사천왕 본부')
  await cmd(`execute in poke:wild run tp A ${px + 120}.5 200 ${pzz}.5`); await sleep(300); await ff(25)   // 게임 모드는 1초(20틱)마다
  assert.ok((await cmd('execute if entity @a[name=A,gamemode=survival]')).includes('passed'), '5. 광장 밖은 생존 모드')
  console.log('> 15. 광장 마을·보호')
  // 광장 안의 불은 저절로 꺼지고, 야생 불은 그대로
  await cmd(`execute in poke:wild run forceload add ${px + 200} ${pzz}`); await sleep(450)
  await cmd(`execute in poke:wild run setblock ${px + 5} ${py + 1} ${pzz + 21} minecraft:fire`)
  await cmd(`execute in poke:wild run setblock ${px + 200} 150 ${pzz} minecraft:stone`)
  await cmd(`execute in poke:wild run setblock ${px + 200} 151 ${pzz} minecraft:fire`); await ff(60)   // 불은 놓이고 30~40틱 뒤 틱
  assert.ok((await cmd(`execute in poke:wild if block ${px + 5} ${py + 1} ${pzz + 21} minecraft:air`)).includes('passed'), '광장 불은 꺼짐')
  assert.ok((await cmd(`execute in poke:wild if block ${px + 200} 151 ${pzz} minecraft:fire`)).includes('passed'), '야생 불은 그대로')
  console.log('> 광장 불 자동으로 꺼짐')

  console.log('ALL PASS'); A.quit(); B.quit(); await rc.end(); process.exit(0)
})().catch(e => { console.error('FAIL', e.message); process.exit(1) })
