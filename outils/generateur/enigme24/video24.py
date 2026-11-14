import json, math, random, sys, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import soundfile as sf

W, H, FPS = 1080, 1920, 30
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
_fc = {}
def F(s):
    s = max(1, int(s))
    if s not in _fc: _fc[s] = ImageFont.truetype(FB, s)
    return _fc[s]


NUM = "24"; TITRE = "LES POTEAUX DE LA CLÔTURE"; CONTRAINTE = "SA PLACE EN JEU"
TITRE_HIER = "LE RAIL À COUPER"
HOOK = ["COMPTE SES POTEAUX", "OU IL EST VIRÉ !"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Il compte ses poteaux, ou il est viré !",
        "Il doit planter une clôture de 10 mètres.",
        "Un poteau à chaque mètre, aux 2 bouts aussi.",
        "Le petit crie : 10 poteaux ! Et le chef éclate de rire.",
        "Combien de poteaux en tout : 10, 11, ou 9 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 9 minutes, pas 10 !"]
NL = len(SUBS)
GAP = 0.3
s0 = 0.0
s1 = s0 + D[0] + 0.1
s2 = s1 + D[1] + GAP
s3 = s2 + D[2] + GAP
s4 = s3 + D[3] + GAP
CS = s4 + D[4] - 0.2
CE = CS + CHR
s5 = CE + 0.05
STAMP = s5 + D[5] * 0.55
ANS = s5 + D[5] + 0.2
s6 = ANS + 0.2
FADE = s6 + D[6] + 0.5
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, s5, s6]
NF = int(round(T * FPS))
KEY = [["poteaux", "viré"], ["clôture", "10", "mètres"], ["poteau", "chaque", "mètre", "2", "bouts"],
       ["10", "poteaux", "rire"], ["poteaux", "10", "11", "9"], ["commentaire", "vite"], ["9", "minutes", "pas", "10"]]
