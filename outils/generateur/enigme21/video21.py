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


NUM = "21"; TITRE = "LES CHATS DE LA FERME"; CONTRAINTE = "LA FERME EN DANGER"
TITRE_HIER = "LES MOIS À 28 JOURS"
HOOK = ["100 SOURIS", "VONT RUINER SA FERME"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["100 souris vont ruiner sa ferme !",
        "3 chats attrapent 3 souris en 3 minutes.",
        "Il doit attraper 100 souris en 100 minutes.",
        "Le fermier crie : 100 chats ! Et la fermière éclate de rire.",
        "Alors, combien de chats : 100, 33, ou 3 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 12 ! Tous ont au moins 28 jours !"]
NL = len(SUBS)
GAP = 0.12
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
KEY = [["100", "souris", "ferme"], ["3", "chats", "souris", "minutes"], ["100", "souris", "minutes"],
       ["100", "chats", "rire"], ["100", "33", "3", "chats"], ["commentaire", "vite"], ["12", "28", "jours"]]
TORCH = [(170, 560), (910, 560)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

CHAR['FERMIER'] = dict(x=250, col=(90, 180, 90), hair=(120, 70, 36), style='short', skin=(220, 166, 120))
CHAR['FERMIÈRE'] = dict(x=850, col=(230, 110, 160), hair=(70, 40, 30), style='long', skin=(230, 176, 130))
T_CHATS = wtime(1, 'chats'); T_ATT = wtime(1, 'attrapent')
T_100 = wtime(2, '100'); T_MIN2 = wtime(2, 'minutes')
T_FAUX = wtime(3, '100')
T_SOURIT = wtime(3, 'éclate')
T_REP = wtime(6, '12')
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 690
FLOOR = 930
XP, XG = 250, 850

def farm(S):
    rnd = random.Random(3)
    im = Image.new('RGB', (W * S, H * S), (16, 14, 34))
    d = ImageDraw.Draw(im)
    for y in range(0, FLOOR):
        u = clamp((y - 300) / (FLOOR - 300))
        c = (int(16 + 50 * u), int(14 + 26 * u), int(34 + 36 * u))
        d.rectangle([0, y * S, W * S, (y + 1) * S], fill=c)
    for k in range(70):
        x = rnd.randint(0, W); y = rnd.randint(330, 720); r = rnd.choice([2, 2, 3, 4])
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(230, 220, 190))
    # lune
    for r, c in [(110, (44, 38, 60)), (80, (70, 60, 76)), (52, (250, 236, 190))]:
        d.ellipse([(930 - r) * S, (420 - r) * S, (930 + r) * S, (420 + r) * S], fill=c)
    d.ellipse([(948 - 14) * S, (406 - 14) * S, (948 + 14) * S, (406 + 14) * S], fill=(226, 212, 168))
    # collines
    d.polygon([(0, 820 * S), (200 * S, 760 * S), (420 * S, 800 * S), (700 * S, 750 * S), (1080 * S, 810 * S), (1080 * S, 940 * S), (0, 940 * S)], fill=(34, 28, 46))
    # grange
    d.polygon([(220 * S, 540 * S), (540 * S, 395 * S), (860 * S, 540 * S)], fill=(70, 26, 26))
    d.line([(214 * S, 544 * S), (540 * S, 392 * S), (866 * S, 544 * S)], fill=(210, 190, 160), width=10 * S)
    d.rectangle([250 * S, 540 * S, 830 * S, FLOOR * S], fill=(118, 42, 38))
    for x in range(250, 830, 36):
        d.line([(x * S, 540 * S), (x * S, FLOOR * S)], fill=(96, 32, 30), width=3 * S)
    d.rectangle([505 * S, 445 * S, 575 * S, 505 * S], fill=(255, 196, 96), outline=(210, 190, 160), width=6 * S)
    d.rectangle([400 * S, 680 * S, 680 * S, FLOOR * S], fill=(34, 18, 20))
    for (x0, x1) in [(400, 540), (540, 680)]:
        d.rectangle([x0 * S, 680 * S, x1 * S, FLOOR * S], outline=(210, 190, 160), width=8 * S)
    # sol herbeux
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(30, 36, 26))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(38, 46, 32), width=3 * S)
    # botte de foin
    d.rounded_rectangle([20 * S, 820 * S, 210 * S, 935 * S], radius=30 * S, fill=(196, 150, 60))
    for x in range(40, 200, 22):
        d.line([(x * S, 830 * S), ((x + 8) * S, 925 * S)], fill=(160, 116, 40), width=3 * S)
    # clôtures
    for (xa, xb) in [(0, 245), (835, 1080)]:
        for y in (840, 885):
            d.rectangle([xa * S, y * S, xb * S, (y + 14) * S], fill=(98, 70, 46))
        for x in range(xa + 20, xb, 70):
            d.rectangle([x * S, 810 * S, (x + 16) * S, 935 * S], fill=(84, 60, 40))
    # lanternes sur poteaux
    for (tx, ty) in TORCH:
        d.rectangle([(tx - 8) * S, (ty + 30) * S, (tx + 8) * S, 935 * S], fill=(70, 50, 34))
        d.rounded_rectangle([(tx - 30) * S, (ty + 8) * S, (tx + 30) * S, (ty + 34) * S], radius=6 * S, fill=(60, 50, 50))
    return im

