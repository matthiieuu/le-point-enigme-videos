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

NUM = "08"; TITRE = "QUI A VOLÉ LE DIAMANT ?"; CONTRAINTE = "UN SEUL DIT LA VÉRITÉ"
TITRE_HIER = "L'ÎLE DES MENTEURS"
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Un seul de ces 3 suspects dit la vérité… trouve qui a volé le diamant !",
        "Léa dit : «C'est Hugo.»",
        "Hugo dit : «Léa ment.»",
        "Nina dit : «Ce n'est pas moi.»",
        "Alors, qui est le voleur ?",
        "Écris LÉA, HUGO ou NINA. Réponse demain !",
        "Réponse d'hier : VRAI ! A dit vrai, donc B ment."]
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
KEY = [["seul", "3", "vérité", "volé", "diamant"], ["hugo"], ["léa", "ment"], ["pas", "moi"],
       ["voleur"], ["léa", "hugo", "nina", "demain"], ["vrai", "ment"]]

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
    return w_.lower().strip(".,!?:;…'’«»").replace("qu'", '').replace("n'", '').replace("c'", '')

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

T_VOLE = wtime(0, 'volé')
T_SEUL = wtime(0, 'seul')
T_VRAI6 = wtime(6, 'vrai'); T_MENT6 = wtime(6, 'ment')

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

WIN = (330, 400, 750, 760)
def draw_window(im, S):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = WIN
    d.rounded_rectangle([(x0 - 30) * S, (y0 - 30) * S, (x1 + 30) * S, (y1 + 24) * S], radius=200 * S, fill=(84, 62, 74))
    sky = Image.new('RGB', ((x1 - x0) * S, (y1 - y0) * S))
    sd = ImageDraw.Draw(sky)
    for yy in range((y1 - y0) * S):
        u = yy / ((y1 - y0) * S)
        sd.line([0, yy, (x1 - x0) * S, yy], fill=(int(20 + 40 * u), int(24 + 30 * u), int(60 + 50 * u)))
    rnd = random.Random(3)
    for k in range(26):
        sx, sy = rnd.randint(0, (x1 - x0) * S), rnd.randint(0, int((y1 - y0) * S * 0.55))
        r = rnd.choice([2, 3, 4]); sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(230, 230, 250))
    sd.ellipse([250 * S, 50 * S, 330 * S, 130 * S], fill=(250, 240, 200))
    sd.ellipse([272 * S, 42 * S, 352 * S, 122 * S], fill=(26, 28, 66))
    sd.chord([30 * S, 200 * S, 200 * S, 300 * S], 180, 360, fill=(16, 22, 30))
    mask = Image.new('L', sky.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sky.size[0] - 1, sky.size[1] - 1], radius=190 * S, fill=255)
    im.paste(sky, (x0 * S, y0 * S), mask)

def draw_waves(d, t):
    x0, y0, x1, y1 = WIN
    for k in range(5):
        yy = 640 + k * 24
        col = (40 + k * 6, 60 + k * 8, 110 + k * 10)
        pts = [(x, yy + 6 * math.sin(x / 26 + t * (1.6 + k * 0.3) + k)) for x in range(x0 + 4, x1 - 3, 6)]
        d.line(pts, fill=col, width=5)

