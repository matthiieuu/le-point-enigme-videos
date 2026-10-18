import json, math, random, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

W, H, FPS = 1080, 1920, 30
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
_fc = {}
def F(s):
    if s not in _fc: _fc[s] = ImageFont.truetype(FB, s)
    return _fc[s]

D = json.load(open('durees.json'))
LIGNES = json.load(open('lignes.json'))
s0 = 0.0
s1 = s0 + D[0] + 0.25
s2 = s1 + D[1] + 0.25
s3 = s2 + D[2] + 0.25
CS = s3 + D[3] + 0.2
CE = CS + 8.0
s4 = CE + 0.1
STAMP = s4 + D[4] * 0.6
ANS = s4 + D[4] + 0.35
s5 = ANS + 0.3
FADE = s5 + D[5] + 0.5
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, s5]
NF = int(round(T * FPS))
KEY = [["trois", "fausses"], ["seul", "fruit"], ["cachot"], ["a", "b", "c"], ["lettre", "demain"], ["dix", "binaire", "morts"]]

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ss(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------------- statique ----------------
JC = (214, 86, 70)   # couleur geolier
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

def radial(size, col, r, a):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    return None

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

def build_static():
    S = 2
    big = stone_wall(S)
    draw_table_boxes(big, S)
    base = np.asarray(big.resize((W, H), Image.LANCZOS)).astype(np.float32)
    dark = np.clip(base * 0.82 + glow_layer(0.30) * 0.6, 0, 255)
    lit = np.clip(base * 1.0 + glow_layer(0.55) * 0.7, 0, 255)
    return Image.fromarray(dark.astype(np.uint8)), Image.fromarray(lit.astype(np.uint8))

def build_wall_only():
    big = stone_wall(2)
    base = np.asarray(big.resize((W, H), Image.LANCZOS)).astype(np.float32)
    return Image.fromarray(np.clip(base * 0.75 + glow_layer(0.4) * 0.6, 0, 255).astype(np.uint8))

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

# ---------------- personnages ----------------
def draw_jailer(t, mouth, blink):
    S = 2; w, h = 520, 330
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    br = math.sin(t * 2 * math.pi / 3.2) * 4
    cx = w // 2; hy = 120 + br * 0.5
    # corps
    d.rounded_rectangle([(cx - 175) * S, (205 + br) * S, (cx + 175) * S, (h + 60) * S], radius=70 * S, fill=(92, 34, 34))
    d.polygon([(cx - 60) * S, (205 + br) * S, (cx + 60) * S, (205 + br) * S, cx * S, (280 + br) * S], fill=(60, 22, 24))
    d.rectangle([(cx - 175) * S, (290 + br) * S, (cx + 175) * S, (312 + br) * S], fill=(50, 32, 22))
    d.ellipse([(cx + 70) * S, (284 + br) * S, (cx + 104) * S, (318 + br) * S], outline=(200, 170, 80), width=5 * S)
    # cou + tete
    d.rectangle([(cx - 34) * S, (hy + 60) * S, (cx + 34) * S, (hy + 100) * S], fill=(196, 140, 100))
    d.ellipse([(cx - 96) * S, (hy - 12) * S, (cx - 64) * S, (hy + 30) * S], fill=(210, 152, 110))
    d.ellipse([(cx + 64) * S, (hy - 12) * S, (cx + 96) * S, (hy + 30) * S], fill=(210, 152, 110))
    d.ellipse([(cx - 86) * S, (hy - 88) * S, (cx + 86) * S, (hy + 86) * S], fill=(226, 170, 124))
    # crane / bandeau
    d.chord([(cx - 86) * S, (hy - 88) * S, (cx + 86) * S, (hy + 86) * S], 190, 350, fill=(60, 40, 40))
    # barbe
    d.chord([(cx - 82) * S, (hy - 40) * S, (cx + 82) * S, (hy + 88) * S], 20, 160, fill=(110, 70, 50))
    # sourcils
    for sgn in (-1, 1):
        x0 = cx + sgn * 62; x1 = cx + sgn * 14
        d.line([x0 * S, (hy - 34) * S, x1 * S, (hy - 20) * S], fill=(40, 24, 20), width=11 * S)
    # yeux
    for sgn in (-1, 1):
        ex = cx + sgn * 36; ey = hy - 4
        if blink:
            d.line([(ex - 10) * S, ey * S, (ex + 10) * S, ey * S], fill=(30, 20, 20), width=5 * S)
        else:
            d.ellipse([(ex - 10) * S, (ey - 10) * S, (ex + 10) * S, (ey + 10) * S], fill=(30, 20, 20))
            d.ellipse([(ex - 5) * S, (ey - 7) * S, (ex + 1) * S, (ey - 1) * S], fill=(255, 255, 255))
    # nez
    d.ellipse([(cx - 14) * S, (hy + 4) * S, (cx + 14) * S, (hy + 26) * S], fill=(206, 140, 100))
    # bouche
    my = hy + 46
    if mouth < 0.08:
        d.arc([(cx - 30) * S, (my - 18) * S, (cx + 30) * S, (my + 8) * S], 20, 160, fill=(70, 30, 30), width=6 * S)
    else:
        oh = 6 + mouth * 26
        d.ellipse([(cx - 24) * S, (my - oh / 2) * S, (cx + 24) * S, (my + oh / 2) * S], fill=(70, 22, 26))
        d.ellipse([(cx - 12) * S, (my + oh / 2 - 9) * S, (cx + 12) * S, (my + oh / 2 - 1) * S], fill=(200, 90, 90))
    return im.resize((w, h), Image.LANCZOS)

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

# ---------------- rendu ----------------
G = {}
def init():
    random.seed(1)
    G['dark'], G['lit'] = build_static()
    G['wall'] = build_wall_only()
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['sil'] = silhouette()
    G['faux'] = stamp_img('FAUX', (226, 40, 40), 46, 18, rot=-14)
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    G['env'] = mouth_env(2)

def mouth_env(i):
    v, sr = sf.read(f'v{i}.wav')
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(v[k:k + hop] ** 2)) for k in range(0, len(v), hop)])
    return e / (e.max() + 1e-9)

