#!/usr/bin/env bash
# 모드(pokeserver) 서버 쪽 테스트: Fabric 서버 + Fabric API + 우리 모드 + 데이터팩, 봇 2명
# (Cobblemon은 빼고 돌림: 봇이 접속할 수 있게. 모드 전용 데이터팩 함수는 비움)
set -euo pipefail
cd "$(dirname "$0")"; W=.modwork; R=..
mkdir -p $W/mods $W/config/pokeserver
if [ ! -f $W/fabric-server-launch.jar ]; then
  [ -f .work/server.jar ] || { echo "먼저 tests/run.sh 를 한 번 실행하세요 (바닐라 서버 jar)"; exit 1; }
  cp .work/server.jar $W/
  v=$(curl -s https://meta.fabricmc.net/v2/versions/installer | python3 -c 'import json,sys;print(json.load(sys.stdin)[0]["version"])')
  curl -sfL -o $W/installer.jar https://maven.fabricmc.net/net/fabricmc/fabric-installer/$v/fabric-installer-$v.jar
  (cd $W && java -jar installer.jar server -mcversion 1.21.1 -loader 0.20.1 > /dev/null)
fi
f=$R/pack/mods/fabric-api.pw.toml; name=$(grep '^filename' $f | cut -d'"' -f2)
[ -f "$W/mods/$name" ] || curl -sfL -o "$W/mods/$name" "$(grep '^url' $f | cut -d'"' -f2)"
cp $R/mod/build/libs/pokeserver-*.jar $W/mods/
cp $R/pack/config/pokeserver/farms.json $W/config/pokeserver/
rm -rf $W/world && mkdir -p $W/world/datapacks && cp -r $R/pack/world/datapacks/pokeserver $W/world/datapacks/
for f in $W/world/datapacks/pokeserver/data/poke/function/mod/*.mcfunction; do echo 'return 0' > $f; done
echo eula=true > $W/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25577\nserver-port=25567\nlevel-type=minecraft\\:flat\nspawn-protection=0\n' > $W/server.properties
[ -d node_modules ] || npm i --silent
(cd $W && java -Xmx2G -jar fabric-server-launch.jar nogui > run.log 2>&1 &)
timeout 180 bash -c "until grep -qE 'Done \(|Exception in thread' $W/run.log; do sleep 1; done" || { echo 'FAIL server did not start'; exit 1; }
grep -q 'Exception in thread' $W/run.log && { echo 'FAIL server crashed'; grep -A3 'Exception in thread' $W/run.log | head; exit 1; }
trap 'node -e "require(\"rcon-client\").Rcon.connect({host:\"localhost\",port:25577,password:\"test\"}).then(async r=>{await r.send(\"stop\");r.end()})"' EXIT
node mod-test.js 2>&1 | grep -E '^>|FAIL|ALL PASS'
