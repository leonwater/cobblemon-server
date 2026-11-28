#!/usr/bin/env bash
# 커밋 직전 검사: pack/ 파일을 고친 뒤 packwiz 목록(index.toml 해시)을 갱신했는지.
# 갱신이 필요했으면 갱신해 두고 실패로 끝남 → git add 후 다시 커밋 (2.6.0: 갱신을 빠뜨려 설치기가 "Hash invalid"로 멈춤)
set -euo pipefail
cd "$(dirname "$0")/../pack"
before=$(sha256sum index.toml pack.toml)
~/go/bin/packwiz refresh > /dev/null
[ "$before" = "$(sha256sum index.toml pack.toml)" ] && echo "pack OK" || { echo "FAIL pack 목록이 바뀌었음: git add pack 후 다시 커밋"; exit 1; }