def cam(t):
    # (zoom, cx, cy)
    keys = [(0, 1.14, 540, 980), (2.2, 1.05, 540, 980), (s1 + 0.1, 1.08, 420, 980), (s2 - 0.1, 1.08, 660, 980),
            (s2 + 0.9, 1.2, 540, 760), (s3 - 0.1, 1.2, 540, 760), (s3 + 0.8, 1.0, 540, 1000), (CS, 1.0, 540, 1000),
            (CE, 1.1, 540, 1000), (CE + 0.6, 1.04, 540, 1000), (ANS, 1.04, 540, 1000)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    hits = [FAUXT + k * 0.14 for k in range(3)] + [STAMP]
    for h in hits:
        if 0 <= t - h < 0.35:
            a = (1 - (t - h) / 0.35) * 16
            sx += a * math.sin((t - h) * 90); sy += a * math.cos((t - h) * 77)
    return sx, sy

w0, tm0 = WT[0]
FAUXT = tm0[-1] + 0.05

def scene(t, fi):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['dark'], G['lit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # geolier (derriere les boites : on redessine les boites ensuite -> on le colle puis on remet la zone avant)
    mouth = 0
    if s2 <= t < s2 + D[2]:
        k = int((t - s2) * FPS)
        if k < len(G['env']): mouth = clamp(G['env'][k] * 1.6)
    blink = ((t + 1.5) % 3.7) < 0.12
    jl = draw_jailer(t, mouth, blink)
    front = G['lit'].crop((0, 870, W, 1300)).convert('RGBA')  # table + boites (premier plan)
    img.alpha_composite(jl, (540 - 260, 610))
    # remettre boites/table devant
    mask = Image.new('L', (W, 430), 0)
    md = ImageDraw.Draw(mask)
    for bx in BOX_X:
        md.rounded_rectangle([bx - BOX_W // 2 - 2, (BOX_BOT - BOX_H - 22) - 870, bx + BOX_W // 2 + 2, BOX_BOT + 14 - 870], radius=10, fill=255)
    md.rectangle([38, TABLE_Y - 12 - 870, 1042, 430], fill=255)
    lit_front = Image.blend(G['dark'], G['lit'], clamp(f)).crop((0, 870, W, 1300)).convert('RGBA')
    img.paste(lit_front, (0, 870), mask)
    d = ImageDraw.Draw(img)
    # tampons FAUX
    for k, bx in enumerate(BOX_X):
        ts = FAUXT + k * 0.14
        if t >= ts:
            sc = 1 + 1.4 * max(0, 1 - (t - ts) / 0.12)
            st = G['faux']; sw, sh = int(st.width * sc), int(st.height * sc)
            s = st.resize((sw, sh), Image.BILINEAR)
            img.alpha_composite(s, (int(bx - sw / 2 + 50), int(BOX_BOT - BOX_H + 30 - sh / 2)))
    # lettres A B C
    if t >= s3 + 0.9:
        for k, bx in enumerate(BOX_X):
            ts = WT[3][1][-3 + k] if k < 3 else s3
            u = ease_back((t - ts) / 0.3) if t >= ts else 0
            if u <= 0: continue
            pul = 1.0
            if CS <= t < CE and int((t - CS) * 2) % 3 == k: pul = 1.12
            r = int(54 * u * pul)
            cy = TABLE_Y + 110
            d.ellipse([bx - r - 5, cy - r - 5, bx + r + 5, cy + r + 5], fill=(20, 12, 18))
            d.ellipse([bx - r, cy - r, bx + r, cy + r], fill=(255, 206, 40))
            if r > 10: d.text((bx, cy + 2), 'ABC'[k], font=F(max(10, int(64 * u * pul))), fill=(30, 18, 20), anchor='mm')
    # toi
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def camera(img, t):
    z, cx, cy = cam(t)
    sx, sy = shake(t)
    if CS <= t < CE:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.18)) % 1
        z *= 1 + 0.012 * math.exp(-ph * 9)
    cx = clamp(cx + sx, W / 2 / z, W - W / 2 / z); cy = cy + sy
    a = 1 / z; c = cx - (W / 2) / z; e = 1 / z; fy = cy - cy / z
    return img.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, fy), resample=Image.BILINEAR)

