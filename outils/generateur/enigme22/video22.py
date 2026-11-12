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


NUM = "22"; TITRE = "LE TRAIN ET LE TUNNEL"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "LES CHATS DE LA FERME"
HOOK = ["1, 2 OU 3 MINUTES ?", "IL EST LIBRE S'IL TROUVE"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["1, 2 ou 3 minutes ? Il sort libre s'il trouve !",
        "Le train fait 1 kilomètre. Le tunnel aussi.",
        "Il roule à 1 kilomètre par minute.",
        "Le prisonnier crie : 1 minute ! Et le gardien éclate de rire.",
        "Combien de minutes pour que tout le train sorte : 1, 2, ou 3 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 3 chats ! Le rythme reste le même !"]
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
KEY = [["1", "2", "3", "minutes", "libre"], ["train", "1", "kilomètre", "tunnel"], ["1", "kilomètre", "minute"],
       ["1", "minute", "rire"], ["tout", "train", "1", "2", "3"], ["commentaire", "vite"], ["3", "chats", "même"]]
TORCH = [(170, 560), (910, 560)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

CHAR['PRISONNIER'] = dict(x=250, col=(200, 130, 70), hair=(70, 44, 30), style='short', skin=(220, 166, 120))
CHAR['GARDIEN'] = dict(x=850, col=(210, 70, 60), hair=(40, 30, 30), style='short', skin=(206, 150, 106))
T_TRAIN = wtime(1, 'train'); T_TUN = wtime(1, 'tunnel')
T_KMMIN = wtime(2, 'roule')
T_FAUX = wtime(3, '1')
T_SOURIT = wtime(3, 'éclate')
T_TOUT = wtime(4, 'tout')
T_REP = wtime(6, '3')
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 690
FLOOR = 930
XP, XG = 250, 850
KM = 330            # 1 km = 330 px
TX0, TX1 = 400, 400 + KM   # tunnel
TRACK = 640

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

def railway(S):
    rnd = random.Random(4)
    im = Image.new('RGB', (W * S, H * S), (16, 14, 34))
    d = ImageDraw.Draw(im)
    for y in range(0, FLOOR):
        u = clamp((y - 300) / (FLOOR - 300))
        c = (int(18 + 60 * u), int(16 + 30 * u), int(40 + 40 * u))
        d.rectangle([0, y * S, W * S, (y + 1) * S], fill=c)
    for k in range(60):
        x = rnd.randint(0, W); y = rnd.randint(330, 560); r = rnd.choice([2, 2, 3])
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(230, 220, 190))
    for r, c in [(80, (44, 38, 60)), (56, (70, 60, 76)), (36, (250, 236, 190))]:
        d.ellipse([(140 - r) * S, (400 - r) * S, (140 + r) * S, (400 + r) * S], fill=c)
    # montagnes lointaines
    d.polygon([(0, 600 * S), (120 * S, 520 * S), (260 * S, 590 * S), (860 * S, 540 * S), (1000 * S, 470 * S), (1080 * S, 520 * S), (1080 * S, 660 * S), (0, 660 * S)], fill=(40, 32, 56))
    # montagne du tunnel
    d.polygon([((TX0 - 70) * S, (TRACK + 12) * S), ((TX0 + 60) * S, 470 * S), ((TX0 + 170) * S, 410 * S), ((TX1 - 60) * S, 455 * S), ((TX1 + 70) * S, (TRACK + 12) * S)], fill=(84, 64, 74))
    d.polygon([((TX0 + 120) * S, 430 * S), ((TX0 + 170) * S, 410 * S), ((TX0 + 215) * S, 428 * S), ((TX0 + 170) * S, 445 * S)], fill=(236, 236, 246))
    for k in range(18):
        x = rnd.randint(TX0, TX1); y = rnd.randint(480, 620)
        d.ellipse([(x - 16) * S, (y - 8) * S, (x + 16) * S, (y + 8) * S], fill=(100, 78, 86))
    # rails + traverses
    d.rectangle([0, (TRACK + 12) * S, W * S, (FLOOR) * S], fill=(46, 40, 50))
    for x in range(-10, W, 34):
        d.rectangle([x * S, (TRACK + 4) * S, (x + 16) * S, (TRACK + 20) * S], fill=(96, 70, 50))
    d.rectangle([0, (TRACK + 2) * S, W * S, (TRACK + 7) * S], fill=(190, 190, 200))
    # sol
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(30, 34, 30))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(38, 44, 36), width=3 * S)
    for (tx, ty) in TORCH:
        d.rectangle([(tx - 8) * S, (ty + 30) * S, (tx + 8) * S, 935 * S], fill=(70, 50, 34))
        d.rounded_rectangle([(tx - 30) * S, (ty + 8) * S, (tx + 30) * S, (ty + 34) * S], radius=6 * S, fill=(60, 50, 50))
    return im

