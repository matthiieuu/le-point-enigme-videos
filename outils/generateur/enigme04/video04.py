import json, math, random, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

W, H, FPS = 1080, 1920, 30
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
_fc = {}
def F(s):
    s = max(1, int(s))
    if s not in _fc: _fc[s] = ImageFont.truetype(FB, s)
    return _fc[s]

NUM = "04"; TITRE = "LES CHAPEAUX DU CACHOT"; CONTRAINTE = "3 BLANCS • 2 NOIRS • A NE VOIT RIEN"
TITRE_HIER = "LES 3 BOÎTES MENTEUSES"
CHR = 6.0
D = json.load(open('durees.json'))
LIGNES = json.load(open('lignes.json'))
SUBS = list(LIGNES); SUBS[2] = "C dit: «Je ne sais pas.» B: «Moi non plus.»"
s0 = 0.0
s1 = s0 + D[0] + 0.25
s2 = s1 + D[1] + 0.25
s3 = s2 + D[2] + 0.25
CS = s3 + D[3] + 0.2
CE = CS + CHR
s4 = CE + 0.1
STAMP = s4 + D[4] * 0.6
ANS = s4 + D[4] + 0.35
s5 = ANS + 0.3
FADE = s5 + D[5] + 0.35
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, s5]
NF = int(round(T * FPS))
KEY = [["chapeau", "cachot"], ["blancs", "noirs"], ["sais", "non"], ["blanc", "noir"], ["blanc", "noir", "demain"], ["mélange", "pomme", "pommes"]]

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ss(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

JC = (214, 86, 70)
BOX_X = [270, 540, 810]; BOX_W, BOX_H = 236, 184; BOX_BOT = 1086; TABLE_Y = 1080
LABELS = ["POMMES", "ORANGES", "MÉLANGE"]
TORCH = [(105, 640), (975, 640)]
def stone_wall(S):
    rnd = random.Random(3)
    im = Image.new('RGB', (W * S, H * S), (30, 21, 30))
    d = ImageDraw.Draw(im)
    y = 330 * S; row = 0
    while y < 1300 * S:
        hgt = rnd.randint(78, 96) * S
        x = -rnd.randint(0, 120) * S
        while x < W * S:
            w = rnd.randint(130, 210) * S
            b = rnd.randint(-10, 10)
            col = (62 + b, 44 + b, 58 + b + rnd.randint(-4, 6))
            d.rounded_rectangle([x + 4 * S, y + 4 * S, x + w - 4 * S, y + hgt - 4 * S], radius=12 * S, fill=col)
            d.rounded_rectangle([x + 10 * S, y + 8 * S, x + w - 14 * S, y + 18 * S], radius=5 * S, fill=(col[0] + 9, col[1] + 7, col[2] + 9))
            if rnd.random() < 0.25:
                cx = x + rnd.randint(30, 100) * S; cy = y + rnd.randint(30, 60) * S
                d.line([cx, cy, cx + 22 * S, cy + 14 * S, cx + 30 * S, cy + 34 * S], fill=(40, 28, 38), width=3 * S)
            x += w
        y += hgt; row += 1
    # sol
    d.rectangle([0, 1250 * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(14):
        yy = (1290 + i * 52) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    # haut sombre
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    # porte barreaux a l'arriere (cachot)
    for i in range(6):
        xx = (430 + i * 44) * S
        d.rectangle([xx, 430 * S, xx + 10 * S, 700 * S], fill=(24, 18, 24))
    d.rectangle([410 * S, 420 * S, 680 * S, 436 * S], fill=(24, 18, 24))
    # torches supports
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    return im

def draw_table_boxes(im, S):
    d = ImageDraw.Draw(im)
    # table
    d.rounded_rectangle([40 * S, (TABLE_Y - 10) * S, 1040 * S, (TABLE_Y + 30) * S], radius=10 * S, fill=(128, 82, 48))
    d.rectangle([60 * S, (TABLE_Y + 30) * S, 1020 * S, (TABLE_Y + 190) * S], fill=(92, 58, 36))
    for i in range(1, 5):
        yy = (TABLE_Y + 30 + i * 32) * S
        d.line([60 * S, yy, 1020 * S, yy], fill=(80, 50, 30), width=3 * S)
    d.line([40 * S, (TABLE_Y - 8) * S, 1040 * S, (TABLE_Y - 8) * S], fill=(160, 108, 66), width=4 * S)
    for i, bx in enumerate(BOX_X):
        x0, x1 = (bx - BOX_W // 2) * S, (bx + BOX_W // 2) * S
        y0, y1 = (BOX_BOT - BOX_H) * S, BOX_BOT * S
        d.ellipse([x0 - 6 * S, y1 - 14 * S, x1 + 6 * S, y1 + 12 * S], fill=(60, 36, 22))
        d.rounded_rectangle([x0, y0, x1, y1], radius=10 * S, fill=(176, 120, 64), outline=(110, 70, 36), width=5 * S)
        for k in range(1, 4):
            yy = y0 + k * (y1 - y0) // 4
            d.line([x0 + 6 * S, yy, x1 - 6 * S, yy], fill=(146, 96, 50), width=4 * S)
        d.rounded_rectangle([x0, y0 - 20 * S, x1, y0 + 8 * S], radius=8 * S, fill=(150, 98, 52), outline=(110, 70, 36), width=4 * S)
        # etiquette
        lw = 200 * S; lh = 62 * S; lx = bx * S - lw // 2; ly = y0 + 52 * S
        d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=8 * S, fill=(240, 226, 196), outline=(90, 60, 34), width=3 * S)
        f = F(int(38 * S) if i < 2 else int(36 * S))
        tw = d.textlength(LABELS[i], font=f)
        d.text((bx * S - tw / 2, ly + lh / 2), LABELS[i], font=f, fill=(60, 36, 24), anchor='lm')
        d.ellipse([lx - 10 * S, ly + lh // 2 - 6 * S, lx + 2 * S, ly + lh // 2 + 6 * S], fill=(90, 60, 34))

def glow_layer(strength):
    arr = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for (tx, ty) in TORCH:
        dd = np.sqrt((xx - tx) ** 2 + ((yy - ty + 20) * 0.9) ** 2)
        g = np.exp(-(dd / 330.0) ** 2) * strength
        arr[..., 0] += g * 255; arr[..., 1] += g * 150; arr[..., 2] += g * 60
    dd = np.sqrt((xx - 540) ** 2 + (yy - 900) ** 2)
    g = np.exp(-(dd / 520.0) ** 2) * strength * 0.35
    arr[..., 0] += g * 255; arr[..., 1] += g * 170; arr[..., 2] += g * 90
    return arr

def vignette(col=(0, 0, 0), power=2.2, amt=0.85):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dd = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = np.clip(dd ** power, 0, 1) * amt
    img = np.zeros((H, W, 4), np.uint8); img[..., :3] = col; img[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')

def grad_band(y0, y1, peak, top_solid=False):
    img = np.zeros((H, W, 4), np.uint8)
    for y in range(y0, y1):
        u = (y - y0) / (y1 - y0)
        a = (1 - u) if top_solid else math.sin(math.pi * u) ** 0.7
        img[y, :, 3] = int(255 * peak * a)
    img[..., :3] = (12, 8, 14)
    return Image.fromarray(img, 'RGBA')

def stamp_img(text, col, size, w_pad=26, rot=-12):
    f = F(size)
    tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    tw = tmp.textlength(text, font=f)
    w, h = int(tw + w_pad * 2), int(size * 1.45)
    im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w * 2 - 6, h * 2 - 6], radius=18, outline=col + (255,), width=12)
    d.text((w, h), text, font=F(size * 2), fill=col + (255,), anchor='mm')
    im = im.resize((w, h), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
    return im

def silhouette():
    S = 2
    im = Image.new('RGBA', (460 * S, 700 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = (255, 140, 40, 255); b = (14, 10, 16, 255)
    d.ellipse([60 * S, 380 * S, 460 * S, 900 * S], fill=o)
    d.ellipse([66 * S, 386 * S, 454 * S, 894 * S], fill=b)
    d.ellipse([130 * S, 120 * S, 390 * S, 400 * S], fill=o)
    d.ellipse([136 * S, 126 * S, 384 * S, 394 * S], fill=b)
    d.rectangle([80 * S, 600 * S, 460 * S, 700 * S], fill=b)
    return im.resize((460, 700), Image.LANCZOS)

def flame(d, x, y, t, k):
    fl = 1 + 0.18 * math.sin(t * 23 + k) + 0.1 * math.sin(t * 37 + 2 * k)
    hh = 70 * fl
    pts = [(x - 22, y + 8), (x - 16, y - hh * 0.4), (x + math.sin(t * 15 + k) * 8, y - hh), (x + 16, y - hh * 0.45), (x + 22, y + 8)]
    d.polygon(pts, fill=(255, 140, 40))
    pts2 = [(x - 11, y + 6), (x - 7, y - hh * 0.3), (x + math.sin(t * 17 + k) * 4, y - hh * 0.65), (x + 7, y - hh * 0.3), (x + 11, y + 6)]
    d.polygon(pts2, fill=(255, 226, 120))

# ---------------- texte ----------------
def text_stroke(d, xy, txt, f, fill, stroke=(10, 6, 12), sw=6, anchor='mm'):
    d.text(xy, txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def wrap(d, text, f, maxw):
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        tst = (cur + ' ' + w_).strip()
        if d.textlength(tst, font=f) <= maxw: cur = tst
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def norm(w_):
    return w_.lower().strip(".,!?:;…'’").replace("qu'", '')

def word_times(i):
    words = LIGNES[i].split()
    wts = [len(w_) + 3 + (6 if w_[-1] in '.,!?:…' else 0) for w_ in words]
    tot = sum(wts); acc = 0; out = []
    for w_, wt in zip(words, wts):
        out.append(STARTS[i] + D[i] * acc / tot * 0.95); acc += wt
    return words, out

WT = [word_times(i) for i in range(6)]

def chunks(words, d, f, maxw):
    # groupes de mots tenant sur 2 lignes
    res = []; cur = []
    for k, w_ in enumerate(words):
        test = cur + [k]
        lines = wrap(d, ' '.join(words[j] for j in test), f, maxw)
        if len(lines) > 2 or (cur and words[cur[-1]][-1] in '.!?' and len(cur) >= 2):
            res.append(cur); cur = [k]
        else: cur = test
    if cur: res.append(cur)
    return res

def draw_subs(img, d, t):
    f = F(64)
    for i in [0, 1, 3, 4, 5]:
        st = STARTS[i]; en = st + D[i] + 0.25
        if i == 4: en = ANS - 0.05
        if not (st - 0.001 <= t < en) and not (i == 0 and t < 0.001): continue
        words, times = WT[i]
        grp = chunks(words, d, f, 900)
        cur = 0
        for gi, g in enumerate(grp):
            if t >= times[g[0]] - 0.02: cur = gi
        g = grp[cur]
        vis = [k for k in g if t >= times[k] - 0.02 or k == g[0]]
        lines = wrap(d, ' '.join(words[k] for k in g), f, 900)
        # placer mot par mot
        idx = 0; y = 1450 if len(lines) == 2 else 1480
        for li, ln in enumerate(lines):
            lw = ln.split(); total = d.textlength(ln, font=f)
            x = W / 2 - total / 2
            for w_ in lw:
                k = g[idx]; idx += 1
                ww = d.textlength(w_, font=f)
                if k in vis:
                    age = t - times[k]
                    sc = 1 + 0.25 * max(0, 1 - age / 0.15) if age > 0 else 1
                    col = (255, 214, 50) if norm(w_) in KEY[i] else (255, 255, 255)
                    fs = F(int(64 * sc))
                    text_stroke(d, (x + ww / 2, y + li * 82), w_, fs, col, sw=6)
                x += ww + d.textlength(' ', font=f)

# ======== énigme 04 ========
PX = {'C': 230, 'B': 525, 'A': 820}
PCOL = {'C': (80, 140, 230), 'B': (90, 190, 120), 'A': (180, 110, 230)}
HEADY = 870

def norm(w_):
    return w_.lower().strip(".,!?:;…'’«»").replace("qu'", '')

def word_times(i):
    words = SUBS[i].split()
    wts = [len(w_) + 3 + (6 if w_.rstrip('»')[-1] in '.,!?:…' else 0) for w_ in words]
    tot = sum(wts); acc = 0; out = []
    for w_, wt in zip(words, wts):
        out.append(STARTS[i] + D[i] * acc / tot * 0.95); acc += wt
    return words, out
WT = [word_times(i) for i in range(6)]
def wtime(i, word, nth=0):
    ws, ts = WT[i]; c = 0
    for w_, tt in zip(ws, ts):
        if norm(w_) == word:
            if c == nth: return tt
            c += 1
    return STARTS[i]

T_CACHOT = wtime(0, 'cachot')
T_B2 = wtime(2, 'b')
T_BLANC3 = wtime(3, 'blanc')
T_MEL = wtime(5, 'mélange'); T_POM = wtime(5, 'pomme'); T_POMS = wtime(5, 'pommes'); T_RESTE = wtime(5, 'reste')
FAUXT = T_CACHOT

def chunks(words, d, f, maxw):
    res = []; cur = []
    for k, w_ in enumerate(words):
        test = cur + [k]
        lines = wrap(d, ' '.join(words[j] for j in test), f, maxw)
        if len(lines) > 2 or (cur and words[cur[-1]].rstrip('»')[-1] in '.!?' and len(cur) >= 2):
            res.append(cur); cur = [k]
        else: cur = test
    if cur: res.append(cur)
    return res

def draw_subs(img, d, t):
    f = F(64)
    for i in range(6):
        st = STARTS[i]; en = st + D[i] + 0.25
        if i == 4: en = ANS - 0.05
        if i == 3: en = CS + 0.6
        if not (st - 0.001 <= t < en) and not (i == 0 and t < 0.001): continue
        words, times = WT[i]
        grp = chunks(words, d, f, 900)
        cur = 0
        for gi, g in enumerate(grp):
            if t >= times[g[0]] - 0.02: cur = gi
        g = grp[cur]
        vis = [k for k in g if t >= times[k] - 0.02 or k == g[0]]
        lines = wrap(d, ' '.join(words[k] for k in g), f, 900)
        idx = 0; y = 1450 if len(lines) == 2 else 1480
        for li, ln in enumerate(lines):
            lw = ln.split(); total = d.textlength(ln, font=f) + 12 * (len(lw) - 1)
            x = W / 2 - total / 2
            for w_ in lw:
                k = g[idx]; idx += 1
                ww = d.textlength(w_, font=f)
                if k in vis:
                    age = t - times[k]
                    sc = 1 + 0.25 * max(0, 1 - age / 0.15) if age > 0 else 1
                    col = (255, 214, 50) if norm(w_) in KEY[i] else (255, 255, 255)
                    text_stroke(d, (x + ww / 2, y + li * 82), w_, F(int(64 * sc)), col, sw=6)
                x += ww + d.textlength(' ', font=f) + 12

def build_static():
    big = stone_wall(2)
    base = np.asarray(big.resize((W, H), Image.LANCZOS)).astype(np.float32)
    dark = np.clip(base * 0.8 + glow_layer(0.30) * 0.6, 0, 255)
    lit = np.clip(base * 1.0 + glow_layer(0.55) * 0.7, 0, 255)
    return Image.fromarray(dark.astype(np.uint8)), Image.fromarray(lit.astype(np.uint8))

def build_boxes():
    big = stone_wall(2); draw_table_boxes(big, 2)
    base = np.asarray(big.resize((W, H), Image.LANCZOS)).astype(np.float32)
    return Image.fromarray(np.clip(base * 0.85 + glow_layer(0.45) * 0.6, 0, 255).astype(np.uint8))

def draw_prisoner(L, t, mouth, blink, hl=0.0):
    S = 2; w, h = 300, 560
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = PCOL[L]
    br = math.sin(t * 2 * math.pi / 3.0 + PX[L]) * 4
    cx = w // 2; hy = 230 + br * 0.5   # centre tete (coord locales)
    # corps (tenue rayee)
    by0 = 320 + br
    d.rounded_rectangle([(cx - 110) * S, by0 * S, (cx + 110) * S, (h + 40) * S], radius=60 * S, fill=(205, 200, 190))
    for k in range(6):
        yy = by0 + 30 + k * 38
        d.rectangle([(cx - 108) * S, yy * S, (cx + 108) * S, (yy + 16) * S], fill=(60, 56, 70))
    d.polygon([(cx - 46) * S, by0 * S, (cx + 46) * S, by0 * S, cx * S, (by0 + 50) * S], fill=col)
    # plaque lettre
    d.rounded_rectangle([(cx - 42) * S, (by0 + 80) * S, (cx + 42) * S, (by0 + 160) * S], radius=14 * S, fill=(250, 240, 220), outline=col, width=6 * S)
    d.text((cx * S, (by0 + 121) * S), L, font=F(60 * S), fill=(30, 20, 26), anchor='mm')
    # cou + tete
    d.rectangle([(cx - 26) * S, (hy + 50) * S, (cx + 26) * S, (hy + 92) * S], fill=(196, 140, 100))
    d.ellipse([(cx - 80) * S, (hy - 80) * S, (cx + 80) * S, (hy + 80) * S], fill=(226, 170, 124))
    # sourcils inquiets
    for sgn in (-1, 1):
        x0 = cx + 6 + sgn * 46; x1 = cx + 6 + sgn * 14
        d.line([x0 * S, (hy - 22) * S, x1 * S, (hy - 34) * S], fill=(50, 30, 24), width=9 * S)
    # yeux (regardent vers la droite)
    for sgn in (-1, 1):
        ex = cx + 8 + sgn * 30; ey = hy - 2
        if blink:
            d.line([(ex - 10) * S, ey * S, (ex + 10) * S, ey * S], fill=(30, 20, 20), width=5 * S)
        else:
            d.ellipse([(ex - 13) * S, (ey - 13) * S, (ex + 13) * S, (ey + 13) * S], fill=(255, 255, 255))
            d.ellipse([(ex - 1) * S, (ey - 8) * S, (ex + 13) * S, (ey + 8) * S], fill=(30, 20, 20))
    d.ellipse([(cx + 2) * S, (hy + 10) * S, (cx + 24) * S, (hy + 28) * S], fill=(206, 140, 100))
    my = hy + 48
    if mouth < 0.08:
        d.arc([(cx - 14) * S, (my - 10) * S, (cx + 30) * S, (my + 8) * S], 200, 340, fill=(70, 30, 30), width=5 * S)
    else:
        oh = 6 + mouth * 24
        d.ellipse([(cx - 12) * S, (my - oh / 2) * S, (cx + 28) * S, (my + oh / 2) * S], fill=(70, 22, 26))
    # chapeau mystere
    hb = hy - 66
    d.rounded_rectangle([(cx - 98) * S, (hb - 14) * S, (cx + 98) * S, (hb + 10) * S], radius=10 * S, fill=(70, 66, 80), outline=col, width=4 * S)
    d.rounded_rectangle([(cx - 62) * S, (hb - 120) * S, (cx + 62) * S, (hb - 6) * S], radius=12 * S, fill=(90, 86, 104), outline=col, width=4 * S)
    d.rectangle([(cx - 60) * S, (hb - 34) * S, (cx + 60) * S, (hb - 18) * S], fill=col)
    d.text((cx * S, (hb - 72) * S), '?', font=F(80 * S), fill=(255, 255, 255), anchor='mm')
    im = im.resize((w, h), Image.LANCZOS)
    return im

def eye_arrow(d, x0, x1, y, lift, u, col=(255, 214, 50)):
    # arc pointille de x0 a x1 (progression u)
    pts = []
    for k in range(41):
        s = k / 40 * u
        x = x0 + (x1 - x0) * s; yy = y - lift * math.sin(math.pi * s)
        pts.append((x, yy))
    for k in range(0, len(pts) - 1, 2):
        d.line([pts[k], pts[k + 1]], fill=col, width=9)
    if u > 0.95:
        x, yy = pts[-1]
        d.polygon([(x + 4, yy + 4), (x - 26, yy - 14), (x - 14, yy + 22)], fill=col)

def small_bubble(img, d, cx, cy, txt, col, u, n):
    if u <= 0: return
    f = F(42)
    lines = wrap(d, txt, f, 300)
    bw = max(d.textlength(l, font=f) for l in lines) + 60; bh = 40 + 54 * len(lines)
    sc = clamp(u, 0.01, 1.2)
    def S(x, y): return (cx + (x - cx) * sc, cy + (y - cy) * sc)
    x0, y0 = cx - bw / 2, cy - bh / 2
    p0, p1 = S(x0, y0), S(x0 + bw, y0 + bh)
    d.rounded_rectangle([p0[0] - 6, p0[1] - 6, p1[0] + 6, p1[1] + 6], radius=30, fill=col)
    d.polygon([S(cx - 26, y0 + bh), S(cx + 26, y0 + bh), S(cx + 6, y0 + bh + 46)], fill=col)
    d.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]], radius=26, fill=(255, 255, 255))
    d.polygon([S(cx - 16, y0 + bh - 3), S(cx + 16, y0 + bh - 3), S(cx + 5, y0 + bh + 32)], fill=(255, 255, 255))
    if u > 0.9:
        shown = 0
        for li, ln in enumerate(lines):
            part = ln[:max(0, n - shown)]; shown += len(ln) + 1
            d.text((cx - d.textlength(ln, font=f) / 2, y0 + 20 + 27 + li * 54), part, font=f, fill=(30, 20, 26), anchor='lm')

def silhouette():
    S = 2
    im = Image.new('RGBA', (460 * S, 700 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = (255, 140, 40, 255); b = (14, 10, 16, 255)
    d.ellipse([60 * S, 380 * S, 460 * S, 900 * S], fill=o)
    d.ellipse([66 * S, 386 * S, 454 * S, 894 * S], fill=b)
    d.ellipse([130 * S, 120 * S, 390 * S, 400 * S], fill=o)
    d.ellipse([136 * S, 126 * S, 384 * S, 394 * S], fill=b)
    d.rectangle([80 * S, 600 * S, 460 * S, 700 * S], fill=b)
    return im.resize((460, 700), Image.LANCZOS)

G = {}
def mouth_env(i):
    v, sr = sf.read(f'v{i}.wav')
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(v[k:k + hop] ** 2)) for k in range(0, len(v), hop)])
    return e / (e.max() + 1e-9)

def init():
    random.seed(1)
    G['dark'], G['lit'] = build_static()
    G['boxes'] = build_boxes()
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    G['env'] = mouth_env(2)

def cam(t):
    keys = [(0, 1.12, 540, 900), (2.2, 1.04, 540, 900),
            (s1 + 0.2, 1.16, 330, 860), (s1 + 1.5, 1.08, 600, 860), (s2 - 0.05, 1.0, 540, 900),
            (s2 + 0.3, 1.14, 360, 760), (T_B2 - 0.1, 1.14, 360, 760), (T_B2 + 0.3, 1.14, 620, 760), (s3 - 0.05, 1.08, 600, 800),
            (s3 + 0.4, 1.2, 780, 860), (CS - 0.1, 1.2, 780, 860), (CS + 0.5, 1.0, 540, 900),
            (CE, 1.08, 540, 900), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh in [FAUXT, STAMP]:
        if 0 <= t - hh < 0.35:
            a = (1 - (t - hh) / 0.35) * 16
            sx += a * math.sin((t - hh) * 90); sy += a * math.cos((t - hh) * 77)
    return sx, sy

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['dark'], G['lit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # mur face a A (a droite)
    # projecteur sur A pendant la question
    if s3 + 0.2 <= t < CE:
        a = clamp((t - s3 - 0.2) / 0.4) * (0.85 + 0.15 * math.sin(t * 8))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.polygon([(PX['A'] - 40, 330), (PX['A'] + 40, 330), (PX['A'] + 190, 1260), (PX['A'] - 190, 1260)], fill=(255, 220, 120, int(60 * a)))
        lay = lay.filter(ImageFilter.GaussianBlur(18)); img.alpha_composite(lay)
    # personnages
    for L in ['C', 'B', 'A']:
        mouth = 0
        if L == 'C' and s2 + 0.35 <= t < T_B2 - 0.05:
            k = int((t - s2) * FPS); mouth = clamp(G['env'][k] * 1.6) if k < len(G['env']) else 0
        if L == 'B' and T_B2 <= t < s2 + D[2]:
            k = int((t - s2) * FPS); mouth = clamp(G['env'][k] * 1.6) if k < len(G['env']) else 0
        blink = ((t + PX[L] / 300) % 3.4) < 0.12
        im = draw_prisoner(L, t, mouth, blink)
        bounce = 0
        if L == 'A' and t >= s3 + 0.2 and t < CE:
            bounce = -abs(math.sin((t - s3) * 5)) * 10
        img.alpha_composite(im, (PX[L] - 150, int(HEADY - 230 + bounce)))
    d = ImageDraw.Draw(img)
    # fleches du regard
    if s1 + 0.6 <= t < s2 + 0.2:
        tv1 = wtime(1, 'voit'); tv2 = wtime(1, 'voit', 1)
        fade = 1 - clamp((t - s2) / 0.2)
        if t >= tv1: eye_arrow(d, PX['C'] + 30, PX['B'] - 10, 610, 70, ss((t - tv1) / 0.35))
        if t >= tv1 + 0.3: eye_arrow(d, PX['C'] + 30, PX['A'] - 10, 590, 150, ss((t - tv1 - 0.3) / 0.45))
        if t >= tv2: eye_arrow(d, PX['B'] + 30, PX['A'] - 10, 610, 70, ss((t - tv2) / 0.35), (120, 230, 150))
    # bulles
    tc = s2 + 0.35
    if tc <= t < s3 + 0.3:
        small_bubble(img, d, PX['C'] + 20, 500, "Je ne sais pas…", PCOL['C'], ease_back((t - tc) / 0.25), int((t - tc) * 22))
    if T_B2 <= t < s3 + 0.5:
        small_bubble(img, d, PX['B'] + 20, 500, "Moi non plus…", PCOL['B'], ease_back((t - T_B2) / 0.25), int((t - T_B2) * 22))
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def camera(img, t):
    z, cx, cy = cam(t)
    sx, sy = shake(t)
    if CS <= t < CE:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
        z *= 1 + 0.012 * math.exp(-ph * 9)
    cx = clamp(cx + sx, W / 2 / z, W - W / 2 / z); cy = cy + sy
    a = 1 / z; c = cx - (W / 2) / z; e = 1 / z; fy = cy - cy / z
    return img.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, fy), resample=Image.BILINEAR)

def ui_top(img, d, t, answer=False):
    img.alpha_composite(G['top'])
    d.rectangle([0, 0, int(W * t / T), 12], fill=(255, 206, 40))
    pill = "RÉPONSE D'HIER" if answer else f"ÉNIGME #{NUM}"
    f = F(38); tw = d.textlength(pill, font=f)
    d.rounded_rectangle([40, 40, 40 + tw + 44, 98], radius=29, fill=(255, 206, 40) if not answer else (90, 200, 120))
    d.text((62, 69), pill, font=f, fill=(24, 14, 20), anchor='lm')
    if not answer:
        f2 = F(30); lab = "DIFFICULTÉ "
        x = W - 40 - d.textlength(lab, font=f2) - 5 * 30
        d.text((x, 69), lab, font=f2, fill=(255, 255, 255), anchor='lm')
        x += d.textlength(lab, font=f2)
        for k in range(5):
            d.ellipse([x + k * 30 + 2, 57, x + k * 30 + 24, 79], fill=(255, 80, 60) if k < 4 else (90, 80, 90))
    title = TITRE_HIER if answer else TITRE
    ft = F(80)
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
        f3 = F(36); tw = d.textlength(CONTRAINTE, font=f3)
        d.rounded_rectangle([W / 2 - tw / 2 - 26, 252, W / 2 + tw / 2 + 26, 312], radius=30, fill=(200, 44, 44))
        d.text((W / 2, 283), CONTRAINTE, font=f3, fill=(255, 255, 255), anchor='mm')

def choices(img, d, t):
    if not (T_BLANC3 - 0.05 <= t < ANS): return
    for k, (lab, fill, tc, x) in enumerate([("BLANC", (245, 242, 235), (30, 20, 26), 300), ("NOIR", (24, 20, 28), (255, 255, 255), 780)]):
        ts = T_BLANC3 + k * 0.35
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 2) % 2 == k: pul = 1.08
        s = u * pul
        bw, bh = 330 * s, 110 * s; y = 1310
        d.rounded_rectangle([x - bw / 2 - 6, y - bh / 2 - 6, x + bw / 2 + 6, y + bh / 2 + 6], radius=int(60 * s) + 6, fill=(255, 206, 40))
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(60 * s), fill=fill)
        if s > 0.3:
            r = 26 * s
            d.ellipse([x - bw / 2 + 24 * s, y - r, x - bw / 2 + 24 * s + 2 * r, y + r], fill=fill, outline=(255, 206, 40), width=5)
            d.text((x + 28 * s, y + 3), lab, font=F(62 * s), fill=tc, anchor='mm')

def chrono(img, d, t):
    if not (CS <= t < CE + 0.3): return
    rem = max(0, CE - t); frac = rem / CHR
    ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
    beat = 1 + 0.08 * math.exp(-ph * 8)
    cx, cy, r = W / 2, 470, int(108 * beat)
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=(16, 10, 16, 230))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(70, 50, 60), width=20)
    col = (255, 206, 40) if rem > 2.5 else (255, 60, 50)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=col, width=20)
    d.text((cx, cy + 4), str(int(math.ceil(rem))) if rem > 0 else "0", font=F(int(110 * beat)), fill=(255, 255, 255), anchor='mm')
    d.text((cx, cy + 108 + 52), "A : BLANC OU NOIR ?", font=F(44), fill=(255, 255, 255), stroke_width=6, stroke_fill=(10, 6, 12), anchor='mm')