def ui_top(img, d, t, answer=False):
    img.alpha_composite(G['top'])
    d.rectangle([0, 0, int(W * t / T), 12], fill=(255, 206, 40))
    pill = "RÉPONSE D'HIER" if answer else "ÉNIGME #03"
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
    title = "LES 1000 BOUTEILLES" if answer else "LES 3 BOÎTES MENTEUSES"
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
        txt = "3 ÉTIQUETTES FAUSSES • 1 SEUL FRUIT"
        f3 = F(36); tw = d.textlength(txt, font=f3)
        pu = 1 + 0.03 * math.sin(t * 5)
        d.rounded_rectangle([W / 2 - tw / 2 - 26, 252, W / 2 + tw / 2 + 26, 312], radius=30, fill=(200, 44, 44))
        d.text((W / 2, 283), txt, font=f3, fill=(255, 255, 255), anchor='mm')

def bubble(img, d, t):
    if not (s2 - 0.05 <= t < s3 + 0.1): return
    txt = LIGNES[2]
    u = ease_back((t - s2 + 0.05) / 0.25)
    n = int(len(txt) * clamp((t - s2) / (D[2] * 0.85)))
    f = F(50)
    lines = wrap(d, txt, f, 820)
    bw, bh = 900, 70 + 66 * len(lines)
    x0, y0 = W / 2 - bw / 2, 352
    # bulle avec liseré
    sc = clamp(u, 0.01, 1.2)
    cx, cy = W / 2, y0 + bh / 2
    def S(x, y): return (cx + (x - cx) * sc, cy + (y - cy) * sc)
    p0, p1 = S(x0, y0), S(x0 + bw, y0 + bh)
    d.rounded_rectangle([p0[0] - 7, p0[1] - 7, p1[0] + 7, p1[1] + 7], radius=40, fill=JC)
    d.polygon([S(W / 2 - 40, y0 + bh), S(W / 2 + 40, y0 + bh), S(W / 2 + 10, y0 + bh + 58)], fill=JC)
    d.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]], radius=34, fill=(255, 255, 255))
    d.polygon([S(W / 2 - 28, y0 + bh - 4), S(W / 2 + 28, y0 + bh - 4), S(W / 2 + 8, y0 + bh + 40)], fill=(255, 255, 255))
    if u > 0.9:
        shown = 0
        for li, ln in enumerate(lines):
            part = ln[:max(0, n - shown)]; shown += len(ln) + 1
            col = (30, 20, 26)
            d.text((W / 2 - d.textlength(ln, font=f) / 2, y0 + 66 + li * 66), part, font=f, fill=col, anchor='lm')

