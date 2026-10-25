import json, math, random, sys, subprocess
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

NUM = "10"; TITRE = "LES AIGUILLES À 3 H 15"; CONTRAINTE = "L'ANGLE EXACT = TA LIBERTÉ"
TITRE_HIER = "L'ESCARGOT DANS LE PUITS"
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Le gardien te libère si tu donnes l'angle exact entre les aiguilles à 3 h 15 !",
        "La grande aiguille est pile sur le 3.",
        "Mais la petite, elle, a bougé…",
        "Le gardien demande : «Quel est l'angle exact ?»",
        "Attention au piège : 0, 7,5 ou 15 degrés ?",
        "Écris ton nombre. Réponse demain !",
        "Réponse d'hier : 8 JOURS ! Le 8e, il sort avant de glisser."]
NL = len(SUBS)
GAP = 0.4
s0 = 0.0
s1 = s0 + D[0] + 0.3
s2 = s1 + D[1] + GAP
s3 = s2 + D[2] + GAP
s4 = s3 + D[3] + GAP
CS = s4 + D[4] + 0.2
CE = CS + CHR
s5 = CE + 0.1
STAMP = s5 + D[5] * 0.6
ANS = s5 + D[5] + 0.35
s6 = ANS + 0.25
FADE = s6 + D[6] + 0.45
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, s5, s6]
NF = int(round(T * FPS))
KEY = [["libère", "angle", "exact", "aiguilles", "3", "15"], ["grande", "3"], ["petite", "bougé"], ["angle", "exact"],
       ["piège", "0", "7,5", "15"], ["nombre", "demain"], ["8", "jours", "8e", "sort"]]

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ss(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

TORCH = [(105, 640), (975, 640)]

def stone_wall(S):
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
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    return im

# vitrine du diamant (au centre, en haut du mur)
CASE = (420, 380, 660, 560)
def draw_case(im, S):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = CASE
    # rideau rouge derrière
    d.rounded_rectangle([(x0 - 60) * S, (y0 - 40) * S, (x1 + 60) * S, (y1 + 30) * S], radius=30 * S, fill=(110, 26, 34))
    for k in range(8):
        xx = x0 - 50 + k * 47
        d.line([xx * S, (y0 - 36) * S, xx * S, (y1 + 26) * S], fill=(86, 18, 26), width=8 * S)
    # socle
    d.rectangle([(x0 + 20) * S, (y1 - 10) * S, (x1 - 20) * S, (y1 + 26) * S], fill=(150, 112, 70))
    d.rectangle([(x0 + 10) * S, (y1 + 22) * S, (x1 - 10) * S, (y1 + 34) * S], fill=(120, 86, 52))
    # coussin
    d.ellipse([(x0 + 70) * S, (y1 - 40) * S, (x1 - 70) * S, (y1 - 4) * S], fill=(170, 40, 60))
    # vitre
    d.rounded_rectangle([(x0 + 26) * S, y0 * S, (x1 - 26) * S, (y1 - 10) * S], radius=10 * S, outline=(190, 210, 230), width=5 * S)
    d.line([(x0 + 60) * S, (y0 + 20) * S, (x0 + 90) * S, (y0 + 70) * S], fill=(200, 220, 240), width=4 * S)

def diamond(d, cx, cy, s, t):
    pts_top = [(cx - 46 * s, cy - 14 * s), (cx - 26 * s, cy - 38 * s), (cx + 26 * s, cy - 38 * s), (cx + 46 * s, cy - 14 * s)]
    d.polygon(pts_top + [(cx, cy + 50 * s)], fill=(120, 220, 250))
    d.polygon([(cx - 46 * s, cy - 14 * s), (cx + 46 * s, cy - 14 * s), (cx, cy + 50 * s)], fill=(80, 180, 230))
    d.polygon([(cx - 26 * s, cy - 38 * s), (cx + 26 * s, cy - 38 * s), (cx + 10 * s, cy - 14 * s), (cx - 10 * s, cy - 14 * s)], fill=(200, 245, 255))
    sp = 0.5 + 0.5 * math.sin(t * 6)
    r = 16 * s * sp
    d.line([(cx + 30 * s - r, cy - 44 * s), (cx + 30 * s + r, cy - 44 * s)], fill=(255, 255, 255), width=4)
    d.line([(cx + 30 * s, cy - 44 * s - r), (cx + 30 * s, cy - 44 * s + r)], fill=(255, 255, 255), width=4)

def glow_layer(strength):
    arr = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for (tx, ty) in TORCH:
        dd = np.sqrt((xx - tx) ** 2 + ((yy - ty + 20) * 0.9) ** 2)
        g = np.exp(-(dd / 330.0) ** 2) * strength
        arr[..., 0] += g * 255; arr[..., 1] += g * 150; arr[..., 2] += g * 60
    dd = np.sqrt((xx - 540) ** 2 + (yy - 820) ** 2)
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
    return w_.lower().strip(".,!?:;…'’«»").replace("qu'", '').replace("n'", '').replace("c'", '').replace("l'", '').replace("d'", '')

def word_times(i):
    words = SUBS[i].split()
    wts = [len(w_) + 3 + (6 if w_.rstrip('»')[-1] in '.,!?:…' else 0) for w_ in words]
    tot = sum(wts); acc = 0; out = []
    for w_, wt in zip(words, wts):
        out.append(STARTS[i] + D[i] * acc / tot * 0.95); acc += wt
    return words, out
WT = [word_times(i) for i in range(NL)]
def wtime(i, word, nth=0):
    ws, ts = WT[i]; c = 0
    for w_, tt in zip(ws, ts):
        if norm(w_) == word:
            if c == nth: return tt
            c += 1
    return STARTS[i]

T_DIX = wtime(0, '15')
T_ANG = wtime(0, 'angle')
T_PIEGE = wtime(4, 'piège')
T_HUIT6 = wtime(6, '8')
T_VOLE = T_DIX

def chunks(words, d, f, maxw):
    res = []; cur = []
    for k, w_ in enumerate(words):
        test = cur + [k]
        lines = wrap(d, ' '.join(words[j] for j in test), f, maxw)
        if len(lines) > 2 or (cur and words[cur[-1]].rstrip('»')[-1] in '.!?…' and len(cur) >= 2):
            res.append(cur); cur = [k]
        else: cur = test
    if cur: res.append(cur)
    return res

def draw_subs(img, d, t):
    f = F(64)
    for i in range(NL):
        st = STARTS[i]; en = st + D[i] + GAP
        if i == 5: en = ANS - 0.05
        if i == 4: en = CS + 0.6
        if i == 6: en = T + 1
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
                    sc = 1 + 0.12 * max(0, 1 - age / 0.15) if age > 0 else 1
                    col = (255, 214, 50) if norm(w_) in KEY[i] else (255, 255, 255)
                    text_stroke(d, (x + ww / 2, y + li * 82), w_, F(int(64 * sc)), col, sw=6)
                x += ww + d.textlength(' ', font=f) + 12

# ---------------- personnages ----------------
CHAR = {
    'LÉA': dict(x=200, col=(230, 110, 160), hair=(50, 30, 26), style='long', skin=(226, 170, 124)),
    'HUGO': dict(x=540, col=(80, 150, 230), hair=(130, 80, 40), style='short', skin=(206, 150, 106)),
    'NINA': dict(x=880, col=(90, 200, 120), hair=(190, 80, 40), style='bun', skin=(236, 186, 140)),
    'GARDIEN': dict(x=190, col=(210, 70, 60), hair=(40, 30, 30), style='short', skin=(206, 150, 106)),
    'PRISONNIER': dict(x=440, col=(200, 130, 70), hair=(70, 44, 30), style='short', skin=(220, 166, 120)),
    'A': dict(x=330, col=(180, 110, 230), hair=(60, 36, 28), style='short', skin=(226, 170, 124)),
    'B': dict(x=750, col=(90, 190, 120), hair=(150, 70, 40), style='short', skin=(226, 170, 124)),
}
PY = 680

def draw_person(name, t, mouth, blink, mood=0):
    """mood : 0 neutre, 1 sourire en coin (suspect), -1 inquiet"""
    c = CHAR[name]
    S = 2; w, h = 300, 560
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = c['col']; skin = c['skin']; hair = c['hair']
    br = math.sin(t * 2 * math.pi / 3.0 + c['x']) * 4
    cx = w // 2; hy = 230 + br * 0.5
    by0 = 320 + br
    if c['style'] == 'long':
        d.rounded_rectangle([(cx - 92) * S, (hy - 60) * S, (cx + 92) * S, (hy + 150) * S], radius=50 * S, fill=hair)
    d.rounded_rectangle([(cx - 110) * S, by0 * S, (cx + 110) * S, (h + 40) * S], radius=60 * S, fill=tuple(int(v * 0.75) for v in col))
    d.polygon([(cx - 46) * S, by0 * S, (cx + 46) * S, by0 * S, cx * S, (by0 + 60) * S], fill=skin)
    # plaque nominative
    fs = 40 if len(name) > 1 else 60
    tw = d.textlength(name, font=F(fs * S)) / S
    d.rounded_rectangle([(cx - tw / 2 - 18) * S, (by0 + 82) * S, (cx + tw / 2 + 18) * S, (by0 + 150) * S], radius=14 * S, fill=(250, 240, 220), outline=col, width=6 * S)
    d.text((cx * S, (by0 + 117) * S), name, font=F(fs * S), fill=(30, 20, 26), anchor='mm')
    d.rectangle([(cx - 26) * S, (hy + 50) * S, (cx + 26) * S, (hy + 92) * S], fill=tuple(int(v * 0.88) for v in skin))
    d.ellipse([(cx - 80) * S, (hy - 80) * S, (cx + 80) * S, (hy + 80) * S], fill=skin)
    d.chord([(cx - 84) * S, (hy - 88) * S, (cx + 84) * S, (hy + 40) * S], 180, 360, fill=hair)
    for k in range(5):
        xx = cx - 70 + k * 35
        d.ellipse([(xx - 22) * S, (hy - 70) * S, (xx + 22) * S, (hy - 34) * S], fill=hair)
    if c['style'] == 'bun':
        d.ellipse([(cx - 36) * S, (hy - 130) * S, (cx + 36) * S, (hy - 62) * S], fill=hair)
    if c['style'] == 'long':
        d.chord([(cx - 84) * S, (hy - 86) * S, (cx + 20) * S, (hy - 10) * S], 180, 360, fill=hair)
    # sourcils
    for sgn in (-1, 1):
        x0 = cx + sgn * 44; x1 = cx + sgn * 14
        if mood == 1 and sgn == 1: d.line([x0 * S, (hy - 36) * S, x1 * S, (hy - 24) * S], fill=(50, 30, 24), width=9 * S)
        elif mood == 1: d.line([x0 * S, (hy - 26) * S, x1 * S, (hy - 28) * S], fill=(50, 30, 24), width=9 * S)
        elif mood == -1: d.line([x0 * S, (hy - 26) * S, x1 * S, (hy - 38) * S], fill=(50, 30, 24), width=9 * S)
        else: d.line([x0 * S, (hy - 22) * S, x1 * S, (hy - 30) * S], fill=(50, 30, 24), width=9 * S)
    for sgn in (-1, 1):
        ex = cx + sgn * 30; ey = hy - 2
        if blink:
            d.line([(ex - 10) * S, ey * S, (ex + 10) * S, ey * S], fill=(30, 20, 20), width=5 * S)
        else:
            d.ellipse([(ex - 13) * S, (ey - 13) * S, (ex + 13) * S, (ey + 13) * S], fill=(255, 255, 255))
            d.ellipse([(ex - 7) * S, (ey - 8) * S, (ex + 7) * S, (ey + 8) * S], fill=(30, 20, 20))
    d.ellipse([(cx - 10) * S, (hy + 10) * S, (cx + 12) * S, (hy + 28) * S], fill=tuple(int(v * 0.9) for v in skin))
    my = hy + 48
    if mouth >= 0.08:
        oh = 6 + mouth * 24
        d.ellipse([(cx - 20) * S, (my - oh / 2) * S, (cx + 20) * S, (my + oh / 2) * S], fill=(70, 22, 26))
    elif mood == 1:
        d.arc([(cx - 10) * S, (my - 22) * S, (cx + 34) * S, (my + 8) * S], 20, 150, fill=(70, 30, 30), width=6 * S)
    elif mood == -1:
        d.arc([(cx - 18) * S, (my - 2) * S, (cx + 18) * S, (my + 16) * S], 200, 340, fill=(70, 30, 30), width=5 * S)
    else:
        d.arc([(cx - 22) * S, (my - 10) * S, (cx + 22) * S, (my + 8) * S], 20, 160, fill=(70, 30, 30), width=5 * S)
    return im.resize((w, h), Image.LANCZOS)

def small_bubble(img, d, cx, cy, txt, col, u, n, tail_x=None, maxw=300):
    if u <= 0: return
    f = F(42)
    lines = wrap(d, txt, f, maxw)
    bw = max(d.textlength(l, font=f) for l in lines) + 50; bh = 36 + 54 * len(lines)
    sc = clamp(u, 0.01, 1.2)
    tx = cx if tail_x is None else tail_x
    def S(x, y): return (cx + (x - cx) * sc, cy + (y - cy) * sc)
    x0, y0 = cx - bw / 2, cy - bh / 2
    p0, p1 = S(x0, y0), S(x0 + bw, y0 + bh)
    d.rounded_rectangle([p0[0] - 6, p0[1] - 6, p1[0] + 6, p1[1] + 6], radius=30, fill=col)
    d.polygon([S(tx - 22, y0 + bh), S(tx + 22, y0 + bh), S(tx - 6, y0 + bh + 46)], fill=col)
    d.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]], radius=26, fill=(255, 255, 255))
    d.polygon([S(tx - 13, y0 + bh - 3), S(tx + 13, y0 + bh - 3), S(tx - 3, y0 + bh + 32)], fill=(255, 255, 255))
    if u > 0.9:
        shown = 0
        for li, ln in enumerate(lines):
            part = ln[:max(0, n - shown)]; shown += len(ln) + 1
            d.text((cx - d.textlength(ln, font=f) / 2, y0 + 18 + 27 + li * 54), part, font=f, fill=(30, 20, 26), anchor='lm')

