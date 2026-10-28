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

NUM = "13"; TITRE = "LA BALLE ET LA BATTE"; CONTRAINTE = "LE BON PRIX = LA LIBERTÉ"
TITRE_HIER = "LES 3 PORTES DU GARDIEN"
HOOK = ["TROUVE", "LE PRIX", "IL SORT !"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Trouve le prix de la balle, et il sort !",
        "La batte et la balle coûtent 1,10 € en tout.",
        "La batte coûte 1 € de plus que la balle.",
        "Le prisonnier répond vite : 10 centimes ! Le gardien sourit.",
        "Alors, la balle coûte : 10 centimes, 5 centimes, ou 1 euro ?",
        "Écris ton prix en commentaire. Réponse demain !",
        "Réponse d'hier : changer ! 2 chances sur 3."]
NL = len(SUBS)
GAP = 0.35
s0 = 0.0
s1 = s0 + D[0] + 0.2
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
KEY = [["prix", "balle", "sort"], ["batte", "balle", "1,10", "€", "tout"], ["batte", "1", "€", "plus", "balle"],
       ["10", "centimes", "sourit"], ["10", "5", "1", "centimes", "euro"], ["prix", "demain"], ["changer", "2", "3"]]
TORCH = [(395, 500), (685, 500)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

T_TOT = wtime(1, '1,10')
T_PLUS = wtime(2, '1')
T_FAUX = wtime(3, '10')
T_SOURIT = wtime(3, 'sourit')
T_REP = wtime(6, 'changer')
HOOK_END = 1.75; HOOK_UP = 2.25

CHAR['PRISONNIER']['x'] = 210
CHAR['GARDIEN']['x'] = 870
PY = 720
FLOOR = 980
TX0, TX1, TY = 330, 750, 1040   # table

def wall(S, doors=True):
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
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    if doors:
        # porte de sortie au fond, avec barreaux
        x0, x1, y0, y1 = 440, 640, 640, FLOOR
        d.rounded_rectangle([(x0 - 24) * S, (y0 - 24) * S, (x1 + 24) * S, (y1 + 4) * S], radius=110 * S, fill=(96, 84, 92))
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=100 * S, fill=(12, 8, 12))
    else:
        # table du gardien
        d.rectangle([(TX0 + 30) * S, TY * S, (TX0 + 60) * S, (TY + 200) * S], fill=(70, 44, 26))
        d.rectangle([(TX1 - 60) * S, TY * S, (TX1 - 30) * S, (TY + 200) * S], fill=(70, 44, 26))
        d.rounded_rectangle([TX0 * S, (TY - 26) * S, TX1 * S, (TY + 16) * S], radius=10 * S, fill=(128, 82, 46))
        d.rectangle([TX0 * S, (TY + 4) * S, TX1 * S, (TY + 16) * S], fill=(96, 60, 32))
    return im

BAT = (440, 995); BALL = (665, 966)
def draw_bat(d, x, y, hi=False):
    # batte couchée (en biais)
    k = 1.25
    pts = [(x + k * a, y + k * b) for a, b in [(-120, 14), (-118, -4), (20, -30), (120, -44), (132, -22), (122, 4), (20, 6)]]
    if hi: d.polygon([(px + (px - x) * 0.04, py + (py - y) * 0.15) for px, py in pts], fill=(255, 150, 40))
    d.polygon(pts, fill=(196, 140, 80), outline=(60, 36, 20))
    d.ellipse([x - 165, y - 8, x - 138, y + 24], fill=(150, 100, 56))
    d.line([x - 138, y + 8, x - 88, y - 2], fill=(40, 30, 30), width=10)

def draw_ball(d, x, y, hi=False):
    r = 46
    d.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill=(255, 150, 40) if hi else (40, 26, 18))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 240, 230))
    d.arc([x - r - 18, y - r, x - 6, y + r], -60, 60, fill=(210, 40, 40), width=6)
    d.arc([x + 6, y - r, x + r + 18, y + r], 120, 240, fill=(210, 40, 40), width=6)

