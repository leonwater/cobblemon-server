#!/usr/bin/env bash
# 검증용 스크린샷: 모드 서버(Cobblemon 포함) + 실제 클라이언트를 띄워 장면별로 찍음
# 사용: tools/shots.sh <단계 파일> <저장 폴더>
#   단계 파일 한 줄씩:  rcon <명령>  |  wait <밀리초>  |  shot <이름>  |  xdo <xdotool 인자> (클릭·키 입력)
set -uo pipefail
R=$(cd "$(dirname "$0")/.." && pwd); STEPS=$1; OUT=$2; W=${SHOTS_WORK:-/tmp/pokeserver-shots}
mkdir -p "$OUT" $W/srv/mods $W/srv/config
S=$W/srv
# 서버: Fabric + 팩의 서버용 모드 + 우리 모드 + 데이터팩·설정 (새 월드)
if [ ! -f $S/fabric-server-launch.jar ]; then
  curl -sfL -o $S/server.jar "$(curl -s "$(curl -s https://piston-meta.mojang.com/mc/game/version_manifest_v2.json | python3 -c 'import json,sys;print([v["url"] for v in json.load(sys.stdin)["versions"] if v["id"]=="1.21.1"][0])')" | python3 -c 'import json,sys;print(json.load(sys.stdin)["downloads"]["server"]["url"])')"
  v=$(curl -s https://meta.fabricmc.net/v2/versions/installer | python3 -c 'import json,sys;print(json.load(sys.stdin)[0]["version"])')
  curl -sfL -o $S/installer.jar https://maven.fabricmc.net/net/fabricmc/fabric-installer/$v/fabric-installer-$v.jar
  (cd $S && java -jar installer.jar server -mcversion 1.21.1 -loader 0.20.1 > /dev/null)
fi
for f in $R/pack/mods/*.pw.toml; do
  grep -q '^side = "client"' $f && continue
  n=$(grep '^filename' $f | cut -d'"' -f2); [ -f "$S/mods/$n" ] || curl -sfL -o "$S/mods/$n" "$(grep '^url' $f | cut -d'"' -f2)"
done
rm -f $S/mods/pokeserver-*.jar; cp $R/pack/mods/pokeserver-*.jar $S/mods/
cp -r $R/pack/config/. $S/config/
rm -rf $S/world && mkdir -p $S/world/datapacks && cp -r $R/pack/world/datapacks/* $S/world/datapacks/
echo eula=true > $S/eula.txt
printf 'online-mode=false\nenable-rcon=true\nrcon.password=test\nrcon.port=25575\nspawn-protection=0\n' > $S/server.properties
(cd $S && java -Xmx4G -jar fabric-server-launch.jar nogui > run.log 2>&1 &)
timeout 240 bash -c "until grep -qE 'Done \(|Exception in thread' $S/run.log; do sleep 1; done" || { echo "FAIL server boot"; exit 1; }
# 클라이언트 (화면 :99)
Xvfb :99 -screen 0 1280x720x24 > /dev/null 2>&1 &
XV=$!
sleep 2
DISPLAY=:99 python3 $R/tools/prod_client.py $W/client localhost:25565 > $W/client.log 2>&1 &
CL=$!
timeout 300 bash -c "until grep -q 'Dev joined the game' $S/run.log; do sleep 2; done" || { echo "FAIL client join"; tail -5 $W/client.log; kill $CL $XV; exit 1; }
sleep 8
node -e '
const {Rcon}=require("'$R'/tests/node_modules/rcon-client");const {execSync}=require("child_process");const fs=require("fs");
(async()=>{const r=await Rcon.connect({host:"localhost",port:25575,password:"test",timeout:20000});
for (const line of fs.readFileSync(process.argv[1],"utf8").split("\n")) {
  const [k,...rest]=line.trim().split(" "); const a=rest.join(" ");
  if (k==="rcon") console.log(">",a,"→",(await r.send(a)).slice(0,160));
  else if (k==="wait") await new Promise(s=>setTimeout(s,+a));
  else if (k==="xdo") { execSync(`DISPLAY=:99 xdotool ${a}`); console.log("xdo",a) }
  else if (k==="xdo2") { execSync(`DISPLAY=:100 xdotool ${a}`); console.log("xdo2",a) }
  else if (k==="shot2") { execSync(`import -display :100 -window root ${process.argv[2]}/${a}.png`); console.log("shot2",a) }
  else if (k==="player2") { execSync(`(Xvfb :100 -screen 0 1280x720x24 >/dev/null 2>&1 &); sleep 2; (DISPLAY=:100 python3 '$R'/tools/prod_client.py '$W'/client localhost:25565 ${a} > '$W'/client2.log 2>&1 &)`); console.log("player2",a) }
  else if (k==="shot") { execSync(`import -display :99 -window root ${process.argv[2]}/${a}.png`); console.log("shot",a) }
}
await r.send("stop"); r.end()})().catch(e=>{console.error("FAIL",e.message);process.exit(1)})' "$STEPS" "$OUT"
kill $CL $XV 2>/dev/null; pkill -f -- "--username [^D]" ; pkill -f "Xvfb :100"; sleep 3; kill -9 $CL 2>/dev/null; true
# 서버가 stop 후 30초 안에 안 꺼지면 HANG 기록 후 강제 종료
for i in $(seq 30); do pgrep -f fabric-server-launch.jar >/dev/null || exit 0; sleep 1; done
echo "HANG server did not exit after stop"; pkill -9 -f fabric-server-launch.jar; true