def wall(S, forge=False):
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
            x += w
        y += hgt
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(26, 18, 25))
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
    return im

def cat(d, x, y, s, t=0.0, ph=0.0, col=(232, 140, 50)):
    bob = math.sin(t * 4 + ph) * 3 * s
    dk = tuple(int(v * 0.7) for v in col); ol = (24, 14, 16)
    tw = math.sin(t * 3 + ph) * 18
    d.line([(x + 40 * s, y + 20 * s), (x + 70 * s, y - 10 * s + tw * s), (x + 62 * s, y - 50 * s + tw * s)], fill=dk, width=max(3, int(12 * s)), joint='curve')
    d.ellipse([x - 44 * s, y - 16 * s + bob, x + 48 * s, y + 46 * s + bob], fill=col, outline=ol, width=max(2, int(4 * s)))
    hx, hy = x - 30 * s, y - 34 * s + bob
    for sg in (-1, 1):
        d.polygon([(hx + sg * 10 * s, hy - 22 * s), (hx + sg * 30 * s, hy - 52 * s), (hx + sg * 34 * s, hy - 12 * s)], fill=col, outline=ol)
    d.ellipse([hx - 36 * s, hy - 32 * s, hx + 36 * s, hy + 30 * s], fill=col, outline=ol, width=max(2, int(4 * s)))
    for sg in (-1, 1):
        ex = hx + sg * 15 * s
        d.ellipse([ex - 9 * s, hy - 10 * s, ex + 9 * s, hy + 8 * s], fill=(190, 230, 80))
        d.ellipse([ex - 2.5 * s, hy - 9 * s, ex + 2.5 * s, hy + 7 * s], fill=(16, 10, 12))
    d.polygon([(hx - 5 * s, hy + 10 * s), (hx + 5 * s, hy + 10 * s), (hx, hy + 16 * s)], fill=(240, 120, 140))
    for sg in (-1, 1):
        d.line([(hx + sg * 10 * s, hy + 16 * s), (hx + sg * 40 * s, hy + 12 * s)], fill=(250, 240, 230), width=max(1, int(2 * s)))

