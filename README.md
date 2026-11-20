# pokeserver — Cobblemon 서버

Minecraft 1.21.1 · Fabric 0.20.1 · Cobblemon 1.8.4

문서: [작업 규칙](docs/작업규칙.md) · [서버 안내](docs/서버안내.md) · [UI 정리](docs/UI정리.md) · [명령어](docs/명령어.md) · [서버 여는 법](docs/서버_여는법.md)

## 폴더 구조

| 폴더 | 내용 |
|---|---|
| `pack/` | 모드 목록 + 데이터팩 (packwiz). 서버·클라이언트가 실행할 때 여기서 자동으로 받아감 |
| `pack/world/datapacks/pokeserver/` | 튜토리얼·마을·NPC, 서버 규칙, 워프, 체육관 1인 제한 |
| `pack/config/` | 모드 설정 (상점 목록, 농장 땅, 메뉴 공지, 폭발 방지, 포켓몬 스폰 차원) |
| `mod/` | 전용 모드 (땅·상점·메뉴·배틀 제한·NPC 스킨·어두운 UI). 수정 후 `mod/install.sh` → 모드팩에 반영 |
| `tools/` | 마을·농장 생성기 `build_world.py`, 체육관 리그 `build_league.py`, NPC 스킨 `make_skins.py`, UI 색 `make_ui.py`, 야생 스폰 계산 `spawn_levels.py`, 실제 화면 확인 `shots.sh` |
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

### 셰이더
모드팩에 **Iris + Sodium + Complementary Reimagined 셰이더**가 들어 있어 처음 실행하면 켜진 상태입니다 (그림자·하늘·물 효과).
- **K 키**: 셰이더 켜기/끄기 · 무거우면 `비디오 설정 → 셰이더 팩`에서 끄거나 다른 팩 선택 (한 번 바꾼 설정은 업데이트해도 유지)

### 막힐 때

| 증상 | 해결 |
|---|---|
| `Unable to access jarfile ...` | 탐색기 주소창에 `%APPDATA%\PrismLauncher\instances\인스턴스이름\minecraft` → **보기 → 파일 확장명** 켜고 확인: `.jar.jar`·`(1)` 붙었으면 이름 고치기 / `.crdownload`거나 없으면 브라우저 `Ctrl+J`에서 **유지** 후 다시 넣기 / 한 칸 위 폴더에 있으면 `minecraft` 안으로 옮기기 |
| 게임이 느리거나 꺼짐 | Edit → Settings → Java → 최대 메모리 4096MB 정도로 |
| Java 오류 | 같은 Java 화면에서 Java 21 자동 감지/다운로드 |
| 인스턴스에 `world/datapacks` 폴더가 생김 | 서버용 파일이라 게임엔 영향 없음 |

## 게임 흐름

