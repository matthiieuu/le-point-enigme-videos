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


# #36 LA CHARRETTE (26/11) — dérivée de video35.py.
# Gardés : T23 (3 choix visibles dès 0,0 s), T24 (prisonnier enchaîné + gardien).
# Non gardés (26/11) : T30 (titre court -> retour au nom de l'énigme), T34 (panneau -> retiré), T31 (chrono 4 s, conservé
# seulement comme partie du format court T35, à confirmer). À confirmer -> conservés : T32 (hook sans bandeau), T35 (vidéo ≤ 20 s).
# Test du jour : T36 — la réponse piège « 45 KM/H » tamponnée « FAUX ? » en rouge dès 0,0 s (pendant le hook).
NUM = "36"; TITRE = "LA CHARRETTE"; CONTRAINTE = "SA LIBERTÉ EN JEU"
TITRE_HIER = "LES BILLES DANS LE NOIR"
HOOK = ["LA BONNE VITESSE", "ET IL EST LIBRE !"]
CHR = 4.0
D = json.load(open('durees.json'))
SUBS = ["La bonne vitesse, et il est libre !",
        "La charrette va au village à 30 km/h.",
        "Elle revient par la même route, à 60.",
        "GARDIEN : Quelle est sa vitesse moyenne ?",
        "PRISONNIER : 45 ! GARDIEN : Ha ha ! Tu es sûr ?",
        "45, 40, ou 50 km/h ?",
        "Écris ta réponse en commentaire !",
        "Hier : 5 billes !"]
SPLIT4 = json.load(open('split.json'))['split4']
NL = len(SUBS)
GAP = 0.25
s0 = 0.0
s1 = s0 + D[0] + 0.15
s2 = s1 + D[1] + 0.2
s3 = s2 + D[2] + 0.25          # gardien « Combien pour être sûr d'avoir 2 bleues ? »
s4 = s3 + D[3] + 0.2           # prisonnier « 2 ! » puis gardien
sQ = s4 + D[4] + GAP
CS = sQ + D[5] - 0.2
CE = CS + CHR
sC = CE + 0.05
STAMP = sC + D[6] * 0.55
ANS = sC + D[6] + 0.15
sA = ANS + 0.1
FADE = sA + D[7] + 0.15
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, sQ, sC, sA]
NF = int(round(T * FPS))
KEY = [["vitesse", "libre"], ["village", "30", "km/h"], ["revient", "même", "route", "60"], ["vitesse", "moyenne"],
       ["45", "sûr"], ["45", "40", "50"], ["commentaire"], ["5", "billes"]]
TORCH = [(70, 640), (1010, 430)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())
def _spread(sub, a, b): return [a + (b - a) * j / len(sub) * 0.9 for j in range(len(sub))]
def _wt4():
    ws = SUBS[4].split(); kg = ws.index('GARDIEN')
    return ws, _spread(ws[:kg], s4, s4 + SPLIT4 - 0.15) + _spread(ws[kg:], s4 + SPLIT4 - 0.1, s4 + D[4])
WT[4] = _wt4()

T_GO = wtime(1, 'charrette') - 0.1                    # aller : départ lent
T_ARR = s2 - 0.15
T_30 = wtime(1, '30') - 0.15
T_BACK = wtime(2, 'revient') - 0.05                   # retour : rapide
T_BACK_END = T_BACK + 0.7
T_ROUTE = wtime(2, 'même') - 0.1
T_60 = wtime(2, '60') - 0.15
T_Q = s3 - 0.05
T_FAUX = s4
T_SOURIT = s4 + SPLIT4
T_REP = sA
CHRONO_XY = (540, 1100)
HOOK_END = 1.3; HOOK_UP = 1.65
FAUX_T0 = 0.0
PY = 700
FLOOR = 930
XP, XG = 150, 930
CHAR['PRISONNIER']['x'] = XP; CHAR['GARDIEN']['x'] = XG
ORANGE = (255, 150, 40)
GREEN = (90, 200, 120); RED = (230, 60, 50)
BRED = (225, 50, 45); BBLUE = (50, 120, 235)
BALLS = [BRED] * 3 + [BBLUE] * 5
RX0, RX1, RY = 400, 680, 1040                         # route : cachot (gauche) -> village (droite)

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

def ball(d, x, y, r, col, q=False):
    d.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill=(14, 8, 14))
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    d.ellipse([x - r * 0.55, y - r * 0.6, x - r * 0.05, y - r * 0.15], fill=tuple(min(255, c + 90) for c in col))

