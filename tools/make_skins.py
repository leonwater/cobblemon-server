"""NPC 스킨(64x64, 일반 플레이어 형식) + Cobblemon NPC 외형 파일 생성.

외형 이름 = NPC 종류 ID(poke:nurse 등). 모델은 Cobblemon의 사람 크기 모델(cobblemon:steve.geo).
사용: python3 tools/make_skins.py
"""
import json, random, sys
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


def head(rng, hair, hair_dark, long_hair=False, bangs=2, skin=SKIN):
    def at(face, x, y, w, h):
        if face == 'top' or face == 'back':
            return hair if (x + y) % 5 else hair_dark
        if face == 'bottom':
            return skin
        if face in ('right', 'left'):
            return hair if y < (7 if long_hair else 3) else skin
        # 앞: 앞머리 + 옆머리
        if y < bangs or (long_hair and (x == 0 or x == 7) and y < 7):
            return hair if (x + y) % 4 else hair_dark
        return skin
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
          jacket_at=None, sleeve_at=None, skin=SKIN):
    rng = random.Random(name)
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    paint(img, 'head', head(rng, hair, hair_dark, long_hair, skin=skin), rng)
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
    mouth = [(3, 6, (200, 110, 110)), (4, 6, (200, 110, 110))] if skin == SKIN else [(3, 6, tuple(int(c * .75) for c in skin)), (4, 6, tuple(int(c * .75) for c in skin))]
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


def gym_guide():
    """원작 체육관 안내원: 선글라스, 초록 트레이닝복(흰 줄)."""
    green, white = (40, 150, 90), (240, 240, 240)

    def body(face, x, y, w, h):
        if face == 'front' and x in (3, 4):
            return (30, 110, 65) if y > 0 else white                   # 지퍼
        return white if x in (0, w - 1) and face in ('front', 'back') else green

    def arm(face, x, y, w, h):
        return (white if x == 1 else green) if y < 10 else SKIN

    def leg(face, x, y, w, h):
        return (250, 250, 250) if y >= 10 else (35, 40, 50)
    shades = [(1, 4, (20, 20, 25)), (2, 4, (20, 20, 25)), (5, 4, (20, 20, 25)), (6, 4, (20, 20, 25)),
              (3, 4, (60, 60, 60)), (4, 4, (60, 60, 60))]
    img = build('gym_guide', (30, 25, 25), (15, 12, 12), body, arm, leg, eye=(20, 20, 25), extra=shades)
    for x in (9, 10, 13, 14):                                          # 선글라스가 눈을 덮게
        img.putpixel((x, 13), (20, 20, 25, 255))
    return img


def tutorial_guide():
    """오박사: 회색 뾰족 머리, 흰 가운(앞이 열림), 자주색 셔츠, 카키 바지, 갈색 구두."""
    coat, coat_d, shirt, khaki = (245, 245, 240), (215, 215, 210), (150, 40, 60), (175, 150, 105)

    def body(face, x, y, w, h):
        if face == 'front' and 2 <= x <= 5:
            return (110, 25, 45) if x in (3, 4) and y == 0 else shirt   # 셔츠 + 옷깃 그늘
        return coat

    def arm(face, x, y, w, h):
        return coat if y < 10 else SKIN

    def leg(face, x, y, w, h):
        return (95, 60, 35) if y >= 10 else khaki

    def jacket(face, x, y, w, h):                                     # 가운 자락이 허벅지까지 (옷깃 V자)
        if face == 'front':
            if 2 <= x <= 5:
                return None
            return coat_d if (x in (1, 6) and y < 3) else coat
        return coat if face != 'top' else None

    def sleeve(face, x, y, w, h):
        return (coat if y < 9 else coat_d) if y < 10 else None

    def hat(face, x, y, w, h):                                        # 뾰족 솟은 앞머리
        if face == 'front' and y == 0:
            return (205, 205, 210) if x % 2 else (165, 165, 175)
        if face == 'front' and y == 1 and x in (0, 2, 5, 7):
            return (185, 185, 192)
        return None
    brows = [(1, 3, (150, 150, 158)), (2, 3, (150, 150, 158)), (5, 3, (150, 150, 158)), (6, 3, (150, 150, 158))]
    img = build('tutorial_guide', (190, 190, 198), (150, 150, 160), body, arm, leg, eye=(70, 55, 45), hat_at=hat,
                extra=brows, jacket_at=jacket, sleeve_at=sleeve)
    return img