def portal(d):
    """entrées du tunnel (dessinées par-dessus le train)"""
    for x0, sg in [(TX0, 1), (TX1, -1)]:
        d.rectangle([x0 - 26, 540, x0 + 26, TRACK + 12], fill=(120, 100, 96))
        for yy in range(548, TRACK + 6, 22):
            d.line([(x0 - 26, yy), (x0 + 26, yy)], fill=(96, 78, 76), width=3)
        d.rectangle([x0 - 34, 528, x0 + 34, 548], fill=(140, 118, 110))

def train(d, xf, t, inside_dark=True, prisoner=False):
    """train de 1 km (KM px) dont l'avant est en xf ; caché dans le tunnel"""
    xr = xf - KM
    n = 4; wl = KM / n
    for k in range(n):
        a = xr + k * wl + 4; b = xr + (k + 1) * wl - 4
        loco = (k == n - 1)
        col = (210, 60, 50) if loco else (60, 110, 190)
        top = TRACK - (108 if loco else 92)
        d.rounded_rectangle([a, top, b, TRACK - 12], radius=12, fill=col, outline=(16, 10, 16), width=4)
        if loco:
            d.rectangle([b - 40, top - 34, b - 18, top], fill=(40, 34, 40))
            d.ellipse([b - 14, TRACK - 64, b + 4, TRACK - 46], fill=(255, 230, 140))
        else:
            for w in range(2):
                wx = a + 12 + w * (wl - 8) / 2
                d.rounded_rectangle([wx, top + 14, wx + (wl - 8) / 2 - 18, top + 46], radius=6, fill=(255, 220, 140))
        for wx in (a + 18, b - 18):
            d.ellipse([wx - 13, TRACK - 24, wx + 13, TRACK + 2], fill=(30, 26, 30), outline=(150, 150, 160), width=3)
        if k > 0: d.line([(a - 8, TRACK - 30), (a, TRACK - 30)], fill=(30, 26, 30), width=6)

def bracket(d, x0, x1, y, txt, u, col):
    if u <= 0: return
    m = (x0 + x1) / 2; h = (x1 - x0) / 2 * clamp(u, 0, 1)
    d.line([(m - h, y), (m + h, y)], fill=(16, 10, 16), width=12)
    d.line([(m - h, y), (m + h, y)], fill=col, width=6)
    for xx in (m - h, m + h):
        d.line([(xx, y - 18), (xx, y + 18)], fill=(16, 10, 16), width=12)
        d.line([(xx, y - 16), (xx, y + 16)], fill=col, width=6)
    badge(d, m, y - 46, txt, ease_back(u), fill=col, size=46)

def train_x(t):
    """position de l'avant : arrive par la gauche puis s'arrête à l'entrée (on ne montre pas la suite)"""
    u = ss(clamp(t / (T_KMMIN + 0.6)))
    return 260 + (TX0 - 260) * u

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

