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



NUM = "29"; TITRE = "LES 9 DU CACHOT"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "LES POMMES DU CACHOT"
HOOK = ["COMPTE LES 9", "ET IL EST LIBRE !"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["PRISONNIER : 10 ! Compte les 9, et il est libre !",
        "Il écrit tous les nombres de 1 à 100.",
        "Puis il compte tous les chiffres 9.",
        "GARDIEN : Combien de 9 as-tu écrits ?",
        "PRISONNIER : 10 ! GARDIEN : Ha ha ! Tu es sûr ?",
        "Combien de 9 : 10, 11, ou 20 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 2 pommes, pas 1 !"]
_SP = json.load(open('split.json')); SPLIT4 = _SP['split4']; SPLIT0 = _SP['split0']   # T27 : ligne 0 = cri du prisonnier puis narratrice   # T26 : début de la réplique du gardien dans la ligne 4
NL = len(SUBS)
GAP = 0.3
s0 = 0.0
s1 = s0 + D[0] + 0.15
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
RELANCE = s6 + D[7] + 0.3      # T25 : la question revient en gros avant la boucle
FADE = RELANCE + 0.9
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, sQ, s5, s6]
NF = int(round(T * FPS))
KEY = [["10", "9", "libre"], ["1", "100", "nombres"], ["9", "chiffres", "compte"], ["combien", "9"],
       ["10", "sûr"], ["9", "10", "11", "20"], ["commentaire", "vite"], ["2", "pommes", "pas", "1"]]
TORCH = [(70, 430), (1010, 430)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())
# T26 : ligne 4 = 2 répliques (prisonnier puis gardien) -> mots répartis sur chaque réplique
def _wt4():
    ws = SUBS[4].split(); kg = ws.index('GARDIEN')
    def spread(sub, a, b):
        return [a + (b - a) * j / len(sub) * 0.9 for j in range(len(sub))]
    return ws, spread(ws[:kg], s4, s4 + SPLIT4 - 0.15) + spread(ws[kg:], s4 + SPLIT4 - 0.1, s4 + D[4])
WT[4] = _wt4()
def _wt0():
    ws = SUBS[0].split(); kg = ws.index('Compte')
    def spread(sub, a, b):
        return [a + (b - a) * j / len(sub) * 0.9 for j in range(len(sub))]
    return ws, spread(ws[:kg], s0, s0 + SPLIT0 - 0.15) + spread(ws[kg:], s0 + SPLIT0 - 0.05, s0 + D[0])
WT[0] = _wt0()

T_3 = wtime(1, 'écrit'); T_PREND = wtime(2, '9')
T_FAUX = s4
T_SOURIT = s4 + SPLIT4
T_REP = wtime(7, '2')
DROPS = [T_3 - 0.1 + j * 0.45 for j in range(3)]   # les 3 lignes du tableau s'écrivent
T_MEME = 99.0
CHRONO_XY = (540, 1040)
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 700
FLOOR = 930
XP, XG = 250, 850
CHAR['PRISONNIER']['x'] = XP; CHAR['GARDIEN']['x'] = XG
# marmite dans la cheminée
POTX, POTY = 540, 640     # centre du haut de la marmite (surface de l'eau)
EGGX = [480, 540, 600]
# bougies (réponse #26)
CX = [205 + k * 74.4 for k in range(10)]
SHELF = 650
OFF = (1, 4, 8)
CH0 = 150

