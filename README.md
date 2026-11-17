# pokeserver — Cobblemon 서버

Minecraft 1.21.1 · Fabric 0.20.1 · Cobblemon 1.8.4

## 폴더 구조

| 폴더 | 내용 | 바뀌면 |
|---|---|---|
| `pack/` | 모드 목록 (packwiz). 서버·클라이언트가 같이 씀 | 서버 재시작, 클라이언트는 다음 실행 때 자동 업데이트 |
| `datapacks/pokeserver/` | 튜토리얼 → 물자 지급, 포탈, 체육관 1인 제한 | `/reload`만 하면 됨 (접속 유지) |
| `server/` | Docker 서버 설정 | 서버 재시작 |
| `scripts/sync.sh` | 저장소 변경을 서버에 자동 반영 | — |
| `tests/` | 데이터팩 로직 테스트 (봇 2명) | — |

## 서버 켜기 (서버 PC)

필요: Docker, git. 저장소가 **public**이어야 `PACK_URL`(GitHub raw 주소)을 서버와 클라이언트가 읽을 수 있습니다.

```bash
cd server && cp .env.example .env   # PACK_URL, OPS 수정
docker compose up -d
```

자동 반영 (1분마다 확인): `crontab -e`에 추가

```
* * * * * /경로/cobblemon-server/scripts/sync.sh >> /tmp/pokeserver-sync.log 2>&1
```

## 클라이언트 (플레이하는 PC)

1. [Prism Launcher](https://prismlauncher.org/) 설치 → 새 인스턴스: Minecraft 1.21.1 + Fabric.
2. [packwiz-installer-bootstrap.jar](https://github.com/packwiz/packwiz-installer-bootstrap/releases)를 인스턴스의 `minecraft` 폴더에 넣기.
3. 인스턴스 설정 → 사용자 지정 명령 → 실행 전 명령:
   ```
   "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/leonwater/cobblemon-server/main/pack/pack.toml
   ```
4. 이제 실행할 때마다 모드가 서버와 자동으로 맞춰집니다.

## 맵에 연결하기 (명령 블록)

좌표는 **`datapacks/pokeserver/data/poke/function/config.mcfunction` 한 곳**에서 수정합니다.

| 용도 | 명령 블록 내용 (압력판과 함께) |
|---|---|
| 튜토리얼 끝 지점 | `execute as @p run function poke:tutorial/finish` |
| 바이옴 포탈 | `execute as @p run function poke:portal/go {to:"forest"}` |
| 체육관 입구 | `execute as @p run function poke:gym/enter {id:1}` |
| 체육관 출구 | `execute as @p run function poke:gym/leave` |

- 첫 접속 → 튜토리얼 위치로 이동. 끝 지점에서 기본 물자(`kit.mcfunction`) 1회 지급 → 허브로 이동.
- 체육관: 같은 번호의 체육관엔 한 명만. 도전자가 **나가기 / 로그아웃 / 사망**하면 자동으로 비워짐.
- 테스트용 초기화: `/function poke:admin/reset_me` → 튜토리얼부터 다시.

## 모드 추가

```bash
cd pack && packwiz modrinth add <모드 이름>
```

## 테스트

```bash
tests/run.sh
```
