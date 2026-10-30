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

NUM = "15"; TITRE = "LES MACHINES DU FORGERON"; CONTRAINTE = "LE BON TEMPS = LA LIBERTÉ"
TITRE_HIER = "LES NÉNUPHARS DU CACHOT"
HOOK = ["LE BON TEMPS", "LE LIBÈRE"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Ce forgeron sort s'il donne le bon temps !",
        "5 machines font 5 épées en 5 minutes.",
        "Le roi veut 100 épées, avec 100 machines.",
        "Le forgeron dit : 100 minutes ! Le gardien sourit.",
        "Alors, il faut : 100 minutes, ou 5 minutes ?",
        "Écris ta réponse en commentaire. Réponse demain !",
        "Réponse d'hier : jour 47, pas 24 !"]
NL = len(SUBS)
GAP = 0.35
s0 = 0.0
s1 = s0 + D[0] + 0.2
s2 = s1 + D[1] + GAP + 0.3
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
KEY = [["forgeron", "bon", "temps"], ["5", "machines", "épées", "minutes"], ["100", "épées", "machines"],
       ["100", "minutes", "sourit"], ["100", "5", "minutes"], ["commentaire", "demain"], ["jour", "47", "24"]]
TORCH = [(395, 500), (685, 500)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

T_5M = wtime(1, 'machines')
T_5E = wtime(1, 'épées')
T_5MIN = wtime(1, '5', 2)
T_100E = wtime(2, '100')
T_100M = wtime(2, '100', 1)
T_FAUX = wtime(3, '100')
T_SOURIT = wtime(3, 'sourit')
T_REP = wtime(6, '47')
HOOK_END = 1.75; HOOK_UP = 2.25

CHAR['PRISONNIER']['x'] = 190
CHAR['GARDIEN']['x'] = 890
PY = 690
FLOOR = 930
LX, LY, LRX, LRY = 540, 1085, 300, 140   # lac (réponse d'hier)

def wall(S, lake=False):
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
    if lake:
        d.ellipse([(LX - LRX - 26) * S, (LY - LRY - 22) * S, (LX + LRX + 26) * S, (LY + LRY + 22) * S], fill=(96, 84, 92))
        d.ellipse([(LX - LRX) * S, (LY - LRY) * S, (LX + LRX) * S, (LY + LRY) * S], fill=(28, 70, 96))
    else:
        # forge : foyer rougeoyant au fond + établi
        d.rounded_rectangle([430 * S, 760 * S, 650 * S, 930 * S], radius=20 * S, fill=(50, 34, 40))
        d.rounded_rectangle([460 * S, 800 * S, 620 * S, 930 * S], radius=14 * S, fill=(150, 60, 24))
        d.rounded_rectangle([480 * S, 840 * S, 600 * S, 930 * S], radius=10 * S, fill=(240, 140, 40))
        d.rectangle([300 * S, 1215 * S, 780 * S, 1240 * S], fill=(96, 62, 36))
    return im

def _pads():
    rnd = random.Random(3); P = []
    for j in range(-6, 7):
        for i in range(-9, 10):
            x = LX + i * 32 + (j % 2) * 16; y = LY + j * 22
            if ((x - LX) / (LRX - 26)) ** 2 + ((y - LY) / (LRY - 18)) ** 2 <= 1: P.append((x, y))
    rnd.shuffle(P)
    P.sort(key=lambda p: ((p[0] - LX) / LRX) ** 2 + ((p[1] - LY) / LRY) ** 2 + rnd.random() * 0.15)
    return P
PADS = _pads()

def draw_pads(d, n):
    for k, (x, y) in enumerate(PADS[:n]):
        r = 21
        d.ellipse([x - r, y - r * 0.62, x + r, y + r * 0.62], fill=(70, 170, 80), outline=(30, 90, 40), width=2)
        d.polygon([(x, y), (x + r, y - r * 0.25), (x + r, y + r * 0.1)], fill=(28, 70, 96))
        if k % 7 == 0: d.ellipse([x - 6, y - 10, x + 6, y - 2], fill=(240, 150, 200))

def machine(d, x, y, s, t, k):
    """petite presse-marteau : socle, montant, marteau qui frappe"""
    w = 70 * s
    d.rounded_rectangle([x - w / 2, y - 22 * s, x + w / 2, y], radius=int(6 * s), fill=(110, 110, 124), outline=(20, 14, 20), width=max(1, int(3 * s)))
    d.rectangle([x + w / 2 - 14 * s, y - 100 * s, x + w / 2 - 4 * s, y - 22 * s], fill=(80, 80, 92))
    d.rectangle([x - w / 2 + 4 * s, y - 108 * s, x + w / 2 - 4 * s, y - 96 * s], fill=(80, 80, 92))
    ph = (t * 2.2 + k * 0.37) % 1
    hy = y - 92 * s + 50 * s * (ph / 0.3 if ph < 0.3 else max(0, 1 - (ph - 0.3) / 0.7))
    d.rectangle([x - 3 * s, y - 96 * s, x + 3 * s, hy], fill=(60, 60, 70))
    d.rounded_rectangle([x - 18 * s, hy, x + 18 * s, hy + 18 * s], radius=int(4 * s), fill=(170, 170, 184), outline=(20, 14, 20), width=max(1, int(2 * s)))
    if ph < 0.38 and s > 0.5:
        for a in (-1, 1):
            d.line([x + a * 20 * s, y - 26 * s, x + a * 36 * s, y - 40 * s], fill=(255, 200, 60), width=max(2, int(4 * s)))

def sword(d, x, y, s):
    d.polygon([(x - 6 * s, y), (x + 6 * s, y), (x + 6 * s, y - 70 * s), (x, y - 84 * s), (x - 6 * s, y - 70 * s)], fill=(220, 224, 236), outline=(30, 24, 30))
    d.rectangle([x - 20 * s, y, x + 20 * s, y + 8 * s], fill=(200, 160, 60))
    d.rectangle([x - 5 * s, y + 8 * s, x + 5 * s, y + 30 * s], fill=(110, 66, 36))

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

BUBS = [
    ('PRISONNIER', "100 minutes !", lambda: T_FAUX - 0.05, lambda: s4 + 0.2, 300, 770, 210),
    ('GARDIEN', "Tu es sûr ?", lambda: T_SOURIT, lambda: s4 + 0.6, 780, 770, 880),
]

def cam(t):
    keys = [(0, 1.10, 260, 960), (0.4, 1.0, 540, 960), (s1, 1.0, 540, 960), (s1 + 0.4, 1.12, 540, 1060), (s3 - 0.2, 1.12, 540, 1060),
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
    for hh, amp in [(0.0, 14), (T_100M, 12), (T_FAUX, 8), (STAMP, 16)]:
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
    big = t >= T_100M - 0.1
    if not big:
        # 5 machines alignées sur l'établi, une épée sort de chacune
        for k in range(5):
            x = 345 + k * 97
            machine(d, x, 1215, 1.0, t, k)
            if t >= T_5E - 0.1:
                u = ease_back((t - (T_5E - 0.1) - k * 0.08) / 0.3)
                if u > 0: sword(d, x, 1060, clamp(u, 0, 1.1) * 1.2)
    else:
        # 100 machines : grille 10 x 10
        u0 = (t - (T_100M - 0.1)) / 0.6
        for j in range(10):
            for i in range(10):
                k = j * 10 + i
                u = clamp(u0 * 1.6 - k / 100)
                if u <= 0: continue
                machine(d, 360 + i * 40, 985 + j * 25, 0.42 * u, t, k)
    bl = (t % 3.2) < 0.12
    mp = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    pm = -1 if t < T_FAUX - 0.6 else 0
    img.alpha_composite(draw_person('PRISONNIER', t, mp, bl, pm), (CHAR['PRISONNIER']['x'] - 150, PY))
    img.alpha_composite(draw_person('GARDIEN', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0), (CHAR['GARDIEN']['x'] - 150, PY))
    d = ImageDraw.Draw(img)
    for k in range(7):
        cx = CHAR['PRISONNIER']['x'] - 90 + k * 16; cy = PY + 470 + (k % 2) * 6
        d.ellipse([cx - 10, cy - 7, cx + 10, cy + 7], outline=(150, 150, 160), width=4)
    # règles montrées au moment où elles sont dites
    if s1 - 0.1 <= t < T_100E - 0.1:
        badge(d, 540, 450, "5 MACHINES = 5 ÉPÉES", ease_back((t - (T_5M - 0.2)) / 0.3) if t >= T_5M - 0.2 else 0, fill=(80, 150, 230), tcol=(255, 255, 255), size=54)
        if t >= T_5MIN - 0.1:
            badge(d, 540, 570, "EN 5 MINUTES", ease_back((t - (T_5MIN - 0.1)) / 0.3), fill=(255, 206, 40), size=58)
    if t >= T_100E - 0.1:
        badge(d, 540, 450, "100 MACHINES = 100 ÉPÉES", ease_back((t - (T_100E - 0.1)) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=52)
        badge(d, 455, 570, "5 MACHINES = 5 ÉPÉES EN 5 MIN", 1.0 if t >= T_100E + 0.3 else 0, fill=(80, 150, 230), tcol=(255, 255, 255), size=44)
    if s4 <= t < CE:
        badge(d, 460, 690, "COMBIEN DE MINUTES ?", ease_back((t - s4) / 0.3) * (1 + 0.05 * math.sin(t * 8)), fill=RED, tcol=(255, 255, 255), size=52)
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
    d.text((W / 2, y - 40), "ÉCRIS 100 OU 5", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

# T13 : 2 choix seulement
CHN = [('100', 'MINUTES'), ('5', 'MINUTES')]
CHC = [(255, 150, 40), (80, 150, 230)]
def choices(img, d, t):
    if not (wtime(4, '100') - 0.3 <= t < ANS): return
    for k, (big, small) in enumerate(CHN):
        col = CHC[k]
        ts = wtime(4, big) - 0.15
        u = ease_back((t - ts) / 0.3) if t >= ts else 0
        if u <= 0: continue
        pul = 1.0
        if CS <= t < CE and int((t - CS) * 2) % 2 == k: pul = 1.08
        s = u * pul
        x = 300 + k * 480; y = 1290
        bw, bh = 400 * s, 160 * s
        d.rounded_rectangle([x - bw / 2 - 7, y - bh / 2 - 7, x + bw / 2 + 7, y + bh / 2 + 7], radius=int(50 * s) + 7, fill=col)
        d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(50 * s), fill=(26, 18, 30))
        if s > 0.3:
            d.text((x, y + 24 * s), big, font=F(92 * s), fill=(255, 255, 255), anchor='mm')
            d.text((x, y - 48 * s), small, font=F(38 * s), fill=col, anchor='mm')

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['adark'], G['alit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    got = t >= T_REP
    n = len(PADS) // 2
    if got and t >= T_REP + 1.2: n = int(len(PADS) * (0.5 + 0.5 * clamp((t - T_REP - 1.2) / 0.4)))
    draw_pads(d, n)
    if got:
        u = ease_back((t - T_REP) / 0.3)
        badge(d, 540, 470, "JOUR 47 !", u, fill=GREEN, tcol=(255, 255, 255), size=84)
        badge(d, 540, 620, "JOUR 47 = MOITIÉ", clamp((t - T_REP - 0.3) / 0.3), fill=(255, 206, 40), size=54)
        badge(d, 540, 750, "× 2 = JOUR 48 : TOUT", clamp((t - T_REP - 1.0) / 0.3), fill=(80, 150, 230), tcol=(255, 255, 255), size=54)
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