def mouse(d, x, y, s, t=0.0, ph=0.0):
    jx = math.sin(t * 9 + ph * 3) * 5 * s; jy = abs(math.sin(t * 12 + ph)) * -4 * s
    x += jx; y += jy
    d.line([(x + 18 * s, y + 4 * s), (x + 34 * s, y - 6 * s), (x + 44 * s, y + 2 * s)], fill=(230, 150, 160), width=max(2, int(3 * s)))
    d.ellipse([x - 22 * s, y - 12 * s, x + 22 * s, y + 12 * s], fill=(176, 172, 180), outline=(30, 22, 28), width=max(1, int(3 * s)))
    d.ellipse([x - 22 * s, y - 20 * s, x - 6 * s, y - 4 * s], fill=(240, 170, 180), outline=(30, 22, 28), width=max(1, int(2 * s)))
    d.ellipse([x - 27 * s, y - 4 * s, x - 21 * s, y + 2 * s], fill=(20, 12, 16))

def swarm_pos(k):
    r, c = divmod(k, 10)
    return 120 + c * 90 + (r % 2) * 40, 570 + r * 26

def swarm_alpha(t):
    """1 = les 100 souris visibles"""
    if t < T_CHATS - 0.3: return 1.0
    if t < T_100 - 0.2: return 0.0
    return clamp((t - (T_100 - 0.2)) / 0.3)

BUBS = [
    ('FERMIER', "100 chats !", lambda: T_FAUX - 0.15, lambda: s4, 330, 770, 280),
    ('FERMIÈRE', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: s4, 760, 760, 840),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:6]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP + 60, 960), (0.4, 1.0, 540, 960), (s3 - 0.2, 1.0, 540, 960),
            (s3 + 0.3, 1.08, 450, 900), (T_SOURIT - 0.1, 1.08, 450, 900), (T_SOURIT + 0.3, 1.08, 650, 900), (s4 - 0.1, 1.08, 650, 900),
            (s4 + 0.4, 1.0, 540, 900), (CE, 1.06, 540, 880), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_ATT, 10), (T_100, 10), (T_FAUX, 12), (T_SOURIT, 14), (s4, 8), (STAMP, 18)]:
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

MOIS = ["JANV", "FÉVR", "MARS", "AVR", "MAI", "JUIN", "JUIL", "AOÛT", "SEPT", "OCT", "NOV", "DÉC"]
def month_tile(d, x, y, s, name, ok=0.0):
    w, h = 74 * s, 70 * s
    d.rounded_rectangle([x - w - 4, y - h - 4, x + w + 4, y + h + 4], radius=int(14 * s) + 4, fill=(16, 10, 16))
    top = (220, 50, 60)
    d.rounded_rectangle([x - w, y - h, x + w, y + h], radius=int(14 * s), fill=(245, 240, 228))
    d.rounded_rectangle([x - w, y - h, x + w, y - h + 40 * s], radius=int(14 * s), fill=top)
    d.rectangle([x - w, y - h + 24 * s, x + w, y - h + 40 * s], fill=top)
    if s > 0.4:
        d.text((x, y - h + 21 * s), name, font=F(28 * s), fill=(255, 255, 255), anchor='mm')
        d.text((x, y + 20 * s), "28", font=F(46 * s), fill=(40, 150, 70) if ok > 0 else (60, 44, 56), anchor='mm')

def init():
    random.seed(1)
    for nm, im in [('r', farm(2)), ('d', wall(2, True))]:
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