1. 첫 접속 → **오박사 연구소**(튜토리얼 방). **오박사** 우클릭 → 실제 게임 화면 사진이 든 설명 11쪽(←/→, 도감 사용법, 마지막 쪽 **닉네임 입력**). **준비 완료!** → 보상 + **스타팅 포켓몬 고르기**(1~9세대 중 무작위 한 세대의 3마리, 피카츄·이브이 없음). 창을 닫았으면 G 메뉴 → 내 파티로 다시 열림. 사진은 `mod/src/main/resources/assets/pokeserver/textures/gui/tutorial/`
2. 기본 물품(5,000원·러닝 슈즈·몬스터볼 10개·**농장 땅 문서 1장**·**포켓몬 도감**)은 **처음 한 번만**. 튜토리얼을 끝내면 **바로 광장 마을**로 이동, 2초 뒤 스타팅 고르기 창. 닉네임은 첫 튜토리얼에서만 정함 (다시 하면 보여 주기만)
3. **광장 마을은 야생 안**(첫 스폰 자리, 꽃 숲). 서버를 처음 켤 때 모드(`Plaza.java`)가 꽃 숲 칸 중 땅이 넓고 평평한 곳을 노이즈 높이로 골라 반지름 72칸을 고르고(둘레 28칸은 자연 지형과 완만하게 이음), 데이터팩 `build/plaza/*`(생성기 `tools/plaza.py`, 광장 기준 상대 좌표)가 지음
   - 가운데 분수 + 몬스터볼 조형물, 동쪽 **포켓몬센터**·서쪽 **프렌들리 숍**(원작풍 흰 벽·계단 지붕·대형 몬스터볼 간판), **포켓몬 상식 건물 6채**(식당풍·청록 지붕 집·이끼 지붕 집·**따라큐 모양**·체육관풍) — 안의 NPC 우클릭 → 설명(`tools/tips.py`). 굽은 흙길, 나무·꽃·연못·밭·바위·가로등
   - 반지름 72칸: 블록 수정 금지·포켓몬 스폰 금지. 그 밖 200칸까지 저레벨(≤15). 둘레 벽 없음
   - **체육관**(따로 떨어진 섬, `poke:town`): 넓은 계단 위 흰 벽·파란 창 띠·빨강 흰 기둥·겹친 황토색 지붕·노란 차양 건물. 경기장은 타입마다 팔레트·바닥 상징·관중석. 예전 회의장·상점가 섬은 지워짐
4. **G 키 메인 메뉴** (왼쪽 분류 포켓몬[내 파티·PC·도감] · 간편 메뉴[튜토리얼·칭호·기본 명령어·휴지통] · 워프[야생·광장·농장·체육관], 왼쪽 아래 작은 버튼 명령어·휴지통, 오른쪽 내 정보 카드[잡은/마주친 포켓몬·잔액·배지·레벨 제한]·공지사항). **튜토리얼을 끝내기 전엔 워프·`/광장` 잠금**. 워프: 광장·체육관은 항상 같은 자리, 농장·야생은 **마지막으로 있던 곳**
5. **야생** (서버를 처음 켜면 ① 광장 지형 다듬기(틱마다 15ms만) → ② 광장 건물 → ③ Chunky로 첫 스폰 둘레 미리 만들기 순서로 하나씩 해서 느린 PC에서도 멈추지 않음. 처음 몇 분은 조금 느릴 수 있음): 끝없는 맵, 모든 바이옴이 256×256 칸으로 같은 넓이씩 반복. 첫 방문은 **모두 같은 자리**(포켓몬 평균 레벨이 가장 낮은 꽃 숲), 그 주변 200칸은 **15레벨 이하**만 나옴
6. **포켓몬은 야생에서만** 나옴. 야생·플레이어 배틀은 **야생(광장 마을 포함)**에서만 (NPC·체육관 배틀은 어디서나). **1시간마다**(서버가 켜져 있는 동안, 그 시각에 야생에 아무도 없으면 다음 시각으로) 야생의 무작위 플레이어 근처(초보 구역엔 안 나옴)에 그 바이옴에 출현 설정이 있는 **전설·환상 1마리** (`/pokeserver legend`로 바로). 내 파티 최고 레벨보다 5레벨 넘게 높은 포켓몬은 1레벨당 포획률 5%씩 낮아짐 (최저 10%)
7. **블록은 야생에서만 자유롭게** 캐고 놓을 수 있음. **농장**(25칸)은 상점에서 산 **땅 문서**로 등록한 **내 땅만** (길·빈 땅·남의 땅은 불가, 관리자도 크리에이티브일 때만). 땅 문서는 한 사람이 살수록 비싸짐 (기본가 × (산 개수 + 1), 사람마다 따로)
8. **포켓몬센터**: 회복 장치, PC(G 키 메뉴의 PC로도 열림), 교환은 Cobblemon 기본 방식(상대를 바라보고 R키 → 교환)
9. **상점**: 볼 20종을 배지별로 판매(0개: 몬스터·프리미어·힐볼 → 5개: 레벨·루어·헤비·문·러브러브·프렌드·스피드볼 → 8개: 퀵·타이머볼 1,500원, 볼 중 최고가). **성격·노력치** 분류: 비타민 6종(배지 3)·파워 아이템 6종(배지 4)·특성캡슐(배지 5)·성격민트 21종(배지 6). **마스터볼은 제작 불가**(`data/cobblemon/recipe/master_ball.json`이 Cobblemon 제작법을 끔), 나머지 볼은 Cobblemon 제작법 그대로. 상품 클릭 → 수량 창(−/+, 1·8·16·32·64, 휠·방향키) → **구매하기**(Enter)를 눌러야 거래. 배지가 늘수록 살 수 있는 상품이 늘어남 (판매는 언제나 가능). 상품별 필요 배지는 `shop.json`의 `badges`
10. **모든 포켓몬 모델**: Cobblemon에 모델이 없던 120종(전설·환상·울트라비스트·패러독스 등)은 **Complete Cobblemon Collection**, 메가진화·거다이맥스·Z기술·테라스탈은 **Mega Showdown**(메가스톤은 제작·야생 유적). 전설류는 야생에서 아주 드물게 50~70레벨로 나오고, 첫 스폰 근처(15레벨 구역)엔 안 나옴. 애드온 경로 오류(아르세우스·우라오스 텍스처)는 `tools/ccc_fix.py`가 보정
11. **글 강조**: 튜토리얼·팁 NPC 대화의 중요한 말은 노란색 (`§e…§r`)