def cart_layer(t, moving, speed):
    """âne + charrette, tournés vers la droite (miroir pour le retour)"""
    S = 2; w, h = 300, 170
    lay = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def P(*pts): return [v * S for v in pts]
    bob = math.sin(t * (18 if speed > 1 else 9)) * (3 if moving else 0)
    # âne (à droite)
    leg = math.sin(t * (22 if speed > 1 else 11)) * (14 if moving else 0)
    for k, (lx, ph) in enumerate([(200, 1), (215, -1), (250, -1), (265, 1)]):
        d.line(P(lx, 112 + bob, lx + leg * ph * 0.5, 160), fill=(90, 80, 86), width=9 * S)
    d.ellipse(P(185, 70 + bob, 285, 125 + bob), fill=(130, 120, 128))
    d.polygon(P(262, 88 + bob, 280, 40 + bob, 300, 52 + bob, 285, 100 + bob), fill=(130, 120, 128))
    d.ellipse(P(268, 30 + bob, 300, 70 + bob), fill=(140, 130, 138))
    d.polygon(P(272, 36 + bob, 266, 6 + bob, 282, 32 + bob), fill=(110, 100, 108))
    d.polygon(P(284, 34 + bob, 286, 4 + bob, 294, 34 + bob), fill=(110, 100, 108))
    d.ellipse(P(284, 42 + bob, 291, 49 + bob), fill=(20, 14, 16))
    d.line(P(150, 95 + bob * 0.5, 200, 92 + bob), fill=(70, 46, 26), width=6 * S)
    # charrette (à gauche)
    d.polygon(P(10, 62, 165, 62, 155, 112, 20, 112), fill=(150, 96, 50))
    for k in range(3): d.line(P(14 + k * 2, 74 + k * 13, 162 - k * 2, 74 + k * 13), fill=(118, 72, 36), width=3 * S)
    d.rectangle(P(5, 56, 170, 66), fill=(110, 68, 34))
    # foin dans la charrette
    for k in range(5): d.ellipse(P(20 + k * 28, 36, 62 + k * 28, 70), fill=(220, 180, 80))
    # roue qui tourne
    ang = -t * (14 if speed > 1 else 6) if moving else 0
    wx, wy, wr = 88, 128, 38
    d.ellipse(P(wx - wr, wy - wr, wx + wr, wy + wr), outline=(60, 38, 20), width=8 * S)
    for k in range(6):
        a = ang + k * math.pi / 3
        d.line(P(wx, wy, wx + math.cos(a) * wr, wy + math.sin(a) * wr), fill=(70, 46, 26), width=4 * S)
    d.ellipse(P(wx - 8, wy - 8, wx + 8, wy + 8), fill=(60, 38, 20))
    return lay.resize((w, h), Image.LANCZOS)

def cart_pos(t):
    """renvoie (x centre, sens, en mouvement, vitesse)"""
    if t < T_GO: return RX0, 1, False, 1
    if t < T_ARR:
        u = (t - T_GO) / (T_ARR - T_GO); return RX0 + (RX1 - RX0) * u, 1, True, 1
    if t < T_BACK: return RX1, -1, False, 1
    if t < T_BACK_END:
        u = ss((t - T_BACK) / (T_BACK_END - T_BACK)); return RX1 + (RX0 - RX1) * u, -1, True, 2
    return RX0, -1, False, 2

def road(img, d, t):
    """route de terre entre le CACHOT et le VILLAGE + l'âne et sa charrette"""
    hl = T_ROUTE <= t < sC
    d.rounded_rectangle([RX0 - 120, RY + 50, RX1 + 120, RY + 92], radius=20, fill=(96, 70, 48) if not hl else (150, 110, 60))
    for k in range(9):
        xx = RX0 - 90 + k * 75
        d.line([xx, RY + 71, xx + 30, RY + 71], fill=(70, 50, 34), width=4)
    # village : petite maison à droite
    x, sg, mv, sp = cart_pos(t)
    lay = cart_layer(t, mv, sp)
    if sg < 0: lay = lay.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(lay, (int(x - lay.width / 2), int(RY - 75)))
    d = ImageDraw.Draw(img)
    if mv and sp > 1:                                  # traits de vitesse au retour
        for k in range(5):
            yy = RY - 50 + k * 26; xx = x + 160 + (k % 2) * 30
            d.line([xx, yy, xx + 90, yy], fill=(255, 255, 255), width=5)
    if mv and sp == 1:
        for k in range(3):
            pu = x - 160 - k * 24; d.ellipse([pu - 10, RY + 40 - k * 6, pu + 10, RY + 60 - k * 6], fill=(150, 120, 90))
    if hl and t < T_Q:
        badge(d, 540, RY - 140, "MÊME ROUTE", ease_back((t - T_ROUTE) / 0.3), fill=(255, 206, 40), size=50)

