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

NUM = "06"; TITRE = "LES DEUX CORDES"; CONTRAINTE = "2 CORDES DE 1 H  •  MESURE 45 MIN"
TITRE_HIER = "LE CODE DE LA BOMBE"
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Mesure exactement 45 minutes… ou la grille se referme sur toi.",
        "Deux cordes. Chacune brûle en 1 heure, mais de façon irrégulière.",
        "Le piège : couper une corde en deux ne marche pas !",
        "Combien de bouts allumes-tu au départ ?",
        "Écris A, B ou C. Réponse demain !",
        "Réponse d'hier : A ÷ ! 6 ÷ (1 − 3/4) = 24 !"]
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
KEY = [["45", "minutes", "grille", "referme"], ["deux", "cordes", "1", "heure", "irrégulière"], ["piège", "couper", "pas"],
       ["combien", "bouts", "départ"], ["a", "b", "c", "demain"], ["a", "÷", "24"]]

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ss(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

TORCH = [(105, 640), (975, 640)]
TABLE_Y = 1080
KX = [540 + (k - 1.5) * 112 for k in range(4)]; KY = 1005; KD = ['1', '3', '4', '6']

def stone_wall(S, bars=True):
    rnd = random.Random(5)
    im = Image.new('RGB', (W * S, H * S), (30, 21, 30))
    d = ImageDraw.Draw(im)
    y = 330 * S
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
        y += hgt
    d.rectangle([0, 1250 * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(14):
        yy = (1290 + i * 52) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    if bars:
        for i in range(6):
            xx = (430 + i * 44) * S
            d.rectangle([xx, 430 * S, xx + 10 * S, 700 * S], fill=(24, 18, 24))
        d.rectangle([410 * S, 420 * S, 680 * S, 436 * S], fill=(24, 18, 24))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    return im

def draw_bomb(im, S):
    d = ImageDraw.Draw(im)
    # table
    d.rounded_rectangle([40 * S, (TABLE_Y - 10) * S, 1040 * S, (TABLE_Y + 30) * S], radius=10 * S, fill=(128, 82, 48))
    d.rectangle([60 * S, (TABLE_Y + 30) * S, 1020 * S, (TABLE_Y + 190) * S], fill=(92, 58, 36))
    for i in range(1, 5):
        yy = (TABLE_Y + 30 + i * 32) * S
        d.line([60 * S, yy, 1020 * S, yy], fill=(80, 50, 30), width=3 * S)
    d.line([40 * S, (TABLE_Y - 8) * S, 1040 * S, (TABLE_Y - 8) * S], fill=(160, 108, 66), width=4 * S)
    # ombre
    d.ellipse([270 * S, 1055 * S, 810 * S, 1095 * S], fill=(60, 36, 22))
    # bâtons de dynamite derrière
    for k in range(5):
        cx = 340 + k * 100
        d.rounded_rectangle([(cx - 40) * S, 690 * S, (cx + 40) * S, 800 * S], radius=12 * S, fill=(196, 52, 42), outline=(110, 24, 20), width=4 * S)
        d.ellipse([(cx - 40) * S, 676 * S, (cx + 40) * S, 704 * S], fill=(226, 92, 70), outline=(110, 24, 20), width=4 * S)
        d.rectangle([(cx - 40) * S, 730 * S, (cx + 40) * S, 744 * S], fill=(230, 200, 140))
    # corps métal
    d.rounded_rectangle([290 * S, 780 * S, 790 * S, 1075 * S], radius=26 * S, fill=(62, 64, 76), outline=(28, 28, 36), width=6 * S)
    d.rounded_rectangle([306 * S, 792 * S, 774 * S, 812 * S], radius=8 * S, fill=(84, 88, 102))
    for (x, y) in [(316, 800), (764, 800), (316, 1050), (764, 1050)]:
        d.ellipse([(x - 9) * S, (y - 9) * S, (x + 9) * S, (y + 9) * S], fill=(120, 124, 138))
    # fils
    for col, (a, b, lift) in [((230, 50, 50), (300, 760, 110)), ((70, 140, 240), (330, 720, 150)), ((250, 210, 60), (360, 690, 80))]:
        pts = []
        for k in range(31):
            u = k / 30; x = a + (b - a) * u; y = 800 - lift * math.sin(math.pi * u) + 18 * math.sin(u * 9)
            pts.append((x * S, y * S))
        d.line(pts, fill=(20, 16, 20), width=14 * S, joint='curve')
        d.line(pts, fill=col, width=9 * S, joint='curve')
    # cadre écran + clavier
    d.rounded_rectangle([392 * S, 826 * S, 688 * S, 934 * S], radius=12 * S, fill=(26, 26, 32))
    d.rounded_rectangle([318 * S, 944 * S, 762 * S, 1064 * S], radius=16 * S, fill=(44, 46, 56))

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
    return im.resize((w, h), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)

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
    d.polygon([(x - 22, y + 8), (x - 16, y - hh * 0.4), (x + math.sin(t * 15 + k) * 8, y - hh), (x + 16, y - hh * 0.45), (x + 22, y + 8)], fill=(255, 140, 40))
    d.polygon([(x - 11, y + 6), (x - 7, y - hh * 0.3), (x + math.sin(t * 17 + k) * 4, y - hh * 0.65), (x + 7, y - hh * 0.3), (x + 11, y + 6)], fill=(255, 226, 120))

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

T_EXPL = wtime(0, 'referme')
T_CORDES = wtime(1, 'cordes'); T_HEURE = wtime(1, 'heure'); T_IRR = wtime(1, 'irrégulière')
T_PIEGE = wtime(2, 'piège'); T_COUPER = wtime(2, 'couper'); T_PAS = wtime(2, 'pas')
T_SIGNE = wtime(3, 'bouts')
T_A5 = wtime(5, 'a'); T_EQ5 = wtime(5, '6')

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
        vis = [k for k in g if t >= times[k] - 0.02 or k == g[0] or (i == 0 and cur == 0)]
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

# ---------------- personnages ----------------
PX = {'C': 230, 'B': 525, 'A': 820}
PCOL = {'C': (80, 140, 230), 'B': (90, 190, 120), 'A': (180, 110, 230)}
HEADY = 870

def draw_prisoner(L, t, mouth, blink, hat=None):
    S = 2; w, h = 300, 560
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = PCOL[L]
    br = math.sin(t * 2 * math.pi / 3.0 + PX[L]) * 4
    cx = w // 2; hy = 230 + br * 0.5
    by0 = 320 + br
    d.rounded_rectangle([(cx - 110) * S, by0 * S, (cx + 110) * S, (h + 40) * S], radius=60 * S, fill=(205, 200, 190))
    for k in range(6):
        yy = by0 + 30 + k * 38
        d.rectangle([(cx - 108) * S, yy * S, (cx + 108) * S, (yy + 16) * S], fill=(60, 56, 70))
    d.polygon([(cx - 46) * S, by0 * S, (cx + 46) * S, by0 * S, cx * S, (by0 + 50) * S], fill=col)
    d.rounded_rectangle([(cx - 42) * S, (by0 + 80) * S, (cx + 42) * S, (by0 + 160) * S], radius=14 * S, fill=(250, 240, 220), outline=col, width=6 * S)
    d.text((cx * S, (by0 + 121) * S), L, font=F(60 * S), fill=(30, 20, 26), anchor='mm')
    d.rectangle([(cx - 26) * S, (hy + 50) * S, (cx + 26) * S, (hy + 92) * S], fill=(196, 140, 100))
    d.ellipse([(cx - 80) * S, (hy - 80) * S, (cx + 80) * S, (hy + 80) * S], fill=(226, 170, 124))
    happy = hat is not None and L == 'A'
    for sgn in (-1, 1):
        x0 = cx + 6 + sgn * 46; x1 = cx + 6 + sgn * 14
        if happy: d.line([x0 * S, (hy - 34) * S, x1 * S, (hy - 30) * S], fill=(50, 30, 24), width=9 * S)
        else: d.line([x0 * S, (hy - 22) * S, x1 * S, (hy - 34) * S], fill=(50, 30, 24), width=9 * S)
    for sgn in (-1, 1):
        ex = cx + 8 + sgn * 30; ey = hy - 2
        if blink:
            d.line([(ex - 10) * S, ey * S, (ex + 10) * S, ey * S], fill=(30, 20, 20), width=5 * S)
        else:
            d.ellipse([(ex - 13) * S, (ey - 13) * S, (ex + 13) * S, (ey + 13) * S], fill=(255, 255, 255))
            d.ellipse([(ex - 1) * S, (ey - 8) * S, (ex + 13) * S, (ey + 8) * S], fill=(30, 20, 20))
    d.ellipse([(cx + 2) * S, (hy + 10) * S, (cx + 24) * S, (hy + 28) * S], fill=(206, 140, 100))
    my = hy + 48
    if happy:
        d.chord([(cx - 22) * S, (my - 18) * S, (cx + 36) * S, (my + 18) * S], 0, 180, fill=(70, 22, 26))
    elif mouth < 0.08:
        d.arc([(cx - 14) * S, (my - 10) * S, (cx + 30) * S, (my + 8) * S], 200, 340, fill=(70, 30, 30), width=5 * S)
    else:
        oh = 6 + mouth * 24
        d.ellipse([(cx - 12) * S, (my - oh / 2) * S, (cx + 28) * S, (my + oh / 2) * S], fill=(70, 22, 26))
    hb = hy - 66
    if hat == 'blanc':
        hc, oc, tc = (246, 244, 236), (255, 214, 50), None
    elif hat == 'noir':
        hc, oc, tc = (26, 22, 30), col, None
    else:
        hc, oc, tc = (90, 86, 104), col, '?'
    d.rounded_rectangle([(cx - 98) * S, (hb - 14) * S, (cx + 98) * S, (hb + 10) * S], radius=10 * S, fill=hc if hat else (70, 66, 80), outline=oc, width=4 * S)
    d.rounded_rectangle([(cx - 62) * S, (hb - 120) * S, (cx + 62) * S, (hb - 6) * S], radius=12 * S, fill=hc, outline=oc, width=4 * S)
    d.rectangle([(cx - 60) * S, (hb - 34) * S, (cx + 60) * S, (hb - 18) * S], fill=col)
    if tc: d.text((cx * S, (hb - 72) * S), tc, font=F(80 * S), fill=(255, 255, 255), anchor='mm')
    return im.resize((w, h), Image.LANCZOS)

VX, VY = 912, 700   # saboteur
def draw_villain(t, mouth, blink):
    S = 2; w, h = 300, 520
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    br = math.sin(t * 2 * math.pi / 2.6) * 4
    cx = w // 2; hy = 170 + br * 0.5
    hood = (96, 50, 128); dk = (60, 28, 84)
    d.rounded_rectangle([(cx - 120) * S, (260 + br) * S, (cx + 120) * S, (h + 40) * S], radius=70 * S, fill=hood)
    d.polygon([(cx - 20) * S, (270 + br) * S, (cx + 20) * S, (270 + br) * S, cx * S, (420 + br) * S], fill=dk)
    # capuche
    d.ellipse([(cx - 104) * S, (hy - 112) * S, (cx + 104) * S, (hy + 100) * S], fill=hood)
    d.polygon([(cx - 30) * S, (hy - 100) * S, (cx + 60) * S, (hy - 150) * S, (cx + 40) * S, (hy - 80) * S], fill=hood)
    d.ellipse([(cx - 76) * S, (hy - 76) * S, (cx + 76) * S, (hy + 80) * S], fill=(34, 20, 40))
    d.ellipse([(cx - 64) * S, (hy - 60) * S, (cx + 64) * S, (hy + 70) * S], fill=(214, 168, 128))
    # sourcils méchants
    for sgn in (-1, 1):
        d.line([(cx + sgn * 46) * S, (hy - 28) * S, (cx + sgn * 12) * S, (hy - 14) * S], fill=(40, 20, 30), width=9 * S)
    for sgn in (-1, 1):
        ex = cx + sgn * 26; ey = hy
        if blink: d.line([(ex - 10) * S, ey * S, (ex + 10) * S, ey * S], fill=(30, 20, 20), width=5 * S)
        else:
            d.ellipse([(ex - 12) * S, (ey - 11) * S, (ex + 12) * S, (ey + 11) * S], fill=(255, 255, 255))
            d.ellipse([(ex - 12) * S, (ey - 6) * S, (ex + 0) * S, (ey + 6) * S], fill=(30, 20, 20))
    my = hy + 38
    if mouth < 0.08:
        d.chord([(cx - 30) * S, (my - 14) * S, (cx + 30) * S, (my + 14) * S], 0, 180, fill=(70, 22, 26))
        d.rectangle([(cx - 24) * S, my * S, (cx + 24) * S, (my + 5) * S], fill=(250, 250, 240))
    else:
        oh = 8 + mouth * 26
        d.ellipse([(cx - 22) * S, (my - oh / 2) * S, (cx + 22) * S, (my + oh / 2) * S], fill=(70, 22, 26))
    return im.resize((w, h), Image.LANCZOS)

def small_bubble(img, d, cx, cy, txt, col, u, n, tail_x=None):
    if u <= 0: return
    f = F(42)
    lines = wrap(d, txt, f, 330)
    bw = max(d.textlength(l, font=f) for l in lines) + 60; bh = 40 + 54 * len(lines)
    sc = clamp(u, 0.01, 1.2)
    tx = cx if tail_x is None else tail_x
    def S(x, y): return (cx + (x - cx) * sc, cy + (y - cy) * sc)
    x0, y0 = cx - bw / 2, cy - bh / 2
    p0, p1 = S(x0, y0), S(x0 + bw, y0 + bh)
    d.rounded_rectangle([p0[0] - 6, p0[1] - 6, p1[0] + 6, p1[1] + 6], radius=30, fill=col)
    d.polygon([S(tx - 26, y0 + bh), S(tx + 26, y0 + bh), S(tx + 30, y0 + bh + 46)], fill=col)
    d.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]], radius=26, fill=(255, 255, 255))
    d.polygon([S(tx - 16, y0 + bh - 3), S(tx + 16, y0 + bh - 3), S(tx + 24, y0 + bh + 32)], fill=(255, 255, 255))
    if u > 0.9:
        shown = 0
        for li, ln in enumerate(lines):
            part = ln[:max(0, n - shown)]; shown += len(ln) + 1
            d.text((cx - d.textlength(ln, font=f) / 2, y0 + 20 + 27 + li * 54), part, font=f, fill=(30, 20, 26), anchor='lm')

