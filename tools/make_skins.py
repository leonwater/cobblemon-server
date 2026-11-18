"""NPC 스킨(64x64, 일반 플레이어 형식) + Cobblemon NPC 외형 파일 생성.

외형 이름 = NPC 종류 ID(poke:nurse 등). 모델은 Cobblemon의 사람 크기 모델(cobblemon:steve.geo).
사용: python3 tools/make_skins.py
"""
import json, random
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / 'mod/src/main/resources/assets/pokeserver'
SKIN = (255, 214, 180)

# 부위: (u, v, 가로, 높이, 깊이) — 일반 스킨 배치
PARTS = {
    'head': (0, 0, 8, 8, 8), 'hat': (32, 0, 8, 8, 8),
    'body': (16, 16, 8, 12, 4), 'rarm': (40, 16, 4, 12, 4), 'larm': (32, 48, 4, 12, 4),
    'rleg': (0, 16, 4, 12, 4), 'lleg': (16, 48, 4, 12, 4),
    # 바깥 층 (입체감): 겉옷·소매
    'jacket': (16, 32, 8, 12, 4), 'rsleeve': (40, 32, 4, 12, 4), 'lsleeve': (48, 48, 4, 12, 4),
}
SHADE = {'top': 1.06, 'bottom': 0.82, 'front': 1.0, 'back': 0.86, 'right': 0.92, 'left': 0.92}


def faces(part):
    u, v, w, h, d = PARTS[part]
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'right': (u, v + d, d, h),
            'front': (u + d, v + d, w, h), 'left': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h)}


def paint(img, part, color_at, rng):
    """color_at(face, x, y, w, h) → (r,g,b) 또는 None(투명)."""
    for face, (fx, fy, w, h) in faces(part).items():
        for y in range(h):
            for x in range(w):
                c = color_at(face, x, y, w, h)
                if c is None:
                    continue
                k = SHADE[face] * (1 + rng.uniform(-0.03, 0.03))
                img.putpixel((fx + x, fy + y), tuple(max(0, min(255, int(ch * k))) for ch in c) + (255,))


def face_details(img, eyes, hair_front_rows, hair, extra=None):
    fx, fy = 8, 8  # 머리 앞면
    for x, y, c in eyes:
        img.putpixel((fx + x, fy + y), c + (255,))
    if extra:
        for x, y, c in extra:
            img.putpixel((fx + x, fy + y), c + (255,))


def head(rng, hair, hair_dark, long_hair=False, bangs=2):
    def at(face, x, y, w, h):
        if face == 'top' or face == 'back':
            return hair if (x + y) % 5 else hair_dark
        if face == 'bottom':
            return SKIN
        if face in ('right', 'left'):
            return hair if y < (7 if long_hair else 3) else SKIN
        # 앞: 앞머리 + 옆머리
        if y < bangs or (long_hair and (x == 0 or x == 7) and y < 7):
            return hair if (x + y) % 4 else hair_dark
        return SKIN
    return at


def hair_layer(hair, hair_dark, long_hair, hat_at=None):
    def at(face, x, y, w, h):
        c = hat_at(face, x, y, w, h) if hat_at else None
        if c:
            return c
        if face in ('top', 'back'):
            return hair if (x * 3 + y) % 7 else hair_dark
        if face in ('right', 'left'):
            return hair if y < (6 if long_hair else 2) else None
        if face == 'front':
            return hair if y == 0 or (y == 1 and x % 3 != 1) or (long_hair and x in (0, 7) and y < 6) else None
        return None
    return at


def build(name, hair, hair_dark, body_at, arm_at, leg_at, eye=(60, 50, 90), long_hair=False, hat_at=None, extra=None,
          jacket_at=None, sleeve_at=None):
    rng = random.Random(name)
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    paint(img, 'head', head(rng, hair, hair_dark, long_hair), rng)
    paint(img, 'hat', hair_layer(hair, hair_dark, long_hair, hat_at), rng)
    if jacket_at:
        paint(img, 'jacket', jacket_at, rng)
    if sleeve_at:
        for sl in ('rsleeve', 'lsleeve'):
            paint(img, sl, sleeve_at, rng)
    paint(img, 'body', body_at, rng)
    for arm in ('rarm', 'larm'):
        paint(img, arm, arm_at, rng)
    for leg in ('rleg', 'lleg'):
        paint(img, leg, leg_at, rng)
    white = (250, 250, 250)
    lash = tuple(int(c * 0.5) for c in eye)
    eyes = [(1, 4, lash), (2, 4, lash), (5, 4, lash), (6, 4, lash),        # 위 속눈썹
            (1, 5, white), (2, 5, eye), (5, 5, eye), (6, 5, white)]      # 흰자 + 눈동자
    mouth = [(3, 6, (200, 110, 110)), (4, 6, (200, 110, 110))]
    face_details(img, eyes + mouth, 2, hair, extra)
    return img