def badges(d, t):
    if T_30 <= t < T_Q:
        badge(d, 540, 425, "ALLER : 30 KM/H", ease_back((t - T_30) / 0.3), fill=ORANGE, size=60)
    if T_60 <= t < T_Q:
        badge(d, 540, 530, "RETOUR : 60 KM/H", ease_back((t - T_60) / 0.3), fill=(90, 160, 255), size=60)
    if T_Q <= t < CE + 0.3:
        badge(d, 540, 425, "ALLER 30 · RETOUR 60", 1.0, fill=ORANGE, size=50)
        badge(d, 540, 530, "VITESSE MOYENNE ?", ease_back((t - T_Q) / 0.3), fill=(255, 206, 40), size=62)

# --- réponse #35 : 5 billes (pire cas : les 3 rouges sortent d'abord, puis 2 bleues) ---
ABALLS = [BRED] * 3 + [BBLUE] * 2
def answer_scene(img, t):
    d = ImageDraw.Draw(img)
    for k, col in enumerate(ABALLS):
        tk = ANS + 0.05 + k * 0.12
        if t < tk: continue
        u = ease_back((t - tk) / 0.25)
        x = 180 + k * 180; y = 1000
        ball(d, x, y, 62 * clamp(u, 0.05, 1.2), col)
        badge(d, x, 1110, str(k + 1), u, size=50)
    badge(d, 540, 420, "3 ROUGES + 2 BLEUES", ease_back((t - ANS) / 0.25), fill=(255, 206, 40), size=62)
    badge(d, 540, 600, "5 BILLES !", ease_back((t - T_REP + 0.1) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)

BUBS = [
    ('GARDIEN', "Quelle est sa vitesse moyenne ?", lambda: s3 - 0.1, lambda: s4 - 0.05, 790, 840, 930),
    ('PRISONNIER', "45 !", lambda: T_FAUX - 0.1, lambda: sQ, 250, 820, 160),
    ('GARDIEN', "HA HA ! Tu es sûr ?", lambda: T_SOURIT, lambda: sQ, 790, 840, 930),
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
    for hh, amp in [(0.0, 16), (0.15, 10), (T_BACK, 8), (T_FAUX, 12), (T_SOURIT, 14), (sQ, 8), (STAMP, 18)]:
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
    G['faux'] = stamp_img('FAUX ?', (240, 50, 45), 84, 24, rot=-10)
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
    road(img, ImageDraw.Draw(img), t)
    im = draw_person('GARDIEN', t + 1, gm, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
    img.alpha_composite(im, (int(XG - 150), PY))
    im = draw_person('PRISONNIER', t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
    img.alpha_composite(im, (int(XP - 150), PY))
    d = ImageDraw.Draw(img)
    chains(d)
    badges(d, t)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=420)
    if t >= HOOK_UP:
        badge(d, 412, 1150, "CACHOT", 1.0, fill=(200, 190, 200), size=42)
        badge(d, 668, 1150, "VILLAGE", 1.0, fill=(200, 190, 200), size=42)
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
    d.text((W / 2, y - 40), "ÉCRIS 45, 40 OU 50", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('45', 'KM/H', '45', 0), ('40', 'KM/H', '40', 0), ('50', 'KM/H', '50', 0)]
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
        if k == 0 and FAUX_T0 <= t < HOOK_UP:          # T36 : la réponse piège tamponnée « FAUX ? » dès 0,0 s
            a = 1.0 if t < HOOK_UP - 0.15 else clamp((HOOK_UP - t) / 0.15)
            sc = 1 + 1.4 * max(0, 1 - (t - FAUX_T0) / 0.12)
            d.line([x - bw / 2 + 10, y + bh / 2 - 10, x + bw / 2 - 10, y - bh / 2 + 10], fill=(230, 46, 46), width=12)
            st = G['faux']; st2 = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
            if a < 1: st2.putalpha(st2.getchannel('A').point(lambda v: int(v * a)))
            img.alpha_composite(st2, (int(x - st2.width / 2 + 40), int(y - 125 - st2.height / 2)))

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
                   'FAUX0': FAUX_T0, 'GO': T_GO, 'BACK': T_BACK, 'ROUTE': T_ROUTE, 'TREP': T_REP, 'SPLIT': T_SOURIT, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
