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


NUM = "30"; TITRE = "LA GRENOUILLE DU PUITS"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "LES 9 DU CACHOT"
HOOK = ["SI LA GRENOUILLE SORT", "IL EST LIBRE !"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["PRISONNIER : 20 ! Si la grenouille sort, il est libre !",
        "Le puits fait 20 mètres.",
        "Le jour, elle monte de 5 mètres.",
        "La nuit, elle glisse de 4 mètres.",
        "GARDIEN : Quel jour sort-elle ?",
        "PRISONNIER : Le 20e ! GARDIEN : Ha ha ! Tu es sûr ?",
        "Quel jour : 20, 16, ou 15 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 20 fois, pas 10 !"]
_SP = json.load(open('split.json')); SPLIT5 = _SP['split5']; SPLIT0 = _SP['split0']
NL = len(SUBS)
GAP = 0.3
s0 = 0.0
s1 = s0 + D[0] + 0.15
s2 = s1 + D[1] + GAP
s3 = s2 + D[2] + GAP
s4 = s3 + D[3] + GAP
s5b = s4 + D[4] + GAP          # ligne 5 : prisonnier « Le 20e ! » puis gardien
sQ = s5b + D[5] + GAP
CS = sQ + D[6] - 0.2
CE = CS + CHR
s5 = CE + 0.05
STAMP = s5 + D[7] * 0.55
ANS = s5 + D[7] + 0.2
s6 = ANS + 0.2
RELANCE = s6 + D[8] + 0.3      # T25 : la question revient en gros avant la boucle
FADE = RELANCE + 0.9
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, s5b, sQ, s5, s6]
NF = int(round(T * FPS))
KEY = [["20", "grenouille", "libre"], ["20", "mètres", "puits"], ["jour", "monte", "5"], ["nuit", "glisse", "4"],
       ["quel", "jour"], ["20e", "sûr"], ["20", "16", "15"], ["commentaire", "vite"], ["20", "fois", "pas", "10"]]
TORCH = [(70, 640), (1010, 430)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())
def _spread(sub, a, b): return [a + (b - a) * j / len(sub) * 0.9 for j in range(len(sub))]
def _wt5():
    ws = SUBS[5].split(); kg = ws.index('GARDIEN')
    return ws, _spread(ws[:kg], s5b, s5b + SPLIT5 - 0.15) + _spread(ws[kg:], s5b + SPLIT5 - 0.1, s5b + D[5])
WT[5] = _wt5()
def _wt0():
    ws = SUBS[0].split(); kg = ws.index('Si')
    return ws, _spread(ws[:kg], s0, s0 + SPLIT0 - 0.15) + _spread(ws[kg:], s0 + SPLIT0 - 0.05, s0 + D[0])
WT[0] = _wt0()

T_20 = wtime(1, '20'); T_MONTE = wtime(2, 'monte'); T_GLISSE = wtime(3, 'glisse')
T_FAUX = s5b
T_SOURIT = s5b + SPLIT5
T_REP = wtime(8, '20')
CHRONO_XY = (860, 600)
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 700
FLOOR = 930
XP, XG = 430, 880
CHAR['PRISONNIER']['x'] = XP; CHAR['GARDIEN']['x'] = XG
ORANGE = (255, 150, 40)
CHALK = (236, 240, 230)
GREEN = (90, 200, 120); RED = (230, 60, 50)
# puits en coupe (recette #09) : graduation 0-20 m à gauche, grenouille sur la paroi droite
WX0, WX1, WTOP, WBOT = 200, 660, 430, 1250
def YM(m): return 1180 - m * 36
FX = WX1 - 52

def wall(S, mode):
    """mur de pierre brun-violet du donjon ; mode 'puits' (scène) ou 'tableau' (réponse d'hier)"""
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
    if mode == 'tableau':
        d.rounded_rectangle([130 * S, 350 * S, 950 * S, 820 * S], radius=14 * S, fill=(96, 62, 38), outline=(40, 24, 18), width=6 * S)
        d.rectangle([150 * S, 370 * S, 930 * S, 800 * S], fill=(34, 48, 44))
        for k in range(14):
            yy = (380 + k * 30) * S
            d.line([158 * S, yy, 922 * S, yy + 6 * S], fill=(38, 53, 49), width=10 * S)
        d.rectangle([180 * S, 806 * S, 900 * S, 822 * S], fill=(110, 74, 46))
    d.rectangle([0, 830 * S, W * S, FLOOR * S], fill=(52, 38, 40))
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    if mode == 'puits': draw_well(im, S)
    return im

