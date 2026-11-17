#!/usr/bin/env bash
# 데이터팩 로직 테스트: 바닐라 1.21.1 서버 + 봇 2명 (Java 21, Node 필요)
set -euo pipefail
cd "$(dirname "$0")"; W=.work
rm -rf $W/world && mkdir -p $W/world/datapacks  # 매번 새 월드: 이전 실행의 인벤토리·태그가 남지 않게
if [ ! -f $W/server.jar ]; then
  meta=$(curl -s https://piston-meta.mojang.com/mc/game/version_manifest_v2.json | python3 -c 'import json,sys;print([v["url"] for v in json.load(sys.stdin)["versions"] if v["id"]=="1.21.1"][0])')
  curl -sfL -o $W/server.jar "$(curl -s "$meta" | python3 -c 'import json,sys;print(json.load(sys.stdin)["downloads"]["server"]["url"])')"
fi
rm -rf $W/world/datapacks/pokeserver && cp -r ../pack/world/datapacks/pokeserver $W/world/datapacks/
# 바닐라엔 모드 명령(Cobblemon·CobbleDollars)이 없으므로 mod/ 함수만 비움
for f in $W/world/datapacks/pokeserver/data/poke/function/mod/*.mcfunction; do echo 'return 0' > $f; done
echo eula=true > $W/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25576\nserver-port=25566\nlevel-type=minecraft\\:flat\n' > $W/server.properties
[ -d node_modules ] || npm i --silent
(cd $W && java -Xmx2G -jar server.jar nogui > run.log 2>&1 &)
timeout 120 bash -c "until grep -q 'Done (' $W/run.log; do sleep 1; done" || { echo 'FAIL server did not start in 120s'; tail -5 $W/run.log; exit 1; }
trap 'node -e "require(\"rcon-client\").Rcon.connect({host:\"localhost\",port:25576,password:\"test\"}).then(async r=>{await r.send(\"stop\");r.end()})"' EXIT  # 실패해도 서버 종료
node datapack-test.js 2>&1 | grep -E '^>|FAIL|ALL PASS'
