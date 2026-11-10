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


NUM = "20"; TITRE = "LES MOIS À 28 JOURS"; CONTRAINTE = "1 QUESTION = LA LIBERTÉ"
TITRE_HIER = "LES PILULES DU GEÔLIER"
HOOK = ["COMPTE LES MOIS", "OU LA PRISON"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Ce prisonnier sort s'il compte bien les mois !",
        "Une SEULE question !",
        "Combien de mois ont 28 jours ?",
        "Il hurle : un seul, février ! Et là… le gardien explose de rire.",
        "Alors : 1, 2, ou 12 ?",
        "Vite, écris ta réponse en commentaire !",
        "Réponse d'hier : 60 minutes ! 0, 30, 60 !"]
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
KEY = [["compte", "mois"], ["seule"], ["mois", "28", "jours"],
       ["février", "rire"], ["1", "2", "12"], ["commentaire", "vite"], ["60", "minutes"]]
TORCH = [(300, 500), (780, 500)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

CHAR['GARDE2'] = dict(x=540, col=(80, 150, 230), hair=(130, 80, 40), style='short', skin=(226, 170, 124))
T_SEULE = wtime(1, 'seule'); T_28 = wtime(2, '28')
T_FAUX = wtime(3, 'février')
T_SOURIT = wtime(3, 'explose')
T_REP = wtime(6, '60')
HOOK_END = 1.55; HOOK_UP = 2.0
PY = 690
FLOOR = 930
XP, XG = 250, 850
CRX, CRY = 540, 1000   # haut de la caisse

def wall(S, forge=False):
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
    if not forge:
        # barreaux de cellule au fond
        for i in range(5):
            x = (60 + i * 40) * S
            d.rectangle([x, 380 * S, x + 12 * S, 930 * S], fill=(44, 36, 44))
        for i in range(5):
            x = (860 + i * 40) * S
            d.rectangle([x, 380 * S, x + 12 * S, 930 * S], fill=(44, 36, 44))
    return im

def sheep(d, x, y, s, t=0.0, ph=0.0):
    """mouton : corps laineux blanc, tête noire, pattes"""
    bob = math.sin(t * 5 + ph) * 3 * s
    for lx in (-20, -6, 10, 22):
        d.rectangle([x + lx * s - 4 * s, y + 14 * s, x + lx * s + 4 * s, y + 38 * s], fill=(30, 24, 30))
    for (cx_, cy_, r) in [(-22, 0, 20), (-6, -10, 22), (12, -8, 21), (24, 4, 18), (0, 10, 22), (-18, 12, 17), (18, 14, 17)]:
        d.ellipse([x + (cx_ - r) * s, y + bob + (cy_ - r) * s, x + (cx_ + r) * s, y + bob + (cy_ + r) * s], fill=(246, 242, 232), outline=(40, 30, 36), width=max(2, int(3 * s)))
    hx = x + 40 * s; hy = y + bob - 8 * s
    d.ellipse([hx - 14 * s, hy - 16 * s, hx + 16 * s, hy + 14 * s], fill=(34, 28, 34))
    d.ellipse([hx - 22 * s, hy - 12 * s, hx - 8 * s, hy - 4 * s], fill=(34, 28, 34))
    d.ellipse([hx + 2 * s, hy - 6 * s, hx + 8 * s, hy], fill=(255, 255, 255))

def sheep_pos(k):
    """17 moutons : 6 / 6 / 5 dans l'enclos"""
    row = 0 if k < 6 else (1 if k < 12 else 2)
    j = k - [0, 6, 12][row]
    n = [6, 6, 5][row]
    x = 540 + (j - (n - 1) / 2) * 150 + (row % 2) * 20
    return x, 500 + row * 85

MOIS = ["JANV", "FÉVR", "MARS", "AVR", "MAI", "JUIN", "JUIL", "AOÛT", "SEPT", "OCT", "NOV", "DÉC"]
def month_tile(d, x, y, s, name, hot=0.0):
    w, h = 74 * s, 70 * s
    d.rounded_rectangle([x - w - 4, y - h - 4, x + w + 4, y + h + 4], radius=int(14 * s) + 4, fill=(16, 10, 16))
    top = (220, 50, 60) if hot <= 0 else (255, 206, 40)
    d.rounded_rectangle([x - w, y - h, x + w, y + h], radius=int(14 * s), fill=(245, 240, 228))
    d.rounded_rectangle([x - w, y - h, x + w, y - h + 40 * s], radius=int(14 * s), fill=top)
    d.rectangle([x - w, y - h + 24 * s, x + w, y - h + 40 * s], fill=top)
    if s > 0.4:
        d.text((x, y - h + 21 * s), name, font=F(28 * s), fill=(255, 255, 255) if hot <= 0 else (24, 14, 20), anchor='mm')
        d.text((x, y + 20 * s), "?", font=F(52 * s), fill=(60, 44, 56), anchor='mm')
def tile_pos(k):
    return 130 + (k % 6) * 135, 455 + (k // 6) * 160

def init():
    random.seed(1)
    for nm, im in [('r', wall(2, False)), ('d', wall(2, True))]:
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
    ('PRISONNIER', "Un seul : février !", lambda: T_FAUX - 0.25, lambda: s4, 330, 770, 280),
    ('GARDIEN', "HA HA HA !", lambda: T_SOURIT, lambda: s4, 790, 770, 840),
]

def cam(t):
    z, x, y = cam0(t)
    for st in STARTS[:6]:
        if 0 <= t - st < 0.3:
            z *= 1 + 0.07 * (1 - ss((t - st) / 0.3))
    return z, x, y

def cam0(t):
    keys = [(0, 1.10, XP + 60, 960), (0.4, 1.0, 540, 960), (s3 - 0.2, 1.0, 540, 960),
            (s3 + 0.3, 1.08, 450, 900), (T_SOURIT - 0.1, 1.08, 450, 900), (T_SOURIT + 0.3, 1.08, 650, 900), (s4 - 0.1, 1.08, 650, 900),
            (s4 + 0.4, 1.0, 540, 900), (CE, 1.06, 540, 880), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 16), (T_SEULE, 10), (T_28, 8), (T_FAUX, 12), (T_SOURIT, 14), (s4, 8), (STAMP, 18)]:
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

