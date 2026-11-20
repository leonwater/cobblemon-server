#!/usr/bin/env python3
"""배틀 화면 텍스처 다시 그리기 (참고 사진: 납작한 어두운 반투명 판 + 얇은 테두리 + 둥근 모서리, 색 아이콘 칸).

Cobblemon 원본(mod/libs의 jar)을 읽어 같은 자리·같은 비율로 2배 해상도로 그림 →
내장 리소스팩(resourcepacks/leaders)에 넣음. 글자·체력 막대·아이콘 위치는 Cobblemon 코드가 정하므로
그 자리(초상화 창, 체력 막대 홈, 기술 타입 아이콘 칸)는 원본과 맞춤. 글자 위치 조정은 BattleUiMixin.

쓰기: python3 tools/battle_skin.py [--preview out.png]
"""
import glob, io, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "mod/src/main/resources/resourcepacks/leaders/assets/cobblemon/textures/gui/battle"
SRC = "assets/cobblemon/textures/gui/battle/"
S = 2  # 해상도 배수 (Cobblemon은 UV를 비율로 쓰므로 크게 그려도 같은 크기로 보임)

BODY = (16, 19, 25, 222)        # Theme.PANEL
BODY_HOVER = (38, 44, 56, 238)
BORDER = (74, 83, 102, 255)     # Theme.BORDER
ACCENT = (136, 160, 200, 255)   # Theme.ACCENT
GROOVE = (6, 7, 10, 235)
STRIP = (10, 12, 16, 150)
UNDER = (34, 40, 52, 255)


def jar():
    return zipfile.ZipFile(sorted(glob.glob(str(ROOT / "mod/libs/Cobblemon-*.jar")))[-1])


def orig(z, name):
    return Image.open(io.BytesIO(z.read(SRC + name))).convert("RGBA")


def canvas(w, h):
    return Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))


def rr(d, x1, y1, x2, y2, fill, outline=None, r=3):
    """둥근 사각형 (원본 1칸 단위 좌표, 끝 포함 안 함). 테두리 두께 1칸."""
    d.rounded_rectangle([x1 * S, y1 * S, x2 * S - 1, y2 * S - 1], radius=r * S, fill=fill,
                        outline=outline, width=S if outline else 0)


def glyph(src, box, thr=200):
    """원본에서 흰 그림(아이콘)만 떼어냄: 밝고 색이 없는 픽셀."""
    g = src.crop(box)
    out = Image.new("RGBA", g.size, (0, 0, 0, 0))
    for y in range(g.height):
        for x in range(g.width):
            r, gg, b, a = g.getpixel((x, y))
            if a > 0 and min(r, gg, b) >= thr:
                out.putpixel((x, y), (255, 255, 255, 255))
    bb = out.getbbox()
    return out.crop(bb) if bb else out


def tint(img, color):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3]:
                px[x, y] = (*color[:3], px[x, y][3])
    return img


def paste_center(dst, g, cx, cy):
    g = g.resize((g.width * S, g.height * S), Image.NEAREST)
    dst.alpha_composite(g, (int(cx * S - g.width / 2), int(cy * S - g.height / 2)))


# ── 행동 버튼 (싸운다·포켓몬·가방·도망·포기) 90x26 × 2상태: 왼쪽 색 아이콘 칸 + 이름 ──
MENU = {"fight": (210, 75, 75), "switch": (62, 160, 85), "bag": (224, 160, 48),
        "run": (60, 140, 210), "forfeit": (220, 222, 226)}


def menu(z, name, color):
    src = orig(z, f"battle_menu_{name}.png")
    ic = glyph(src, (58, 0, 90, 26))
    im = canvas(90, 52)
    d = ImageDraw.Draw(im)
    for st in (0, 1):
        y = st * 26
        rr(d, 0, y, 90, y + 26, BODY_HOVER if st else BODY, ACCENT if st else BORDER)
        tile = color if st else tuple(int(c * 0.85) for c in color)
        rr(d, 3, y + 3, 23, y + 23, tile + (255,), r=2)
        g = tint(ic.copy(), (40, 44, 52) if name == "forfeit" else (255, 255, 255))
        paste_center(im, g, 13, y + 13)
    return im


# ── 기술 버튼 92x24: 바탕(타입 색으로 물듦) + 덮개(물들지 않음) ──
def move_base():
    im = canvas(92, 48)
    d = ImageDraw.Draw(im)
    for st, (ring, tile) in enumerate(((70, 205), (255, 255))):
        y = st * 24
        rr(d, 0, y, 92, y + 24, (ring, ring, ring, 255))      # 테두리 링 (덮개 밖으로 1칸 보임)
        rr(d, 2, y + 2, 21, y + 22, (tile, tile, tile, 255), r=2)  # 타입 아이콘 칸
    return im