def champion_leon_ps():
    """가라르 챔피언 단델: 긴 보라 머리, 모자, 흰 옷 + 빨간 망토."""
    red, gold = (200, 40, 50), (240, 200, 60)

    def body(face, x, y, w, h):
        return (245, 245, 245) if face == 'front' else (30, 30, 35)

    def arm(face, x, y, w, h):
        return (30, 30, 35) if y < 10 else SKIN

    def leg(face, x, y, w, h):
        return (20, 20, 25) if y >= 9 else (245, 245, 245)

    def hat(face, x, y, w, h):
        if face == 'top' or (face in ('front', 'right', 'left', 'back') and y <= 1):
            return (25, 25, 30) if y == 1 or face == 'top' else red
        return None

    def jacket(face, x, y, w, h):                                     # 망토: 어깨~등, 금색 테두리
        if face == 'back' or (face in ('right', 'left') and y < 10):
            return gold if y == 0 or x in (0, w - 1) else red
        if face == 'front' and x in (0, 7):
            return red
        return None
    return build('champion_leon_ps', (110, 50, 140), (80, 30, 110), body, arm, leg, eye=(200, 160, 40), long_hair=True,
                 hat_at=hat, jacket_at=jacket)


def champion_steven_ps():
    """호연 챔피언 성호: 은청색 머리, 검은 정장, 빨간 넥타이."""
    suit = (35, 38, 48)

    def body(face, x, y, w, h):
        if face == 'front' and x in (3, 4):
            return (190, 40, 50) if x == 3 and 1 <= y <= 7 else (235, 235, 240)
        if face == 'front' and x in (2, 5) and y < 4:
            return (150, 155, 170)                                     # 은색 옷깃
        return suit

    def arm(face, x, y, w, h):
        return suit if y < 10 else ((150, 155, 170) if y == 10 else SKIN)

    def leg(face, x, y, w, h):
        return (20, 20, 25) if y >= 10 else suit
    return build('champion_steven_ps', (170, 185, 210), (120, 135, 165), body, arm, leg, eye=(60, 90, 160))



# ── 관장·챔피언 원작풍 스킨 (RCT 기본 스킨이 원작과 달라서). 아직 적용 전: --preview 폴더로만 저장 ──
TAN = (205, 150, 105)


def leader_brock_ps():
    """웅: 까만 피부, 뾰족한 갈색 머리, 실눈, 주황 셔츠 + 초록 조끼, 갈색 바지."""
    def body(face, x, y, w, h):
        return (90, 120, 60) if face != 'front' or x in (0, 1, 6, 7) else (230, 130, 40)

    def arm(face, x, y, w, h):
        return (230, 130, 40) if y < 4 else TAN

    def leg(face, x, y, w, h):
        return (60, 40, 25) if y >= 10 else (120, 85, 50)

    def spikes(face, x, y, w, h):                                       # 뾰족 머리 (겉 층)
        if face == 'top' or (face == 'front' and y == 0) or (face in ('right', 'left', 'back') and y < 3):
            return (95, 60, 35) if (x + y) % 3 else (70, 45, 25)
        return None
    closed = [(1, 5, TAN), (2, 5, (60, 40, 30)), (5, 5, (60, 40, 30)), (6, 5, TAN),
              (1, 4, (95, 60, 35)), (2, 4, (95, 60, 35)), (5, 4, (95, 60, 35)), (6, 4, (95, 60, 35))]
    return build('leader_brock_ps', (95, 60, 35), (70, 45, 25), body, arm, leg, skin=TAN, hat_at=spikes, extra=closed)


def leader_misty_ps():
    """이슬: 주황 머리(옆으로 묶음), 노란 짧은 상의 + 빨간 멜빵, 청반바지."""
    hair, dark = (240, 130, 50), (200, 95, 35)

    def body(face, x, y, w, h):
        if face == 'front' and x in (2, 5):
            return (210, 40, 40)
        return (250, 215, 60) if y < 7 else SKIN

    def arm(face, x, y, w, h):
        return SKIN

    def leg(face, x, y, w, h):
        return (70, 110, 190) if y < 4 else (SKIN if y < 10 else (220, 60, 50))

    def tail(face, x, y, w, h):                                         # 옆으로 묶은 머리
        return (hair if y % 2 else dark) if face == 'right' and y < 7 and x >= 2 else None
    return build('leader_misty_ps', hair, dark, body, arm, leg, eye=(60, 110, 170), hat_at=tail)


def leader_lt_surge_ps():
    """마티스: 금발 짧은 머리, 국방색 민소매, 얼룩무늬 군복 바지."""
    olive = (95, 110, 55)

    def body(face, x, y, w, h):
        return olive if y < 10 else (40, 40, 30)

    def arm(face, x, y, w, h):
        return SKIN

    def leg(face, x, y, w, h):
        if y >= 10:
            return (40, 35, 30)
        return [(110, 120, 70), (80, 90, 50), (120, 100, 60)][(x * 2 + y) % 3]
    tags = [(3, 6, (200, 110, 110)), (4, 6, (200, 110, 110))]
    return build('leader_lt_surge_ps', (240, 210, 90), (210, 180, 60), body, arm, leg, eye=(60, 100, 60), extra=tags)


