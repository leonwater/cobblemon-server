# pokeserver — Cobblemon 서버

Minecraft 1.21.1 · Fabric 0.20.1 · Cobblemon 1.8.4

## 폴더 구조

| 폴더 | 내용 |
|---|---|
| `pack/` | 모드 목록 + 데이터팩 (packwiz). 서버·클라이언트가 실행할 때 여기서 자동으로 받아감 |
| `pack/world/datapacks/pokeserver/` | 튜토리얼 → 물자 지급, 포탈, 체육관 1인 제한 |
| `server/` | 서버 실행 파일 (`start.bat`, `update.bat`) |
| `tests/` | 데이터팩 로직 테스트 (봇 2명) |

## 서버 켜기 (Windows, 설치 없이 폴더 하나로)

Docker·설치 프로그램 없이 **폴더 하나**로 돌아갑니다. 지우고 싶으면 폴더만 삭제하면 끝.

### 1. 폴더 만들기
`C:\pokeserver` 처럼 **한글·공백 없는 경로**로 만듭니다.

### 2. 파일 4개 넣기

| 파일 | 받는 곳 | 고를 것 |
|---|---|---|
| Java 21 (설치 안 하는 zip) | https://adoptium.net/temurin/releases/?os=windows&arch=x64&package=jdk&version=21 | **.zip** (`.msi` 아님) → 압축 풀어서 `jdk-21...` 폴더째로 넣기 |
| Fabric 서버 | https://fabricmc.net/use/server/ | Minecraft **1.21.1**, Loader **0.20.1** → Executable Server (.jar) |
| packwiz-installer-bootstrap.jar | https://github.com/packwiz/packwiz-installer-bootstrap/releases | 최신 릴리스의 `packwiz-installer-bootstrap.jar` |
| start.bat, update.bat | https://github.com/leonwater/cobblemon-server/tree/main/server | 파일 클릭 → 오른쪽 위 다운로드 버튼(Download raw file) |

다 넣으면 이렇게 됩니다:

```
C:\pokeserver\
  jdk-21.0.x+y\            ← Java (폴더째)
  fabric-server-mc.1.21.1-loader.0.20.1-launcher....jar
  packwiz-installer-bootstrap.jar
  start.bat
  update.bat
```

### 3. 처음 실행
1. `start.bat` 더블클릭 → 모드·데이터팩을 받은 뒤 서버가 켜지다가 **EULA 안내와 함께 멈춥니다** (정상).
2. 폴더에 생긴 `eula.txt`를 메모장으로 열어 `eula=false` → `eula=true`로 저장
   ([Minecraft EULA](https://aka.ms/MinecraftEULA)에 동의한다는 뜻입니다).
3. `start.bat` 다시 더블클릭 → `Done (...)! For help, type "help"`가 나오면 켜진 것.
4. **Windows 방화벽 창이 뜨면 "취소"** — 혼자 테스트할 땐 필요 없습니다.
5. 서버 창에 `op 내닉네임` 입력 → 관리자 권한.

### 4. 접속
마인크래프트(아래 클라이언트 설정) → 멀티플레이 → 서버 주소 `localhost`

### 5. 끄기
서버 창에 `stop` 입력. (창을 X로 닫으면 월드 저장이 덜 될 수 있음)

## 수정사항 반영

| 바뀐 것 | 할 일 |
|---|---|
| 데이터팩 (튜토리얼·체육관·포탈 등) | `update.bat` 더블클릭 → 서버 창에 `reload` (접속 유지) |
| 모드 | 서버 창에 `stop` → `start.bat` 더블클릭 |

## 클라이언트 (플레이하는 PC)

1. [Prism Launcher](https://prismlauncher.org/) 설치 → 새 인스턴스: Minecraft 1.21.1 + Fabric.
2. `packwiz-installer-bootstrap.jar`를 인스턴스의 `minecraft` 폴더에 넣기.
3. 인스턴스 설정 → 사용자 지정 명령 → 실행 전 명령:
   ```
   "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/leonwater/cobblemon-server/main/pack/pack.toml
   ```
4. 실행할 때마다 모드가 서버와 자동으로 맞춰집니다.
   (인스턴스에 `world/datapacks` 폴더도 생기는데, 게임에 영향 없습니다.)

## 맵에 연결하기 (명령 블록)

좌표는 **`pack/world/datapacks/pokeserver/data/poke/function/config.mcfunction` 한 곳**에서 수정합니다.

| 용도 | 명령 블록 내용 (압력판과 함께) |
|---|---|
| 튜토리얼 끝 지점 | `execute as @p run function poke:tutorial/finish` |
| 바이옴 포탈 | `execute as @p run function poke:portal/go {to:"forest"}` |
| 체육관 입구 | `execute as @p run function poke:gym/enter {id:1}` |
| 체육관 출구 | `execute as @p run function poke:gym/leave` |

- 첫 접속 → 튜토리얼 위치로 이동. 끝 지점에서 기본 물자(`kit.mcfunction`) 1회 지급 → 허브로 이동.
- 체육관: 같은 번호의 체육관엔 한 명만. 도전자가 **나가기 / 로그아웃 / 사망**하면 자동으로 비워짐.
- 테스트용 초기화: `/function poke:admin/reset_me` → 튜토리얼부터 다시.

## 친구 초대 (나중에)

`start.bat`이 처음 만드는 `server.properties`에 `server-ip=127.0.0.1`이 들어 있어 **이 PC에서만** 접속됩니다.
공유기 포트포워딩은 집 IP가 노출되므로 권장하지 않습니다. 친구를 부를 때 안전한 방법을 따로 정합니다.

## 모드 추가 (관리용)

```bash
cd pack && packwiz modrinth add <모드 이름> && packwiz refresh
```

## 테스트

```bash
tests/run.sh
```