G = {}
def mouth_env(i):
    v, sr = sf.read(f'v{i}.wav')
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(v[k:k + hop] ** 2)) for k in range(0, len(v), hop)])
    return e / (e.max() + 1e-9)

def init():
    random.seed(1)
    hall = stone_wall(2); draw_clock(hall, 2)
    well = stone_wall(2); draw_well(well, 2)
    for nm, im in [('c', hall), ('w', well)]:
        base = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32)
        G[nm + 'dark'] = Image.fromarray(np.clip(base * 0.8 + glow_layer(0.30) * 0.6, 0, 255).astype(np.uint8))
        G[nm + 'lit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.55) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    for i in (3,): G[f'env{i}'] = mouth_env(i)
    G['night'] = Image.new('RGBA', (W, H), (20, 30, 90, 0))

WX0, WX1, WTOP, WBOT = 300, 780, 420, 1250
def YM(m): return 1228 - m * 76
def draw_well(im, S):
    d = ImageDraw.Draw(im)
    # intérieur du puits (pierres plus sombres)
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
    # ombre sur les bords
    for k in range(40):
        a = 1 - k / 40
        c = (int(10 + 30 * (1 - a)), int(7 + 20 * (1 - a)), int(10 + 28 * (1 - a)))
    d.rectangle([WX0 * S, WTOP * S, (WX0 + 22) * S, WBOT * S], fill=(12, 8, 12))
    d.rectangle([(WX1 - 22) * S, WTOP * S, WX1 * S, WBOT * S], fill=(12, 8, 12))
    # fond : paille + eau
    d.rectangle([WX0 * S, (WBOT - 22) * S, WX1 * S, WBOT * S], fill=(90, 70, 40))
    for k in range(30):
        xx = WX0 + 10 + rnd.randint(0, WX1 - WX0 - 20)
        d.line([xx * S, (WBOT - 20) * S, (xx + rnd.randint(-20, 20)) * S, (WBOT - 36) * S], fill=(170, 140, 70), width=3 * S)
    # margelle
    d.rounded_rectangle([(WX0 - 40) * S, (WTOP - 34) * S, (WX1 + 40) * S, (WTOP + 20) * S], radius=16 * S, fill=(96, 74, 86))
    for k in range(7):
        xx = WX0 - 40 + k * 80
        d.line([xx * S, (WTOP - 34) * S, xx * S, (WTOP + 20) * S], fill=(70, 52, 62), width=4 * S)
    d.rectangle([(WX0 - 40) * S, (WTOP - 34) * S, (WX1 + 40) * S, (WTOP - 24) * S], fill=(120, 96, 108))
    # graduation
    gx = WX1 + 70
    d.line([gx * S, YM(0) * S, gx * S, YM(10) * S], fill=(220, 200, 170), width=5 * S)
    for m in range(11):
        L = 26 if m % 5 == 0 else 14
        d.line([(gx - L) * S, YM(m) * S, gx * S, YM(m) * S], fill=(220, 200, 170), width=5 * S)
    for m in (0, 5, 10):
        d.text(((gx + 14) * S, YM(m) * S), f"{m} m", font=F(36 * S), fill=(240, 225, 200), anchor='lm')

def snail(d, x, y, t, sc=1.0):
    # escargot qui grimpe sur la paroi droite, tête vers le haut
    bob = 2 * math.sin(t * 6)
    d.rounded_rectangle([x - 12 * sc, y - 46 * sc + bob, x + 14 * sc, y + 40 * sc], radius=int(13 * sc), fill=(150, 170, 110))
    for sgn in (-1, 1):
        ex = x + sgn * 8 * sc; ey = y - 70 * sc + bob
        d.line([x + sgn * 3 * sc, y - 40 * sc + bob, ex, ey], fill=(150, 170, 110), width=int(5 * sc))
        d.ellipse([ex - 6 * sc, ey - 6 * sc, ex + 6 * sc, ey + 6 * sc], fill=(30, 20, 20))
    cx, cy, r = x - 26 * sc, y + 4 * sc, 32 * sc
    d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(90, 50, 24))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(230, 150, 50))
    for k, rr in enumerate([0.72, 0.46, 0.22]):
        d.arc([cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr], 30 + k * 40, 330 + k * 40, fill=(140, 76, 26), width=int(5 * sc))