def leader_erika_ps():
    """민화: 까만 단발 + 빨간 머리띠, 초록 기모노(흰 깃·노란 띠), 빨간 하카마."""
    def body(face, x, y, w, h):
        if face == 'front' and y < 4 and abs(x - 3.5) < 4 - y:
            return (245, 245, 240)                                     # V 깃
        return (240, 200, 70) if y in (8, 9) else (80, 150, 80)

    def arm(face, x, y, w, h):
        return (80, 150, 80) if y < 10 else SKIN

    def leg(face, x, y, w, h):
        return (190, 50, 50) if y < 11 else (245, 245, 240)

    def band(face, x, y, w, h):
        return (210, 40, 40) if face in ('top',) and y == 3 or face in ('right', 'left') and y == 1 else None
    return build('leader_erika_ps', (25, 25, 30), (10, 10, 15), body, arm, leg, eye=(40, 40, 50), long_hair=True, hat_at=band)


def leader_koga_ps():
    """독수: 보라 닌자복, 얼굴 아래 가리개, 회색 목도리, 까만 머리."""
    purple = (80, 50, 110)

    def body(face, x, y, w, h):
        return (170, 170, 180) if y < 2 else (purple if y != 8 else (40, 30, 50))

    def arm(face, x, y, w, h):
        return purple if y < 10 else (40, 30, 50)

    def leg(face, x, y, w, h):
        return purple if y < 9 else (40, 30, 50)
    mask = [(x, 6, (70, 45, 95)) for x in range(8)] + [(x, 7, (70, 45, 95)) for x in range(8)]
    return build('leader_koga_ps', (30, 30, 35), (15, 15, 20), body, arm, leg, eye=(80, 60, 40), extra=mask)


def leader_sabrina_ps():
    """초련: 긴 까만(녹색빛) 머리, 빨간 상의 + 까만 허리띠, 까만 타이츠."""
    def body(face, x, y, w, h):
        return (40, 30, 40) if y in (9, 10) else (190, 40, 60)

    def arm(face, x, y, w, h):
        return (190, 40, 60) if y < 11 else SKIN

    def leg(face, x, y, w, h):
        return (30, 25, 35)
    def back_hair(face, x, y, w, h):                                    # 등까지 내려오는 긴 머리
        return ((35, 55, 50) if (x + y) % 4 else (20, 35, 30)) if face == 'back' and y < 8 else None
    return build('leader_sabrina_ps', (35, 55, 50), (20, 35, 30), body, arm, leg, eye=(170, 40, 60), long_hair=True, jacket_at=back_hair)


def leader_blaine_ps():
    """강연: 대머리, 흰 콧수염, 까만 선글라스, 흰 가운."""
    bald, mous = (235, 190, 160), (240, 240, 240)

    def body(face, x, y, w, h):
        if face == 'front' and x in (3, 4):
            return (60, 60, 70)                                        # 가운 안 셔츠
        return (245, 245, 245)

    def arm(face, x, y, w, h):
        return (245, 245, 245) if y < 10 else SKIN

    def leg(face, x, y, w, h):
        return (110, 80, 55) if y < 10 else (50, 35, 25)
    glasses = [(x, 4, (25, 25, 30)) for x in range(1, 7)] + [(1, 5, (25, 25, 30)), (2, 5, (25, 25, 30)), (5, 5, (25, 25, 30)), (6, 5, (25, 25, 30)),
                                                             (3, 5, (25, 25, 30)), (4, 5, (25, 25, 30))]
    glasses += [(x, 6, mous) for x in range(2, 6)] + [(1, 7, mous), (6, 7, mous)]
    return build('leader_blaine_ps', bald, (225, 180, 150), body, arm, leg, extra=glasses)


def leader_giovanni_ps():
    """비주기: 까만 머리, 주황빛 갈색 정장 + 검은 셔츠·빨간 넥타이."""
    suit = (190, 110, 50)

    def body(face, x, y, w, h):
        if face == 'front' and x in (3, 4):
            return (180, 30, 40) if x == 3 and 1 <= y <= 6 else (30, 30, 35)
        return suit

    def arm(face, x, y, w, h):
        return suit if y < 11 else SKIN

    def leg(face, x, y, w, h):
        return suit if y < 10 else (30, 25, 25)
    return build('leader_giovanni_ps', (30, 30, 35), (15, 15, 20), body, arm, leg, eye=(50, 40, 40))