def wall(S, mode):
    """mur de pierre brun-violet du donjon, torches ; mode 'cuisine' (cheminée) ou 'cachot' (soupirail + étagère, réponse d'hier)"""
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
        d.rounded_rectangle([430 * S, 348 * S, 650 * S, 430 * S], radius=10 * S, fill=(14, 18, 34))
        for k in range(6):
            xx = (452 + k * 35) * S
            d.rectangle([xx - 5 * S, 348 * S, xx + 5 * S, 430 * S], fill=(96, 92, 104))
        d.rounded_rectangle([422 * S, 340 * S, 658 * S, 438 * S], radius=12 * S, outline=(90, 70, 84), width=8 * S)
        d.rectangle([0, 830 * S, W * S, FLOOR * S], fill=(52, 38, 40))
    else:
        # #29 : grand tableau noir (ardoise) accroché au mur, cadre en bois
        d.rounded_rectangle([130 * S, 350 * S, 950 * S, 820 * S], radius=14 * S, fill=(96, 62, 38), outline=(40, 24, 18), width=6 * S)
        d.rectangle([150 * S, 370 * S, 930 * S, 800 * S], fill=(34, 48, 44))
        for k in range(14):
            yy = (380 + k * 30) * S
            d.line([158 * S, yy, 922 * S, yy + 6 * S], fill=(38, 53, 49), width=10 * S)
        d.rectangle([180 * S, 806 * S, 900 * S, 822 * S], fill=(110, 74, 46))
        d.rounded_rectangle([700 * S, 796 * S, 760 * S, 810 * S], radius=6 * S, fill=(240, 240, 232))
        d.rectangle([0, 830 * S, W * S, FLOOR * S], fill=(52, 38, 40))
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

def egg(d, x, y, s=1.0, hi=False):
    w, h = 40 * s, 52 * s
    d.ellipse([x - w - 4, y - h - 4, x + w + 4, y + h * 0.8 + 4], fill=(255, 150, 40) if hi else (30, 20, 24))
    d.ellipse([x - w, y - h, x + w, y + h * 0.8], fill=(250, 244, 228))
    d.ellipse([x - w * 0.5, y - h * 0.75, x - w * 0.1, y - h * 0.35], fill=(255, 255, 255))

def fire(d, t):
    big = 1.0 + 0.35 * ss((t - (T_MEME - 0.1)) / 0.4) if t >= T_MEME - 0.1 else 1.0
    for k, x in enumerate([450, 500, 540, 580, 630]):
        small_flame(d, x, 806, t, k * 2.3, s=1.5 * big * (1.15 if k == 2 else 0.95))

# --- #28 (réponse d'hier) : table + 3 pommes ---
TY = 770                    # dessus de la table
APX = [410, 540, 670]; APY = TY - 46
ORANGE = (255, 150, 40)
CHALK = (236, 240, 230)

def apple(d, x, y, s=1.0, outline=None):
    r = 40 * s
    if outline: d.ellipse([x - r - 15, y - r - 15, x + r + 15, y + r + 15], fill=outline)
    d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill=(30, 12, 16))
    d.ellipse([x - r, y - r * 0.92, x + 4 * s, y + r], fill=(210, 40, 44))
    d.ellipse([x - 4 * s, y - r * 0.92, x + r, y + r], fill=(200, 34, 40))
    d.ellipse([x - r * 0.6, y - r * 0.6, x - r * 0.2, y - r * 0.15], fill=(255, 140, 130))
    d.line([(x, y - r * 0.8), (x + 6 * s, y - r * 1.35)], fill=(90, 56, 30), width=max(2, int(7 * s)))
    d.ellipse([x + 6 * s, y - r * 1.45, x + 34 * s, y - r * 1.1], fill=(90, 190, 80))

def table(d, x0=310, x1=770):
    d.rectangle([x0 + 40, TY + 26, x0 + 64, FLOOR + 10], fill=(70, 46, 30)); d.rectangle([x1 - 64, TY + 26, x1 - 40, FLOOR + 10], fill=(70, 46, 30))
    d.rounded_rectangle([x0, TY - 4, x1, TY + 30], radius=8, fill=(132, 88, 52), outline=(40, 24, 18), width=4)
    d.line([(x0 + 10, TY + 8), (x1 - 10, TY + 8)], fill=(150, 104, 64), width=4)