def snail_m(t):
    if t < s1 + 0.3: return 0.0
    if t < s1 + 1.5: return 3 * ss((t - s1 - 0.3) / 1.2)
    if t < s2 + 0.3: return 3.0
    if t < s2 + 1.4: return 3 - 2 * ss((t - s2 - 0.3) / 1.1)
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

CCX, CCY, CR = 610, 690, 230
def draw_clock(im, S):
    d = ImageDraw.Draw(im)
    # caisse de l'horloge + balancier
    d.rounded_rectangle([(CCX - 120) * S, (CCY + 150) * S, (CCX + 120) * S, (CCY + 560) * S], radius=24 * S, fill=(92, 58, 36))
    d.rounded_rectangle([(CCX - 92) * S, (CCY + 250) * S, (CCX + 92) * S, (CCY + 530) * S], radius=16 * S, fill=(40, 26, 22))
    # cadran
    d.ellipse([(CCX - CR - 30) * S, (CCY - CR - 30) * S, (CCX + CR + 30) * S, (CCY + CR + 30) * S], fill=(120, 76, 42))
    d.ellipse([(CCX - CR - 16) * S, (CCY - CR - 16) * S, (CCX + CR + 16) * S, (CCY + CR + 16) * S], fill=(160, 108, 60))
    d.ellipse([(CCX - CR) * S, (CCY - CR) * S, (CCX + CR) * S, (CCY + CR) * S], fill=(244, 230, 200))
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = CR - (26 if k % 5 == 0 else 12)
        d.line([(CCX + math.cos(a) * r0) * S, (CCY + math.sin(a) * r0) * S, (CCX + math.cos(a) * (CR - 6)) * S, (CCY + math.sin(a) * (CR - 6)) * S],
               fill=(60, 40, 34), width=(7 if k % 5 == 0 else 3) * S)
    for hh in range(1, 13):
        a = math.radians(hh * 30 - 90); r = CR - 62
        d.text(((CCX + math.cos(a) * r) * S, (CCY + math.sin(a) * r) * S), str(hh), font=F(44 * S), fill=(50, 32, 28), anchor='mm')

