#!/usr/bin/env bash
# 데이터팩 로직 테스트: 바닐라 1.21.1 서버 + 봇 2명 (Java 21, Node 필요)
set -euo pipefail
cd "$(dirname "$0")"; W=.work; mkdir -p $W/world/datapacks
if [ ! -f $W/server.jar ]; then
  meta=$(curl -s https://piston-meta.mojang.com/mc/game/version_manifest_v2.json | python3 -c 'import json,sys;print([v["url"] for v in json.load(sys.stdin)["versions"] if v["id"]=="1.21.1"][0])')
  curl -sfL -o $W/server.jar "$(curl -s "$meta" | python3 -c 'import json,sys;print(json.load(sys.stdin)["downloads"]["server"]["url"])')"
fi
rm -rf $W/world/datapacks/pokeserver && cp -r ../datapacks/pokeserver $W/world/datapacks/
# 바닐라엔 Cobblemon 아이템이 없어 키트만 바닐라 아이템으로 교체 (테스트가 빵 16개를 확인함)
echo 'give @s minecraft:bread 16' > $W/world/datapacks/pokeserver/data/poke/function/kit.mcfunction
echo eula=true > $W/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25576\nserver-port=25566\nlevel-type=minecraft\\:flat\n' > $W/server.properties
[ -d node_modules ] || npm i --silent
(cd $W && java -Xmx2G -jar server.jar nogui > run.log 2>&1 &)
until grep -q 'Done (' $W/run.log; do sleep 1; done
node datapack-test.js 2>/dev/null | grep -E '^>|FAIL|ALL PASS'; status=${PIPESTATUS[0]}
node -e 'require("rcon-client").Rcon.connect({host:"localhost",port:25576,password:"test"}).then(async r=>{await r.send("stop");r.end()})'
exit $status
