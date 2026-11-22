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

# #32 LE LIVRE DU MARCHAND (22/11) — dérivée de video31.py.
# Gardés : T23 (3 choix visibles dès 0,0 s), T24 (prisonnier enchaîné + gardien).
# Abandonnés : T22 (réponse piège barrée), T25 (relance finale), T26 (voix des personnages), T27 (cri de la réponse piège à 0,0 s).
# T30 (titre court) à confirmer -> conservé. Test du jour : T31 chrono 4 s au lieu de 6.
NUM = "32"; TITRE = "UN PRIX PIÉGÉ !"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "LES MICROBES DU BOCAL"
HOOK = ["LE BON PRIX", "ET IL EST LIBRE !"]
CHR = 4.0
D = json.load(open('durees.json'))
SUBS = ["Le bon prix, et il est libre !",
        "Ce livre coûte 10 euros.",
        "Plus la moitié de son prix.",
        "GARDIEN : Combien coûte le livre ?",
        "PRISONNIER : 15 euros ! GARDIEN : Ha ha ! Tu es sûr ?",
        "Combien d'euros : 15, 20, ou 10 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 59 ! 2 microbes, c'est déjà la minute 1."]
SPLIT4 = json.load(open('split.json'))['split4']
NL = len(SUBS)
GAP = 0.35
s0 = 0.0
s1 = s0 + D[0] + 0.2
s2 = s1 + D[1] + 0.15
s3 = s2 + D[2] + GAP
s4b = s3 + D[3] + GAP          # ligne 4 : prisonnier « 15 euros ! » puis gardien
sQ = s4b + D[4] + GAP
CS = sQ + D[5] - 0.2
CE = CS + CHR
s5 = CE + 0.05
STAMP = s5 + D[6] * 0.55
ANS = s5 + D[6] + 0.2
s6 = ANS + 0.2
FADE = s6 + D[7] + 0.25
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4b, sQ, s5, s6]
NF = int(round(T * FPS))
KEY = [["bon", "prix", "libre"], ["10", "euros"], ["moitié", "prix"], ["combien", "livre"], ["15", "sûr"],
       ["15", "20", "10"], ["commentaire", "vite"], ["59", "2", "minute", "1"]]
TORCH = [(70, 640), (1010, 430)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())
def _spread(sub, a, b): return [a + (b - a) * j / len(sub) * 0.9 for j in range(len(sub))]
def _wt4():
    ws = SUBS[4].split(); kg = ws.index('GARDIEN')
    return ws, _spread(ws[:kg], s4b, s4b + SPLIT4 - 0.15) + _spread(ws[kg:], s4b + SPLIT4 - 0.1, s4b + D[4])
WT[4] = _wt4()

T_10 = wtime(1, '10'); T_MOIT = wtime(2, 'moitié')
T_FAUX = s4b
T_SOURIT = s4b + SPLIT4
T_REP = wtime(7, '59'); T_MIN1 = wtime(7, 'minute')
JUMP = T_MIN1 + 0.35
CHRONO_XY = (900, 700)
HOOK_END = 1.3; HOOK_UP = 1.75
PY = 700
FLOOR = 930
XP, XG = 190, 890
CHAR['PRISONNIER']['x'] = XP; CHAR['GARDIEN']['x'] = XG
ORANGE = (255, 150, 40)
GREEN = (90, 200, 120); RED = (230, 60, 50)
MIC = (120, 220, 90); MICD = (30, 80, 30)
TY = 1050
# livre posé debout sur la table (centre)
BX0, BX1, BTOP, BBOT = 395, 685, 680, 1050
# bocal de la réponse d'hier (#31)
JX0, JX1, JTOP, JBOT = 360, 720, 600, 1050

def wall(S):
    """mur de pierre brun-violet du donjon + table de bois au centre"""
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
    d.rounded_rectangle([300 * S, TY * S, 780 * S, (TY + 46) * S], radius=10 * S, fill=(120, 78, 46), outline=(50, 30, 20), width=4 * S)
    d.rectangle([310 * S, (TY + 40) * S, 770 * S, (TY + 52) * S], fill=(80, 50, 30))
    for lx in (330, 730):
        d.rectangle([lx * S, (TY + 46) * S, (lx + 22) * S, (TY + 200) * S], fill=(90, 58, 34))
    return im

def pop_at(t, times, dur=0.3, amp=0.3):
    for td in times:
        if 0 <= t - td < dur: return 1 + amp * (1 - (t - td) / dur)
    return 1.0

