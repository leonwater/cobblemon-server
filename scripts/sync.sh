#!/usr/bin/env bash
# 서버 PC에서 1분마다 실행(cron): 저장소 변경을 받아 서버에 반영
#   데이터팩만 바뀜 → /reload (접속 유지)
#   모드(pack/)·서버 설정(server/) 바뀜 → 서버 재시작
set -euo pipefail
cd "$(dirname "$0")/.."
git fetch -q origin main
changed=$(git diff --name-only HEAD origin/main)
[ -z "$changed" ] && exit 0
git merge -q --ff-only origin/main
cd server
if grep -qE '^(pack|server)/' <<<"$changed"; then
  docker compose up -d --force-recreate mc
elif grep -q '^datapacks/' <<<"$changed"; then
  docker compose exec -T mc rcon-cli reload
fi
