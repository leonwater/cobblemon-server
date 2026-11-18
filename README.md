# pokeserver — Cobblemon 서버

Minecraft 1.21.1 · Fabric 0.20.1 · Cobblemon 1.8.4

## 폴더 구조

| 폴더 | 내용 |
|---|---|
| `pack/` | 모드 목록 + 데이터팩 (packwiz). 서버·클라이언트가 실행할 때 여기서 자동으로 받아감 |
| `pack/world/datapacks/pokeserver/` | 튜토리얼·마을·NPC, 서버 규칙, 워프, 체육관 1인 제한 |
| `pack/config/` | 모드 설정 (상점 목록, 농장 땅, 메뉴 공지, 폭발 방지, 포켓몬 스폰 차원) |
| `mod/` | 전용 모드 (땅·상점·메뉴·배틀 제한·NPC 스킨·어두운 UI). 수정 후 `mod/install.sh` → 모드팩에 반영 |
| `tools/` | 마을·농장 생성기 `build_world.py`, NPC 스킨 `make_skins.py`, UI 색 `make_ui.py`, 야생 스폰 계산 `spawn_levels.py`, 실제 화면 확인 `shots.sh` |
| `server/` | 서버 실행 파일 (`start.bat`, `update.bat`) |
| `tests/` | 자동 테스트: 데이터팩(`run.sh`), 모드(`mod-test.sh`) |

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
| `Unable to access jarfile ...` | 탐색기 주소창에 `%APPDATA%\PrismLauncher\instances\인스턴스이름\minecraft` → **보기 → 파일 확장명** 켜고 확인: `.jar.jar`·`(1)` 붙었으면 이름 고치기 / `.crdownload`거나 없으면 브라우저 `Ctrl+J`에서 **유지** 후 다시 넣기 / 한 칸 위 폴더에 있으면 `minecraft` 안으로 옮기기 |
| 게임이 느리거나 꺼짐 | Edit → Settings → Java → 최대 메모리 4096MB 정도로 |
| Java 오류 | 같은 Java 화면에서 Java 21 자동 감지/다운로드 |
| 인스턴스에 `world/datapacks` 폴더가 생김 | 서버용 파일이라 게임엔 영향 없음 |

## 게임 흐름

1. 첫 접속 → **튜토리얼 방**. 3칸 앞 **안내원 하늘** 우클릭 → 코블몬·서버 기초 안내
2. "준비 완료!" → **회의장**. 기본 물품(5,000원·러닝 슈즈·몬스터볼 10개)은 **처음 한 번만**
3. **마을** (평지, 블록 파괴 불가): 회의장 → 분수 광장 → 북쪽 **상점가**(프렌들리 숍·포켓몬센터) / 동쪽 길 끝 **체육관**
4. **G 키 메인 메뉴 → 워프**: 회의장·상점가·체육관은 항상 같은 자리, 농장·야생은 **마지막으로 있던 곳**. `/trigger home` → 회의장
5. **야생**: 끝없는 맵, 모든 바이옴이 256×256 칸으로 같은 넓이씩 반복. 첫 방문은 **모두 같은 자리**(포켓몬 평균 레벨이 가장 낮은 꽃 숲)
6. **포켓몬은 야생에서만** 자연 스폰. 야생·플레이어 배틀도 야생에서만 (NPC·체육관 배틀은 어디서나)
7. **농장**: 상점에서 산 **땅 문서**로 빈 땅 우클릭 → 확인 → 내 땅. 남의 땅을 건드리면 체력바 위에 "OO님의 땅" 알림

화폐: `/money`(`/돈`) 잔액, `/pay 닉네임 금액`(`/송금`) 보내기

서버 규칙: 포켓몬 외 몬스터·동물 없음 · 배고픔 없음 · 죽어도 아이템 유지 · 폭발로 블록 안 부서짐

## 수정하는 곳

| 바꿀 것 | 방법 |
|---|---|
| 마을·건물·농장 모양과 위치 | `tools/build_world.py` 수정 → 실행 → `load.mcfunction`의 `build:4`(농장은 `farm:2`) 숫자 +1 |
| 워프 도착 위치, 체육관 | `pack/world/datapacks/pokeserver/data/poke/function/config.mcfunction` |
| 기본 물품 | `.../function/kit.mcfunction`(러닝 슈즈), `.../function/mod/kit.mcfunction`(돈·몬스터볼) |
| 안내원·간호사 대화 | `.../data/poke/dialogues/tutorial.json`, `nurse.json` |
| 상점 분류·상품·가격 | `pack/config/pokeserver/shop.json` (`buy`/`sell`이 0이면 그 탭에 안 나옴). 실행 중엔 `/pokeserver reload` |
| 메인 메뉴 공지사항 | `pack/config/pokeserver/menu.json` |
| 포켓몬 스폰 금지 차원 | `pack/config/cobblemon/main.json`의 `worldSpawningBlocklist` |

## NPC

NPC는 Cobblemon NPC 하나로 통일합니다 (대화·회복·배틀 파티를 모두 지원). 사람 크기 모델에 기본 스킨이 입혀져 있고, 게임 안에서 바꿀 수 있습니다.

| 하고 싶은 것 | 방법 (관리자) |
|---|---|
| NPC 스킨을 다른 플레이어 스킨으로 | `/pokeserver npc skin poke.nurse 플레이어이름` (태그: `poke.tutor`·`poke.nurse`·`poke.merchant`) |
| 스킨 이미지 주소로 | `/pokeserver npc skin poke.nurse https://.../skin.png` |
| 기본 스킨으로 되돌리기 | `/pokeserver npc skin poke.nurse reset` |
| 이름·파티 등 세부 편집 | NPC를 바라보고 `/npcedit` (Cobblemon 편집기) |

바꾼 스킨은 월드에 저장되어 마을을 다시 지어도 유지됩니다. 기본 스킨 그림은 `tools/make_skins.py`.

## 체육관 (명령 블록)

| 용도 | 명령 블록 내용 (압력판과 함께) |
|---|---|
| 체육관 입구 | `execute as @p run function poke:gym/enter {id:1}` |
| 체육관 출구 | `execute as @p run function poke:gym/leave` |

- 같은 번호의 체육관엔 한 명만. 도전자가 **나가기 / 로그아웃 / 사망**하면 자동으로 비워짐.
- 관리자: `/pokeserver money give|take|set <플레이어> <금액>`, `/pokeserver deed <플레이어>` 땅 문서, `/pokeserver unclaim <번호>` 땅 주인 해제, `/pokeserver reload` 설정 다시 읽기
- 관리자: `/function poke:admin/reset_me` 내 진행 초기화(튜토리얼부터, 보상은 다시 안 줌), `/function poke:admin/rebuild` 마을·NPC 다시 짓기

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

```bash
tests/mod-test.sh
```