def book(img, t):
    """livre debout sur la table, étiquette de prix sur la couverture"""
    d = ImageDraw.Draw(img)
    sc = pop_at(t, [T_10 - 0.05, T_MOIT - 0.05], 0.3, 0.06)
    cx, cy = (BX0 + BX1) / 2, BBOT
    def P(x, y): return (cx + (x - cx) * sc, cy + (y - cy) * sc)
    x0, y0 = P(BX0, BTOP); x1, y1 = P(BX1, BBOT)
    # tranche (pages) à droite
    d.polygon([(x1, y0 + 10), (x1 + 34 * sc, y0 + 26 * sc), (x1 + 34 * sc, y1 - 6), (x1, y1)], fill=(235, 222, 190), outline=(60, 40, 30))
    for k in range(6):
        yy = y0 + 40 + k * (y1 - y0 - 60) / 6
        d.line([x1 + 6, yy, x1 + 30 * sc, yy + 10], fill=(200, 186, 150), width=2)
    d.rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], radius=18, fill=(30, 14, 18))
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(150, 40, 46))
    d.rectangle([x0, y0, x0 + 34 * sc, y1], fill=(110, 26, 34))
    d.rounded_rectangle([x0 + 50 * sc, y0 + 18 * sc, x1 - 16 * sc, y1 - 18 * sc], radius=10, outline=(230, 190, 90), width=5)
    d.text(((x0 + 34 * sc + x1) / 2, y0 + 70 * sc), "LIVRE", font=F(52 * sc), fill=(240, 205, 110), anchor='mm')
    # étiquette de prix
    if t < s1 - 0.05: l1, l2 = "? €", None
    elif t < s2 - 0.05: l1, l2 = "10 €", None
    else: l1, l2 = "10 €", "+ ½ PRIX"
    tx, ty = (x0 + 34 * sc + x1) / 2, y0 + 205 * sc
    tw, th = 220 * sc, (80 if l2 is None else 138) * sc
    d.rounded_rectangle([tx - tw / 2 - 5, ty - th / 2 - 5, tx + tw / 2 + 5, ty + th / 2 + 5], radius=16, fill=(30, 20, 20))
    d.rounded_rectangle([tx - tw / 2, ty - th / 2, tx + tw / 2, ty + th / 2], radius=14, fill=(250, 244, 225))
    d.ellipse([tx - tw / 2 + 12, ty - th / 2 + 12, tx - tw / 2 + 28, ty - th / 2 + 28], fill=(30, 20, 20))
    if l2 is None:
        d.text((tx + 8, ty + 3), l1, font=F(60 * sc), fill=(30, 20, 26), anchor='mm')
    else:
        d.text((tx + 8, ty - 30 * sc), l1, font=F(56 * sc), fill=(30, 20, 26), anchor='mm')
        d.text((tx + 4, ty + 34 * sc), l2, font=F(46 * sc), fill=(200, 50, 40), anchor='mm')

