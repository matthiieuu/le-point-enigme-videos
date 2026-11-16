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



NUM = "26"; TITRE = "LES BOUGIES DU CACHOT"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "L'ESCALIER DE LA TOUR"
HOOK = ["10 BOUGIES DÉCIDENT", "DE SA LIBERTÉ !"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["10 bougies décident de sa liberté !",
        "Les 10 sont allumées.",
        "Le vent en éteint 3.",
        "Les 7 autres brûlent jusqu'au bout.",
        "Le prisonnier crie : 7 ! Et le gardien éclate de rire.",
        "À la fin, combien reste-t-il de bougies : 7, 3, ou 10 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 75 marches, pas 60 !"]
NL = len(SUBS)
GAP = 0.3
s0 = 0.0
s1 = s0 + D[0] + 0.1
s2 = s1 + D[1] + GAP
s3 = s2 + D[2] + GAP
s4 = s3 + D[3] + GAP
sQ = s4 + D[4] + GAP
CS = sQ + D[5] - 0.2
CE = CS + CHR
s5 = CE + 0.05
STAMP = s5 + D[6] * 0.55
ANS = s5 + D[6] + 0.2
s6 = ANS + 0.2
FADE = s6 + D[7] + 0.5
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, sQ, s5, s6]
NF = int(round(T * FPS))
KEY = [["10", "bougies", "liberté"], ["10", "allumées"], ["vent", "3"], ["7", "bout"],
       ["7", "rire"], ["fin", "7", "3", "10", "bougies"], ["commentaire", "vite"], ["75", "marches", "pas", "60"]]
