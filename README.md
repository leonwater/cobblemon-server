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

### 0. 인스턴스 확인
[Prism Launcher](https://prismlauncher.org/)에서 인스턴스 **오른쪽 클릭 → Edit(편집) → Version(버전)**
- `Minecraft 1.21.1`과 `Fabric Loader`가 둘 다 있으면 통과
- Fabric이 없으면 오른쪽 **Install Fabric** 클릭

### 1. 파일 하나 받기
https://github.com/packwiz/packwiz-installer-bootstrap/releases → 최신 릴리스의 **`packwiz-installer-bootstrap.jar`**

### 2. 그 파일을 `minecraft` 폴더에 넣기
1. 인스턴스 **오른쪽 클릭 → Folder(폴더)** → 탐색기가 열림
2. 보이는 폴더들 중 **`minecraft`** 안으로 들어가기 (`.minecraft`일 수도 있음)
   - 없으면 게임을 한 번 실행했다 끄면 생김
3. 받은 파일을 **여기**에 넣기 (`instance.cfg`가 보이는 곳이 아니라 그 **안쪽** `minecraft` 폴더)
4. 파일 이름이 정확히 `packwiz-installer-bootstrap.jar`인지 확인
   - 두 번 받으면 `packwiz-installer-bootstrap (1).jar`처럼 바뀜 → 이름 고치기

### 3. 실행 전 명령 넣기
1. 인스턴스 **오른쪽 클릭 → Edit → Settings(설정)**
2. **Custom commands(사용자 지정 명령)** 체크
3. **Pre-launch command(실행 전 명령)** 칸에 아래 한 줄을 그대로 붙여넣기
   ```
   "$INST_JAVA" -jar "$INST_MC_DIR/packwiz-installer-bootstrap.jar" --bootstrap-main-jar "$INST_MC_DIR/packwiz-installer.jar" https://raw.githubusercontent.com/leonwater/cobblemon-server/main/pack/pack.toml
   ```
4. 창 닫기 (자동 저장)

### 4. 실행
1. 오른쪽 위 **Accounts(계정) → Add Microsoft**로 로그인 (처음 한 번)
2. 인스턴스 더블클릭 → 작은 다운로드 창이 잠깐 뜬 뒤 게임이 켜짐
3. 타이틀 화면 **Mods**에 **Cobblemon**이 있으면 성공
4. 이후엔 실행할 때마다 서버와 모드가 자동으로 맞춰짐

### 5. 서버 접속
서버(`start.bat`)를 켜둔 상태에서 **멀티플레이 → 서버 추가 → 주소 `localhost`**

### 막힐 때

| 증상 | 해결 |
|---|---|
| `Unable to access jarfile packwiz-installer-bootstrap.jar` | 파일이 `minecraft` 폴더 안에 없거나 이름이 다름 → 2단계 다시 확인. 3단계 명령이 위와 똑같은지 확인 |
| 게임이 느리거나 꺼짐 | Edit → Settings → Java → 최대 메모리 4096MB 정도로 |
| Java 오류 | 같은 Java 화면에서 Java 21 자동 감지/다운로드 |
| 인스턴스에 `world/datapacks` 폴더가 생김 | 서버용 파일이라 게임엔 영향 없음 |

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