화폐: `/money`(`/돈`) 잔액, `/pay 닉네임 금액`(`/송금`) 보내기

명령어는 한국어·영어 둘 다: `/가기`(`/tpa`) · `/부르기`(`/tpahere`) · `/수락`(`/accept`) · `/거절`(`/deny`) · `/광장`(`/spawn`) · `/메뉴`(`/menu`) · `/명령어`(`/commands`). 일반 사용자 텔레포트는 상대 채팅의 **[예]/[아니요]**, 10초 지나면 취소. OP는 바로. 전체: [`docs/명령어.md`](docs/명령어.md)

닉네임·칭호: 튜토리얼 마지막 쪽에서 닉네임 입력 → 채팅·머리 위·탭 목록에 `[칭호] 닉네임` (칭호 18가지, G 메뉴에서 고름: `Titles.java`). 10분마다 바닥 아이템 자동 정리(`ItemCleaner.java`, 지금 정리: `/pokeserver clearitems`, 지우기 30초 전 채팅 알림). 운영자 공지: `/공지 내용` (`/announce`). 오른쪽 가운데 정보창(위치·소지금·배지 / 시간·바이옴·좌표). 배틀 화면은 참고 사진 크기(GUI 2.5배)·어두운 납작한 디자인. 체육관에서 지면 5분 뒤 재도전

서버 규칙: 포켓몬 외 몬스터·동물 없음 · 배고픔 없음 · 죽어도 아이템 유지 · 폭발로 블록 안 부서짐

## 수정하는 곳

| 바꿀 것 | 방법 |
|---|---|
| 섬 둘레 지형 (절벽·아치·기둥·언덕) | `tools/terrain.py` (높이·블록), 섬 크기는 `tools/build_world.py`의 `*_PLAY` → 실행 → `build` 숫자 +1 |
| 체육관·튜토리얼·농장 모양과 위치 | `tools/build_world.py` 수정 → 실행 → `load.mcfunction`의 `build:15`(농장은 `farm:3`) 숫자 +1 |
| 광장 마을 건물·조경 | `tools/plaza.py` 수정 → `tools/build_world.py` 실행 → `Plaza.java`의 `BUILD_VERSION` +1 (모드 다시 빌드) |
| 튜토리얼·농장 도착 위치 | `pack/world/datapacks/pokeserver/data/poke/function/config.mcfunction` |
| 월드 초기화 | `pack/config/pokeserver/reset.json`의 `season` +1 → 다음 서버 시작 때 새 월드 (이전 월드는 서버 폴더의 `world-backup-...`에 보관, 지우지 않음) |
| 기본 물품 | `.../function/kit.mcfunction`(러닝 슈즈), `.../function/mod/kit.mcfunction`(돈·몬스터볼) |
| 안내원·간호사 대화 | `.../data/poke/dialogues/tutorial.json`, `nurse.json` |
| 상점 분류·상품·가격 | `pack/config/pokeserver/shop.json` (`buy`/`sell`이 0이면 그 탭에 안 나옴). 실행 중엔 `/pokeserver reload` |
| 메인 메뉴 공지사항 | `pack/config/pokeserver/menu.json` |

