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


# #34 LES SŒURS DU PRISONNIER (24/11) — dérivée de video33.py.
# Gardés : T23 (3 choix visibles dès 0,0 s), T24 (prisonnier enchaîné + gardien).
# À confirmer -> conservés : T30 (titre court), T31 (chrono 4 s), T32 (hook sans bandeau sombre).
# Test du jour : T34 — la question est écrite en GROS sur l'objet lui-même (panneau de bois « ? ENFANTS »
# accroché au-dessus des 4 sœurs) au lieu d'un petit badge « ? ».
NUM = "34"; TITRE = "UNE FAMILLE PIÉGÉE !"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "LE CHEVAL DU GARDIEN"
HOOK = ["4 SŒURS DÉCIDENT", "DE SA LIBERTÉ !"]
CHR = 4.0
D = json.load(open('durees.json'))
SUBS = ["4 sœurs décident de sa liberté !",
        "Ce prisonnier a 4 sœurs.",
        "Chaque sœur a 1 seul frère.",
        "GARDIEN : Combien d'enfants dans ta famille ?",
        "PRISONNIER : 8 ! GARDIEN : Ha ha ! Tu es sûr ?",
        "Combien d'enfants : 5, 8, ou 9 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 20 euros ! 10, plus 10."]
SPLIT4 = json.load(open('split.json'))['split4']
NL = len(SUBS)
GAP = 0.35
s0 = 0.0
s1 = s0 + D[0] + 0.25
s2 = s1 + D[1] + 0.3
s3 = s2 + D[2] + GAP           # gardien « Combien d'enfants dans ta famille ? »
s4 = s3 + D[3] + 0.25          # prisonnier « 8 ! » puis gardien
sQ = s4 + D[4] + GAP
CS = sQ + D[5] - 0.2
CE = CS + CHR
sC = CE + 0.05
STAMP = sC + D[6] * 0.55
ANS = sC + D[6] + 0.2
sA = ANS + 0.2
FADE = sA + D[7] + 0.35
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, sQ, sC, sA]
NF = int(round(T * FPS))
KEY = [["4", "sœurs", "liberté"], ["4", "sœurs"], ["1", "seul", "frère"], ["combien", "enfants", "famille"],
       ["8", "sûr"], ["5", "8", "9"], ["commentaire", "vite"], ["20", "10"]]
TORCH = [(70, 640), (1010, 430)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())
def _spread(sub, a, b): return [a + (b - a) * j / len(sub) * 0.9 for j in range(len(sub))]
def _wt4():
    ws = SUBS[4].split(); kg = ws.index('GARDIEN')
    return ws, _spread(ws[:kg], s4, s4 + SPLIT4 - 0.15) + _spread(ws[kg:], s4 + SPLIT4 - 0.1, s4 + D[4])
WT[4] = _wt4()

T_4 = wtime(1, '4'); T_SOEURS = wtime(1, 'sœurs')
POPS = [T_4 + 0.18 * k for k in range(4)]          # numéros 1-2-3-4 au-dessus des sœurs
T_FRERE = wtime(2, 'seul')
T_SIGN = s3 + 0.05                                    # T34 : le panneau tombe quand le gardien pose la question
T_FAUX = s4
T_SOURIT = s4 + SPLIT4
T_REP = wtime(7, '20'); T_D1 = wtime(7, '10', 0); T_D2 = wtime(7, '10', 1)
CHRONO_XY = (540, 880)
HOOK_END = 1.3; HOOK_UP = 1.75
PY = 700
FLOOR = 930
XP, XG = 190, 890
CHAR['PRISONNIER']['x'] = XP; CHAR['GARDIEN']['x'] = XG
ORANGE = (255, 150, 40)
GREEN = (90, 200, 120); RED = (230, 60, 50)
# 4 sœurs (au centre, plus petites)
SIS = [('F1', 372), ('F2', 484), ('LÉA', 596), ('NINA', 708)]
SSC = 0.62
SIGN_Y = 668
# carnet du gardien (réponse d'hier #33)
LX0, LX1, LY0 = 110, 750, 470
ROWS = [("ACHÈTE", "−60 €", RED), ("VEND", "+70 €", (40, 150, 80)), ("RACHÈTE", "−80 €", RED), ("REVEND", "+90 €", (40, 150, 80))]
RH = 84