def draw_well(im, S):
    d = ImageDraw.Draw(im)
    d.rectangle([WX0 * S, WTOP * S, WX1 * S, WBOT * S], fill=(18, 12, 18))
    rnd = random.Random(9)
    y = WTOP + 30
    while y < WBOT:
        x = WX0 - rnd.randint(0, 60)
        while x < WX1:
            w = rnd.randint(70, 120); b = rnd.randint(-6, 6)
            d.rounded_rectangle([max(WX0, x + 3) * S, (y + 3) * S, min(WX1, x + w - 3) * S, (y + 44) * S], radius=8 * S, fill=(40 + b, 28 + b, 38 + b))
            x += w
        y += 48
    d.rectangle([WX0 * S, WTOP * S, (WX0 + 22) * S, WBOT * S], fill=(12, 8, 12))
    d.rectangle([(WX1 - 22) * S, WTOP * S, WX1 * S, WBOT * S], fill=(12, 8, 12))
    d.rectangle([WX0 * S, (WBOT - 22) * S, WX1 * S, WBOT * S], fill=(40, 70, 90))
    d.rounded_rectangle([(WX0 - 40) * S, (WTOP - 34) * S, (WX1 + 40) * S, (WTOP + 20) * S], radius=16 * S, fill=(96, 74, 86))
    for k in range(7):
        xx = WX0 - 40 + k * 78
        d.line([xx * S, (WTOP - 34) * S, xx * S, (WTOP + 20) * S], fill=(70, 52, 62), width=4 * S)
    d.rectangle([(WX0 - 40) * S, (WTOP - 34) * S, (WX1 + 40) * S, (WTOP - 24) * S], fill=(120, 96, 108))
    # graduation à gauche
    gx = WX0 - 56
    d.line([gx * S, YM(0) * S, gx * S, YM(20) * S], fill=(220, 200, 170), width=5 * S)
    for m in range(21):
        L = 26 if m % 5 == 0 else 13
        d.line([gx * S, YM(m) * S, (gx + L) * S, YM(m) * S], fill=(220, 200, 170), width=4 * S)
    for m in (0, 10, 20):
        d.text(((gx - 10) * S, YM(m) * S), f"{m} M", font=F(34 * S), fill=(240, 225, 200), anchor='rm')

def frog(d, x, y, t, sc=1.0, jump=0.0):
    """grenouille verte qui grimpe sur la paroi droite, tête vers le haut"""
    bob = 2 * math.sin(t * 6)
    y = y + bob
    k = 1 + 0.25 * jump
    # pattes arrière
    for sgn in (-1, 1):
        d.ellipse([x + sgn * 26 * sc - 18 * sc, y + 18 * sc * k, x + sgn * 26 * sc + 18 * sc, y + 52 * sc * k], fill=(60, 140, 60))
    d.ellipse([x - 40 * sc - 4, y - 36 * sc - 4, x + 40 * sc + 4, y + 40 * sc + 4], fill=(20, 50, 24))
    d.ellipse([x - 40 * sc, y - 36 * sc, x + 40 * sc, y + 40 * sc], fill=(90, 190, 80))
    d.ellipse([x - 22 * sc, y - 6 * sc, x + 22 * sc, y + 30 * sc], fill=(190, 230, 140))
    for sgn in (-1, 1):
        ex, ey = x + sgn * 20 * sc, y - 36 * sc
        d.ellipse([ex - 15 * sc, ey - 15 * sc, ex + 15 * sc, ey + 15 * sc], fill=(90, 190, 80))
        d.ellipse([ex - 9 * sc, ey - 9 * sc, ex + 9 * sc, ey + 9 * sc], fill=(255, 255, 255))
        d.ellipse([ex - 4 * sc, ey - 5 * sc, ex + 4 * sc, ey + 3 * sc], fill=(20, 14, 16))
        # pattes avant agrippées
        d.ellipse([x + sgn * 38 * sc - 10 * sc, y - 20 * sc, x + sgn * 38 * sc + 10 * sc, y], fill=(60, 140, 60))