CATX = [300, 540, 780]
def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['rdark'], G['rlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    pm = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    im = draw_person('FERMIÈRE', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='FERMIÈRE')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('FERMIER', t, pm, (t % 3.2) < 0.12, mood, label='FERMIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    # les 100 souris
    a = swarm_alpha(t)
    if a > 0:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        for k in range(100):
            x, y = swarm_pos(k)
            tk = (T_100 - 0.2 + k * 0.006) if t >= T_CHATS else 0
            if t < tk: continue
            mouse(dl, x, y, 0.78, t, k * 0.37)
        if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
        img.alpha_composite(lay)
        d = ImageDraw.Draw(img)
    # démonstration : 3 chats, 3 souris
    if T_CHATS - 0.3 <= t < T_100 - 0.2:
        out = clamp((t - (T_100 - 0.5)) / 0.3)
        for k, x in enumerate(CATX):
            tk = T_CHATS - 0.25 + k * 0.08
            u = clamp(ease_back((t - tk) / 0.25), 0, 1.15) * (1 - out)
            if u <= 0.02: continue
            pj = clamp((t - (T_ATT + k * 0.12)) / 0.25)
            if pj < 1:
                mouse(d, x - 10, 760, 1.0 * u, t, k)
            cat(d, x + 20, 640 + 90 * math.sin(math.pi * pj) * 0.4 + 60 * pj, 1.25 * u, t, k)
            if pj >= 1:
                cu = clamp(ease_back((t - (T_ATT + k * 0.12 + 0.25)) / 0.2), 0, 1.15) * u
                if cu > 0.05:
                    cx_, cy_, r = x - 20, 560, 34 * cu
                    d.ellipse([cx_ - r - 4, cy_ - r - 4, cx_ + r + 4, cy_ + r + 4], fill=(16, 10, 16))
                    d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=GREEN)
                    d.line([(cx_ - 16 * cu, cy_), (cx_ - 4 * cu, cy_ + 13 * cu), (cx_ + 17 * cu, cy_ - 13 * cu)], fill=(255, 255, 255), width=max(2, int(8 * cu)), joint='curve')
    # « ? CHATS » pendant la fausse réponse et la question
    if T_FAUX - 0.3 <= t < CE:
        u = ease_back((t - (T_FAUX - 0.3)) / 0.3) * (1 + 0.05 * math.sin(t * 8))
        d.ellipse([540 - 120 * clamp(u, 0, 1.1), 680 - 120 * clamp(u, 0, 1.1), 540 + 120 * clamp(u, 0, 1.1), 680 + 120 * clamp(u, 0, 1.1)], fill=(20, 12, 20), outline=(255, 206, 40), width=6)
        cat(d, 545, 700, 1.25 * clamp(u, 0, 1.1), t, 2, col=(110, 100, 120))
        if u > 0.3: text_stroke(d, (540, 640), "?", F(130 * clamp(u, 0, 1.1)), (255, 214, 50), sw=8)
    # règles écrites
    if T_CHATS - 0.1 <= t < CE:
        badge(d, 540, 418, "3 CHATS = 3 SOURIS EN 3 MIN", ease_back((t - (T_CHATS - 0.1)) / 0.25), fill=(255, 206, 40), size=46)
    if T_100 - 0.1 <= t < CE:
        badge(d, 540, 500, "100 SOURIS EN 100 MIN ?", ease_back((t - (T_100 - 0.1)) / 0.25), fill=(255, 120, 60), size=46)
    if s4 - 0.05 <= t < CE:
        badge(d, 540, 830, "COMBIEN DE CHATS ?", ease_back((t - (s4 - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=60)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=380)
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
    d.text((W / 2, y - 40), "ÉCRIS 100, 33 OU 3", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('100', 'CHATS', '100'), ('33', 'CHATS', '33'), ('3', 'CHATS', '3')]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    if not (wtime(4, '100') - 0.3 <= t < ANS): return
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
    img = Image.blend(G['ddark'], G['dlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    for k in range(12):
        x = 130 + (k % 6) * 164; y = 800 + (k // 6) * 170
        tk = ANS + 0.05 + k * 0.06
        if t < tk: continue
        u = clamp(ease_back((t - tk) / 0.22), 0, 1.15) * 0.98
        month_tile(d, x, y, u, MOIS[k], 1.0 if t >= T_REP else 0.0)
    if t >= T_REP - 0.4:
        badge(d, 540, 470, "12 MOIS !", ease_back((t - T_REP + 0.4) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
        badge(d, 540, 620, "TOUS ONT AU MOINS 28 JOURS", ease_back((t - T_REP + 0.2) / 0.3), fill=(255, 206, 40), size=48)
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