TORCH = [(150, 400), (930, 400)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

CHAR['PETIT'] = dict(x=250, col=(70, 170, 200), hair=(150, 90, 40), style='short', skin=(236, 180, 136))
CHAR['CHEF'] = dict(x=850, col=(210, 70, 60), hair=(40, 30, 30), style='short', skin=(206, 150, 106))
T_CLOT = wtime(1, 'clôture'); T_10M = wtime(1, '10')
T_POTEAU = wtime(2, 'poteau'); T_BOUTS = wtime(2, 'bouts')
T_FAUX = wtime(3, '10')
T_SOURIT = wtime(3, 'éclate')
T_TOUT = wtime(4, 'poteaux')
T_REP = wtime(6, '9')
FX0, FX1 = 90, 990; MPX = (FX1 - FX0) / 10   # clôture de 10 m (90 px = 1 m)
FTOP, FGND = 640, 780
BX0, BX1, BY = 70, 1010, 600   # rail à couper (10 morceaux)
KIDS = 0.8
CHRONO_XY = (540, 1010)
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 690
FLOOR = 930
XP, XG = 250, 850
KM = 330            # 1 km = 330 px
TX0, TX1 = 400, 400 + KM   # tunnel
TRACK = 640

def wall(S):
    """cour du cachot : mur de pierre brun-violet, sol de terre, torches (retour au donjon, T19 abandonné)"""
    rnd = random.Random(5)
    im = Image.new('RGB', (W * S, H * S), (30, 21, 30))
    d = ImageDraw.Draw(im)
    y = 330 * S
    while y < FLOOR * S:
        hgt = rnd.randint(78, 96) * S
        x = -rnd.randint(0, 120) * S
        while x < W * S:
            w = rnd.randint(130, 210) * S
            b = rnd.randint(-10, 10)
            col = (62 + b, 44 + b, 58 + b + rnd.randint(-4, 6))
            d.rounded_rectangle([x + 4 * S, y + 4 * S, x + w - 4 * S, y + hgt - 4 * S], radius=12 * S, fill=col)
            d.rounded_rectangle([x + 10 * S, y + 8 * S, x + w - 14 * S, y + 18 * S], radius=5 * S, fill=(col[0] + 9, col[1] + 7, col[2] + 9))
            x += w
        y += hgt
    # bande de terre où planter la clôture
    d.rectangle([0, FGND * S, W * S, (FGND + 26) * S], fill=(74, 52, 38))
    d.rectangle([0, (FGND + 26) * S, W * S, FLOOR * S], fill=(52, 38, 40))
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    return im

def bracket(d, x0, x1, y, txt, u, col, size=46):
    if u <= 0: return
    m = (x0 + x1) / 2; h = (x1 - x0) / 2 * clamp(u, 0, 1)
    d.line([(m - h, y), (m + h, y)], fill=(16, 10, 16), width=12)
    d.line([(m - h, y), (m + h, y)], fill=col, width=6)
    for xx in (m - h, m + h):
        d.line([(xx, y - 18), (xx, y + 18)], fill=(16, 10, 16), width=12)
        d.line([(xx, y - 16), (xx, y + 16)], fill=col, width=6)
    badge(d, m, y - 46, txt, ease_back(u), fill=col, size=size)

def post(d, x, u, hi=False):
    if u <= 0: return
    h = (FGND + 10 - FTOP) * clamp(u, 0, 1.15)
    top = FGND + 10 - h
    col = (255, 206, 40) if hi else (168, 116, 66)
    d.polygon([(x - 13, top + 16), (x, top), (x + 13, top + 16), (x + 13, FGND + 10), (x - 13, FGND + 10)], fill=col, outline=(20, 12, 12))
    d.line([(x - 5, top + 24), (x - 5, FGND + 4)], fill=tuple(int(c * 0.8) for c in col), width=3)

def rails(d, u):
    if u <= 0: return
    xe = FX0 + (FX1 - FX0) * clamp(u)
    for y in (FTOP + 30, FTOP + 78):
        d.rectangle([FX0, y, xe, y + 14], fill=(130, 90, 54), outline=(20, 12, 12))

def fence_scene(d, t):
    if t < T_CLOT - 0.15: return
    rails(d, (t - (T_CLOT - 0.15)) / 0.5)
    if t < CE:
        bracket(d, FX0, FX1, 560, "10 MÈTRES", (t - (T_10M - 0.15)) / 0.35, (120, 200, 255), size=48)
    if t >= T_POTEAU - 0.15:
        u = ease_back((t - (T_POTEAU - 0.15)) / 0.3)
        hi = t >= T_BOUTS - 0.15
        post(d, FX0, u, hi); post(d, FX0 + MPX, ease_back((t - (T_POTEAU + 0.05)) / 0.3))
        if u > 0.5:
            text_stroke(d, (FX0 + MPX / 2, FTOP + 120), "1 M", F(36), (255, 255, 255), sw=5)
        if t < CE:
            badge(d, 540, 425, "1 POTEAU À CHAQUE MÈTRE", u, fill=(255, 140, 60), size=48)
    if t >= T_BOUTS - 0.15:
        u = ease_back((t - (T_BOUTS - 0.15)) / 0.3)
        post(d, FX1, u, True)
        if t < CE:
            badge(d, FX0 + 10, 612, "BOUT", u, fill=(255, 206, 40), size=34)
            badge(d, FX1 - 10, 612, "BOUT", u, fill=(255, 206, 40), size=34)
        for k, x in enumerate((370, 590, 810)):
            text_stroke(d, (x, FTOP + 62 + 6 * math.sin(t * 5 + k)), "?", F(int(80 * clamp(u, 0, 1.1)) + 1), (255, 214, 50), sw=7)

def answer_scene(d, t):
    """réponse #23 : le rail en 10 morceaux, 9 traits de coupe qui apparaissent un par un ; « 10 » barré en rouge (T22)"""
    rail_bar(d, t, show_pieces=True)
    pw = (BX1 - BX0) / 10
    for k in range(1, 10):
        tk = ANS + 0.15 + (k - 1) * 0.12
        if t >= tk:
            x = BX0 + k * pw
            d.line([(x, BY - 40), (x, BY + 40)], fill=(16, 10, 16), width=12)
            d.line([(x, BY - 38), (x, BY + 38)], fill=(255, 60, 50), width=6)
            if t - tk < 0.15:
                for a in range(6):
                    ang = -0.5 - a * 0.4
                    d.line([(x, BY - 30), (x + 40 * math.cos(ang), BY - 30 + 40 * math.sin(ang))], fill=(255, 200, 80), width=4)
    ncut = sum(1 for k in range(1, 10) if t >= ANS + 0.15 + (k - 1) * 0.12)
    if ncut > 0:
        badge(d, 540, 470, f"{ncut} COUPE" + ("S" if ncut > 1 else ""), 1, fill=(255, 140, 60), size=52)
    if t >= T_REP - 0.3:
        badge(d, 540, 800, "9 MINUTES !", ease_back((t - T_REP + 0.3) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
    tp = wtime(6, 'pas') - 0.15
    if t >= tp:
        u = ease_back((t - tp) / 0.3)
        badge(d, 540, 960, "10 MINUTES", u, fill=(150, 140, 150), tcol=(60, 50, 60), size=60)
        if t >= tp + 0.2:
            v = clamp((t - tp - 0.2) / 0.2)
            a, b = (350, 978), (730, 942)
            xe = (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)
            d.line([a, xe], fill=(16, 10, 16), width=16)
            d.line([a, xe], fill=RED, width=9)
            badge(d, 540, 1070, "10 MORCEAUX = 9 COUPES", v, fill=(255, 206, 40), size=46)

def rail_bar(d, t, show_pieces):
    y0, y1 = BY - 22, BY + 22
    for x in (BX0 + 120, BX1 - 120):   # tréteaux
        d.polygon([(x - 50, TRACK + 14), (x - 8, y1), (x + 8, y1), (x + 50, TRACK + 14)], fill=(110, 76, 48), outline=(30, 18, 14))
    d.rounded_rectangle([BX0 - 4, y0 - 4, BX1 + 4, y1 + 4], radius=8, fill=(16, 10, 16))
    pw = (BX1 - BX0) / 10
    for k in range(10):
        a = BX0 + k * pw; b = a + pw
        if show_pieces:
            col = (176, 180, 196) if k % 2 == 0 else (120, 126, 146)
        else:
            col = (150, 154, 170)
        d.rectangle([a, y0, b, y1], fill=col)
        d.rectangle([a, y0, b, y0 + 8], fill=tuple(min(255, c + 50) for c in col))
    if show_pieces:
        for k in range(10):
            cx = BX0 + (k + 0.5) * pw
            d.text((cx, BY + 2), str(k + 1), font=F(38), fill=(24, 18, 30), anchor='mm')

def saw(d, x, t):
    dx = math.sin(t * 28) * 30
    y = BY - 24
    d.polygon([(x - 110 + dx, y - 70), (x + 70 + dx, y - 70), (x + 70 + dx, y - 6), (x - 110 + dx, y - 6)], fill=(210, 214, 226), outline=(20, 14, 20))
    for k in range(9):
        xx = x - 110 + dx + k * 20
        d.polygon([(xx, y - 6), (xx + 10, y + 6), (xx + 20, y - 6)], fill=(210, 214, 226))
    d.rounded_rectangle([x + 60 + dx, y - 86, x + 130 + dx, y - 20], radius=14, fill=(170, 60, 40), outline=(20, 14, 20), width=4)
    rnd = random.Random(int(t * 30))
    for k in range(8):
        ang = rnd.uniform(-2.6, -0.5); r = rnd.uniform(20, 70)
        d.line([(x, BY - 20), (x + r * math.cos(ang), BY - 20 + r * math.sin(ang))], fill=(255, 200, 80), width=4)

BUBS = [
    ('PETIT', "10 poteaux !", lambda: T_FAUX - 0.15, lambda: s4, 320, 800, 270),
    ('CHEF', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: s4, 760, 760, 840),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:6]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP + 60, 960), (0.4, 1.0, 540, 960), (s3 - 0.2, 1.0, 540, 960),
            (s3 + 0.3, 1.04, 480, 1000), (T_SOURIT - 0.1, 1.04, 480, 1000), (T_SOURIT + 0.3, 1.04, 600, 1000), (s4 - 0.1, 1.04, 600, 1000),
            (s4 + 0.4, 1.0, 540, 960), (CE, 1.03, 540, 1000), (CE + 0.6, 1.02, 540, 980), (ANS, 1.02, 540, 980)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_CLOT, 8), (T_POTEAU, 8), (T_BOUTS, 8), (T_FAUX, 12), (T_SOURIT, 14), (s4, 8), (STAMP, 18)]:
        if 0 <= t - hh < 0.35:
            a = (1 - (t - hh) / 0.35) * amp
            sx += a * math.sin((t - hh) * 90 + 1.0); sy += a * math.cos((t - hh) * 77)
    return sx, sy