def init():
    random.seed(1)
    for nm, im in [('d', wall(2, False)), ('a', wall(2, True))]:
        base = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32)
        G[nm + 'dark'] = Image.fromarray(np.clip(base * 0.8 + glow_layer(0.30) * 0.6, 0, 255).astype(np.uint8))
        G[nm + 'lit'] = Image.fromarray(np.clip(base * 1.0 + glow_layer(0.55) * 0.7, 0, 255).astype(np.uint8))
    G['vig'] = vignette()
    G['red'] = vignette((200, 0, 0), 1.6, 1.0)
    G['top'] = grad_band(0, 380, 0.92, top_solid=True)
    G['sub'] = grad_band(1360, 1600, 0.75)
    G['hookband'] = grad_band(520, 1020, 0.6)
    G['sil'] = silhouette()
    G['rd'] = stamp_img('RÉPONSE DEMAIN', (230, 46, 46), 76, 30, rot=-9)
    for i in (3, 4): G[f'env{i}'] = mouth_env(i)

BUBS = [  # (perso, texte, t0, t1, cx, cy, tail_x)
    ('PRISONNIER', "10 centimes !", lambda: T_FAUX - 0.05, lambda: s4 + 0.2, 300, 720, 230),
    ('GARDIEN', "Tu es sûr ?", lambda: T_SOURIT, lambda: s4 + 0.6, 800, 720, 870),
]

def cam(t):
    keys = [(0, 1.10, 300, 1000), (0.4, 1.0, 540, 960), (s1, 1.0, 540, 960), (s1 + 0.5, 1.10, 540, 900), (s3 - 0.2, 1.10, 540, 900),
            (s3 + 0.3, 1.08, 330, 900), (T_SOURIT - 0.1, 1.08, 330, 900), (T_SOURIT + 0.3, 1.08, 760, 900), (s4 - 0.1, 1.08, 760, 900),
            (s4 + 0.4, 1.0, 540, 900), (CE, 1.06, 540, 880), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 14), (T_FAUX, 10), (STAMP, 16)]:
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

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['ddark'], G['dlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # personnages (derrière la table)
    bl = (t % 3.2) < 0.12
    mp = mouth_at(3, t) if T_FAUX - 0.3 <= t < T_SOURIT - 0.1 else 0
    pm = -1 if t < T_FAUX - 0.3 else 0
    img.alpha_composite(draw_person('PRISONNIER', t, mp, bl, pm), (CHAR['PRISONNIER']['x'] - 150, PY))
    img.alpha_composite(draw_person('GARDIEN', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0), (CHAR['GARDIEN']['x'] - 150, PY))
    d = ImageDraw.Draw(img)
    # chaînes du prisonnier
    for k in range(7):
        cx = CHAR['PRISONNIER']['x'] - 90 + k * 16; cy = PY + 470 + (k % 2) * 6
        d.ellipse([cx - 10, cy - 7, cx + 10, cy + 7], outline=(150, 150, 160), width=4)
    # objets
    hb = T_TOT - 0.1 <= t < s3
    draw_bat(d, BAT[0], BAT[1], hb and (t - T_TOT) % 0.6 < 0.3)
    draw_ball(d, BALL[0], BALL[1], hb and (t - T_TOT) % 0.6 >= 0.3)
    u0 = ease_back((t - (s1 - 0.05)) / 0.3) if t >= s1 - 0.05 else 0
    badge(d, BAT[0], 1105, "BATTE", u0, fill=(196, 140, 80), size=48)
    badge(d, BALL[0], 1105, "BALLE", u0, fill=(245, 240, 230), size=48)
    # prix
    if t >= T_TOT - 0.1:
        badge(d, 540, 440, "BATTE + BALLE = 1,10 €", ease_back((t - (T_TOT - 0.1)) / 0.3), fill=(255, 206, 40), size=52)
    if t >= T_PLUS - 0.1:
        badge(d, 540, 560, "BATTE = BALLE + 1 €", ease_back((t - (T_PLUS - 0.1)) / 0.3), fill=(80, 150, 230), tcol=(255, 255, 255), size=52)
    qu = ease_back((t - (s0 + 1.0)) / 0.3) if t >= s0 + 1.0 else 0
    if t < CE:
        badge(d, BALL[0], 880, "? €", qu * (1 + 0.06 * math.sin(t * 8)), fill=RED, tcol=(255, 255, 255), size=50)
    d = ImageDraw.Draw(img)
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
    for k, ln in enumerate(HOOK):
        col = (255, 214, 50) if k != 2 else (255, 80, 60)
        dl.text((W / 2, y0 + (k - 1) * fs * 1.08), ln, font=F(fs), fill=col + (255,), stroke_width=max(3, int(12 * sc)), stroke_fill=(10, 6, 12, 255), anchor='mm')
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

CHX = ['GARDER', 'CHANGER', 'PAREIL']
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    T0 = wtime(4, 'garder') - 0.2
    if not (T0 - 0.05 <= t < ANS): return
    for k, lab in enumerate(CHX):
        col = CHC[k]
        ts = T0 + k * 0.35
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 3) % 3 == k: pul = 1.08
        s = u * pul
        x = 190 + k * 350; y = 1310
        bw, bh = 320 * s, 120 * s
        d.rounded_rectangle([x - bw / 2 - 7, y - bh / 2 - 7, x + bw / 2 + 7, y + bh / 2 + 7], radius=int(50 * s) + 7, fill=col)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(50 * s), fill=(26, 18, 30))
        if s > 0.3:
            fs = 64
            while d.textlength(lab, font=F(fs)) > 270: fs -= 2
            d.text((x, y + 3), lab, font=F(fs * s), fill=(255, 255, 255), anchor='mm')