def nurse():
    pink, pink_d, dress = (245, 140, 185), (215, 100, 150), (250, 175, 205)

    def body(face, x, y, w, h):
        if face == 'front' and 2 <= x <= 5 and y >= 2:            # 흰 앞치마
            return (255, 60, 90) if (x in (3, 4) and y == 4) or (y in (3, 5) and x in (3, 4) and False) else (250, 250, 250)
        if face == 'front' and y < 2 and 2 <= x <= 5:             # 흰 옷깃
            return (250, 250, 250)
        return dress

    def arm(face, x, y, w, h):
        return dress if y < 4 else ((250, 250, 250) if y == 4 else SKIN)

    def leg(face, x, y, w, h):
        return (235, 100, 150) if y >= 10 else (250, 248, 248)

    def hat(face, x, y, w, h):                                     # 간호사 모자 (앞쪽 위)
        if face == 'front' and y <= 1 and 1 <= x <= 6:
            return (255, 70, 100) if x in (3, 4) and y == 0 else (252, 252, 252)
        if face == 'top' and y >= 4:
            return (252, 252, 252)
        if face in ('right', 'left') and y <= 6 and (x == (7 if face == 'right' else 0)):
            return pink                                            # 옆으로 내려오는 머리
        return None
    blush = [(1, 6, (250, 160, 170)), (6, 6, (250, 160, 170))]

    def jacket(face, x, y, w, h):                                  # 앞치마 주름 + 허리 리본
        if face == 'front' and 2 <= x <= 5 and y >= 6:
            return (255, 255, 255) if (x + y) % 3 else (240, 230, 235)
        if y == 6 and face in ('front', 'right', 'left', 'back'):
            return (255, 255, 255)
        return None

    def sleeve(face, x, y, w, h):                                  # 부푼 소매
        return dress if y < 3 else None
    return build('nurse', pink, pink_d, body, arm, leg, eye=(70, 110, 170), long_hair=True, hat_at=hat, extra=blush,
                 jacket_at=jacket, sleeve_at=sleeve)


def merchant():
    blue, white, apron = (70, 120, 220), (245, 245, 250), (40, 60, 125)

    def body(face, x, y, w, h):
        if face == 'front' and 1 <= x <= 6 and y >= 4:
            return (250, 250, 250) if (x, y) == (5, 5) else apron  # 앞치마 + 이름표
        return blue if x % 2 == 0 else white                       # 파란 줄무늬 셔츠

    def arm(face, x, y, w, h):
        return (blue if x % 2 == 0 else white) if y < 6 else SKIN

    def leg(face, x, y, w, h):
        return (40, 30, 30) if y >= 10 else (35, 42, 75)
    def jacket(face, x, y, w, h):                                  # 앞치마 끈·주머니
        if face == 'front' and 1 <= x <= 6 and y >= 4:
            return (30, 45, 100) if y == 8 and 2 <= x <= 5 else None
        if y == 4 and face in ('right', 'left', 'back'):
            return apron
        return None
    return build('merchant', (45, 35, 30), (25, 20, 18), body, arm, leg, eye=(50, 40, 40), jacket_at=jacket)


if __name__ == '__main__':
    (OUT / 'textures/npcs').mkdir(parents=True, exist_ok=True)
    (OUT / 'bedrock/npcs/variations').mkdir(parents=True, exist_ok=True)
    # 안내원은 RCT의 오박사 스킨(손그림, 더 고품질)을 그대로 씀
    for make in (nurse, merchant, None):
        name = make.__name__ if make else 'tutorial_guide'
        tex = f'pokeserver:textures/npcs/{name}.png' if make else 'rctmod:textures/trainers/single/professor_oak_00c8.png'
        if make:
            make().save(OUT / f'textures/npcs/{name}.png')
        # Cobblemon NPC 외형: 이름이 NPC 종류 ID와 같아야 적용됨
        (OUT / f'bedrock/npcs/variations/{name}.json').write_text(json.dumps({
            'name': f'poke:{name}', 'order': 0, 'variations': [
                {'aspects': [], 'layers': [], 'model': 'cobblemon:steve.geo', 'poser': 'cobblemon:standard',
                 'texture': tex},
                {'aspects': ['model-default'], 'layers': [], 'model': 'cobblemon:steve.geo', 'poser': 'cobblemon:standard', 'texture': 'variable'},
                {'aspects': ['model-slim'], 'layers': [], 'model': 'cobblemon:alex.geo', 'poser': 'cobblemon:standard', 'texture': 'variable'}]},
            indent=2))
        print('skin', name)