def hand(d, ang, L, w, col, out=(30, 20, 20)):
    a = math.radians(ang - 90)
    ex, ey = CCX + math.cos(a) * L, CCY + math.sin(a) * L
    bx, by = CCX - math.cos(a) * L * 0.18, CCY - math.sin(a) * L * 0.18
    d.line([bx, by, ex, ey], fill=out, width=w + 8)
    d.line([bx, by, ex, ey], fill=col, width=w)
    return ex, ey

BUBP = "Quel est l'angle exact ?"
BY = 720
PYG = 760
SX = WX1 - 44

def cam(t):
    keys = [(0, 1.08, 560, 820), (T_DIX + 0.4, 1.02, 540, 840),
            (s1 + 0.1, 1.02, 540, 840), (s1 + 0.5, 1.22, CCX, CCY), (s2 + 0.1, 1.22, CCX, CCY), (s2 + 0.6, 1.75, CCX + 40, CCY - 10), (s3 - 0.1, 1.75, CCX + 40, CCY - 10),
            (s3 + 0.3, 1.10, 330, 900), (s4 - 0.1, 1.10, 330, 900),
            (s4 + 0.4, 1.0, 540, 860), (CE, 1.06, 540, 860), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh in [T_DIX, STAMP]:
        if 0 <= t - hh < 0.35:
            a = (1 - (t - hh) / 0.35) * 16
            sx += a * math.sin((t - hh) * 90); sy += a * math.cos((t - hh) * 77)
    return sx, sy

def badge(d, x, y, txt, u, fill=(255, 206, 40), tcol=(24, 14, 20), size=44):
    if u <= 0: return
    f = F(size * clamp(u, 0.05, 1.2)); tw = d.textlength(txt, font=f)
    h = size * 0.75 * clamp(u, 0.05, 1.2)
    if h < 8: return
    d.rounded_rectangle([x - tw / 2 - 20, y - h, x + tw / 2 + 20, y + h], radius=int(h), fill=(16, 10, 16))
    d.rounded_rectangle([x - tw / 2 - 16, y - h + 4, x + tw / 2 + 16, y + h - 4], radius=int(h) - 4, fill=fill)
    d.text((x, y + 2), txt, font=f, fill=tcol, anchor='mm')

GREEN = (90, 200, 120); RED = (230, 60, 50)
def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['cdark'], G['clit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # balancier
    sw = 16 * math.sin(t * math.pi)
    a = math.radians(sw); px, py = CCX, CCY + 250
    ex, ey = px + math.sin(a) * 230, py + math.cos(a) * 230
    d.line([px, py, ex, ey], fill=(200, 160, 70), width=8)
    d.ellipse([ex - 34, ey - 34, ex + 34, ey + 34], fill=(220, 180, 80), outline=(120, 86, 40), width=5)
    # aiguilles à 3 h 15 : grande 90°, petite 97,5°
    hi_m = s1 + 0.2 <= t < s2 + 0.1
    hi_h = s2 + 0.1 <= t < s4
    # la petite glisse doucement du 3 vers sa vraie place pendant la phrase 2
    hang = 90.0 if t < s2 + 0.2 else 90.0 + 7.5 * ss((t - s2 - 0.2) / 0.9)
    if t < s1: hang = 97.5
    if t >= s4: hang = 97.5
    if hi_h or t >= s4:
        # coin rouge entre les aiguilles
        r = CR - 40
        d.pieslice([CCX - r, CCY - r, CCX + r, CCY + r], 0, hang - 90, fill=(230, 60, 50))
    hand(d, hang, CR * 0.55, 18, (255, 214, 50) if hi_h else (50, 34, 30))
    hand(d, 90.0, CR * 0.86, 12, (255, 214, 50) if hi_m else (50, 34, 30))
    d.ellipse([CCX - 16, CCY - 16, CCX + 16, CCY + 16], fill=(200, 60, 50), outline=(30, 20, 20), width=4)
    if hi_m:
        badge(d, CCX + 30, CCY - 120, "GRANDE : SUR LE 3", ease_back((t - s1 - 0.2) / 0.3), size=34)
    if s2 + 0.4 <= t < s3 + 0.2:
        u = ease_back((t - s2 - 0.4) / 0.3)
        badge(d, CCX + 40, CCY + 110, "PETITE : PAS PILE SUR LE 3 !", u, fill=RED, tcol=(255, 255, 255), size=24)
    if s3 + 0.2 <= t < s5 and t >= T_PIEGE:
        badge(d, CCX + 170, CCY + 40, " ?° ", ease_back((t - T_PIEGE) / 0.3), fill=RED, tcol=(255, 255, 255), size=44)
    # gardien
    mouth = 0
    if s3 + 0.05 <= t < s3 + D[3]:
        k = int((t - s3) * FPS); e = G['env3']
        mouth = clamp(e[k] * 1.6) if k < len(e) else 0
    bl = (t % 3.2) < 0.12
    img.alpha_composite(draw_person('GARDIEN', t, mouth, bl, 1), (CHAR['GARDIEN']['x'] - 150, PYG))
    d = ImageDraw.Draw(img)
    # clé de la cellule
    if T_ANG <= t < s1 + 0.2:
        u = ease_back((t - T_ANG) / 0.3); bob = 8 * math.sin(t * 5)
        badge(d, CHAR['GARDIEN']['x'] + 10, 860 + bob, "🗝" if False else "LIBRE ?", u, size=40)
    ts = s3 + 0.35
    if ts - 0.25 <= t < s5:
        small_bubble(img, d, 290, BY, BUBP, CHAR['GARDIEN']['col'],
                     ease_back((t - (ts - 0.25)) / 0.25), int((t - ts + 0.1) * 30), tail_x=CHAR["GARDIEN"]["x"] + 10, maxw=400)
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
        f3 = F(38); tw = d.textlength(CONTRAINTE, font=f3)
        d.rounded_rectangle([W / 2 - tw / 2 - 26, 252, W / 2 + tw / 2 + 26, 312], radius=30, fill=(200, 44, 44))
        d.text((W / 2, 283), CONTRAINTE, font=f3, fill=(255, 255, 255), anchor='mm')

CHX = ['0', '7,5', '15']
CHC = [(230, 110, 160), (80, 150, 230), (90, 200, 120)]
def choices(img, d, t):
    T0 = wtime(4, '0') - 0.2
    if not (T0 - 0.05 <= t < ANS): return
    for k, lab in enumerate(CHX):
        col = CHC[k]
        ts = T0 + k * 0.2
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 3) % 3 == k: pul = 1.08
        s = u * pul
        x = 200 + k * 340; y = 1310
        bw, bh = 300 * s, 120 * s
        d.rounded_rectangle([x - bw / 2 - 7, y - bh / 2 - 7, x + bw / 2 + 7, y + bh / 2 + 7], radius=int(50 * s) + 7, fill=col)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(50 * s), fill=(26, 18, 30))
        if s > 0.3:
            fl = F(72 * s); lw = d.textlength(lab, font=fl); dw = d.textlength("°", font=fl)
            d.text((x - dw / 2, y + 3), lab, font=fl, fill=(255, 255, 255), anchor='mm')
            d.text((x - dw / 2 + lw / 2 + dw / 2 + 2, y + 3), "°", font=fl, fill=(255, 214, 50), anchor='mm')