def wall(S):
    """mur de pierre brun-violet du donjon"""
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

def pop_at(t, times, dur=0.3, amp=0.3):
    for td in times:
        if 0 <= t - td < dur: return 1 + amp * (1 - (t - td) / dur)
    return 1.0

def sisters(img, t):
    """les 4 sœurs, visibles dès 0,0 s ; petit saut quand leur numéro apparaît"""
    for k, (nm, x) in enumerate(SIS):
        im = draw_person(nm, t + k * 0.7, 0, ((t + k * 0.9) % 3.4) < 0.12, 0, label=' ')
        im = im.resize((int(im.width * SSC), int(im.height * SSC)), Image.LANCZOS)
        j = 0
        if 0 <= t - POPS[k] < 0.3: j = math.sin(math.pi * (t - POPS[k]) / 0.3) * 22
        img.alpha_composite(im, (int(x - im.width / 2), int(PY + 560 - im.height - j)))

def sis_numbers(d, t):
    for k, (nm, x) in enumerate(SIS):
        if t < POPS[k] - 0.05 or CS - 0.1 <= t < CE + 0.3: continue
        u = ease_back((t - POPS[k] + 0.05) / 0.25)
        r = 34 * clamp(u, 0.05, 1.2); y = 948
        d.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill=(16, 10, 16))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 206, 40))
        d.text((x, y + 2), str(k + 1), font=F(54 * clamp(u, 0.05, 1.2)), fill=(24, 14, 20), anchor='mm')