def frog_m(t):
    a = T_MONTE - 0.1; b = T_GLISSE - 0.1
    if t < a: return 0.0
    if t < a + 1.0: return 5 * ss((t - a) / 1.0)
    if t < b: return 5.0
    if t < b + 1.0: return 5 - 4 * ss((t - b) / 1.0)
    return 1.0

def sun(d, x, y, t, u):
    r = 34 * u
    for k in range(10):
        a = k * math.pi / 5 + t
        d.line([x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3, x + math.cos(a) * r * 1.8, y + math.sin(a) * r * 1.8], fill=(255, 210, 60), width=6)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 210, 60))
def moon(d, x, y, u):
    r = 34 * u
    d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 235, 210))
    d.ellipse([x - r + 18 * u, y - r - 8 * u, x + r + 18 * u, y + r - 8 * u], fill=(40, 46, 90))

def well_scene(d, t):
    # sortie à 20 m (au mot « 20 »)
    if t >= T_20 - 0.15:
        u = ease_back((t - T_20 + 0.15) / 0.3)
        d.line([WX0 + 24, YM(20), WX1 - 24, YM(20)], fill=(255, 206, 40), width=6)
        if t < CE + 0.3:
            badge(d, 430, YM(20) + 52, "SORTIE : 20 M", u, size=46)
        # flèche jaune sur la graduation, à la hauteur de la grenouille
    m = frog_m(t)
    gx = WX0 - 56
    if t >= T_20:
        d.polygon([(gx + 4, YM(m)), (gx + 30, YM(m) - 14), (gx + 30, YM(m) + 14)], fill=(255, 206, 40))
    jump = 1.0 if (T_MONTE - 0.1 <= t < T_MONTE + 0.9) else 0.0
    frog(d, FX - 6, YM(m) - 14, t, 1.3, jump)
    if T_MONTE - 0.1 <= t < T_GLISSE - 0.1:
        u = ease_back((t - T_MONTE + 0.1) / 0.3)
        sun(d, 430, 610, t, clamp(u, 0, 1.2)); badge(d, 430, 720, "+5 M LE JOUR", u, size=52)
    if T_GLISSE - 0.1 <= t < s4 - 0.1:
        u = ease_back((t - T_GLISSE + 0.1) / 0.3)
        moon(d, 430, 610, clamp(u, 0, 1.2)); badge(d, 430, 720, "−4 M LA NUIT", u, fill=RED, tcol=(255, 255, 255), size=52)
    if s4 - 0.1 <= t < CE + 0.3:
        u = ease_back((t - s4 + 0.1) / 0.3)
        badge(d, 400, 650, "JOUR 1 : 1 M", u, fill=(240, 230, 210), size=48)
        v = ease_back((t - s4) / 0.3); pul = 1 + 0.05 * math.sin(t * 8)
        text_stroke(d, (FX - 10 + 4 * math.sin(t * 5), YM(20) + 150), "?", F(int(100 * clamp(v, 0, 1.1) * pul) + 1), (255, 214, 50), sw=7)