def chrono(img, d, t):
    if not (CS <= t < CE + 0.3): return
    rem = max(0, CE - t); frac = rem / 8.0
    ph = ((t - CS) * (1.2 + (t - CS) * 0.18)) % 1
    beat = 1 + 0.08 * math.exp(-ph * 8)
    cx, cy, r = W / 2, 560, int(120 * beat)
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=(16, 10, 16, 230))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(70, 50, 60), width=20)
    col = (255, 206, 40) if rem > 3 else (255, 60, 50)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=col, width=20)
    d.text((cx, cy + 4), str(int(math.ceil(rem))) if rem > 0 else "0", font=F(int(118 * beat)), fill=(255, 255, 255), anchor='mm')
    d.text((cx, cy + r + 54), "TROUVE LA BONNE BOÎTE", font=F(42), fill=(255, 255, 255), stroke_width=6, stroke_fill=(10, 6, 12), anchor='mm')

def red_vig(img, t):
    if CS <= t < CE + 0.5:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.18)) % 1
        a = (0.25 + 0.55 * (t - CS) / 8) * (0.6 + 0.4 * math.exp(-ph * 6))
        if t > CE: a *= max(0, 1 - (t - CE) / 0.5)
        r = G['red'].copy(); r.putalpha(r.getchannel('A').point(lambda v: int(v * clamp(a))))
        img.alpha_composite(r)

def outro_cta(img, d, t):
    if not (s4 - 0.05 <= t < ANS): return
    u = ease_back((t - s4) / 0.3)
    f = F(int(66 * clamp(u, 0, 1.2)) + 1)
    y = 560
    d.rounded_rectangle([90, y - 120, W - 90, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([90, y - 120, W - 90, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS TA LETTRE", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(820 - s.height / 2)))

BIN = format(613, '010b')
def answer_frame(t):
    img = G['wall'].copy().convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    lt = t - ANS
    # 10 GOUTEURS
    u = ease_back((lt - 0.2) / 0.35)
    if u > 0:
        d.rounded_rectangle([110, 380, W - 110, 560], radius=40, fill=(16, 10, 16))
        d.text((W / 2, 470), "10 GOÛTEURS", font=F(int(96 * clamp(u, 0.05, 1.2))), fill=(255, 214, 50), stroke_width=6, stroke_fill=(10, 6, 12), anchor='mm')
    # tetes
    wts = WT[5][1]; tbin = wts[8]
    for k in range(10):
        row, col = divmod(k, 5)
        x = 160 + col * 190; y = 720 + row * 290
        ta = ANS + 0.6 + k * 0.08
        ua = ease_back((t - ta) / 0.3) if t >= ta else 0
        if ua <= 0: continue
        r = 62 * clamp(ua, 0, 1.2)
        dead = BIN[k] == '1' and t >= tbin + k * 0.12
        skin = (150, 170, 140) if dead else (226, 170, 124)
        d.ellipse([x - r, y - r, x + r, y + r], fill=skin, outline=(20, 12, 16), width=5)
        if r > 30:
            for sgn in (-1, 1):
                ex = x + sgn * 22; ey = y - 6
                if dead:
                    d.line([ex - 9, ey - 9, ex + 9, ey + 9], fill=(30, 20, 20), width=6)
                    d.line([ex - 9, ey + 9, ex + 9, ey - 9], fill=(30, 20, 20), width=6)
                else:
                    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(30, 20, 20))
            if dead: d.line([x - 18, y + 30, x + 18, y + 30], fill=(40, 30, 30), width=5)
            else: d.arc([x - 20, y + 10, x + 20, y + 34], 20, 160, fill=(70, 30, 30), width=5)
        if t >= tbin + k * 0.12:
            dig = BIN[k]
            d.rounded_rectangle([x - 40, y + 82, x + 40, y + 166], radius=16, fill=(255, 206, 40) if dig == '1' else (60, 50, 60))
            d.text((x, y + 126), dig, font=F(64), fill=(20, 12, 16) if dig == '1' else (220, 220, 220), anchor='mm')
    tf = tbin + 1.6
    if t >= tf:
        u = ease_back((t - tf) / 0.35)
        d.rounded_rectangle([140, 1270, W - 140, 1360], radius=30, fill=(200, 44, 44))
        d.text((W / 2, 1316), "BOUTEILLE N° 613 !", font=F(int(58 * clamp(u, 0.05, 1.15))), fill=(255, 255, 255), anchor='mm')
    return img

def frame(fi):
    t = fi / FPS
    if t < ANS:
        img = camera(scene(t, fi), t)
        img.alpha_composite(G['vig'])
        red_vig(img, t)
        d = ImageDraw.Draw(img)
        ui_top(img, d, t)
        bubble(img, d, t)
        chrono(img, d, t)
        outro_cta(img, d, t)
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
        print('T', T, 'CS', CS, 'ANS', ANS)
    else:
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': FAUXT, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 100 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
