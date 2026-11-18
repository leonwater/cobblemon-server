"""검증용: 실제 배포 형태의 클라이언트(Fabric + Cobblemon + pokeserver 모드)를 띄워 서버에 접속.

화면은 Xvfb에서 ImageMagick `import`로 찍는다 (tools/shots.sh 참고). 개발용 runClient는 Cobblemon이 안 돌아서 이걸 씀.
사용: python3 tools/prod_client.py <작업폴더> <접속주소 host:port>
"""
import json, os, subprocess, sys, urllib.request
from pathlib import Path

WIN = os.environ.get('WIN', '1280x720').split('x')   # 창 크기 (좁은 화면 시험용), GUI_SCALE 로 UI 크기

MC, LOADER = '1.21.1', '0.20.1'
ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path.home() / '.gradle/caches/fabric-loom/assets'   # mod/ 에서 gradle runClient 한 번 하면 생김


def get(url, dest=None):
    if dest and dest.exists():
        return dest
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    if dest is None:
        return json.loads(data)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def maven_path(name):
    group, art, ver = name.split(':')[:3]
    return f"{group.replace('.', '/')}/{art}/{ver}/{art}-{ver}.jar"


def main(work, server, user='Dev'):
    work = Path(work)
    idx = ASSETS / 'indexes'
    if not (idx / '17.json').exists():   # Loom은 1.21.1-17.json 이름으로 저장함
        (idx / '17.json').write_bytes((idx / f'{MC}-17.json').read_bytes())
    libs = work / 'libraries'
    manifest = get('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json')
    vjson = get(next(v['url'] for v in manifest['versions'] if v['id'] == MC))
    cp = [get(vjson['downloads']['client']['url'], work / f'client-{MC}.jar')]
    for lib in vjson['libraries']:
        rules = lib.get('rules', [])
        if rules and not any(r['action'] == 'allow' and r.get('os', {}).get('name', 'linux') == 'linux' for r in rules):
            continue
        a = lib['downloads'].get('artifact')
        if a:
            cp.append(get(a['url'], libs / a['path']))
    fabric = get(f'https://meta.fabricmc.net/v2/versions/loader/{MC}/{LOADER}/profile/json')
    for lib in fabric['libraries']:
        cp.append(get(lib['url'].rstrip('/') + '/' + maven_path(lib['name']), libs / maven_path(lib['name'])))
    game = work / ('game' if user == 'Dev' else 'game-' + user)   # 두 번째 플레이어(교환 시험 등)는 따로
    (game / 'mods').mkdir(parents=True, exist_ok=True)
    for f in (ROOT / 'pack/mods').glob('*.pw.toml'):
        t = f.read_text()
        if 'side = "server"' in t:
            continue
        name = t.split('filename = "')[1].split('"')[0]
        get(t.split('url = "')[1].split('"')[0], game / 'mods' / name)
    # 셰이더: SHADERS=1 이면 모드팩 설정대로 켜고, 아니면 꺼서 시험 화면을 가볍게
    (game / 'shaderpacks').mkdir(exist_ok=True)
    for f in (ROOT / 'pack/shaderpacks').glob('*.pw.toml'):
        t = f.read_text()
        get(t.split('url = "')[1].split('"')[0], game / 'shaderpacks' / t.split('filename = "')[1].split('"')[0])
    (game / 'config').mkdir(exist_ok=True)
    iris = (ROOT / 'pack/config/iris.properties').read_text()
    (game / 'config/iris.properties').write_text(iris if os.environ.get('SHADERS') == '1' else iris.replace('enableShaders=true', 'enableShaders=false'))
    for j in (game / 'mods').glob('pokeserver-*.jar'):
        j.unlink()
    for j in (ROOT / 'pack/mods').glob('pokeserver-*.jar'):
        (game / 'mods' / j.name).write_bytes(j.read_bytes())
    (game / 'options.txt').write_text('onboardAccessibility:false\nguiScale:' + os.environ.get('GUI_SCALE', '2') + '\nlang:ko_kr\nsoundCategory_master:0.0\n'
                                      'tutorialStep:none\njoinedFirstServer:true\nskipMultiplayerWarning:true\n')
    cmd = ['java', '-Xmx3G', '-cp', ':'.join(map(str, cp)), fabric['mainClass'],
           '--username', user, '--version', MC, '--gameDir', str(game), '--assetsDir', str(ASSETS),
           '--assetIndex', vjson['assetIndex']['id'], '--uuid', '0000000000000000000000000000000' + ('1' if user == 'Dev' else '2'), '--accessToken', '0',
           '--userType', 'legacy', '--versionType', 'release', '--width', WIN[0], '--height', WIN[1],
           '--quickPlayMultiplayer', server]
    env = dict(os.environ, LIBGL_ALWAYS_SOFTWARE='1')
    sys.exit(subprocess.call(cmd, env=env, cwd=game))


if __name__ == '__main__':
    main(*sys.argv[1:])