G = {}
def mouth_env(i):
    v, sr = sf.read(f'v{i}.wav')
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(v[k:k + hop] ** 2)) for k in range(0, len(v), hop)])
    return e / (e.max() + 1e-9)

RX = [245, 835]; RY0, RY1 = 452, 1115
DOOR = (360, 430, 720, 1250)

def draw_door(im, S):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = DOOR
    d.rounded_rectangle([(x0 - 34) * S, (y0 - 34) * S, (x1 + 34) * S, (y1 + 10) * S], radius=180 * S, fill=(84, 62, 74))
    for k in range(9):
        a = math.pi * (k + 0.5) / 9
        cx = (x0 + x1) / 2 - math.cos(a) * 196; cy = y0 + 180 - math.sin(a) * 196
        d.ellipse([(cx - 22) * S, (cy - 18) * S, (cx + 22) * S, (cy + 18) * S], fill=(104, 78, 90))
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=170 * S, fill=(14, 10, 16))
    # anneaux de fer des cordes
    for x in RX:
        d.rounded_rectangle([(x - 30) * S, (RY0 - 40) * S, (x + 30) * S, (RY0 - 22) * S], radius=6 * S, fill=(52, 48, 58))
        d.ellipse([(x - 18) * S, (RY0 - 30) * S, (x + 18) * S, (RY0 + 6) * S], outline=(120, 116, 130), width=7 * S)

