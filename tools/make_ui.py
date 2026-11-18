"""어두운 반투명 UI 리소스팩 생성기.

원본 텍스처(Cobblemon 대화창, 바닐라 버튼)를 jar에서 읽어 색만 바꿔 저장한다.
색을 바꾸고 싶으면 아래 팔레트만 고치고 다시 실행.

사용: python3 tools/make_ui.py <cobblemon.jar> <minecraft-1.21.1-client.jar>
"""
import io, json, sys, zipfile
from pathlib import Path
from PIL import Image

# ── 팔레트 (RGB) ──
DARK = (16, 19, 25)        # 가장 어두운 바탕
LIGHT = (96, 106, 124)     # 대화창 테두리
HOVER = (136, 149, 175)    # 버튼에 마우스를 올렸을 때 테두리
FILL_ALPHA = 215           # 바탕 불투명도 (0~255, 낮을수록 투명)

OUT = Path(__file__).resolve().parent.parent / 'mod/src/main/resources'   # 모드 안에 넣어 리소스팩 없이 항상 적용
DIALOGUE = 'assets/cobblemon/textures/gui/dialogue/'
WIDGET = 'assets/minecraft/textures/gui/sprites/widget/'


def lum(r, g, b):
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def invert_dark(im):
    """밝은 바탕 → 어두운 반투명, 어두운 테두리 → 밝은 선 (대화창 상자)."""
    out = im.copy()
    px = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            t = 1 - lum(r, g, b)
            px[x, y] = (*mix(DARK, LIGHT, t), FILL_ALPHA if t < 0.35 else a)
    return out


def shift_dark(im, border_white=False):
    """밝기 순서는 유지하고 어둡게 (버튼: 기본 < 마우스 올림 순서 유지)."""
    out = im.copy()
    px = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            L = lum(r, g, b)
            if border_white and L > 0.95:
                px[x, y] = (*HOVER, 255)
                continue
            fill = 0.12 < L < 0.9
            px[x, y] = (*mix(DARK, (136, 148, 172), L ** 1.5), FILL_ALPHA if fill else a)
    return out


def main(cobblemon_jar, client_jar):
    textures = {}
    with zipfile.ZipFile(cobblemon_jar) as z:
        for n in z.namelist():
            if n.startswith(DIALOGUE) and n.endswith('.png'):
                im = Image.open(io.BytesIO(z.read(n))).convert('RGBA')
                textures[n] = invert_dark(im) if 'dialogue_box' in n else shift_dark(im)
    meta = {}
    with zipfile.ZipFile(client_jar) as z:
        for s in ('button', 'button_highlighted', 'button_disabled'):
            im = Image.open(io.BytesIO(z.read(f'{WIDGET}{s}.png'))).convert('RGBA')
            textures[f'{WIDGET}{s}.png'] = shift_dark(im, border_white=(s == 'button_highlighted'))
            # 9-slice 설정은 텍스처와 같은 팩에 있어야 적용됨
            meta[f'{WIDGET}{s}.png.mcmeta'] = z.read(f'{WIDGET}{s}.png.mcmeta')
    for path, im in textures.items():
        (OUT / path).parent.mkdir(parents=True, exist_ok=True)
        im.save(OUT / path)
    for path, data in meta.items():
        (OUT / path).write_bytes(data)
    print(f'{len(textures)} textures -> {OUT}')


if __name__ == '__main__':
    main(*sys.argv[1:])