def init():
    random.seed(1)
    hall = stone_wall(2); draw_case(hall, 2)
    isle = stone_wall(2); draw_window(isle, 2)
    for nm, im in [('h', hall), ('i', isle)]:
        base = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32)
        G[nm + 'dark'] = Image.fromarray(np.clip(base * 0.8 + glow_layer(0.30) * 0.6, 0, 255).astype(np.uint8))
        G[nm + 'lit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.55) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    G['vole'] = stamp_img('VOLÉ !', (230, 46, 46), 60, 20, rot=-10)
    for i in (1, 2, 3, 6): G[f'env{i}'] = mouth_env(i)

SPK = [(1, 'LÉA'), (2, 'HUGO'), (3, 'NINA')]
BUB = {'LÉA': "C'est Hugo !", 'HUGO': "Léa ment !", 'NINA': "Ce n'est pas moi !"}
BY = 640

def cam(t):
    keys = [(0, 1.10, 540, 820), (T_VOLE + 0.4, 1.02, 540, 840),
            (s1 - 0.1, 1.02, 540, 840), (s1 + 0.3, 1.08, 380, 860), (s2 - 0.1, 1.08, 380, 860),
            (s2 + 0.3, 1.08, 540, 860), (s3 - 0.1, 1.08, 540, 860),
            (s3 + 0.3, 1.08, 700, 860), (s4 - 0.1, 1.08, 700, 860),
            (s4 + 0.4, 1.0, 540, 860), (CE, 1.06, 540, 860), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh in [T_VOLE, STAMP]:
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
    img = Image.blend(G['hdark'], G['hlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    x0, y0, x1, y1 = CASE
    if t < T_VOLE:
        diamond(d, (x0 + x1) / 2, y1 - 80, 1.0, t)
    else:
        u = (t - T_VOLE) / 0.25
        if u < 1:
            diamond(d, (x0 + x1) / 2, y1 - 80 - 120 * u, 1 - u, t)
        st = G['vole']; sc = 1 + 1.4 * max(0, 1 - (t - T_VOLE) / 0.13)
        s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int((x0 + x1) / 2 - s.width / 2), int(y1 - 90 - s.height / 2)))
    for i, nm in SPK:
        mouth = 0
        if STARTS[i] + 0.05 <= t < STARTS[i] + D[i]:
            k = int((t - STARTS[i]) * FPS); e = G[f'env{i}']
            mouth = clamp(e[k] * 1.6) if k < len(e) else 0
        mood = -1 if (nm == 'HUGO' and s1 + 0.3 <= t < s2) or (nm == 'LÉA' and s2 + 0.3 <= t < s3) else 0
        if nm == 'NINA' and t >= s3 + D[3]: mood = 1
        bl = ((t + CHAR[nm]['x'] / 300) % 3.2) < 0.12
        img.alpha_composite(draw_person(nm, t, mouth, bl, mood), (CHAR[nm]['x'] - 150, PY))
    d = ImageDraw.Draw(img)
    # « ? » au-dessus des têtes au début
    if T_SEUL <= t < s1:
        for k, (i, nm) in enumerate(SPK):
            u = ease_back((t - T_SEUL - k * 0.12) / 0.3); bob = 8 * math.sin(t * 5 + k)
            badge(d, CHAR[nm]['x'], BY + 40 + bob, " ? ", u, size=56)
    for i, nm in SPK:
        ts = STARTS[i] + 0.35
        if ts - 0.25 <= t < s5:
            small_bubble(img, d, CHAR[nm]['x'], BY, BUB[nm], CHAR[nm]['col'],
                         ease_back((t - (ts - 0.25)) / 0.25), int((t - ts + 0.1) * 30), tail_x=CHAR[nm]['x'] - 10)
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

CHX = ['LÉA', 'HUGO', 'NINA']
def choices(img, d, t):
    T0 = wtime(4, 'voleur') - 0.3
    if not (T0 - 0.05 <= t < ANS): return
    for k, lab in enumerate(CHX):
        col = CHAR[lab]['col']
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
            d.text((x, y + 3), lab, font=F(66 * s), fill=(255, 255, 255), anchor='mm')

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
    d.text((W / 2, y - 40), "ÉCRIS LÉA, HUGO OU NINA", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(740 - s.height / 2)))

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['idark'], G['ilit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    draw_waves(d, t)
    mouth = 0
    img.alpha_composite(draw_person('A', t, 0, (t % 3.1) < 0.12, 1 if t >= T_VRAI6 else 0), (CHAR['A']['x'] - 150, PY))
    img.alpha_composite(draw_person('B', t, 0, ((t + 1.3) % 3.4) < 0.12, -1 if t >= T_MENT6 else 0), (CHAR['B']['x'] - 150, PY))
    d = ImageDraw.Draw(img)
    if t >= T_VRAI6:
        badge(d, CHAR['A']['x'], 740, "VRAI", ease_back((t - T_VRAI6) / 0.3), fill=GREEN, tcol=(16, 30, 20), size=56)
    if t >= T_MENT6:
        badge(d, CHAR['B']['x'], 740, "MENTEUR", ease_back((t - T_MENT6) / 0.3), fill=RED, tcol=(255, 255, 255), size=52)
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
                              '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