# --- réponse #29 : 20 chiffres 9 (10 en unités + 10 en dizaines, 99 compte double) ---
AL = ["9 19 29 39 49 59 69 79 89 99", "90 91 92 93 94 95 96 97 98 99"]
def answer_scene(d, t, img):
    text_stroke(d, (540, 430), "DE 1 À 100", F(56), (255, 214, 50), stroke=(20, 30, 28), sw=4)
    for j, ln in enumerate(AL):
        t0 = ANS + 0.15 + j * 0.45
        if t < t0: continue
        u = ease_back((t - t0) / 0.3)
        y = 540 + j * 150
        text_stroke(d, (520, y), ln, F(int(46 * clamp(u, 0.05, 1.1))), CHALK, stroke=(20, 30, 28), sw=3)
        badge(d, 540, y + 60, "10 EN UNITÉS" if j == 0 else "10 EN DIZAINES", u, fill=ORANGE, size=44)
    # le 99 entouré (compte 2 fois)
    if t >= ANS + 1.0:
        u = clamp((t - ANS - 1.0) / 0.25)
        for (cx, cy) in [(864, 540), (864, 690)]:
            r = 44 * u
            d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], outline=GREEN, width=6)
    if t >= RELANCE: return
    if t >= T_REP - 0.2:
        badge(d, 540, 960, "20 FOIS !", ease_back((t - T_REP + 0.2) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
    tp = wtime(8, 'pas') - 0.15
    if t >= tp:
        u = ease_back((t - tp) / 0.3)
        badge(d, 540, 1110, "10 FOIS", u, fill=(150, 140, 150), tcol=(60, 50, 60), size=64)
        if t >= tp + 0.2:
            v = clamp((t - tp - 0.2) / 0.2)
            a, b = (400, 1145), (680, 1075)
            xe = (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)
            d.line([a, xe], fill=(16, 10, 16), width=16)
            d.line([a, xe], fill=RED, width=9)
            badge(d, 540, 1250, "LE 99 COMPTE 2 FOIS", v, fill=(255, 206, 40), size=50)

BUBS = [
    ('GARDIEN', "Quel jour sort-elle ?", lambda: s4 - 0.1, lambda: s5b - 0.05, 800, 590, 880),
    ('PRISONNIER', "Le 20e !", lambda: T_FAUX - 0.1, lambda: sQ, 430, 790, 430),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: sQ, 800, 600, 880),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:8]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP, 920), (0.4, 1.0, 540, 960), (s1 - 0.1, 1.0, 540, 960),
            (s1 + 0.3, 1.04, 470, 820), (s4 - 0.2, 1.04, 470, 820), (s4 + 0.2, 1.04, 600, 1000), (s5b - 0.2, 1.04, 600, 1000),
            (s5b + 0.3, 1.04, 480, 1000), (T_SOURIT - 0.1, 1.04, 480, 1000), (T_SOURIT + 0.3, 1.04, 600, 1000), (sQ - 0.1, 1.04, 600, 1000),
            (sQ + 0.4, 1.0, 540, 960), (CE, 1.03, 540, 1000), (CE + 0.6, 1.02, 540, 980), (ANS, 1.02, 540, 980)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_20, 8), (T_MONTE + 0.8, 6), (T_GLISSE + 0.8, 8), (T_FAUX, 12), (T_SOURIT, 14), (sQ, 8), (STAMP, 18)]:
        if 0 <= t - hh < 0.35:
            a = (1 - (t - hh) / 0.35) * amp
            sx += a * math.sin((t - hh) * 90 + 1.0); sy += a * math.cos((t - hh) * 77)
    return sx, sy
def mouth_at(i, t):
    st = STARTS[i]
    if not (st + 0.02 <= t < st + D[i]): return 0
    k = int((t - st) * FPS); e = G[f'env{i}']
    return clamp(e[k] * 1.6) if k < len(e) else 0

def init():
    random.seed(1)
    for nm, im in [('c', wall(2, 'puits')), ('k', wall(2, 'tableau'))]:
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
    G['night'] = Image.new('RGBA', (W, H), (20, 30, 90, 0))
    for i in (0, 4, 5): G[f'env{i}'] = mouth_env(i)

