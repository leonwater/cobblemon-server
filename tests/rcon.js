// 사용: node rcon.js <포트> <명령>  → 결과를 출력 (테스트 스크립트용)
require('rcon-client').Rcon.connect({ host: 'localhost', port: +process.argv[2], password: 'test', timeout: 60000 })
  .then(async r => { console.log(await r.send(process.argv[3])); r.end() })