def init():
    random.seed(1)
    wall = stone_wall(2, bars=False); draw_door(wall, 2)
    bomb = stone_wall(2, bars=True); draw_bomb(bomb, 2)
    for nm, im in [('w', wall), ('b', bomb)]:
        base = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32)
        G[nm + 'dark'] = Image.fromarray(np.clip(base * 0.8 + glow_layer(0.30) * 0.6, 0, 255).astype(np.uint8))
        G[nm + 'lit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.55) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    G['env2'] = mouth_env(2)

def cam(t):
    keys = [(0, 1.12, 540, 860), (2.2, 1.04, 540, 860),
            (s1 + 0.2, 1.0, 540, 820), (s2 - 0.05, 1.0, 540, 820),
            (s2 + 0.4, 1.1, 460, 820), (s3 - 0.05, 1.08, 480, 820),
            (s3 + 0.4, 1.04, 540, 800), (CS - 0.1, 1.04, 540, 800), (CS + 0.5, 1.0, 540, 900),
            (CE, 1.08, 540, 900), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh in [T_EXPL, T_PAS, STAMP]:
        if 0 <= t - hh < 0.35:
            a = (1 - (t - hh) / 0.35) * 16
            sx += a * math.sin((t - hh) * 90); sy += a * math.cos((t - hh) * 77)
    return sx, sy

def led_on(t):
    if CS <= t < CE:
        rate = 1.2 + (t - CS) * 0.25
        return ((t - CS) * rate) % 1 < 0.35
    return (t % 1.0) < 0.3

def grille_y(t):
    if t < T_EXPL: return 720
    if t < T_EXPL + 0.3: return 720 + 140 * ss((t - T_EXPL) / 0.3)
    return min(1000, 860 + 140 * (t - T_EXPL - 0.3) / max(0.1, CE - T_EXPL - 0.3))

def draw_grille(d, gy):
    x0, y0, x1, _ = DOOR
    for x in range(x0 + 22, x1 - 10, 42):
        top = y0 + 6 if abs(x - 540) < 120 else y0 + 60
        d.rectangle([x - 7, top, x + 7, gy], fill=(36, 30, 40))
        d.rectangle([x - 7, top, x - 2, gy], fill=(70, 62, 78))
        d.polygon([(x - 10, gy), (x + 10, gy), (x, gy + 26)], fill=(36, 30, 40))
    yy = gy - 70
    while yy > y0 + 80:
        d.rectangle([x0 + 8, yy - 6, x1 - 8, yy + 6], fill=(46, 40, 52)); yy -= 150

def rope(d, x, t, k, wob=0.0):
    pts = []
    n = 70
    sway = 4 * math.sin(t * 1.3 + k)
    for i in range(n + 1):
        u = i / n; y = RY0 + (RY1 - RY0) * u
        xx = x + 9 * math.sin(y / 55 + k * 2) * u + sway * u
        w = 15 + 5 * math.sin(y / 31 + k * 3) + 4 * math.sin(y / 11 + k) + wob * 6 * math.sin(y / 23 + t * 9)
        pts.append((xx, y, max(6, w)))
    for xx, y, w in pts:
        d.ellipse([xx - w / 2 - 3, y - w / 2 - 3, xx + w / 2 + 3, y + w / 2 + 3], fill=(70, 44, 26))
    for i, (xx, y, w) in enumerate(pts):
        d.ellipse([xx - w / 2, y - w / 2, xx + w / 2, y + w / 2], fill=(206, 160, 98) if i % 4 else (170, 124, 70))
    return pts

def badge(d, x, y, txt, u, fill=(255, 206, 40), tcol=(24, 14, 20), size=44):
    if u <= 0: return
    f = F(size * clamp(u, 0.05, 1.2)); tw = d.textlength(txt, font=f)
    h = size * 0.75 * clamp(u, 0.05, 1.2)
    d.rounded_rectangle([x - tw / 2 - 20, y - h, x + tw / 2 + 20, y + h], radius=int(h), fill=(16, 10, 16))
    d.rounded_rectangle([x - tw / 2 - 16, y - h + 4, x + tw / 2 + 16, y + h - 4], radius=int(h) - 4, fill=fill)
    d.text((x, y + 2), txt, font=f, fill=tcol, anchor='mm')

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['wdark'], G['wlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # geôlier derrière la grille
    mouth = 0
    if s2 + 0.1 <= t < s2 + D[2]:
        k = int((t - s2) * FPS); mouth = clamp(G['env2'][k] * 1.6) if k < len(G['env2']) else 0
    blink = (t % 3.1) < 0.12
    img.alpha_composite(draw_villain(t, mouth, blink), (390, 700))
    d = ImageDraw.Draw(img)
    draw_grille(d, grille_y(t))
    # cordes
    wob = 0.0
    if T_IRR - 0.05 <= t < s2 + 0.2: wob = 0.5 + 0.5 * math.sin((t - T_IRR) * 6)
    ptsA = rope(d, RX[0], t, 0, wob); rope(d, RX[1], t, 1, wob)
    if T_HEURE - 0.02 <= t < s3 + 0.2:
        u = ease_back((t - T_HEURE) / 0.3) * (1 - clamp((t - s3) / 0.2))
        for x in RX: badge(d, x + 2, 560, "1 H", u)
    if T_CORDES - 0.02 <= t < T_HEURE:
        u = ease_back((t - T_CORDES) / 0.25)
        for x in RX:
            r = 70 * clamp(u, 0, 1.2)
            d.ellipse([x - r, 785 - r * 5, x + r, 785 + r * 5], outline=(255, 214, 50), width=6)
    # piège : couper en deux
    if T_COUPER - 0.02 <= t < s3 + 0.2:
        xm, ym = ptsA[35][0], ptsA[35][1]
        for xx in range(int(xm - 70), int(xm + 70), 22):
            d.line([xx, ym, xx + 12, ym], fill=(255, 70, 60), width=7)
        if t >= T_PAS:
            u = ease_back((t - T_PAS) / 0.25); r = 52 * clamp(u, 0, 1.2)
            d.line([xm - r, ym - r, xm + r, ym + r], fill=(16, 10, 16), width=26)
            d.line([xm - r, ym + r, xm + r, ym - r], fill=(16, 10, 16), width=26)
            d.line([xm - r, ym - r, xm + r, ym + r], fill=(255, 60, 50), width=16)
            d.line([xm - r, ym + r, xm + r, ym - r], fill=(255, 60, 50), width=16)
            badge(d, xm + 10, ym + 120, "½ CORDE ≠ 30 MIN", u, fill=(255, 80, 60), tcol=(255, 255, 255), size=38)
    if T_PIEGE <= t < s3 + 0.3:
        small_bubble(img, d, 560, 560, "Coupe-la en deux ? Hé hé… elle brûle de travers !", (150, 80, 190), ease_back((t - T_PIEGE) / 0.25), int((t - T_PIEGE) * 22), tail_x=540)
    # les 4 bouts
    if T_SIGNE - 0.02 <= t < ANS:
        for x in RX:
            for y in (RY0 + 4, RY1):
                u = ease_back((t - T_SIGNE) / 0.3)
                pul = 1 + 0.12 * math.sin(t * 8 + x + y)
                r = 30 * clamp(u, 0, 1.2) * pul
                d.ellipse([x - r - 5, y - r - 5, x + r + 5, y + r + 5], fill=(16, 10, 16))
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 206, 40))
                if r > 10: d.text((x, y + 2), "?", font=F(r * 1.4), fill=(24, 14, 20), anchor='mm')
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

CH = [("A", "2"), ("B", "3"), ("C", "4")]
def choices(img, d, t):
    if not (T_SIGNE - 0.05 <= t < ANS): return
    for k, (lab, sym) in enumerate(CH):
        ts = T_SIGNE + k * 0.3
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 3) % 3 == k: pul = 1.08
        s = u * pul
        x = 230 + k * 310; y = 1300
        bw, bh = 250 * s, 120 * s
        d.rounded_rectangle([x - bw / 2 - 6, y - bh / 2 - 6, x + bw / 2 + 6, y + bh / 2 + 6], radius=int(50 * s) + 6, fill=(255, 206, 40))
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(50 * s), fill=(26, 18, 30))
        if s > 0.3:
            r = 34 * s; lx = x - bw / 2 + 22 * s + r
            d.ellipse([lx - r, y - r, lx + r, y + r], fill=(255, 206, 40))
            d.text((lx, y + 2), lab, font=F(46 * s), fill=(24, 14, 20), anchor='mm')
            d.text((x + 36 * s, y + 2), sym, font=F(84 * s), fill=(255, 255, 255), anchor='mm')