def chains(d):
    # chaîne du prisonnier scellée dans la paroi gauche du puits
    x0 = XP - 60; y0 = PY + 500
    for k in range(6):
        cx = WX0 + 24 + k * (x0 - WX0 - 24) / 5; cy = y0 + 14 * math.sin(k / 5 * math.pi)
        if k % 2: d.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], outline=(160, 160, 172), width=5)
        else: d.ellipse([cx - 7, cy - 10, cx + 7, cy + 10], outline=(160, 160, 172), width=5)
    d.rounded_rectangle([x0 - 6, y0 - 12, x0 + 30, y0 + 12], radius=6, fill=(120, 120, 132), outline=(30, 24, 30), width=3)

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['cdark'], G['clit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    na = 0
    if T_GLISSE - 0.2 <= t < s4 + 0.1:
        na = 0.45 * min(ss((t - T_GLISSE + 0.2) / 0.3), ss((s4 + 0.1 - t) / 0.3))
    if na > 0:
        n = G['night'].copy(); n.putalpha(int(255 * na)); img.alpha_composite(n)
    d = ImageDraw.Draw(img)
    pm = mouth_at(5, t) if T_FAUX <= t < T_SOURIT - 0.1 else (mouth_at(0, t) if t < SPLIT0 - 0.1 else 0)
    gm = mouth_at(4, t) or (mouth_at(5, t) if t >= T_SOURIT - 0.05 else 0)
    mood = 0 if t < SPLIT0 else (-1 if t < T_FAUX - 0.6 else 0)
    im = draw_person('GARDIEN', t + 1, gm, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    chains(d)
    well_scene(d, t)
    if sQ - 0.05 <= t < CE:
        badge(d, 430, 860, "QUEL JOUR SORT-ELLE ?", ease_back((t - (sQ - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=50)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=420)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def shout(img, t):
    """T27 : à 0,0 s le prisonnier crie la réponse piège « 20 ! » (bulle en coordonnées écran, sous le hook)"""
    if t >= SPLIT0 + 0.6: return
    d = ImageDraw.Draw(img)
    u = ease_back(t / 0.2) if t > 0 else 1.0
    a = 1.0 if t < SPLIT0 + 0.45 else clamp((SPLIT0 + 0.6 - t) / 0.15)
    sc = clamp(u, 0.05, 1.2) * a
    cx, cy = 690, 1065; w, h = 250 * sc, 120 * sc
    if w < 10: return
    d.polygon([(cx - 90 * sc, cy + 10), (cx - 40 * sc, cy + 30), (510, 1010)], fill=(16, 10, 16))
    d.rounded_rectangle([cx - w / 2 - 7, cy - h / 2 - 7, cx + w / 2 + 7, cy + h / 2 + 7], radius=int(40 * sc) + 7, fill=CHAR['PRISONNIER']['col'])
    d.polygon([(cx - 80 * sc, cy + 6), (cx - 44 * sc, cy + 24), (522, 1018)], fill=(255, 255, 255))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(40 * sc), fill=(255, 255, 255))
    d.text((cx, cy + 4), "20 !", font=F(int(92 * sc)), fill=(220, 40, 40), anchor='mm')


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
    d.text((W / 2, y - 40), "ÉCRIS 20, 16 OU 15", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('20', 'JOUR', '20', 0), ('16', 'JOUR', '16', 0), ('15', 'JOUR', '15', 0)]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    """T23 : les 3 choix sont visibles dès 0,0 s (sous le hook) ; chaque choix grossit quand la voix le dit"""
    if not (t < ANS): return
    for k, (big, small, w_, nth) in enumerate(CHN):
        col = CHC[k]
        u = 1 + 0.1 * max(0, 1 - t / 0.2)
        if u <= 0: continue
        ts = wtime(6, w_, nth) - 0.1
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

def relance(img, t):
    """T25 : la dernière seconde rejoue la question en gros avant de boucler sur l'image 0"""
    if t < RELANCE: return
    u = ease_back((t - RELANCE) / 0.25)
    dk = Image.new('RGBA', (W, H), (10, 6, 12, int(215 * clamp((t - RELANCE) / 0.2))))
    img.alpha_composite(dk)
    d = ImageDraw.Draw(img)
    sc = clamp(u, 0.05, 1.2) * (1 + 0.03 * math.sin(t * 10))
    text_stroke(d, (W / 2, 820), "ET AUJOURD'HUI ?", F(int(70 * sc)), (255, 255, 255), sw=8)
    text_stroke(d, (W / 2, 990), "20, 16 OU 15 ?", F(int(130 * sc)), (255, 214, 50), sw=12)
    text_stroke(d, (W / 2, 1140), "QUEL JOUR SORT-ELLE ?", F(int(62 * sc)), (255, 120, 80), sw=8)

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['kdark'], G['klit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    answer_scene(d, t, img)
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
        shout(img, t)
        hook(img, t)
        if ANS - 0.25 < t: img = Image.blend(img, Image.new('RGBA', (W, H), (0, 0, 0, 255)), clamp((t - (ANS - 0.25)) / 0.25))
    else:
        img = answer_frame(t)
        img.alpha_composite(G['vig'])
        d = ImageDraw.Draw(img)
        ui_top(img, d, t, answer=True)
        img.alpha_composite(G['sub'])
        d = ImageDraw.Draw(img)
        if t < RELANCE: draw_subs(img, d, t)
        relance(img, t)
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
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_FAUX, 'T20': T_20, 'MONTE': T_MONTE, 'GLISSE': T_GLISSE, 'SPLIT': T_SOURIT, 'RELANCE': RELANCE, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '24', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')

