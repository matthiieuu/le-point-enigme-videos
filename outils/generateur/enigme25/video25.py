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



NUM = "25"; TITRE = "L'ESCALIER DE LA TOUR"; CONTRAINTE = "SA PLACE EN JEU"
TITRE_HIER = "LES POTEAUX DE LA CLÔTURE"
HOOK = ["UNE MARCHE DE TROP", "ET IL EST VIRÉ !"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Une marche de trop, et il est viré !",
        "Du 1er au 3e étage : 30 marches.",
        "Tous les étages ont le même escalier.",
        "Le petit crie : 60 ! Et le chef éclate de rire.",
        "Du 1er au 6e étage : 60, 75, ou 90 marches ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 11 poteaux, pas 10 !"]
NL = len(SUBS)
GAP = 0.3
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
KEY = [["marche", "viré", "trop"], ["1er", "3e", "30", "marches"], ["même", "escalier", "étages"],
       ["60", "rire"], ["1er", "6e", "60", "75", "90", "marches"], ["commentaire", "vite"], ["11", "poteaux", "pas", "10"]]
TORCH = [(150, 400), (930, 400)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

CHAR['PETIT'] = dict(x=250, col=(70, 170, 200), hair=(150, 90, 40), style='short', skin=(236, 180, 136))
CHAR['CHEF'] = dict(x=850, col=(210, 70, 60), hair=(40, 30, 30), style='short', skin=(206, 150, 106))
T_1ER = wtime(1, '1er'); T_3E = wtime(1, '3e'); T_30 = wtime(1, '30')
T_MEME = wtime(2, 'même')
T_FAUX = wtime(3, '60')
T_SOURIT = wtime(3, 'éclate')
T_6E = wtime(4, '6e')
T_REP = wtime(6, '11')
FX0, FX1 = 90, 990; MPX = (FX1 - FX0) / 10   # clôture de 10 m (réponse #24)
FTOP, FGND = 640, 780
KIDS = 0.8
CHRONO_XY = (540, 1040)
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 690
FLOOR = 930
XP, XG = 250, 850
# tour : 6 étages
SX0, SX1 = 360, 720
def FY(k): return 830 - (k - 1) * 70
NSTEP = 6

def wall(S, earth=True):
    """mur de pierre brun-violet du donjon, torches ; bande de terre (cour) seulement pour la réponse d'hier"""
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
    if earth:
        d.rectangle([0, FGND * S, W * S, (FGND + 26) * S], fill=(74, 52, 38))
        d.rectangle([0, (FGND + 26) * S, W * S, FLOOR * S], fill=(52, 38, 40))
    else:
        # intérieur de la tour : fond plus sombre derrière l'escalier
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
    if ow > 3:
        d.line(pts + [pts[0]], fill=outline, width=ow)
    # palier
    lx0, lx1 = (SX1, SX1 + 66) if ltr else (SX0 - 66, SX0)
    d.rectangle([lx0, y1, lx1, y1 + 12], fill=col, outline=(16, 10, 16))

def tower_scene(d, t):
    hl13 = t >= T_30 - 0.15
    allq = t >= T_6E - 0.15 and t < CE + 0.3
    for k in range(1, 6):
        col = (118, 98, 112)
        if hl13 and k <= 2: col = (255, 150, 40)
        flight(d, k, col, outline=(255, 214, 50) if allq else (16, 10, 16), ow=7 if allq else 3)
    d.rectangle([SX0 - 66, FY(1), SX0, FY(1) + 12], fill=(118, 98, 112), outline=(16, 10, 16))
    # plaques d'étage 1ER … 6E
    for k in range(1, 7):
        lab = "1ER" if k == 1 else f"{k}E"
        hi = (k in (1, 3) and t >= T_1ER - 0.15 and t < T_6E - 0.15) or (k in (1, 6) and t >= T_6E - 0.15 and t < CE + 0.3)
        u = 1.0
        if k == 1 and T_1ER - 0.15 <= t < T_1ER + 0.15: u = ease_back((t - T_1ER + 0.15) / 0.3) * 0.2 + 1
        if k == 3 and T_3E - 0.15 <= t < T_3E + 0.15: u = ease_back((t - T_3E + 0.15) / 0.3) * 0.2 + 1
        if k == 6 and T_6E - 0.15 <= t < T_6E + 0.15: u = ease_back((t - T_6E + 0.15) / 0.3) * 0.2 + 1
        badge(d, 222, FY(k) - 4, lab, u, fill=(255, 206, 40) if hi else (150, 130, 146), size=46 if not hi else 50)
    if hl13 and t < CE + 0.3:
        u = ease_back((t - (T_30 - 0.15)) / 0.3)
        badge(d, 540, 762, "30 MARCHES", u, fill=(255, 140, 60), size=52)
    if t >= T_MEME - 0.15 and t < CE + 0.3:
        u = ease_back((t - (T_MEME - 0.15)) / 0.3)
        if t < s3:
            badge(d, 540, 420, "MÊME ESCALIER PARTOUT", u, fill=(120, 200, 255), size=48)
        for j, k in enumerate((3, 4, 5)):
            yc = (FY(k) + FY(k + 1)) / 2 - 6
            text_stroke(d, (540, yc + 5 * math.sin(t * 5 + j)), "?", F(int(64 * clamp(u, 0, 1.1)) + 1), (255, 214, 50), sw=6)

def answer_scene(d, t):
    """réponse #24 : la clôture de 10 m, les 11 poteaux qui se plantent un par un ; « 10 POTEAUX » barré en rouge (T22)"""
    for y in (FTOP + 30, FTOP + 78):
        d.rectangle([FX0, y, FX1, y + 14], fill=(130, 90, 54), outline=(20, 12, 12))
    n = 0
    for k in range(11):
        tk = ANS + 0.1 + k * 0.1
        if t >= tk:
            n += 1
            x = FX0 + k * MPX
            post(d, x, ease_back((t - tk) / 0.2), hi=(k in (0, 10)))
            text_stroke(d, (x, FTOP - 30), str(k + 1), F(44), (255, 255, 255), sw=5)
    if n > 0 and t < T_REP - 0.3:
        badge(d, 540, 470, f"{n} POTEAU" + ("X" if n > 1 else ""), 1, fill=(255, 140, 60), size=52)
    if t >= T_REP - 0.3:
        badge(d, 540, 470, "11 POTEAUX !", ease_back((t - T_REP + 0.3) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
    tp = wtime(6, 'pas') - 0.15
    if t >= tp:
        u = ease_back((t - tp) / 0.3)
        badge(d, 540, 900, "10 POTEAUX", u, fill=(150, 140, 150), tcol=(60, 50, 60), size=60)
        if t >= tp + 0.2:
            v = clamp((t - tp - 0.2) / 0.2)
            a, b = (330, 935), (750, 865)
            xe = (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)
            d.line([a, xe], fill=(16, 10, 16), width=16)
            d.line([a, xe], fill=RED, width=9)
            badge(d, 540, 1020, "10 MÈTRES = 11 POTEAUX", v, fill=(255, 206, 40), size=46)

def post(d, x, u, hi=False):
    if u <= 0: return
    h = (FGND + 10 - FTOP) * clamp(u, 0, 1.15)
    top = FGND + 10 - h
    col = (255, 206, 40) if hi else (168, 116, 66)
    d.polygon([(x - 13, top + 16), (x, top), (x + 13, top + 16), (x + 13, FGND + 10), (x - 13, FGND + 10)], fill=col, outline=(20, 12, 12))
    d.line([(x - 5, top + 24), (x - 5, FGND + 4)], fill=tuple(int(c * 0.8) for c in col), width=3)

BUBS = [
    ('PETIT', "60 !", lambda: T_FAUX - 0.15, lambda: s4, 450, 900, 300),
    ('CHEF', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: s4, 640, 1050, 800),
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
    for hh, amp in [(0.0, 16), (T_30, 8), (T_MEME, 8), (T_6E, 8), (T_FAUX, 12), (T_SOURIT, 14), (s4, 8), (STAMP, 18)]:
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
    for nm, im in [('r', wall(2, True)), ('t', wall(2, False))]:
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
    img = Image.blend(G['tdark'], G['tlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    tower_scene(d, t)
    pm = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    im = draw_person('CHEF', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='CHEF')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PETIT', t, pm, (t % 3.2) < 0.12, mood, label='LE PETIT')
    im = im.resize((int(im.width * KIDS), int(im.height * KIDS)), Image.LANCZOS)
    img.alpha_composite(im, (int(XP - im.width / 2), int(PY + 560 * (1 - KIDS) - 10)))
    d = ImageDraw.Draw(img)
    if s4 - 0.05 <= t < CE:
        badge(d, 540, 915, "COMBIEN DE MARCHES ?", ease_back((t - (s4 - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=60)
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
    d.text((W / 2, y - 40), "ÉCRIS 60, 75 OU 90", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('60', 'MARCHES', '60'), ('75', 'MARCHES', '75'), ('90', 'MARCHES', '90')]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    """T23 : les 3 choix sont visibles dès 0,0 s (sous le hook) ; chaque choix grossit quand la voix le dit"""
    if not (t < ANS): return
    for k, (big, small, w_) in enumerate(CHN):
        col = CHC[k]
        u = 1 + 0.1 * max(0, 1 - t / 0.2)
        if u <= 0: continue
        ts = wtime(4, w_) - 0.1
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
    answer_scene(d, t)
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

