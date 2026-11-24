"""상점 문서(직접 눌러 보는 인게임 상점 화면) 만들기: pack/config/pokeserver/shop.json → <출력 폴더>/index.html + data.json + galmuri9.ttf
사용: python3 tools/shop_doc.py <출력 폴더>   상점을 바꿀 때마다 돌리고 상점 문서 아티팩트를 다시 올림 (docs/작업규칙.md)
아이콘 = 각 jar의 아이템 모델 → 텍스처 (블록은 윗면·옆면으로 게임처럼 비스듬한 정육면체), 이름 = 한국어 언어 파일."""
import base64, io, json, shutil, sys, warnings, zipfile
warnings.filterwarnings('ignore', category=DeprecationWarning)   # Pillow getdata 예고
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path.home() / '.gradle/caches/fabric-loom/assets'      # 마인크래프트 한국어 (gradle runClient 한 번 하면 생김)
MC_JAR = Path('/tmp/pokeserver-shots/client/client-1.21.1.jar')  # tools/shots.sh가 받아 둔 클라이언트
MOD_RES = ROOT / 'mod/src/main/resources'


class Res:
    """여러 jar·폴더를 하나처럼 읽음 (assets/<ns>/...)."""
    def __init__(self):
        self.zips = [zipfile.ZipFile(j) for j in [MC_JAR, *sorted((ROOT / 'tools/.jarcache').glob('*.jar'))] if j.exists()]

    def read(self, path):
        f = MOD_RES / path
        if f.exists(): return f.read_bytes()
        for z in self.zips:
            try: return z.read(path)
            except KeyError: pass
        return None


R = Res()


def names():
    idx = json.loads((ASSETS / 'indexes/1.21.1-17.json').read_text())['objects']['minecraft/lang/ko_kr.json']['hash']
    ko = json.loads((ASSETS / 'objects' / idx[:2] / idx).read_text(encoding='utf-8'))
    for ns in ('cobblemon', 'mega_showdown'):
        b = R.read(f'assets/{ns}/lang/ko_kr.json')
        if b: ko.update(json.loads(b))
    return ko


def model(ref):
    """'ns:item/x' 모델의 textures를 부모 쪽까지 합치고, 맨 위 부모 이름도 돌려줌."""
    tex, chain = {}, []
    while ref and len(chain) < 12:
        ns, p = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
        b = R.read(f'assets/{ns}/models/{p}.json')
        if not b: break
        m = json.loads(b)
        chain.append(p)
        for k, v in m.get('textures', {}).items(): tex.setdefault(k, v)
        ref = m.get('parent')
    for k, v in list(tex.items()):                       # '#side' 같은 참조 풀기
        for _ in range(4):
            if isinstance(v, str) and v.startswith('#'): v = tex.get(v[1:], v)
        tex[k] = v
    return tex, chain


def png(ref):
    ns, p = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
    b = R.read(f'assets/{ns}/textures/{p}.png')
    if not b: return None
    im = Image.open(io.BytesIO(b)).convert('RGBA')
    return im.crop((0, 0, im.width, im.width)) if im.height > im.width else im      # 움직이는 텍스처는 첫 장면만


def face(out, im, o, a, b):
    """텍스처(16×16)를 점 o에서 벡터 a(가로)·b(세로) 방향 평행사변형으로 붙임. PIL은 출력→입력 역변환을 받음."""
    det = a[0] * b[1] - a[1] * b[0]
    ia, ib, ic, id_ = b[1] / det, -b[0] / det, -a[1] / det, a[0] / det       # [a b]^-1
    ox, oy = o
    out.alpha_composite(im.transform(out.size, Image.AFFINE,
                                     (ia, ib, -(ia * ox + ib * oy), ic, id_, -(ic * ox + id_ * oy)), Image.NEAREST))


def tint(im, c):
    im = im.copy(); im.putdata([(r * c[0] // 255, g * c[1] // 255, b * c[2] // 255, a) for r, g, b, a in im.getdata()]); return im


def cube(top, side, front):
    """게임 인벤토리처럼 비스듬한 정육면체 (32px): 윗면 밝게, 왼쪽 면 어둡게, 오른쪽 면 중간."""
    def prep(im, f):
        im = im.resize((16, 16), Image.NEAREST)
        im.putdata([(int(r * f), int(g * f), int(b * f), a) for r, g, b, a in im.getdata()])
        return im
    out = Image.new('RGBA', (32, 32))
    face(out, prep(top, 1.0), (0, 8), (1, -0.5), (1, 0.5))
    face(out, prep(side, 0.62), (0, 8), (1, 0.5), (0, 1))
    face(out, prep(front, 0.80), (16, 16), (1, -0.5), (0, 1))
    return out


def icon(item):
    if item == 'pokeserver:farm_deed': item = 'minecraft:paper'
    ns, n = item.split(':')
    tex, chain = model(f'{ns}:item/{n}')
    block = any(c.startswith('block/cube') or c == 'block/block' for c in chain) or ('all' in tex and 'layer0' not in tex)
    if block and 'layer0' not in tex:
        side = tex.get('side') or tex.get('all') or tex.get('front') or tex.get('texture') or tex.get('particle')
        top = tex.get('top') or tex.get('end') or tex.get('all') or side
        front = tex.get('front') or side
        ims = [png(x) for x in (top, side, front) if x]
        if ims and top and 'grass_block_top' in top: ims[0] = tint(ims[0], (124, 189, 107))   # 잔디 윗면은 게임이 바이옴 색을 입힘
        if len(ims) == 3: return cube(*ims)
    for k in ('layer0', 'cross', 'texture', 'all', 'particle'):
        if k in tex and (im := png(tex[k])): return im.resize((32, 32), Image.NEAREST)
    for p in (f'{ns}:item/{n}', f'{ns}:block/{n}'):
        if im := png(p): return im.resize((32, 32), Image.NEAREST)
    return None


def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    shop = json.loads((ROOT / 'pack/config/pokeserver/shop.json').read_text(encoding='utf-8'))
    ko = names()
    ids = {x['item'] for c in shop['categories'] for x in c['items']} | {c['icon'] for c in shop['categories']} | {'minecraft:gold_nugget'}
    icons, nm, missing = {}, {}, []
    for i in sorted(ids):
        ns, n = i.split(':')
        nm[i] = '땅 문서' if i == 'pokeserver:farm_deed' else ko.get(f'item.{ns}.{n}') or ko.get(f'block.{ns}.{n}') or n
        im = icon(i)
        if im: icons[i] = uri(im)
        else: missing.append(i)
    ver = (ROOT / 'pack/pack.toml').read_text().split('version = "')[1].split('"')[0]
    data = {'version': ver, 'categories': shop['categories'], 'names': nm, 'icons': icons, 'league': [
        {'n': g['n'], 'leader': g['leader'], 'badge': g['badge']} for g in json.loads((ROOT / 'pack/config/pokeserver/league.json').read_text(encoding='utf-8'))[:8]]}
    (out / 'data.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    shutil.copy(ROOT / 'tools/shop_doc.html', out / 'index.html')
    shutil.copy(MOD_RES / 'assets/pokeserver/font/galmuri9.ttf', out / 'galmuri9.ttf')
    print(f'상품 {sum(len(c["items"]) for c in shop["categories"])}개, 아이콘 {len(icons)}/{len(ids)}', '아이콘 없음:', missing[:20])


if __name__ == '__main__':
    main(sys.argv[1])