GREEN = (90, 200, 120); RED = (230, 60, 50)
def mouth_at(i, t):
    st = STARTS[i]
    if not (st + 0.02 <= t < st + D[i]): return 0
    k = int((t - st) * FPS); e = G[f'env{i}']
    return clamp(e[k] * 1.6) if k < len(e) else 0

def init():
    random.seed(1)
    for nm, im in [('r', wall(2))]:
        base = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32)
        G[nm + 'dark'] = Image.fromarray(np.clip(base * 0.85 + glow_layer(0.26) * 0.6, 0, 255).astype(np.uint8))
        G[nm + 'lit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.48) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['hookband'] = grad_band(520, 1020, 0.6)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    for i in (3, 4): G[f'env{i}'] = mouth_env(i)

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['rdark'], G['rlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    fence_scene(d, t)
    pm = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    im = draw_person('CHEF', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='CHEF')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PETIT', t, pm, (t % 3.2) < 0.12, mood, label='LE PETIT')
    im = im.resize((int(im.width * KIDS), int(im.height * KIDS)), Image.LANCZOS)
    img.alpha_composite(im, (int(XP - im.width / 2), int(PY + 560 * (1 - KIDS) - 10)))
    d = ImageDraw.Draw(img)
    if s4 - 0.05 <= t < CE:
        badge(d, 540, 875, "COMBIEN DE POTEAUX ?", ease_back((t - (s4 - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=60)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=460)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def hook(img, t):
    if t >= HOOK_UP: return
    if t < HOOK_END:
        img.alpha_composite(G['hookband'])
    d = ImageDraw.Draw(img)
    sc = 1 + 0.25 * max(0, 1 - t / 0.15)
    y0 = 770
    if t >= HOOK_END:
        u = ss((t - HOOK_END) / (HOOK_UP - HOOK_END))
        sc = 1 - 0.6 * u; y0 = 770 - 590 * u
    a = 255 if t < HOOK_UP - 0.15 else int(255 * clamp((HOOK_UP - t) / 0.15))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    fs = int(124 * sc)
    while max(dl.textlength(l, font=F(fs)) for l in HOOK) > 1010: fs -= 2
    for k, ln in enumerate(HOOK):
        col = (255, 214, 50) if k != len(HOOK) - 1 else (255, 80, 60)
        dl.text((W / 2, y0 + (k - (len(HOOK) - 1) / 2) * fs * 1.08), ln, font=F(fs), fill=col + (255,), stroke_width=max(3, int(12 * sc)), stroke_fill=(10, 6, 12, 255), anchor='mm')
    if a < 255: lay.putalpha(lay.getchannel('A').point(lambda v: v * a // 255))
    img.alpha_composite(lay)


def ui_top(img, d, t, answer=False):
    img.alpha_composite(G['top'])
    d.rectangle([0, 0, int(W * t / T), 12], fill=(255, 206, 40))
    pill = "RÉPONSE D'HIER" if answer else f"ÉNIGME #{NUM}"
    f = F(38); tw = d.textlength(pill, font=f)
    d.rounded_rectangle([40, 40, 40 + tw + 44, 98], radius=29, fill=(255, 206, 40) if not answer else (90, 200, 120))
    d.text((62, 69), pill, font=f, fill=(24, 14, 20), anchor='lm')
    if not answer:
        # pastille PIÈGE dès 0,0 s
        px = 40 + tw + 44 + 16; pul = 1 + 0.06 * math.sin(t * 8)
        fp = F(int(34 * pul)); pw = d.textlength("PIÈGE", font=fp)
        d.rounded_rectangle([px, 69 - 29 * pul, px + pw + 40, 69 + 29 * pul], radius=29, fill=(220, 40, 40), outline=(255, 255, 255), width=3)
        d.text((px + 20 + pw / 2, 70), "PIÈGE", font=fp, fill=(255, 255, 255), anchor='mm')
        f2 = F(30); lab = "DIFFICULTÉ "
        x = W - 40 - d.textlength(lab, font=f2) - 5 * 30
        d.text((x, 69), lab, font=f2, fill=(255, 255, 255), anchor='lm')
        x += d.textlength(lab, font=f2)
        for k in range(5):
            d.ellipse([x + k * 30 + 2, 57, x + k * 30 + 24, 79], fill=(255, 80, 60) if k < 4 else (90, 80, 90))
    title = TITRE_HIER if answer else TITRE
    tu = 1.0 if answer else (ease_back((t - (HOOK_UP - 0.15)) / 0.3) if t >= HOOK_UP - 0.15 else 0)
    if tu > 0:
        ft = F(80 * clamp(tu, 0.05, 1.15))
        tw = sum(d.textlength(ch, font=ft) for ch in title)
        while tw > 1000:
            ft = F(ft.size - 2); tw = sum(d.textlength(ch, font=ft) for ch in title)
        x = W / 2 - tw / 2
        for k, ch in enumerate(title):
            cw = d.textlength(ch, font=ft)
            y = 175 + 7 * math.sin(t * 4 + k * 0.45)
            d.text((x + cw / 2, y), ch, font=ft, fill=(255, 214, 50), stroke_width=7, stroke_fill=(20, 10, 16), anchor='mm')
            x += cw
    if not answer:
        f3 = F(38); tw = d.textlength(CONTRAINTE, font=f3)
        d.rounded_rectangle([W / 2 - tw / 2 - 26, 252, W / 2 + tw / 2 + 26, 312], radius=30, fill=(200, 44, 44))
        d.text((W / 2, 283), CONTRAINTE, font=f3, fill=(255, 255, 255), anchor='mm')



def outro_cta(img, d, t):
    if not (s5 - 0.05 <= t < ANS): return
    u = ease_back((t - s5) / 0.3)
    f = F(int(56 * clamp(u, 0, 1.2)) + 1)
    y = 560
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS 10, 11 OU 9", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('10', 'POTEAUX', '10'), ('11', 'POTEAUX', '11'), ('9', 'POTEAUX', '9')]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    if not (wtime(4, '10') - 0.3 <= t < ANS): return
    for k, (big, small, w_) in enumerate(CHN):
        col = CHC[k]
        ts = wtime(4, w_) - 0.15
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 3) % 3 == k: pul = 1.08
        s = u * pul
        x = 195 + k * 345; y = 1290
        bw, bh = 310 * s, 160 * s
        d.rounded_rectangle([x - bw / 2 - 7, y - bh / 2 - 7, x + bw / 2 + 7, y + bh / 2 + 7], radius=int(46 * s) + 7, fill=col)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(46 * s), fill=(26, 18, 30))
        if s > 0.3:
            d.text((x, y + 24 * s), big, font=F(90 * s), fill=(255, 255, 255), anchor='mm')
            d.text((x, y - 50 * s), small, font=F(34 * s), fill=col, anchor='mm')

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['rdark'], G['rlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    answer_scene(d, t)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def frame(fi):
    t = fi / FPS
    if t < ANS:
        img = camera(scene(t), t)
        img.alpha_composite(G['vig'])
        red_vig(img, t)
        d = ImageDraw.Draw(img)
        ui_top(img, d, t)
        chrono(img, d, t)
        outro_cta(img, d, t)
        choices(img, d, t)
        if t < ANS - 0.3: img.alpha_composite(G['sub'])
        d = ImageDraw.Draw(img)
        if t < ANS - 0.05: draw_subs(img, d, t)
        hook(img, t)
        if ANS - 0.25 < t: img = Image.blend(img, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t - (ANS - 0.25)) / 0.25))
    else:
        img = answer_frame(t)
        img.alpha_composite(G['vig'])
        d = ImageDraw.Draw(img)
        ui_top(img, d, t, answer=True)
        img.alpha_composite(G['sub'])
        d = ImageDraw.Draw(img)
        draw_subs(img, d, t)
        if t < ANS + 0.25: img = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), img, clamp((t - ANS) / 0.25))
    if t >= FADE:
        if 'f0' not in G: G['f0'] = frame(0)
        img = Image.blend(img.convert('RGB'), G['f0'], clamp((t - FADE) / 0.4))
    return img.convert('RGB')

def work(fi):
    return frame(fi).tobytes()

if __name__ == '__main__':
    import multiprocessing as mp
    mode = sys.argv[1]
    if mode == 'still':
        init()
        for tt in sys.argv[2:]:
            fi = min(NF - 1, int(float(tt) * FPS))
            frame(fi).save(f'f_{tt}.png')
        print('T', T, 'CS', CS, 'ANS', ANS, 'starts', [round(x, 2) for x in STARTS], 'faux', T_FAUX)
    else:
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_FAUX, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')