BUBS = [
    ('PRISONNIER', "1 minute !", lambda: T_FAUX - 0.15, lambda: s4, 330, 770, 280),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: s4, 760, 760, 840),
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
    for hh, amp in [(0.0, 16), (T_TRAIN, 8), (T_TUN, 8), (T_KMMIN, 10), (T_FAUX, 12), (T_SOURIT, 14), (s4, 8), (STAMP, 18)]:
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
    for nm, im in [('r', railway(2)), ('d', farm(2))]:
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
    # train (avant en xf) : arrive et s'arrête à l'entrée du tunnel
    xf = train_x(t)
    train(d, xf, t)
    # fumée
    for k in range(5):
        ph = (t * 0.8 + k * 0.2) % 1
        r = 10 + 26 * ph
        cx_, cy_ = xf - 30 - 60 * ph, TRACK - 150 - 90 * ph
        d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=(int(200 - 60 * ph), int(196 - 60 * ph), int(206 - 60 * ph)))
    portal(d)
    # contour rouge « TOUT LE TRAIN » (ligne 4)
    if T_TOUT - 0.1 <= t < CE:
        pu = 0.5 + 0.5 * math.sin(t * 9)
        d.rounded_rectangle([xf - KM - 8, TRACK - 150, xf + 10, TRACK + 8], radius=18, outline=(255, int(80 + 120 * pu), 60), width=8)
    # mesures
    if T_TRAIN - 0.15 <= t < CE:
        bracket(d, xf - KM + 4, xf - 4, 495, "TRAIN 1 KM", (t - (T_TRAIN - 0.15)) / 0.3, (255, 206, 40))
    if T_TUN - 0.15 <= t < CE:
        bracket(d, TX0, TX1, 495, "TUNNEL 1 KM", (t - (T_TUN - 0.15)) / 0.3, (120, 200, 255))
    if T_KMMIN - 0.1 <= t < CE:
        badge(d, 540, 372, "VITESSE : 1 KM PAR MINUTE", ease_back((t - (T_KMMIN - 0.1)) / 0.25), fill=(255, 140, 60), size=46)
    # « ? MIN » sur la montagne
    if T_FAUX - 0.3 <= t < CE:
        u = clamp(ease_back((t - (T_FAUX - 0.3)) / 0.3), 0, 1.1) * (1 + 0.05 * math.sin(t * 8))
        r = 62 * u
        d.ellipse([565 - r, 585 - r, 565 + r, 585 + r], fill=(20, 12, 20), outline=(255, 206, 40), width=6)
        if u > 0.3: text_stroke(d, (565, 580), "?", F(96 * u), (255, 214, 50), sw=6)
    pm = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    im = draw_person('GARDIEN', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    if T_TOUT - 0.1 <= t < CE:
        badge(d, 540, 760, "TOUT LE TRAIN DOIT SORTIR", ease_back((t - (T_TOUT - 0.1)) / 0.25), fill=(255, 120, 60), size=48)
    if s4 - 0.05 <= t < CE:
        badge(d, 540, 860, "COMBIEN DE MINUTES ?", ease_back((t - (s4 - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=60)
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
    d.text((W / 2, y - 40), "ÉCRIS 1, 2 OU 3", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('1', 'MINUTE', '1'), ('2', 'MINUTES', '2'), ('3', 'MINUTES', '3')]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    if not (wtime(4, '1') - 0.3 <= t < ANS): return
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

CATX = [270, 540, 810]
def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['ddark'], G['dlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    for k, x in enumerate(CATX):
        tk = ANS + 0.05 + k * 0.12
        if t < tk: continue
        u = clamp(ease_back((t - tk) / 0.25), 0, 1.15)
        cat(d, x + 20, 1050, 1.7 * u, t, k)
        if t >= T_REP:
            cu = clamp(ease_back((t - T_REP - k * 0.1) / 0.2), 0, 1.15)
            if cu > 0.05:
                cx_, cy_, r = x, 880, 40 * cu
                d.ellipse([cx_ - r - 4, cy_ - r - 4, cx_ + r + 4, cy_ + r + 4], fill=(16, 10, 16))
                d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=GREEN)
                d.line([(cx_ - 18 * cu, cy_), (cx_ - 4 * cu, cy_ + 15 * cu), (cx_ + 19 * cu, cy_ - 15 * cu)], fill=(255, 255, 255), width=max(2, int(9 * cu)), joint='curve')
    if t >= T_REP - 0.4:
        badge(d, 540, 470, "3 CHATS !", ease_back((t - T_REP + 0.4) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
        badge(d, 540, 620, "1 SOURIS / 3 MIN CHACUN", ease_back((t - T_REP + 0.2) / 0.3), fill=(255, 206, 40), size=48)
        badge(d, 540, 720, "EN 100 MIN = 100 SOURIS", ease_back((t - T_REP) / 0.3), fill=(255, 206, 40), size=48)
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