# --- #29 : le tableau noir, les nombres de 1 à 100 ---
BLINES = ["1, 2, 3, 4, 5, 6…", "… 50, 51, 52…", "… 98, 99, 100"]
BLY = [555, 640, 725]
def board_scene(d, t):
    # titre à la craie « DE 1 À 100 »
    hu = 1.0
    if s1 - 0.1 <= t < s2: hu = 1 + 0.12 * math.sin(math.pi * clamp((t - (s1 - 0.1)) / 0.4))
    text_stroke(d, (470, 450), "DE 1 À 100", F(int(64 * hu)), (255, 214, 50), stroke=(20, 30, 28), sw=4)
    if t >= s1 - 0.1:
        u = clamp((t - (s1 - 0.1)) / 0.35)
        d.line([(300, 494), (300 + 340 * u, 494)], fill=ORANGE, width=8)
    for j, ln in enumerate(BLINES):
        sc = 1.0
        if DROPS[j] <= t < DROPS[j] + 0.4: sc = 1 + 0.16 * math.sin(math.pi * (t - DROPS[j]) / 0.4)
        text_stroke(d, (470, BLY[j]), ln, F(int(54 * sc)), CHALK, stroke=(20, 30, 28), sw=3)
    # le « 9 » à compter (cerclé), puis « ? » quand le gardien demande
    if t >= T_PREND - 0.15:
        u = ease_back((t - (T_PREND - 0.15)) / 0.3)
        pul = 1 + (0.05 * math.sin(t * 8) if t >= s3 else 0)
        r = 66 * clamp(u, 0.05, 1.2) * pul; cx, cy = 840, 560
        d.ellipse([cx - r - 7, cy - r - 7, cx + r + 7, cy + r + 7], fill=(16, 10, 16))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 206, 40))
        d.text((cx, cy + 4), "9", font=F(int(96 * clamp(u, 0.05, 1.2) * pul)), fill=(24, 14, 20), anchor='mm')
        if t >= s3 - 0.1 and t < CE + 0.3:
            v = ease_back((t - (s3 - 0.1)) / 0.3)
            text_stroke(d, (840 + 4 * math.sin(t * 5), 700), "?", F(int(100 * clamp(v, 0, 1.1)) + 1), (255, 214, 50), sw=7)

def board_badges(d, t):
    if s1 - 0.1 <= t < s2 - 0.1:
        badge(d, 540, 915, "IL ÉCRIT DE 1 À 100", ease_back((t - (s1 - 0.1)) / 0.3), fill=(255, 255, 255), size=56)
    if s2 - 0.1 <= t < s3 - 0.1:
        badge(d, 540, 915, "IL COMPTE LES CHIFFRES 9", ease_back((t - (s2 - 0.1)) / 0.3), fill=ORANGE, size=52)