def badges(d, t):
    if s1 - 0.1 <= t < s2 - 0.1:
        badge(d, 540, 470, "IL COÛTE 10 €…", ease_back((t - s1 + 0.1) / 0.3), size=60)
    if s2 - 0.1 <= t < sQ - 0.05:
        badge(d, 540, 470, "+ LA MOITIÉ DE SON PRIX", ease_back((t - s2 + 0.1) / 0.3), fill=ORANGE, size=52)
    if sQ - 0.05 <= t < CE:
        badge(d, 540, 470, "COMBIEN COÛTE LE LIVRE ?", ease_back((t - (sQ - 0.05)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=50)
    if s3 - 0.1 <= t < CE + 0.3:
        v = ease_back((t - s3) / 0.3); pul = 1 + 0.05 * math.sin(t * 8)
        text_stroke(d, (540 + 4 * math.sin(t * 5), 590), "?", F(int(120 * clamp(v, 0, 1.1) * pul) + 1), (255, 214, 50), sw=8)

def microbe(d, x, y, t, r=26, k=0):
    wob = 1 + 0.08 * math.sin(t * 7 + k)
    rx, ry = r * wob, r / wob
    d.ellipse([x - rx - 4, y - ry - 4, x + rx + 4, y + ry + 4], fill=MICD)
    d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=MIC)
    for sgn in (-1, 1):
        d.ellipse([x + sgn * r * 0.35 - 6, y - r * 0.3 - 7, x + sgn * r * 0.35 + 6, y - r * 0.3 + 7], fill=(255, 255, 255))
        d.ellipse([x + sgn * r * 0.35 - 3, y - r * 0.3 - 3, x + sgn * r * 0.35 + 3, y - r * 0.3 + 4], fill=(20, 14, 16))
    for a in range(6):
        aa = a * math.pi / 3 + t * 2 + k
        d.line([x + math.cos(aa) * r, y + math.sin(aa) * r, x + math.cos(aa) * (r + 9), y + math.sin(aa) * (r + 9)], fill=MICD, width=4)

_r = random.Random(3)
FULLDOTS = [(JX0 + 30 + _r.random() * (JX1 - JX0 - 60), JTOP + 40 + _r.random() * (JBOT - JTOP - 70)) for _ in range(150)]

# --- réponse #31 : 59 minutes (2 microbes = l'état « minute 1 » du bocal à 1 microbe) ---
def answer_scene(img, t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle([JX0, JTOP, JX1, JBOT], radius=50, fill=(170, 210, 230, 55), outline=(210, 235, 245, 220), width=8)
    dl.rounded_rectangle([JX0 + 40, JTOP - 46, JX1 - 40, JTOP + 6], radius=14, fill=(150, 110, 70, 255), outline=(60, 40, 24, 255), width=5)
    u = ss((t - JUMP) / 0.4) if t >= JUMP else 0
    top = JBOT - 10 - (JBOT - JTOP - 20) * u
    if u > 0: dl.rounded_rectangle([JX0 + 10, top, JX1 - 10, JBOT - 10], radius=40, fill=(90, 190, 70, 230))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    if u > 0:
        for k, (x, y) in enumerate(FULLDOTS):
            if y > top + 14: microbe(d, x, y, t, r=13, k=k)
    if u < 1:
        for k, (x, y) in enumerate([(470, 980), (610, 980)]):
            microbe(d, x, y, t, r=38, k=k)
    d.line([JX0 + 26, JTOP + 60, JX0 + 26, JBOT - 80], fill=(230, 245, 255), width=6)
    if t >= ANS + 0.1:
        badge(d, 540, 470, "2 MICROBES = MINUTE 1", ease_back((t - ANS - 0.1) / 0.3), fill=ORANGE, size=52)
    if t >= T_REP - 0.2:
        badge(d, 540, TY + 24, "59 MIN !" if t < JUMP else "PLEIN À 59 MIN !", ease_back((t - T_REP + 0.2) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=48)
    if t >= T_REP - 0.2:
        badge(d, 540, 1300, "59 MINUTES !", ease_back((t - T_REP + 0.2) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)

BUBS = [
    ('GARDIEN', "Combien coûte le livre ?", lambda: s3 - 0.1, lambda: s4b - 0.05, 850, 640, 890),
    ('PRISONNIER', "15 euros !", lambda: T_FAUX - 0.1, lambda: sQ, 240, 720, 200),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: sQ, 850, 640, 890),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:7]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP, 920), (0.4, 1.0, 540, 960), (s1 - 0.1, 1.0, 540, 960),
            (s1 + 0.3, 1.05, 540, 860), (s3 - 0.2, 1.05, 540, 860), (s3 + 0.2, 1.04, 620, 960), (s4b - 0.2, 1.04, 620, 960),
            (s4b + 0.3, 1.04, 460, 960), (T_SOURIT - 0.1, 1.04, 460, 960), (T_SOURIT + 0.3, 1.04, 620, 960), (sQ - 0.1, 1.04, 620, 960),
            (sQ + 0.4, 1.0, 540, 960), (CE, 1.03, 540, 1000), (CE + 0.6, 1.02, 540, 980), (ANS, 1.02, 540, 980)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_10, 8), (T_MOIT, 8), (T_FAUX, 12), (T_SOURIT, 14), (sQ, 8), (STAMP, 18)]:
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
    G['cdark'] = Image.fromarray(np.clip(base * 0.85 + glow_layer(0.26) * 0.6, 0, 255).astype(np.uint8))
    G['clit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.48) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['hookband'] = grad_band(520, 1020, 0.6)
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

def bg(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['cdark'], G['clit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    return img

def scene(t):
    img = bg(t)
    pm = mouth_at(4, t) if T_FAUX <= t < T_SOURIT - 0.1 else 0
    gm = mouth_at(3, t) or (mouth_at(4, t) if t >= T_SOURIT - 0.05 else 0)
    mood = -1 if t < T_FAUX - 0.6 else 0
    im = draw_person('GARDIEN', t + 1, gm, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    chains(d)
    book(img, t)
    d = ImageDraw.Draw(img)
    badges(d, t)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=440)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img

def hook(img, t):
    if t >= HOOK_UP: return
    if t < HOOK_END:
        img.alpha_composite(G['hookband'])
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
    if not (s5 - 0.05 <= t < ANS): return
    u = ease_back((t - s5) / 0.3)
    f = F(int(56 * clamp(u, 0, 1.2)) + 1)
    y = 560
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS 15, 20 OU 10", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('15 €', 'EUROS', '15', 0), ('20 €', 'EUROS', '20', 0), ('10 €', 'EUROS', '10', 0)]
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
    img = bg(t)
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
                   'T10': T_10, 'TMOIT': T_MOIT, 'JUMP': JUMP, 'SPLIT': T_SOURIT, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '24', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