def sign(img, d, t):
    """T34 : grand panneau de bois accroché au-dessus des sœurs, la question écrite dessus"""
    if t < T_SIGN or t >= sC - 0.05: return
    u = clamp((t - T_SIGN) / 0.35)
    drop = (1 - ease_back(u)) * -260
    ang = math.sin((t - T_SIGN) * 7) * 4 * math.exp(-(t - T_SIGN) * 2.2)
    pul = 1 + (0.035 * math.sin(t * 8) if t < CE else 0)
    S = 2; w, h = 660, 170
    lay = Image.new('RGBA', ((w + 40) * S, (h + 140) * S), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    ox, oy = 20, 120
    for xx in (110, w - 110):
        dl.line([(ox + xx) * S, 0, (ox + xx) * S, (oy + 20) * S], fill=(150, 120, 90), width=6 * S)
    dl.rounded_rectangle([ox * S, oy * S, (ox + w) * S, (oy + h) * S], radius=22 * S, fill=(40, 24, 14))
    dl.rounded_rectangle([(ox + 8) * S, (oy + 8) * S, (ox + w - 8) * S, (oy + h - 8) * S], radius=18 * S, fill=(176, 120, 66))
    for k in range(3):
        yy = oy + 40 + k * 45
        dl.line([(ox + 20) * S, yy * S, (ox + w - 20) * S, (yy + 4) * S], fill=(150, 100, 54), width=3 * S)
    f = F(112 * S)
    q = "?"; rest = " ENFANTS"
    tw = dl.textlength(q + rest, font=f); x0 = (ox + w / 2) * S - tw / 2; yc = (oy + h / 2 + 4) * S
    dl.text((x0, yc), q, font=f, fill=(230, 50, 40), anchor='lm', stroke_width=5 * S, stroke_fill=(30, 14, 10))
    dl.text((x0 + dl.textlength(q, font=f), yc), rest, font=f, fill=(255, 238, 200), anchor='lm', stroke_width=5 * S, stroke_fill=(30, 14, 10))
    lay = lay.resize((int((w + 40) * pul), int((h + 140) * pul)), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, center=(lay.width / 4, 0))
    img.alpha_composite(lay, (int(540 - lay.width / 2), int(SIGN_Y - (oy + h / 2) * pul + drop)))

def badges(d, t):
    if T_SOEURS - 0.1 <= t < CE + 0.3:
        badge(d, 540, 425, "4 SŒURS", ease_back((t - T_SOEURS + 0.1) / 0.3), fill=ORANGE, size=60)
    if T_FRERE - 0.1 <= t < CE + 0.3:
        badge(d, 540, 528, "CHAQUE SŒUR : 1 SEUL FRÈRE", ease_back((t - T_FRERE + 0.1) / 0.3), fill=(255, 206, 40), size=50)

# --- réponse #33 : 20 € (−60 + 70 = +10, puis −80 + 90 = +10) ---
def answer_scene(img, t):
    d = ImageDraw.Draw(img)
    y1 = LY0 + 70 + 4 * RH + 10
    d.rounded_rectangle([LX0 - 6, LY0 - 6, LX1 + 6, y1 + 6], radius=24, fill=(30, 18, 16))
    d.rounded_rectangle([LX0, LY0, LX1, y1], radius=20, fill=(246, 234, 206))
    d.text(((LX0 + LX1) / 2, LY0 + 38), "CARNET DU GARDIEN", font=F(46), fill=(120, 70, 40), anchor='mm')
    d.line([LX0 + 24, LY0 + 68, LX1 - 24, LY0 + 68], fill=(200, 170, 130), width=3)
    for k, (verb, price, col) in enumerate(ROWS):
        y = LY0 + 70 + RH / 2 + k * RH + 2
        d.text((LX0 + 30, y), f"{k + 1}.", font=F(52), fill=(120, 90, 70), anchor='lm')
        d.text((LX0 + 100, y), verb, font=F(60), fill=col, anchor='lm')
        d.text((LX1 - 30, y), price, font=F(60), fill=(30, 20, 26), anchor='rm')
    for k, tt in enumerate((T_D1, T_D2)):
        if t < tt - 0.15: continue
        u = ease_back((t - tt + 0.15) / 0.3)
        ya = LY0 + 70 + 10 + 2 * k * RH; yb = ya + 2 * RH - 20
        bx = LX1 + 26
        d.line([bx, ya, bx + 24, ya, bx + 24, yb, bx, yb], fill=(255, 206, 40), width=8)
        badge(d, 905, (ya + yb) / 2, "+10 €", u, fill=GREEN, tcol=(255, 255, 255), size=58)
    if t >= T_REP - 0.2:
        badge(d, 540, 1230, "20 EUROS !", ease_back((t - T_REP + 0.2) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
    if t >= T_D2 + 0.2:
        badge(d, 540, 395, "10 + 10 = 20 €", ease_back((t - T_D2 - 0.2) / 0.3), fill=(255, 206, 40), size=60)

BUBS = [
    ('GARDIEN', "Combien d'enfants dans ta famille ?", lambda: s3 - 0.1, lambda: s4 - 0.05, 790, 800, 890),
    ('PRISONNIER', "8 !", lambda: T_FAUX - 0.1, lambda: sQ, 250, 800, 200),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: sQ, 790, 800, 890),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:6]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP, 920), (0.4, 1.0, 540, 960), (s1 - 0.1, 1.0, 540, 960),
            (s1 + 0.3, 1.04, 540, 930), (s3 - 0.2, 1.04, 540, 930), (s3 + 0.2, 1.04, 620, 960), (s4 - 0.2, 1.04, 620, 960),
            (s4 + 0.3, 1.04, 460, 960), (T_SOURIT - 0.1, 1.04, 460, 960), (T_SOURIT + 0.3, 1.04, 620, 960), (sQ - 0.1, 1.04, 620, 960),
            (sQ + 0.4, 1.0, 540, 960), (CE, 1.03, 540, 1000), (CE + 0.6, 1.02, 540, 980), (ANS, 1.02, 540, 980)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_SIGN + 0.3, 10), (T_FAUX, 12), (T_SOURIT, 14), (sQ, 8), (STAMP, 18)]:
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
    base = np.asarray(wall(2).resize((W, H), Image.LANCZOS)).astype(np.float32)
    for key in ('c', 'a'):
        G[key + 'dark'] = Image.fromarray(np.clip(base * 0.85 + glow_layer(0.26) * 0.6, 0, 255).astype(np.uint8))
        G[key + 'lit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.48) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    for i in (3, 4): G[f'env{i}'] = mouth_env(i)

def chains(d):
    x0 = XP - 40; y0 = PY + 500
    for k in range(6):
        cx = 6 + k * (x0 - 6) / 5; cy = y0 + 14 * math.sin(k / 5 * math.pi)
        if k % 2: d.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], outline=(160, 160, 172), width=5)
        else: d.ellipse([cx - 7, cy - 10, cx + 7, cy + 10], outline=(160, 160, 172), width=5)
    d.rounded_rectangle([x0 - 6, y0 - 12, x0 + 30, y0 + 12], radius=6, fill=(120, 120, 132), outline=(30, 24, 30), width=3)