def outro_cta(img, d, t):
    if not (s5 - 0.05 <= t < ANS): return
    u = ease_back((t - s5) / 0.3)
    f = F(int(56 * clamp(u, 0, 1.2)) + 1)
    y = 560
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, fill=(16, 10, 16))
    d.rounded_rectangle([60, y - 120, W - 60, y + 120], radius=40, outline=(255, 206, 40), width=6)
    d.text((W / 2, y - 40), "ÉCRIS TON PRIX", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('10', 'CENTIMES'), ('5', 'CENTIMES'), ('1', 'EURO')]
def choices(img, d, t):
    T0 = wtime(4, '10') - 0.2
    if not (T0 - 0.05 <= t < ANS): return
    for k, (big, small) in enumerate(CHN):
        col = CHC[k]
        ts = wtime(4, ['10', '5', '1'][k]) - 0.15
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 3) % 3 == k: pul = 1.08
        s = u * pul
        x = 190 + k * 350; y = 1290
        bw, bh = 320 * s, 150 * s
        d.rounded_rectangle([x - bw / 2 - 7, y - bh / 2 - 7, x + bw / 2 + 7, y + bh / 2 + 7], radius=int(50 * s) + 7, fill=col)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(50 * s), fill=(26, 18, 30))
        if s > 0.3:
            d.text((x, y - 22 * s), big, font=F(80 * s), fill=(255, 255, 255), anchor='mm')
            d.text((x, y + 44 * s), small, font=F(42 * s), fill=col, anchor='mm')

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['adark'], G['alit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # 3 portes : 1 (son choix, 1 sur 3), 2 (ouverte, lumière, 2 sur 3), 3 (mur)
    got = t >= T_REP
    for k, cx in enumerate([250, 540, 830]):
        x0, x1, y0, y1 = cx - 105, cx + 105, 560, 980
        d.rounded_rectangle([x0 - 22, y0 - 22, x1 + 22, y1 + 4], radius=125, fill=(96, 84, 92))
        if k == 1 and got:
            u = clamp((t - T_REP) / 0.4)
            d.rounded_rectangle([x0, y0, x1, y1], radius=105, fill=(int(255 * u + 10 * (1 - u)), int(220 * u + 6 * (1 - u)), int(120 * u + 10 * (1 - u))))
        elif k == 2:
            d.rounded_rectangle([x0, y0, x1, y1], radius=105, fill=(150, 64, 44))
            for r in range(14):
                yy = y0 + 70 + r * 26
                d.line([x0 + 6, yy, x1 - 6, yy], fill=(90, 40, 30), width=4)
        else:
            d.rounded_rectangle([x0 + 6, y0 + 4, x1 - 6, y1 - 2], radius=100, fill=(128, 82, 46), outline=(40, 26, 18), width=4)
        d.ellipse([cx - 40, y0 + 50, cx + 40, y0 + 130], fill=(250, 240, 220), outline=(40, 26, 18), width=5)
        d.text((cx, y0 + 92), str(k + 1), font=F(60), fill=(30, 20, 26), anchor='mm')
    if got:
        u = ease_back((t - T_REP) / 0.3)
        badge(d, 540, 420, "CHANGER !", u, fill=GREEN, tcol=(255, 255, 255), size=80)
        badge(d, 540, 1080, "2 CHANCES SUR 3", clamp((t - T_REP - 0.35) / 0.3), fill=(255, 206, 40), size=56)
        badge(d, 250, 1180, "1 SUR 3", clamp((t - T_REP - 0.7) / 0.3), fill=(240, 230, 210), size=46)
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