def place_tag(d, x, y, txt, col, u):
    if u <= 0: return
    r = 54 * u
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(20, 12, 18), width=6)
    d.text((x, y + 2), txt, font=F(54 * u), fill=(255, 255, 255), anchor='mm', stroke_width=3, stroke_fill=(20, 12, 18))

def fog(t):
    """0 = enclos visible, 1 = enclos caché par le brouillard « ? »"""
    if t < T_MEUR - 0.1: return 0.0
    return clamp((t - (T_MEUR - 0.1)) / 0.35)

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['rdark'], G['rlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    pm = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    for nm, x in [('GARDIEN', XG), ('PRISONNIER', XP)]:
        if nm == 'PRISONNIER':
            im = draw_person(nm, t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
        else:
            im = draw_person(nm, t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
        img.alpha_composite(im, (int(x - 150), PY))
    d = ImageDraw.Draw(img)
    # le calendrier des 12 mois : les cases apparaissent en rafale sur « mois »
    T_M = wtime(2, 'mois') - 0.2
    for k in range(12):
        x, y = tile_pos(k)
        tk = T_M + k * 0.05
        if t < tk: continue
        u = clamp(ease_back((t - tk) / 0.22), 0, 1.15)
        hot = 1.0 if (k == 1 and T_FAUX - 0.1 <= t < s4) else 0.0
        pul = 1 + (0.18 * math.sin(math.pi * clamp((t - (T_FAUX - 0.1)) / 0.35)) if k == 1 else 0)
        month_tile(d, x, y + 3 * math.sin(t * 3 + k), u * pul, MOIS[k], hot)
    if T_SEULE - 0.1 <= t < wtime(2, 'mois') - 0.3:
        badge(d, 540, 560, "1 SEULE QUESTION", ease_back((t - (T_SEULE - 0.1)) / 0.25) * (1 + 0.05 * math.sin(t * 10)), fill=(255, 206, 40), size=76)
    if (T_28 - 0.1 <= t < T_FAUX - 0.3) or (s4 - 0.05 <= t < CE):
        badge(d, 540, 830, "COMBIEN ONT 28 JOURS ?", ease_back((t - (T_28 - 0.1)) / 0.25) * (1 + 0.04 * math.sin(t * 9)), fill=(255, 206, 40), size=56)
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
    d.text((W / 2, y - 40), "ÉCRIS 1, 2 OU 12", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('1', 'MOIS', '1'), ('2', 'MOIS', '2'), ('12', 'MOIS', '12')]
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

def sock(d, x, y, s, black, rot=0.0):
    col = (24, 22, 28) if black else (245, 242, 236)
    ol = (200, 190, 200) if black else (30, 22, 28)
    pts = [(-14, -44), (14, -44), (14, 12), (30, 12), (34, 30), (26, 44), (-6, 44), (-14, 32)]
    c, sn = math.cos(rot), math.sin(rot)
    P = [(x + s * (px_ * c - py_ * sn), y + s * (px_ * sn + py_ * c)) for px_, py_ in pts]
    d.polygon(P, fill=col, outline=ol)
    d.line([P[0], P[1]], fill=(200, 60, 60) if black else (90, 150, 230), width=max(2, int(6 * s)))

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['ddark'], G['dlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # 3 pilules sur une frise : 0, 30, 60 minutes
    d.line([(150, 860), (930, 860)], fill=(255, 206, 40), width=10)
    for j, (lab, x) in enumerate([("0 MIN", 200), ("30 MIN", 540), ("60 MIN", 880)]):
        tj = ANS + 0.1 + j * 0.35
        if t < tj: continue
        u = clamp(ease_back((t - tj) / 0.25), 0, 1.2)
        d.ellipse([x - 22, 838, x + 22, 882], fill=(255, 206, 40), outline=(20, 12, 18), width=4)
        w_, h_ = 70 * u, 30 * u
        d.rounded_rectangle([x - w_, 760 - h_, x + w_, 760 + h_], radius=int(h_) + 1, fill=(245, 242, 236), outline=(16, 10, 16), width=4)
        d.rounded_rectangle([x - w_, 760 - h_, x, 760 + h_], radius=int(h_) + 1, fill=(220, 50, 60))
        if u > 0.5: d.text((x, 940), lab, font=F(46), fill=(255, 255, 255), stroke_width=4, stroke_fill=(16, 10, 16), anchor='mm')
    if t >= T_REP - 0.4:
        badge(d, 540, 470, "60 MINUTES !", ease_back((t - T_REP + 0.4) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=90)
        badge(d, 540, 620, "PAS 90 : LA 1RE EST À 0", ease_back((t - T_REP + 0.2) / 0.3), fill=(255, 206, 40), size=50)
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