TORCH = [(80, 380), (1000, 380)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

T_10 = wtime(1, '10')
T_VENT = wtime(2, 'vent'); T_ET = wtime(2, '3')
T_7 = wtime(3, '7'); T_BOUT = wtime(3, 'bout')
T_FAUX = wtime(4, '7')
T_SOURIT = wtime(4, 'éclate')
T_FIN = wtime(5, 'fin')
T_REP = wtime(7, '75')
CHRONO_XY = (540, 1040)
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 700
FLOOR = 930
XP, XG = 250, 850
CHAR['PRISONNIER']['x'] = XP; CHAR['GARDIEN']['x'] = XG
# bougies : 10 sur une étagère de pierre
CX = [205 + k * 74.4 for k in range(10)]
SHELF = 650
OFF = (1, 4, 8)          # les 3 que le vent éteint
CH0 = 150                # hauteur d'une bougie neuve
# tour (réponse #25) : 6 étages
SX0, SX1 = 360, 720
def FY(k): return 830 - (k - 1) * 70
NSTEP = 6

def wall(S, mode):
    """mur de pierre brun-violet du donjon, torches ; mode 'cachot' (soupirail + étagère) ou 'tour' (réponse d'hier)"""
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
    if mode == 'cachot':
        # soupirail à barreaux (d'où vient le vent)
        d.rounded_rectangle([430 * S, 348 * S, 650 * S, 430 * S], radius=10 * S, fill=(14, 18, 34))
        for k in range(6):
            xx = (452 + k * 35) * S
            d.rectangle([xx - 5 * S, 348 * S, xx + 5 * S, 430 * S], fill=(96, 92, 104))
        d.rounded_rectangle([422 * S, 340 * S, 658 * S, 438 * S], radius=12 * S, outline=(90, 70, 84), width=8 * S)
        # étagère de pierre
        d.rectangle([150 * S, SHELF * S, 930 * S, (SHELF + 30) * S], fill=(110, 86, 98))
        d.rectangle([150 * S, (SHELF + 30) * S, 930 * S, (SHELF + 40) * S], fill=(48, 34, 44))
        for xx in (190, 890):
            d.polygon([(xx - 20) * S, (SHELF + 40) * S, (xx + 20) * S, (SHELF + 40) * S, xx * S, (SHELF + 90) * S], fill=(80, 62, 74))
        d.rectangle([0, 830 * S, W * S, FLOOR * S], fill=(52, 38, 40))
    else:
        d.rounded_rectangle([(SX0 - 70) * S, (FY(6) - 80) * S, (SX1 + 70) * S, (FY(1) + 14) * S], radius=20 * S, fill=(24, 16, 24))
        for k in range(1, 7):
            yy = FY(k)
            d.rectangle([(SX0 - 70) * S, (yy - 2) * S, (SX1 + 70) * S, (yy + 2) * S], fill=(44, 32, 42))
        d.rectangle([(SX0 - 84) * S, (FY(6) - 90) * S, (SX0 - 66) * S, (FY(1) + 14) * S], fill=(80, 60, 74))
        d.rectangle([(SX1 + 66) * S, (FY(6) - 90) * S, (SX1 + 84) * S, (FY(1) + 14) * S], fill=(80, 60, 74))
        d.rectangle([0, (FY(1) + 14) * S, W * S, FLOOR * S], fill=(52, 38, 40))
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    return im

def small_flame(d, x, y, t, k, s=1.0):
    fl = 1 + 0.2 * math.sin(t * 23 + k) + 0.1 * math.sin(t * 37 + 2 * k)
    hh = 34 * fl * s; wx = math.sin(t * 15 + k) * 4
    d.ellipse([x - 26 * s, y - 40 * s, x + 26 * s, y + 10 * s], fill=(120, 70, 30))
    d.polygon([(x - 10 * s, y), (x - 8 * s, y - hh * 0.45), (x + wx, y - hh), (x + 8 * s, y - hh * 0.45), (x + 10 * s, y)], fill=(255, 150, 40))
    d.polygon([(x - 5 * s, y), (x + wx * 0.5, y - hh * 0.6), (x + 5 * s, y)], fill=(255, 236, 150))

def candle(d, k, t):
    x = CX[k]
    off = k in OFF and t >= T_ET - 0.1 and t < CE + 0.3
    # les bougies allumées baissent un peu à partir de « brûlent » (on ne montre pas la fin)
    melt = 0
    if not off and t >= T_7 - 0.1:
        melt = 0.35 * clamp((t - (T_7 - 0.1)) / (CE - T_7))
    h = CH0 * (1 - melt)
    top = SHELF - h
    lit_col = (245, 236, 214)
    col = (176, 172, 182) if off else lit_col
    hi = (not off) and T_7 - 0.15 <= t < CE + 0.3
    d.rounded_rectangle([x - 19, top, x + 19, SHELF + 2], radius=6, fill=col, outline=(255, 150, 40) if hi else (30, 20, 26), width=5 if hi else 2)
    if melt > 0:
        d.ellipse([x - 24, SHELF - 8, x + 24, SHELF + 6], fill=lit_col)
        d.line([(x - 12, top + 4), (x - 12, top + 24 + 30 * melt)], fill=(230, 220, 196), width=6)
    d.line([(x, top), (x, top - 10)], fill=(40, 30, 30), width=3)
    if not off:
        small_flame(d, x, top - 8, t, k)
    else:
        # fumée qui monte de la mèche éteinte
        for j in range(4):
            ph = ((t - T_ET) * 0.9 + j * 0.25) % 1
            yy = top - 14 - ph * 120; xx = x + math.sin(ph * 7 + j) * 12
            r = 8 + ph * 16
            g = int(150 * (1 - ph))
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(g // 2 + 60, g // 2 + 60, g // 2 + 66))

def wind(d, t):
    """rafale qui sort du soupirail et balaie les bougies"""
    if not (T_VENT - 0.2 <= t < T_ET + 0.6): return
    u = (t - (T_VENT - 0.2)) / (T_ET + 0.8 - T_VENT)
    for j in range(5):
        y0 = 440 + j * 30
        xs = 300 + 900 * clamp(u * 1.3 - j * 0.06) - 400
        pts = [(xs + i * 30, y0 + 22 * math.sin(i * 0.6 + j + t * 6) + i * 3) for i in range(12)]
        d.line(pts, fill=(200, 220, 255), width=6, joint='curve')

def candles_scene(d, t):
    wind(d, t)
    for k in range(10): candle(d, k, t)
    if s1 - 0.1 <= t < s2 - 0.1:
        badge(d, 540, 770, "10 BOUGIES ALLUMÉES", ease_back((t - (s1 - 0.1)) / 0.3), fill=(255, 206, 40), size=50)
    if s2 - 0.1 <= t < s3 - 0.1:
        badge(d, 540, 770, "LE VENT EN ÉTEINT 3", ease_back((t - (s2 - 0.1)) / 0.3), fill=(150, 200, 255), size=50)
    if s3 - 0.1 <= t < s4 - 0.1:
        badge(d, 540, 770, "LES 7 AUTRES BRÛLENT", ease_back((t - (s3 - 0.1)) / 0.3), fill=(255, 150, 40), size=50)
    if T_BOUT - 0.1 <= t < s4 - 0.1:
        badge(d, 540, 862, "JUSQU'AU BOUT", ease_back((t - (T_BOUT - 0.1)) / 0.3), fill=(255, 150, 40), size=50)
    if t >= s4 - 0.1 and t < CE + 0.3:
        u = ease_back((t - (s4 - 0.1)) / 0.3)
        text_stroke(d, (540 + 6 * math.sin(t * 5), 455), "?", F(int(90 * clamp(u, 0, 1.1)) + 1), (255, 214, 50), sw=7)

def answer_scene(d, t, tower_flight):
    """réponse #25 : les 5 volées s'allument une par une (15, 30 … 75) ; « 60 » barré en rouge (T22)"""
    n = 0
    for k in range(1, 6):
        tk = ANS + 0.15 + (k - 1) * 0.28
        on = t >= tk
        if on: n = k
        tower_flight(d, k, (255, 150, 40) if on else (118, 98, 112))
    d.rectangle([SX0 - 66, FY(1), SX0, FY(1) + 12], fill=(118, 98, 112), outline=(16, 10, 16))
    for k in range(1, 7):
        lab = "1ER" if k == 1 else f"{k}E"
        hi = k in (1, 6)
        badge(d, 222, FY(k) - 4, lab, 1, fill=(255, 206, 40) if hi else (150, 130, 146), size=50 if hi else 46)
    for k in range(1, n + 1):
        yc = (FY(k) + FY(k + 1)) / 2 - 4
        text_stroke(d, (860, yc), f"+15", F(44), (255, 214, 50), sw=5)
    if n > 0 and t < T_REP - 0.2:
        badge(d, 540, 950, f"{15 * n} MARCHES", 1, fill=(255, 140, 60), size=56)
    if t >= T_REP - 0.2:
        badge(d, 540, 950, "75 MARCHES !", ease_back((t - T_REP + 0.2) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=92)
    tp = wtime(7, 'pas') - 0.15
    if t >= tp:
        u = ease_back((t - tp) / 0.3)
        badge(d, 540, 1100, "60 MARCHES", u, fill=(150, 140, 150), tcol=(60, 50, 60), size=60)
        if t >= tp + 0.2:
            v = clamp((t - tp - 0.2) / 0.2)
            a, b = (330, 1135), (750, 1065)
            xe = (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)
            d.line([a, xe], fill=(16, 10, 16), width=16)
            d.line([a, xe], fill=RED, width=9)
            badge(d, 540, 1220, "5 ÉTAGES × 15 = 75", v, fill=(255, 206, 40), size=50)

def flight(d, k, col, outline=(16, 10, 16), ow=3):
    """volée d'escalier de l'étage k à k+1 (zigzag)"""
    y0, y1 = FY(k), FY(k + 1)
    ltr = (k % 2 == 1)
    xa, xb = (SX0, SX1) if ltr else (SX1, SX0)
    sw = (xb - xa) / NSTEP; rise = (y1 - y0) / NSTEP
    pts = [(xa, y0)]
    for s in range(NSTEP):
        x = xa + s * sw; y = y0 + (s + 1) * rise
        pts += [(x, y), (x + sw, y)]
    pts += [(xb, y1 + 34), (xa + sw, y0 + 14), (xa, y0 + 14)]
    d.polygon(pts, fill=col, outline=outline)
    lx0, lx1 = (SX1, SX1 + 66) if ltr else (SX0 - 66, SX0)
    d.rectangle([lx0, y1, lx1, y1 + 12], fill=col, outline=(16, 10, 16))

BUBS = [
    ('PRISONNIER', "7 !", lambda: T_FAUX - 0.15, lambda: sQ, 450, 900, 300),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: sQ, 640, 1050, 800),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:7]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP + 60, 960), (0.4, 1.0, 540, 960), (s2 - 0.1, 1.0, 540, 960),
            (s2 + 0.3, 1.05, 540, 820), (s4 - 0.2, 1.05, 540, 820),
            (s4 + 0.3, 1.04, 480, 1000), (T_SOURIT - 0.1, 1.04, 480, 1000), (T_SOURIT + 0.3, 1.04, 600, 1000), (sQ - 0.1, 1.04, 600, 1000),
            (sQ + 0.4, 1.0, 540, 960), (CE, 1.03, 540, 1000), (CE + 0.6, 1.02, 540, 980), (ANS, 1.02, 540, 980)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_10, 8), (T_ET, 12), (T_7, 8), (T_FAUX, 12), (T_SOURIT, 14), (sQ, 8), (STAMP, 18)]:
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
    for nm, im in [('c', wall(2, 'cachot')), ('r', wall(2, 'tour'))]:
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
    for i in (4,): G[f'env{i}'] = mouth_env(i)