def champion_cynthia_ps():
    """난천: 긴 금발(한쪽 눈을 가림), 까만 코트, 까만 바지."""
    gold, dark = (245, 215, 120), (215, 180, 90)

    def body(face, x, y, w, h):
        return (30, 30, 35) if not (face == 'front' and x in (3, 4) and y < 3) else (240, 240, 240)

    def arm(face, x, y, w, h):
        return (30, 30, 35) if y < 11 else SKIN

    def leg(face, x, y, w, h):
        return (30, 30, 35)

    def coat(face, x, y, w, h):                                         # 코트 자락·털 장식
        if face == 'front' and y < 1:
            return (60, 60, 65)
        if face == 'back' and y < 9:
            return gold if (x + y) % 4 else dark                       # 등까지 내려오는 금발
        return (25, 25, 30) if face in ('back', 'right', 'left') else None
    cover = [(5, 4, gold), (6, 4, gold), (5, 5, dark), (6, 5, gold), (7, 5, gold)]
    return build('champion_cynthia_ps', gold, dark, body, arm, leg, eye=(70, 70, 80), long_hair=True, jacket_at=coat, extra=cover)


def trainer_red_ps():
    """레드: 빨강·흰 모자, 까만 머리, 빨간 반팔 재킷 + 까만 셔츠, 청바지."""
    red = (200, 40, 40)

    def body(face, x, y, w, h):
        if face == 'front' and x in (3, 4):
            return (30, 30, 35)
        return red if y < 10 else (240, 240, 240)

    def arm(face, x, y, w, h):
        return (240, 240, 240) if y < 2 else (red if y < 4 else SKIN)

    def leg(face, x, y, w, h):
        return (60, 90, 160) if y < 10 else red

    def cap(face, x, y, w, h):
        if face == 'top':
            return red if y > 2 else (240, 240, 240)
        if face in ('front', 'right', 'left', 'back') and y <= 1:
            return (240, 240, 240) if face == 'front' and y == 1 else red
        return None
    return build('trainer_red_ps', (30, 25, 25), (15, 10, 10), body, arm, leg, eye=(170, 40, 40), hat_at=cap)


LEADERS = (leader_brock_ps, leader_misty_ps, leader_lt_surge_ps, leader_erika_ps, leader_koga_ps, leader_sabrina_ps,
           leader_blaine_ps, leader_giovanni_ps, champion_cynthia_ps, trainer_red_ps)
# RCT 트레이너 ID (진행도·레벨 제한이 이 ID를 씀 → 바꾸지 않고, 같은 경로의 스킨만 우리 모드가 덮어씀)
RCT_ID = {'leader_brock_ps': 'leader_brock_019e', 'leader_misty_ps': 'leader_misty_019f', 'leader_lt_surge_ps': 'leader_lt_surge_01a0',
          'leader_erika_ps': 'leader_erika_01a1', 'leader_koga_ps': 'leader_koga_01a2', 'leader_sabrina_ps': 'leader_sabrina_01a4',
          'leader_blaine_ps': 'leader_blaine_01a3', 'leader_giovanni_ps': 'leader_giovanni_015e',
          'champion_cynthia_ps': 'champion_cynthia_03a5', 'trainer_red_ps': 'trainer_red_0003'}

if __name__ == '__main__' and sys.argv[1:2] == ['--preview']:
    # 적용하지 않고 미리보기 폴더에만: python3 tools/make_skins.py --preview <폴더>
    Path(sys.argv[2]).mkdir(parents=True, exist_ok=True)
    for make in LEADERS:
        make().save(Path(sys.argv[2]) / f'{make.__name__}.png')
elif __name__ == '__main__':
    (OUT / 'textures/npcs').mkdir(parents=True, exist_ok=True)
    (OUT / 'bedrock/npcs/variations').mkdir(parents=True, exist_ok=True)
    for make in (nurse, merchant, gym_guide, tutorial_guide):
        name = make.__name__
        tex = f'pokeserver:textures/npcs/{name}.png'
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
    # 사천왕 중 RCT에 없는 챔피언: RCT가 트레이너 ID로 찾는 스킨 자리에 둠
    rct = OUT.parent / 'rctmod/textures/trainers/single'
    rct.mkdir(parents=True, exist_ok=True)
    for make in (champion_leon_ps, champion_steven_ps):
        make().save(rct / f'{make.__name__}.png')
        print('skin', make.__name__)
    # 3. 관장·챔피언 원작풍 스킨: RCT 모드의 같은 경로 그림이 우리 모드 것보다 우선이라, 항상 켜지는 내장 리소스팩으로 덮어씀
    pack = OUT.parent.parent / 'resourcepacks/leaders/assets/rctmod/textures/trainers/single'
    pack.mkdir(parents=True, exist_ok=True)
    for make in LEADERS:
        (rct / f'{RCT_ID[make.__name__]}.png').unlink(missing_ok=True)
        make().save(pack / f'{RCT_ID[make.__name__]}.png')
        print('skin', RCT_ID[make.__name__])
