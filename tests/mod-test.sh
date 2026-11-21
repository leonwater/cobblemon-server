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
rm -f $W/mods/pokeserver-*.jar; cp $R/mod/build/libs/pokeserver-*.jar $W/mods/
cp $R/pack/config/pokeserver/*.json $W/config/pokeserver/
# 배지 해금 시험용: 실제 상점의 해금 물품은 Cobblemon 것이라(이 서버엔 없음) 바닐라 철 블록(배지 1개)을 마지막 분류 끝에 덧붙임
python3 -c "import json,sys;p=sys.argv[1];d=json.load(open(p));d['categories'][-1]['items'].append({'item':'minecraft:iron_block','buy':1200,'sell':300,'badges':1});json.dump(d,open(p,'w'),ensure_ascii=False)" $W/config/pokeserver/shop.json
rm -rf $W/world $W/world-backup-* && mkdir -p $W/world/datapacks $W/world/region && cp -r $R/pack/world/datapacks/pokeserver $W/world/datapacks/
echo old > $W/world/level.dat; echo old > $W/world/region/r.0.0.mca   # 8. 예전 월드 흉내: 시작할 때 백업 폴더로 옮겨져야 함
for f in $W/world/datapacks/pokeserver/data/poke/function/mod/*.mcfunction; do echo 'return 0' > $f; done
echo eula=true > $W/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25577\nserver-port=25567\nlevel-type=minecraft\\:flat\nspawn-protection=0\n' > $W/server.properties
[ -d node_modules ] || npm i --silent
(cd $W && java -Xmx2G -jar fabric-server-launch.jar nogui > run.log 2>&1 &)
timeout 180 bash -c "until grep -qE 'Done \(|Exception in thread' $W/run.log; do sleep 1; done" || { echo 'FAIL server did not start'; exit 1; }
grep -q 'Exception in thread' $W/run.log && { echo 'FAIL server crashed'; grep -A3 'Exception in thread' $W/run.log | head; exit 1; }
b=$(ls -d $W/world-backup-season0-* 2>/dev/null | head -1)
[ -n "$b" ] && [ "$(cat $b/region/r.0.0.mca)" = old ] && [ -f $b/level.dat ] && [ -d $W/world/datapacks/pokeserver ] && [ "$(cat $W/world/pokeserver-season.txt)" = 2 ] \
  && echo '> 8. 초기화: 예전 월드는 백업 폴더로, 데이터팩은 남음' || { echo 'FAIL 8. 월드 초기화'; ls $W $W/world; exit 1; }
trap 'node -e "require(\"rcon-client\").Rcon.connect({host:\"localhost\",port:25577,password:\"test\"}).then(async r=>{await r.send(\"stop\");r.end()})"' EXIT
node mod-test.js 2>&1 | grep -E '^>|FAIL|ALL PASS'