## NPC

NPC는 Cobblemon NPC 하나로 통일합니다 (대화·회복·배틀 파티를 모두 지원). 사람 크기 모델에 기본 스킨이 입혀져 있고, 게임 안에서 바꿀 수 있습니다.

| 하고 싶은 것 | 방법 (관리자) |
|---|---|
| NPC 스킨을 다른 플레이어 스킨으로 | `/pokeserver npc skin poke.nurse 플레이어이름` (태그: `poke.tutor`·`poke.nurse`·`poke.merchant`·`poke.gymguide`) |
| 스킨 이미지 주소로 | `/pokeserver npc skin poke.nurse https://.../skin.png` |
| 기본 스킨으로 되돌리기 | `/pokeserver npc skin poke.nurse reset` |
| 이름·파티 등 세부 편집 | NPC를 바라보고 `/npcedit` (Cobblemon 편집기) |

바꾼 스킨은 월드에 저장되어 마을을 다시 지어도 유지됩니다. 기본 스킨 그림은 `tools/make_skins.py`.

## 체육관 리그 (RCT 모드)

**체육관 섬**의 포켓몬 체육관 건물 안 **체육관 안내원**을 우클릭 → 도전 목록. 목록엔 **클리어한 곳(하늘색 테두리 + CLEARED 도장)**과 **지금 도전할 수 있는 곳(초록)**만 보이고 (다른 사람이 싸우는 중이면 주황으로 이름 표시, 누르면 알림), 아직 못 가는 체육관·사천왕은 안 보임. 고르면 그 관장의 경기장(닫힌 방)으로 순간이동.

- 배지 체육관 8곳: 앞 배지를 모두 모아야 다음 도전, 이긴 체육관은 다시 도전 불가
- 관장마다 **도전자 한 명만** (경기장엔 관장만 있음). 지거나 나가기(주황 발판)·로그아웃·사망 시 로비로 나오고 자리가 비워짐
- **레벨 제한**: 처음 20 → 배지마다 10씩 (30·40·…·90), 배지 8개 뒤 100. 관장 최고 레벨 = 그다음 레벨 제한
- **사천왕** = 역대 최강 챔피언 4명 (성호 → 단델 → 난천 → 레드), 원작 팀 그대로이고 종족값이 높은 포켓몬일수록 레벨이 높음. 배지 8개 필요, 4명을 **연속으로** 이겨야 클리어(지면 처음부터). 클리어하면 명예의 전당
- **다이맥스**: 원래 파워 스팟 근처에서만 되지만, 체육관·사천왕 도전 중 배틀과 플레이어 배틀에서는 어디서나 됨 (`DynamaxSpotMixin`)
- **클리어 공지**: 체육관·사천왕(한 명씩)·챔피언이 되면 서버 전체 채팅에 공지
- **팀 보관**: 바꾸기 전 팀은 `docs/관장팀_v1.md`, `tools/league_v1.json`
- **상금**: 관장을 이기면 레벨 제한 × 100원 (1번 2,000원 ~ 8번 9,000원), 사천왕 클리어 10,000원. 돈은 이 상금, 처음 받는 5,000원, 물건 판매(야생 채집·낚시·광질·구조물 파밍, 농장)로 법니다