def red_vig(img, t):
    if CS <= t < CE + 0.5:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
        a = (0.25 + 0.55 * (t - CS) / CHR) * (0.6 + 0.4 * math.exp(-ph * 6))
        if t > CE: a *= max(0, 1 - (t - CE) / 0.5)
        r = G['red'].copy(); r.putalpha(r.getchannel('A').point(lambda v: int(v * clamp(a))))
        img.alpha_composite(r)

def outro_cta(img, d, t):
    if not (s4 - 0.05 <= t < ANS): return
    u = ease_back((t - s4) / 0.3)
    f = F(int(62 * clamp(u, 0, 1.2)) + 1)
    y = 520
    d.rounded_rectangle([90, y - 120, W - 90, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([90, y - 120, W - 90, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS BLANC OU NOIR", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(760 - s.height / 2)))

def relabel(d, bx, txt, u):
    if u <= 0: return
    lw, lh = 200, 62; ly = BOX_BOT - BOX_H + 52
    s = clamp(u, 0, 1.2)
    w2, h2 = lw / 2 * s, lh / 2 * s; cy = ly + lh / 2
    d.rounded_rectangle([bx - w2, cy - h2, bx + w2, cy + h2], radius=8, fill=(190, 240, 190), outline=(30, 120, 60), width=4)
    if s > 0.4: d.text((bx, cy + 1), txt, font=F((36 if len(txt) > 6 else 38) * s), fill=(20, 80, 40), anchor='mm')

def answer_frame(t):
    img = G['boxes'].copy().convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # surbrillance boite Melange
    if t >= T_MEL:
        bx = BOX_X[2]; p = 0.5 + 0.5 * math.sin((t - T_MEL) * 8)
        d.rounded_rectangle([bx - BOX_W / 2 - 14, BOX_BOT - BOX_H - 34, bx + BOX_W / 2 + 14, BOX_BOT + 12], radius=18, outline=(255, 214, 50), width=int(6 + 4 * p))
        u = ease_back((t - T_MEL) / 0.3)
        d.rounded_rectangle([bx - 70 * u, 1150 - 40 * u, bx + 70 * u, 1150 + 40 * u], radius=20, fill=(255, 206, 40))
        if u > 0.4: d.text((bx, 1152), "C", font=F(64 * u), fill=(24, 14, 20), anchor='mm')
    # pomme qui sort
    if t >= T_POM:
        u = ease_back((t - T_POM) / 0.35); bx = BOX_X[2]; y = 820 - 40 * u
        r = 62 * clamp(u, 0, 1.2)
        d.ellipse([bx - r - 5, y - r - 5, bx + r + 5, y + r + 5], fill=(40, 10, 10))
        d.ellipse([bx - r, y - r, bx + r, y + r], fill=(220, 40, 40))
        d.ellipse([bx - r * 0.5, y - r * 0.6, bx - r * 0.15, y - r * 0.2], fill=(255, 140, 130))
        d.line([bx, y - r, bx + 6, y - r - 26 * u], fill=(90, 50, 20), width=7)
        d.ellipse([bx + 8, y - r - 30 * u, bx + 40 * u, y - r - 12 * u], fill=(70, 170, 70))
    relabel(d, BOX_X[2], "POMMES", ease_back((t - T_POMS) / 0.3) if t >= T_POMS else 0)
    relabel(d, BOX_X[1], "MÉLANGE", ease_back((t - T_RESTE) / 0.3) if t >= T_RESTE else 0)
    relabel(d, BOX_X[0], "ORANGES", ease_back((t - T_RESTE - 0.3) / 0.3) if t >= T_RESTE + 0.3 else 0)
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
        print('T', T, 'CS', CS, 'ANS', ANS, 'starts', [round(x, 2) for x in STARTS])
    else:
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': FAUXT, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