def chrono(img, d, t):
    if not (CS <= t < CE + 0.3): return
    rem = max(0, CE - t); frac = rem / CHR
    ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
    beat = 1 + 0.08 * math.exp(-ph * 8)
    cx, cy, r = W / 2, 480, int(104 * beat)
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=(16, 10, 16, 230))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(70, 50, 60), width=20)
    col = (255, 206, 40) if rem > 2.5 else (255, 60, 50)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=col, width=20)
    d.text((cx, cy + 4), str(int(math.ceil(rem))) if rem > 0 else "0", font=F(int(106 * beat)), fill=(255, 255, 255), anchor='mm')
    d.text((cx, cy + 104 + 60), "COMBIEN DE BOUTS ?", font=F(54), fill=(255, 255, 255), stroke_width=6, stroke_fill=(10, 6, 12), anchor='mm')

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
    d.text((W / 2, y - 40), "ÉCRIS A, B OU C", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(770 - s.height / 2)))

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['bdark'], G['blit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    ok = t >= T_EQ5
    d.rounded_rectangle([402, 836, 678, 924], radius=8, fill=(6, 40, 14) if ok else (40, 6, 8))
    d.text((540, 882), "= 24 OK" if ok else "= ??", font=F(60), fill=(80, 240, 120) if ok else (255, 60, 50), anchor='mm')
    lc = (60, 230, 100) if ok else ((255, 50, 40) if (t % 1.0) < 0.3 else (90, 20, 20))
    d.ellipse([706, 850, 742, 886], fill=lc)
    for k, (x, dg) in enumerate(zip(KX, KD)):
        fill = (232, 226, 210)
        if ok and t < T_EQ5 + 1.6 and t >= T_EQ5 + k * 0.25: fill = (255, 214, 50)
        d.rounded_rectangle([x - 46, KY - 46, x + 46, KY + 46], radius=14, fill=(20, 20, 26))
        d.rounded_rectangle([x - 42, KY - 44, x + 42, KY + 40], radius=12, fill=fill)
        d.text((x, KY - 2), dg, font=F(60), fill=(30, 20, 26), anchor='mm')
    if ok:
        u = ease_back((t - T_EQ5) / 0.35)
        s = clamp(u, 0.02, 1.2)
        y = 560
        d.rounded_rectangle([540 - 440 * s, y - 95 * s, 540 + 440 * s, y + 95 * s], radius=int(40 * s), fill=(255, 206, 40))
        d.rounded_rectangle([540 - 432 * s, y - 87 * s, 540 + 432 * s, y + 87 * s], radius=int(36 * s), fill=(16, 10, 16))
        if s > 0.4:
            parts = [("6 ", (255, 255, 255)), ("÷", (255, 214, 50)), (" (1 − 3/4) = 24", (255, 255, 255))]
            ff = F(84 * s); tw = sum(d.textlength(p, font=ff) for p, _ in parts); x = 540 - tw / 2
            for p, c in parts:
                d.text((x, y + 4), p, font=ff, fill=c, anchor='lm'); x += d.textlength(p, font=ff)
    if t >= T_A5:
        u = ease_back((t - T_A5) / 0.3); s = clamp(u, 0.02, 1.2)
        x, y = 540, 1225
        d.rounded_rectangle([x - 170 * s, y - 50 * s, x + 170 * s, y + 50 * s], radius=int(34 * s), fill=(90, 200, 120))
        if s > 0.4: d.text((x, y + 2), "A = ÷", font=F(60 * s), fill=(16, 30, 20), anchor='mm')
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
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_EXPL, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
