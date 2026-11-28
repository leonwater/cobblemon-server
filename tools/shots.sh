#!/usr/bin/env bash
# 검증용 스크린샷: 모드 서버(Cobblemon 포함) + 실제 클라이언트를 띄워 장면별로 찍음
# 사용: tools/shots.sh <단계 파일> <저장 폴더>
#   KEEP=1 이면 끝난 뒤에도 켜 둔 채 $W/queue/*.txt 를 받아 이어서 실행 (결과 로그는 같은 이름 .out)
#   단계 파일 한 줄씩:  rcon <명령>  |  wait <밀리초>  |  until <명령> ~ <정규식> ~ <최대 ms> (조건이 맞을 때까지 대기)  |  shot <이름>  |  xdo <xdotool 인자>
set -uo pipefail
R=$(cd "$(dirname "$0")/.." && pwd); STEPS=$1; OUT=$2; W=${SHOTS_WORK:-/tmp/pokeserver-shots}
PW=${PACKWIZ_JARS:-$W/packwiz}   # PROD=1: packwiz-installer-bootstrap.jar(bootstrap.jar)·packwiz-installer.jar 가 있는 곳
mkdir -p "$OUT" $W/srv/mods $W/srv/config
S=$W/srv
# 서버: Fabric + 팩의 서버용 모드 + 우리 모드 + 데이터팩·설정 (새 월드)
if [ ! -f $S/fabric-server-launch.jar ]; then
  curl -sfL -o $S/server.jar "$(curl -s "$(curl -s https://piston-meta.mojang.com/mc/game/version_manifest_v2.json | python3 -c 'import json,sys;print([v["url"] for v in json.load(sys.stdin)["versions"] if v["id"]=="1.21.1"][0])')" | python3 -c 'import json,sys;print(json.load(sys.stdin)["downloads"]["server"]["url"])')"
  v=$(curl -s https://meta.fabricmc.net/v2/versions/installer | python3 -c 'import json,sys;print(json.load(sys.stdin)[0]["version"])')
  curl -sfL -o $S/installer.jar https://maven.fabricmc.net/net/fabricmc/fabric-installer/$v/fabric-installer-$v.jar
  (cd $S && java -jar installer.jar server -mcversion 1.21.1 -loader 0.20.1 > /dev/null)
fi
if [ "${PROD:-}" = 1 ]; then
  # 실제 배포와 똑같이: GitHub main의 모드팩을 packwiz 설치기로 받음 (start.bat과 같은 명령)
  PACK=https://raw.githubusercontent.com/leonwater/cobblemon-server/main/pack/pack.toml
  rm -rf $S/mods $S/config $S/world $S/packwiz.json && mkdir -p $S/mods
  cp $PW/bootstrap.jar $PW/packwiz-installer.jar $S/
  (cd $S && java -jar bootstrap.jar -g -s server $PACK > pw.log 2>&1) || { echo "FAIL packwiz server"; tail -5 $S/pw.log; exit 1; }
else
for f in $R/pack/mods/*.pw.toml; do
  grep -q '^side = "client"' $f && continue
  n=$(grep '^filename' $f | cut -d'"' -f2); [ -f "$S/mods/$n" ] || curl -sfL -o "$S/mods/$n" "$(grep '^url' $f | cut -d'"' -f2)"
done
rm -f $S/mods/pokeserver-*.jar; cp $R/pack/mods/pokeserver-*.jar $S/mods/
cp -r $R/pack/config/. $S/config/
rm -rf $S/world && mkdir -p $S/world/datapacks && cp -r $R/pack/world/datapacks/* $S/world/datapacks/
fi
# 월드는 한 번만 짓고 계속 재사용: 지어 둔 월드에 지금 데이터팩만 덮어씀.
# 바뀐 부분은 월드 안 버전 표시가 알아서 다시 지음 (load.mcfunction {build:N} → 마을·경기장, Plaza.BUILD_VERSION → 광장). 모드 jar만 바뀌면 다시 짓지 않음.
# FRESH=1 이면 지어 둔 월드를 버리고 새로 지음 (지형·사전 생성 쪽을 바꿨을 때)
CACHE=$W/cache/world; [ "${FRESH:-}" = 1 ] && rm -rf $W/cache
if [ -d $CACHE ]; then
  rm -rf $W/dp.tmp && mv $S/world/datapacks $W/dp.tmp && rm -rf $S/world && cp -r $CACHE $S/world && rm -rf $S/world/datapacks && mv $W/dp.tmp $S/world/datapacks
  echo "지어 둔 월드 재사용 (데이터팩만 새로)"
fi
rc() { node -e 'require("'$R'/tests/node_modules/rcon-client").Rcon.connect({host:"localhost",port:25575,password:"test"}).then(async r=>{console.log(await r.send(process.argv[1]));r.end()})' "$1"; }
echo eula=true > $S/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25575\nspawn-protection=0\n' > $S/server.properties
(cd $S && java -Xmx4G ${SERVER_JAVA_OPTS:-} -jar fabric-server-launch.jar nogui > run.log 2>&1 &)
timeout 240 bash -c "until grep -qE 'Done \(|Exception in thread' $S/run.log; do sleep 1; done" || { echo "FAIL server boot"; exit 1; }
# 짓기(처음이면 사전 생성까지)가 끝나길 기다렸다가 월드 저장 (클라이언트 접속 전이라 플레이어 기록 없음). 이미 지어진 버전이면 바로 지나감
N=$(grep -o '{build:[0-9]*}' $S/world/datapacks/pokeserver/data/poke/function/load.mcfunction | grep -o '[0-9]*')
FRESHW=$([ -d $CACHE ] || echo 1)
rc 'tick sprint 24000' > /dev/null   # 짓기·지형 다듬기 동안 게임 시간을 빨리
PV=$(grep -o 'BUILD_VERSION = [0-9]*' $R/mod/src/main/java/com/pokeserver/Plaza.java | grep -o '[0-9]*$')   # 광장도 다 지어진 뒤 저장 (안 그러면 세션마다 광장을 다시 지음)
for i in $(seq 200); do rc 'data get storage poke:state' | grep -q "build: $N[,}]" && rc 'data get storage poke:state plaza' | grep -q "built: $PV[,}]" && { [ -z "$FRESHW" ] || grep -q 'Chunky\] Task finished' $S/run.log; } && break; sleep 3; done
rc 'tick sprint stop' > /dev/null; rc save-off > /dev/null; rc 'save-all flush' > /dev/null; sleep 2
rm -rf $CACHE.new && cp -r $S/world $CACHE.new && rm -f $CACHE.new/session.lock && rm -rf $CACHE && mv $CACHE.new $CACHE
rc save-on > /dev/null; echo "월드 저장 (build $N)"
# 클라이언트 (화면 :99)
Xvfb :99 -screen 0 ${WIN:-1280x720}x24 > /dev/null 2>&1 &
XV=$!
sleep 2
if [ "${PROD:-}" = 1 ]; then
  G=$W/client/game-prod; rm -rf $G; mkdir -p $G; cp $PW/bootstrap.jar $PW/packwiz-installer.jar $G/
  (cd $G && java -jar bootstrap.jar -g -s client $PACK > pw.log 2>&1) || { echo "FAIL packwiz client"; tail -5 $G/pw.log; exit 1; }
  export PROD_GAME=$G
fi
start_client() {
  local n=$(grep -c 'Dev joined the game' $S/run.log)
  DISPLAY=:99 python3 $R/tools/prod_client.py $W/client localhost:25565 > $W/client.log 2>&1 &
  CL=$!
  timeout 300 bash -c "until [ \$(grep -c 'Dev joined the game' $S/run.log) -gt $n ]; do sleep 2; done" || { echo "FAIL client join"; tail -5 $W/client.log; kill $CL $XV; exit 1; }
}
stop_client() { kill $CL 2>/dev/null; pkill -f -- "--username Dev"; sleep 3; pkill -9 -f -- "--username Dev"; true; }
start_client
sleep 8
cat > $W/steps.js <<'JS'
const {Rcon}=require(process.env.R+"/tests/node_modules/rcon-client");const {execSync}=require("child_process");const fs=require("fs");
(async()=>{const r=await Rcon.connect({host:"localhost",port:25575,password:"test",timeout:20000});
for (const line of fs.readFileSync(process.argv[2],"utf8").split("\n")) {
  const [k,...rest]=line.trim().split(" "); const a=rest.join(" ");
  if (k==="rcon") console.log(">",a,"→",(await r.send(a)).slice(0,1500));
  else if (k==="until") { const [cmd,re,ms]=a.split(" ~ "); const t0=Date.now(); let o="";
    while (Date.now()-t0 < (+ms||60000)) { o=await r.send(cmd); if (new RegExp(re).test(o)) break; await new Promise(s=>setTimeout(s,500)) }
    console.log("until",cmd,"→",o.slice(0,120),((Date.now()-t0)/1000).toFixed(1)+"s") }
  else if (k==="wait") await new Promise(s=>setTimeout(s,+a));
  else if (k==="xdo") { execSync(`DISPLAY=:99 xdotool ${a}`); console.log("xdo",a) }
  else if (k==="xdo2") { execSync(`DISPLAY=:100 xdotool ${a}`); console.log("xdo2",a) }
  else if (k==="shot2") { execSync(`import -display :100 -window root ${process.argv[3]}/${a}.png`); console.log("shot2",a) }
  else if (k==="player2") { execSync(`(Xvfb :100 -screen 0 1280x720x24 >/dev/null 2>&1 &); sleep 2; (DISPLAY=:100 python3 ${process.env.R}/tools/prod_client.py ${process.env.W}/client localhost:25565 ${a} > ${process.env.W}/client2.log 2>&1 &)`); console.log("player2",a) }
  else if (k==="shot") { execSync(`import -display :99 -window root ${process.argv[3]}/${a}.png`); console.log("shot",a) }
}
r.end()})().catch(e=>{console.error("FAIL",e.message);process.exit(1)})
JS
run_steps() { R=$R W=$W node $W/steps.js "$1" "$OUT"; }
run_steps "$STEPS"
# KEEP=1: 서버·게임을 켠 채로 $W/queue/*.txt 단계 파일을 기다려 이어서 실행 (다시 찍을 때 껐다 켜지 않게). $W/queue/stop 을 만들면 종료
if [ "${KEEP:-}" = 1 ]; then
  mkdir -p $W/queue; echo "대기 중: $W/queue/*.txt (끝내려면 touch $W/queue/stop)"
  # 모드만 바꿨을 때 다시 켜기 (월드·서버 그대로): touch $W/queue/client → 새 jar로 게임만 다시 / touch $W/queue/server → 서버도 같은 월드로 다시
  while [ ! -f $W/queue/stop ]; do
    if [ -f $W/queue/server ]; then rm -f $W/queue/server; stop_client; rc stop > /dev/null
      for i in $(seq 60); do pgrep -f fabric-server-launch.jar >/dev/null || break; sleep 1; done
      rm -f $S/mods/pokeserver-*.jar; cp $R/pack/mods/pokeserver-*.jar $S/mods/; rm -rf $S/world/datapacks && cp -r $R/pack/world/datapacks $S/world/
      (cd $S && java -Xmx4G ${SERVER_JAVA_OPTS:-} -jar fabric-server-launch.jar nogui > run.log 2>&1 &)
      timeout 240 bash -c "until grep -qE 'Done \(|Exception in thread' $S/run.log; do sleep 1; done"; start_client; echo "서버·게임 다시 켬"; fi
    if [ -f $W/queue/client ]; then rm -f $W/queue/client; stop_client; start_client; echo "게임만 다시 켬"; fi
    for f in $W/queue/*.txt; do [ -f "$f" ] || continue; mv "$f" "$f.run"; run_steps "$f.run" > "$f.out" 2>&1; mv "$f.run" "$f.done"; done; sleep 2
  done
  rm -rf $W/queue
fi
rc stop > /dev/null
kill $CL $XV 2>/dev/null; pkill -f -- "--username [^D]" ; pkill -f "Xvfb :100"; sleep 3; kill -9 $CL 2>/dev/null; true
# 서버가 stop 후 30초 안에 안 꺼지면 HANG 기록 후 강제 종료
for i in $(seq 30); do pgrep -f fabric-server-launch.jar >/dev/null || exit 0; sleep 1; done
echo "HANG server did not exit after stop"; pkill -9 -f fabric-server-launch.jar; true