| 바꿀 것 | 방법 |
|---|---|
| 관장 이름·포켓몬·기술·레벨·대사 | `tools/build_league.py` 수정 → 실행 → `reload`. `COBBLEMON_SPECIES=<Cobblemon 종 데이터 폴더>`를 주면 기술을 배울 수 있는지·레벨 규칙도 검사 |
| 관장 다시 배치 | `/data modify storage poke:state leaders set value 0` (다음 틱에 다시 소환) |

## 관리자 명령

전체 목록(일반·OP 구분): [`docs/명령어.md`](docs/명령어.md)


- 관리자: `/pokeserver money give|take|set <플레이어> <금액>`, `/pokeserver deed <플레이어>` 땅 문서, `/pokeserver unclaim <번호>` 땅 주인 해제, `/pokeserver reload` 설정 다시 읽기
- 글꼴: 우리 화면·표지판 글자는 [갈무리9](https://github.com/quiple/galmuri) (닌텐도 DS 글꼴에서 영감을 받은 한글 픽셀 글꼴, SIL OFL 1.1, 라이선스는 모드 안 `assets/pokeserver/font/Galmuri-OFL.txt`)
- 관리자: `/function poke:admin/reset_me` 튜토리얼만 다시(보상은 다시 안 줌), `/function poke:admin/rebuild` 마을·NPC 다시 짓기
- **전체 초기화**: OP만 `/초기화` → 안내 → `/초기화 확인` (자기 자신만). 관리자 `/pokeserver reset <플레이어>`. 인벤토리·엔더 상자·돈·농장 땅·포켓몬(파티·PC)·스타팅 선택·배지·레벨 제한 진행을 모두 지우고 첫 튜토리얼부터 (기본 물품도 다시 받음). 도감 기록은 남음

## 친구와 같이 하기 (playit.gg 터널)

집 IP를 드러내거나 공유기 설정(포트포워딩)을 바꾸지 않고, 무료 터널 프로그램 **playit.gg**로 친구가 들어옵니다.
서버 설정(`server-ip=127.0.0.1`)은 그대로 둡니다 — playit이 이 PC 안에서 서버에 연결하기 때문.

**서버 PC (한 번만)**
1. https://playit.gg 가입 → **Download** → Windows용 설치 → 실행해서 로그인
2. playit 웹 화면 **Tunnels → Add Tunnel** → 종류 **Minecraft Java**, Local Address `127.0.0.1`, Local Port `25565` → 만들기
3. 받은 주소(예: `xxxx.joinmc.link`)를 친구에게 알려 줌. 서버를 켤 때 playit 프로그램도 켜져 있어야 함
4. 서버 콘솔에서 아무나 못 들어오게 화이트리스트:
   ```
   whitelist on
   whitelist add 내마인크래프트아이디
   whitelist add 친구마인크래프트아이디
   ```

**친구 PC**
1. 위 **클라이언트** 설치를 그대로 (Prism Launcher + packwiz 한 줄) → 모드·데이터팩이 서버와 자동으로 같아짐
2. 멀티플레이 → 서버 추가 → 주소에 playit 주소
3. 정품 계정이어야 접속됨 (서버가 정품 확인을 함)

## 모드 추가 (관리용)

```bash
cd pack && packwiz modrinth add <모드 이름> && packwiz refresh
```

## 테스트

`tests/all.sh` 하나로 두 테스트를 동시에 돌립니다 (약 1분 20초). 데이터팩이 바뀌지 않았으면 지어 둔 월드를 재사용합니다.

`tests/run.sh`는 데이터팩 테스트 전에 `tools/check_holes.py`로 건물 벽·바닥·지붕 빈칸도 검사합니다.

```bash
tests/run.sh
```

```bash
tests/mod-test.sh
```
