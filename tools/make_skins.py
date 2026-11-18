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


def build(name, hair, hair_dark, body_at, arm_at, leg_at, eye=(60, 50, 90), long_hair=False, hat_at=None, extra=None):
    rng = random.Random(name)
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    paint(img, 'head', head(rng, hair, hair_dark, long_hair), rng)
    if hat_at:
        paint(img, 'hat', hat_at, rng)
    paint(img, 'body', body_at, rng)
    for arm in ('rarm', 'larm'):
        paint(img, arm, arm_at, rng)
    for leg in ('rleg', 'lleg'):
        paint(img, leg, leg_at, rng)
    white = (250, 250, 250)
    eyes = [(2, 4, white), (5, 4, white), (2, 5, eye), (5, 5, eye), (1, 4, eye), (6, 4, eye)]
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
    return build('nurse', pink, pink_d, body, arm, leg, eye=(70, 110, 170), long_hair=True, hat_at=hat, extra=blush)


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
    return build('merchant', (45, 35, 30), (25, 20, 18), body, arm, leg, eye=(50, 40, 40))


def tutor():
    coat, shirt = (238, 238, 244), (140, 190, 235)

    def body(face, x, y, w, h):
        if face == 'front' and x in (3, 4):                        # 열린 가운 사이 셔츠·넥타이
            return (200, 60, 60) if x == 3 and 1 <= y <= 6 else shirt
        if face == 'front' and x in (2, 5) and y < 3:
            return (210, 210, 220)                                 # 옷깃
        return coat

    def arm(face, x, y, w, h):
        return coat if y < 10 else SKIN

    def leg(face, x, y, w, h):
        return (90, 60, 40) if y >= 10 else (85, 78, 70)
    glasses = [(x, 4, (90, 90, 100)) for x in (1, 3, 4, 6)]
    return build('tutorial_guide', (115, 75, 45), (85, 55, 30), body, arm, leg, eye=(60, 90, 60), extra=glasses)


if __name__ == '__main__':
    (OUT / 'textures/npcs').mkdir(parents=True, exist_ok=True)
    (OUT / 'bedrock/npcs/variations').mkdir(parents=True, exist_ok=True)
    for make in (nurse, merchant, tutor):
        img = make()
        name = {'nurse': 'nurse', 'merchant': 'merchant', 'tutor': 'tutorial_guide'}[make.__name__]
        img.save(OUT / f'textures/npcs/{name}.png')
        # Cobblemon NPC 외형: 이름이 NPC 종류 ID와 같아야 적용됨
        (OUT / f'bedrock/npcs/variations/{name}.json').write_text(json.dumps({
            'name': f'poke:{name}', 'order': 0, 'variations': [{
                'aspects': [], 'layers': [], 'model': 'cobblemon:steve.geo', 'poser': 'cobblemon:standard',
                'texture': f'pokeserver:textures/npcs/{name}.png'}]}, indent=2))
        print('skin', name)
