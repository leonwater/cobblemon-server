#!/usr/bin/env bash
# 모드를 빌드해 모드팩(pack/mods)에 넣음 → 서버·클라이언트가 다음 실행 때 자동으로 받음
set -euo pipefail
cd "$(dirname "$0")"
f=../pack/mods/cobblemon.pw.toml; mkdir -p libs
[ -f "libs/$(grep '^filename' $f | cut -d'"' -f2)" ] || curl -sfL -o "libs/$(grep '^filename' $f | cut -d'"' -f2)" "$(grep '^url' $f | cut -d'"' -f2)"
gradle build --no-daemon -q --max-workers=1
rm -f ../pack/mods/pokeserver-*.jar
cp build/libs/pokeserver-$(grep ^mod_version gradle.properties | cut -d= -f2).jar ../pack/mods/   # 버전이 바뀌면 예전 jar가 build/libs에 남아 있어 지금 버전만
cd ../pack && PATH=$PATH:~/go/bin packwiz refresh