def move_overlay():
    im = canvas(92, 24)
    d = ImageDraw.Draw(im)
    rr(d, 1, 1, 91, 23, (16, 19, 25, 236), r=2)
    d.rectangle([22 * S, 13 * S, 90 * S - 1, 22 * S - 1], fill=(8, 10, 14, 236))   # 아래 줄 (분류·PP)
    d.rounded_rectangle([2 * S, 2 * S, 21 * S - 1, 22 * S - 1], radius=2 * S, fill=(0, 0, 0, 0))  # 아이콘 칸 구멍
    return im


# ── 체력 판 140x40: 초상화 창(5,9 ~ 33,37 투명) + 이름 띠 + 체력 막대 홈(40~136, 21~27) ──
def info_base():
    im = canvas(140, 40)
    d = ImageDraw.Draw(im)
    rr(d, 1, 5, 139, 29, BODY, BORDER)                     # 이름·막대 판
    rr(d, 1, 5, 37, 40, BODY, BORDER)                      # 초상화 틀
    d.rectangle([2 * S, 6 * S, 36 * S - 1, 28 * S - 1], fill=BODY)  # 두 판 이음매 지움
    d.rounded_rectangle([5 * S, 9 * S, 33 * S - 1, 37 * S - 1], radius=2 * S, fill=(0, 0, 0, 0))
    rr(d, 39, 21, 137, 27, GROOVE, r=1)                    # 체력 막대 홈
    return im


def underlay(w, h):
    im = canvas(w, h)
    rr(ImageDraw.Draw(im), 0, 0, w, h, UNDER, r=2)
    return im


# ── 배틀 기록 ──
def log(z, name, w, h):
    src = orig(z, name)
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    rr(d, 0, 0, w, h, BODY, BORDER, r=4)
    paste_center(im, glyph(src, (w - 12, h - 10, w, h), 140), w - 6, h - 5)   # 펼치기 화살표
    return im


def back(z):
    src = orig(z, "battle_back.png")
    ic = glyph(src, (0, 0, 58, 34))
    im = canvas(58, 68)
    d = ImageDraw.Draw(im)
    for st in (0, 1):
        y = st * 34
        rr(d, 2, y + 2, 56, y + 30, BODY_HOVER if st else BODY, ACCENT if st else BORDER, r=4)
        paste_center(im, ic, 29, y + 16)
    return im


def flat(src):
    """나머지(파티·대상 선택, 작은 체력 판 등): 모양은 두고 어두운 색으로. 흰 그림·색 있는 상태는 유지."""
    out = Image.new("RGBA", src.size)
    sp, op = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = sp[x, y]
            if not a:
                op[x, y] = (0, 0, 0, 0)
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            if mn >= 225:
                op[x, y] = (r, g, b, a)
            elif mx - mn > 60:
                op[x, y] = (int(r * .75), int(g * .75), int(b * .75), a)
            else:
                l = (r + g + b) / 3 / 255
                op[x, y] = (int(12 + 70 * l), int(14 + 76 * l), int(19 + 90 * l), min(a, 230))
    return out.resize((src.width * S, src.height * S), Image.NEAREST)


def build():
    z = jar()
    out = {f"battle_menu_{n}.png": menu(z, n, c) for n, c in MENU.items()}
    out["battle_move.png"] = move_base()
    out["battle_move_overlay.png"] = move_overlay()
    out["battle_info_base.png"] = info_base()
    out["battle_info_base_flipped.png"] = info_base().transpose(Image.FLIP_LEFT_RIGHT)
    out["battle_info_underlay.png"] = underlay(28, 28)
    out["battle_info_underlay_condensed.png"] = underlay(18, 16)
    out["battle_log.png"] = log(z, "battle_log.png", 169, 55)
    out["battle_log_expanded.png"] = log(z, "battle_log_expanded.png", 169, 101)
    out["battle_back.png"] = back(z)
    for n in ["battle_info_base_condensed.png", "battle_info_base_flipped_condensed.png", "party_select.png",
              "party_select_disabled.png", "target_select.png", "target_select_disabled.png", "triple_battle_shift.png"]:
        out[n] = flat(orig(z, n))
    return out


def main():
    out = build()
    OUT.mkdir(parents=True, exist_ok=True)
    for n, im in out.items():
        im.save(OUT / n, optimize=True)
    print(f"{len(out)}개 → {OUT.relative_to(ROOT)}")
    if "--preview" in sys.argv:
        tiles = [im for im in out.values()]
        W = 760
        sheet = Image.new("RGBA", (W, 900), (90, 120, 80, 255))
        x = y = rowh = 0
        for im in tiles:
            if x + im.width > W:
                x, y, rowh = 0, y + rowh + 6, 0
            sheet.alpha_composite(im, (x, y))
            x += im.width + 6
            rowh = max(rowh, im.height)
        sheet.crop((0, 0, W, y + rowh)).save(sys.argv[sys.argv.index("--preview") + 1])


if __name__ == "__main__":
    main()