def chrono(img, d, t):
    if not (CS <= t < CE + 0.3): return
    rem = max(0, CE - t); frac = rem / CHR
    ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
    beat = 1 + 0.08 * math.exp(-ph * 8)
    cx, cy, r = 540, 452, int(82 * beat)
    d.ellipse([cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16], fill=(16, 10, 16, 235))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(70, 50, 60), width=18)
    col = (255, 206, 40) if rem > 2.5 else (255, 60, 50)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=col, width=18)
    d.text((cx, cy + 4), str(int(math.ceil(rem))) if rem > 0 else "0", font=F(int(90 * beat)), fill=(255, 255, 255), anchor='mm')

def red_vig(img, t):
    if CS <= t < CE + 0.5:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
        a = (0.25 + 0.55 * (t - CS) / CHR) * (0.6 + 0.4 * math.exp(-ph * 6))
        if t > CE: a *= max(0, 1 - (t - CE) / 0.5)
        r = G['red'].copy(); r.putalpha(r.getchannel('A').point(lambda v: int(v * clamp(a))))
        img.alpha_composite(r)

def outro_cta(img, d, t):
    if not (s5 - 0.05 <= t < ANS): return
    u = ease_back((t - s5) / 0.3)
    f = F(int(56 * clamp(u, 0, 1.2)) + 1)
    y = 500
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS 0, 7,5 OU 15", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(740 - s.height / 2)))

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['wdark'], G['wlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    got = t >= T_HUIT6
    bl = (t % 3.2) < 0.12
    img.alpha_composite(draw_person('PRISONNIER', t, 0, bl, 0 if got else -1), (CHAR['PRISONNIER']['x'] - 150, 700))
    d = ImageDraw.Draw(img)
    m = 7 + 3 * ss((t - T_HUIT6) / 0.8) if got else 7.0
    snail(d, SX + 4, YM(m), t, 1.35)
    if got:
        u = ease_back((t - T_HUIT6) / 0.3)
        badge(d, 520, 620, "8 JOURS !", u, fill=GREEN, tcol=(255, 255, 255), size=64)
        badge(d, 520, 730, "JOUR 8 : 7 M + 3 M = 10 M", clamp((t - T_HUIT6 - 0.5) / 0.3) * 1.0, fill=(240, 230, 210), size=30)
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
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_VOLE, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '24', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
