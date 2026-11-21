#!/usr/bin/env bash
# 데이터팩 로직 테스트: 바닐라 1.21.1 서버 + 봇 2명 (Java 21, Node 필요)
set -euo pipefail
cd "$(dirname "$0")"; W=.work
# 매번 새 월드 (이전 실행의 인벤토리·태그가 남지 않게). 데이터팩이 같으면 "건물까지 지어 둔 월드"를 복사해 짓기 시간을 아낌
KEY=$(find ../pack/world/datapacks -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum | cut -c1-12); CACHE=.cache/world-$KEY
rm -rf $W/world && mkdir -p $W/world/datapacks
if [ -d $CACHE ]; then cp -r $CACHE/. $W/world/; echo "> 지어 둔 월드 재사용 ($KEY)"; fi
if [ ! -f $W/server.jar ]; then
  meta=$(curl -s https://piston-meta.mojang.com/mc/game/version_manifest_v2.json | python3 -c 'import json,sys;print([v["url"] for v in json.load(sys.stdin)["versions"] if v["id"]=="1.21.1"][0])')
  curl -sfL -o $W/server.jar "$(curl -s "$meta" | python3 -c 'import json,sys;print(json.load(sys.stdin)["downloads"]["server"]["url"])')"
fi
rm -rf $W/world/datapacks/pokeserver && cp -r ../pack/world/datapacks/pokeserver $W/world/datapacks/
# 바닐라엔 모드 명령(Cobblemon·CobbleDollars)이 없으므로 mod/ 함수만 비움
for f in $W/world/datapacks/pokeserver/data/poke/function/mod/*.mcfunction; do echo 'return 0' > $f; done
echo eula=true > $W/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25576\nserver-port=25566\nlevel-type=minecraft\\:flat\n' > $W/server.properties
python3 ../tools/check_holes.py > /dev/null || { echo "FAIL 건물에 빈칸이 있음 (python3 tools/check_holes.py)"; exit 1; }
[ -d node_modules ] || npm i --silent
(cd $W && java -Xmx2G -jar server.jar nogui > run.log 2>&1 &)
timeout 120 bash -c "until grep -q 'Done (' $W/run.log; do sleep 1; done" || { echo 'FAIL server did not start in 120s'; tail -5 $W/run.log; exit 1; }
trap 'node rcon.js 25576 stop > /dev/null 2>&1' EXIT   # 실패해도 서버 종료
# 처음 보는 데이터팩이면: 건물을 다 지은 뒤 월드를 저장해 두고 다음부터 재사용 (봇 접속 전이라 플레이어 기록 없음)
if [ ! -d $CACHE ]; then
  N=$(grep -o '{build:[0-9]*}' ../pack/world/datapacks/pokeserver/data/poke/function/load.mcfunction | grep -o '[0-9]*')
  node rcon.js 25576 'tick sprint 12000' > /dev/null   # 짓는 동안 게임 시간을 빨리
  for i in $(seq 240); do s=$(node rcon.js 25576 'data get storage poke:state' 2>/dev/null || true); [[ $s =~ build:\ $N[,}] && $s =~ farm:\ 3 ]] && break; sleep 0.5; done
  node rcon.js 25576 'tick sprint stop' > /dev/null; node rcon.js 25576 save-off > /dev/null; node rcon.js 25576 'save-all flush' > /dev/null; sleep 1
  rm -rf .cache/world-* && mkdir -p $CACHE && cp -r $W/world/. $CACHE/ && rm -f $CACHE/session.lock
  node rcon.js 25576 save-on > /dev/null
  echo "> 지어 둔 월드 저장 ($KEY)"
fi
node datapack-test.js 2>&1 | grep -E '^>|FAIL|ALL PASS'