def bg(t, key='c'):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G[key + 'dark'], G[key + 'lit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    return img

def scene(t):
    img = bg(t)
    pm = mouth_at(4, t) if T_FAUX <= t < T_SOURIT - 0.1 else 0
    gm = mouth_at(3, t) or (mouth_at(4, t) if t >= T_SOURIT - 0.05 else 0)
    mood = -1 if t < T_FAUX - 0.6 else 0
    sisters(img, t)
    im = draw_person('GARDIEN', t + 1, gm, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    chains(d)
    sis_numbers(d, t)
    badges(d, t)
    sign(img, d, t)
    d = ImageDraw.Draw(img)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=420)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def hook(img, t):
    if t >= HOOK_UP: return
    # T32 (23/11) : pas de bandeau sombre derrière le hook -> le cheval et les personnages restent visibles
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
    if not (sC - 0.05 <= t < ANS): return
    u = ease_back((t - sC) / 0.3)
    f = F(int(56 * clamp(u, 0, 1.2)) + 1)
    y = 560
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS 5, 8 OU 9", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('5', 'ENFANTS', '5', 0), ('8', 'ENFANTS', '8', 0), ('9', 'ENFANTS', '9', 0)]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    """T23 (gardé) : les 3 choix sont visibles dès 0,0 s ; chaque choix grossit quand la voix le dit"""
    if not (t < ANS): return
    for k, (big, small, w_, nth) in enumerate(CHN):
        col = CHC[k]
        u = 1 + 0.1 * max(0, 1 - t / 0.2)
        ts = wtime(5, w_, nth) - 0.1
        pul = 1.0
        if ts <= t < ts + 0.45: pul = 1 + 0.14 * math.sin(math.pi * (t - ts) / 0.45)
        if CS <= t < CE and int((t - CS) * 3) % 3 == k: pul = 1.08
        s = u * pul
        x = 195 + k * 345; y = 1290
        bw, bh = 310 * s, 160 * s
        d.rounded_rectangle([x - bw / 2 - 7, y - bh / 2 - 7, x + bw / 2 + 7, y + bh / 2 + 7], radius=int(46 * s) + 7, fill=col)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(46 * s), fill=(26, 18, 30))
        d.text((x, y + 24 * s), big, font=F(84 * s), fill=(255, 255, 255), anchor='mm')
        d.text((x, y - 50 * s), small, font=F(34 * s), fill=col, anchor='mm')

def answer_frame(t):
    img = bg(t, 'a')
    answer_scene(img, t)
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
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_FAUX,
                   'POPS': POPS, 'SIGN': T_SIGN, 'TREP': T_REP, 'TD1': T_D1, 'TD2': T_D2, 'SPLIT': T_SOURIT, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
