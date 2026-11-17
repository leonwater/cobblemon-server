// 바닐라 1.21.1 서버 + 봇 2명으로 데이터팩 로직 검증
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
  const x = async p => Math.floor(parseFloat((await cmd(`data get entity ${p} Pos[0]`)).match(/(-?[\d.]+)d?$/)[1]))

  let A = await join('A'), B = await join('B'); await sleep(1500)
  assert.match(await cmd('tag A list'), /poke\.joined/, '첫 접속 태그')
  assert.equal(await x('A'), 0, '튜토리얼 위치로 이동 (x=0)')

  await cmd('execute as A run function poke:tutorial/finish')
  await cmd('execute as A run function poke:tutorial/finish')
  assert.match(await cmd('clear A minecraft:bread 0'), /16/, '키트는 1번만 지급')

  await cmd('execute as A run function poke:gym/enter {id:1}')
  assert.match(await gym('A'), /has 1 /, 'A 체육관1 입장')
  assert.equal(await x('A'), 50, 'A 체육관1 좌표로 이동')
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
  assert.equal(await x('A'), 0, 'A 재접속 시 허브로 이동')

  await cmd('kill B'); await sleep(1500)
  assert.doesNotMatch(await gym('B'), /has /, 'B 사망 시 잠금 해제')

  await cmd('execute as A run function poke:portal/go {to:"forest"}')
  assert.equal(await x('A'), 1000, '포탈 forest 이동')

  await cmd('execute as A run function poke:admin/reset_me'); await sleep(500)
  assert.match(await cmd('tag A list'), /poke\.joined/, 'reset_me 후 튜토리얼 재시작')
  assert.doesNotMatch(await cmd('tag A list'), /tutorial_done/)

  console.log('ALL PASS'); A.quit(); B.quit(); await rc.end(); process.exit(0)
})().catch(e => { console.error('FAIL', e.message); process.exit(1) })