def chains(d):
    x0 = XP - 60; y0 = PY + 500
    for k in range(9):
        cx = 20 + k * (x0 - 20) / 8; cy = y0 + 18 * math.sin(k / 8 * math.pi)
        if k % 2: d.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], outline=(160, 160, 172), width=5)
        else: d.ellipse([cx - 7, cy - 10, cx + 7, cy + 10], outline=(160, 160, 172), width=5)
    d.rounded_rectangle([x0 - 6, y0 - 12, x0 + 30, y0 + 12], radius=6, fill=(120, 120, 132), outline=(30, 24, 30), width=3)

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['cdark'], G['clit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    candles_scene(d, t)
    pm = mouth_at(4, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    im = draw_person('GARDIEN', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    chains(d)
    if sQ - 0.05 <= t < CE:
        badge(d, 540, 915, "COMBIEN À LA FIN ?", ease_back((t - (sQ - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=60)
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
    y0 = 800
    if t >= HOOK_END:
        u = ss((t - HOOK_END) / (HOOK_UP - HOOK_END))
        sc = 1 - 0.6 * u; y0 = 800 - 620 * u
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
    d.text((W / 2, y - 40), "ÉCRIS 7, 3 OU 10", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('7', 'BOUGIES', '7'), ('3', 'BOUGIES', '3'), ('10', 'BOUGIES', '10')]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    """T23 : les 3 choix sont visibles dès 0,0 s (sous le hook) ; chaque choix grossit quand la voix le dit"""
    if not (t < ANS): return
    for k, (big, small, w_) in enumerate(CHN):
        col = CHC[k]
        u = 1 + 0.1 * max(0, 1 - t / 0.2)
        if u <= 0: continue
        ts = wtime(5, w_) - 0.1
        pul = 1.0
        if ts <= t < ts + 0.45: pul = 1 + 0.14 * math.sin(math.pi * (t - ts) / 0.45)
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
    answer_scene(d, t, flight)
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
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_FAUX, 'WINDT': T_VENT, 'OFFT': T_ET, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')