# --- réponse #28 : il a les 2 pommes qu'il a prises ---
def answer_scene(d, t, img):
    table(d, 520, 900)
    apple(d, 760, APY, 1.2)                     # la pomme restée sur la table
    im = draw_person('PRISONNIER', t, 0, (t % 3.2) < 0.12, 0, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    hi = GREEN if t >= T_REP - 0.2 else ORANGE
    for j, x in enumerate([190, 310]):
        apple(d, x, 1040 + 4 * math.sin(t * 5 + j), 1.2, outline=hi)
    if t >= RELANCE: return
    if ANS + 0.3 <= t < T_REP - 0.2:
        badge(d, 540, 560, "IL A PRIS 2 POMMES", ease_back((t - ANS - 0.3) / 0.3), fill=ORANGE, size=60)
    if t >= T_REP - 0.2:
        badge(d, 540, 520, "2 POMMES !", ease_back((t - T_REP + 0.2) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
    tp = wtime(7, 'pas') - 0.15
    if t >= tp:
        u = ease_back((t - tp) / 0.3)
        badge(d, 540, 680, "1 POMME", u, fill=(150, 140, 150), tcol=(60, 50, 60), size=64)
        if t >= tp + 0.2:
            v = clamp((t - tp - 0.2) / 0.2)
            a, b = (400, 715), (680, 645)
            xe = (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)
            d.line([a, xe], fill=(16, 10, 16), width=16)
            d.line([a, xe], fill=RED, width=9)
            badge(d, 540, 1225, "IL GARDE LES 2 QU'IL PREND", v, fill=(255, 206, 40), size=50)

BUBS = [
    ('GARDIEN', "Combien de 9 as-tu écrits ?", lambda: s3 - 0.1, lambda: s4 - 0.05, 640, 1060, 800),
    ('PRISONNIER', "10 !", lambda: T_FAUX - 0.1, lambda: sQ, 450, 960, 300),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: sQ, 640, 1060, 800),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:7]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP + 120, 900), (0.4, 1.0, 540, 960), (s1 - 0.1, 1.0, 540, 960),
            (s1 + 0.3, 1.06, 540, 780), (s3 - 0.2, 1.06, 540, 780), (s3 + 0.2, 1.04, 600, 1000), (s4 - 0.2, 1.04, 600, 1000),
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
    for hh, amp in [(0.0, 16), (DROPS[0] + 0.2, 6), (DROPS[2] + 0.2, 8), (T_PREND, 8), (T_FAUX, 12), (T_SOURIT, 14), (sQ, 8), (STAMP, 18)]:
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
    for nm, im in [('c', wall(2, 'tableau')), ('k', wall(2, 'cachot'))]:  # c = scène (tableau noir), k = réponse d'hier (table + pommes)
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
    for i in (0, 3, 4): G[f'env{i}'] = mouth_env(i)

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
    board_scene(d, t)
    # T26 : chaque personnage ouvre la bouche sur SA voix ; T27 : le prisonnier crie « 10 ! » à 0,0 s
    pm = mouth_at(4, t) if T_FAUX <= t < T_SOURIT - 0.1 else (mouth_at(0, t) if t < SPLIT0 - 0.1 else 0)
    gm = mouth_at(3, t) or (mouth_at(4, t) if t >= T_SOURIT - 0.05 else 0)
    mood = 0 if t < SPLIT0 else (-1 if t < T_FAUX - 0.6 else 0)
    im = draw_person('GARDIEN', t + 1, gm, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    chains(d)
    board_badges(d, t)
    if sQ - 0.05 <= t < CE:
        badge(d, 540, 915, "COMBIEN DE CHIFFRES 9 ?", ease_back((t - (sQ - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=54)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=460)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def shout(img, t):
    """T27 : à 0,0 s le prisonnier crie la réponse piège « 10 ! » (bulle en coordonnées écran, sous le hook)"""
    if t >= SPLIT0 + 0.6: return
    d = ImageDraw.Draw(img)
    u = ease_back(t / 0.2) if t > 0 else 1.0
    a = 1.0 if t < SPLIT0 + 0.45 else clamp((SPLIT0 + 0.6 - t) / 0.15)
    sc = clamp(u, 0.05, 1.2) * a
    cx, cy = 500, 1095; w, h = 250 * sc, 120 * sc
    if w < 10: return
    d.polygon([(cx - 90 * sc, cy + 10), (cx - 40 * sc, cy + 30), (330, 1010)], fill=(16, 10, 16))
    d.rounded_rectangle([cx - w / 2 - 7, cy - h / 2 - 7, cx + w / 2 + 7, cy + h / 2 + 7], radius=int(40 * sc) + 7, fill=CHAR['PRISONNIER']['col'])
    d.polygon([(cx - 80 * sc, cy + 6), (cx - 44 * sc, cy + 24), (342, 1018)], fill=(255, 255, 255))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=int(40 * sc), fill=(255, 255, 255))
    d.text((cx, cy + 4), "10 !", font=F(int(92 * sc)), fill=(220, 40, 40), anchor='mm')

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
    d.text((W / 2, y - 40), "ÉCRIS 10, 11 OU 20", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('10', 'FOIS', '10', 0), ('11', 'FOIS', '11', 0), ('20', 'FOIS', '20', 0)]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    """T23 : les 3 choix sont visibles dès 0,0 s (sous le hook) ; chaque choix grossit quand la voix le dit"""
    if not (t < ANS): return
    for k, (big, small, w_, nth) in enumerate(CHN):
        col = CHC[k]
        u = 1 + 0.1 * max(0, 1 - t / 0.2)
        if u <= 0: continue
        ts = wtime(5, w_, nth) - 0.1
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
    text_stroke(d, (W / 2, 990), "10, 11 OU 20 ?", F(int(130 * sc)), (255, 214, 50), sw=12)
    text_stroke(d, (W / 2, 1140), "COMBIEN DE 9 ?", F(int(62 * sc)), (255, 120, 80), sw=8)

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
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_FAUX, 'DROPS': DROPS, 'PREND': T_PREND, 'SPLIT': T_SOURIT, 'RELANCE': RELANCE, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')

