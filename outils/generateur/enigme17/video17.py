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


NUM = "17"; TITRE = "LES CHAUSSETTES DU CACHOT"; CONTRAINTE = "UNE PAIRE = LA LIBERTÉ"
TITRE_HIER = "LA COURSE DU CACHOT"
HOOK = ["UNE PAIRE", "LE LIBÈRE"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Ce prisonnier sort s'il tire une paire !",
        "10 noires, 10 blanches, mélangées.",
        "Il pioche dans le noir.",
        "Il crie : 11 ! Le gardien sourit.",
        "Combien en prendre pour être sûr d'avoir une paire : 2, 3, ou 11 ?",
        "Écris ta réponse en commentaire !",
        "Réponse d'hier : 2e !"]
NL = len(SUBS)
GAP = 0.2
s0 = 0.0
s1 = s0 + D[0] + 0.1
s2 = s1 + D[1] + GAP
s3 = s2 + D[2] + GAP
s4 = s3 + D[3] + GAP
CS = s4 + D[4] - 0.4
CE = CS + CHR
s5 = CE + 0.05
STAMP = s5 + D[5] * 0.55
ANS = s5 + D[5] + 0.2
s6 = ANS + 0.2
FADE = s6 + D[6] + 0.5
T = FADE + 0.4
STARTS = [s0, s1, s2, s3, s4, s5, s6]
NF = int(round(T * FPS))
KEY = [["prisonnier", "paire"], ["10", "noires", "blanches", "mélangées"], ["noir"],
       ["11", "sourit"], ["sûr", "paire", "2", "3", "11"], ["commentaire"], ["2e"]]
TORCH = [(300, 500), (780, 500)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

CHAR['GARDE2'] = dict(x=540, col=(80, 150, 230), hair=(130, 80, 40), style='short', skin=(226, 170, 124))
T_N = wtime(1, 'noires'); T_B = wtime(1, 'blanches'); T_MIX = wtime(1, 'mélangées')
T_NOIR = wtime(2, 'noir')
T_FAUX = wtime(3, '11')
T_SOURIT = wtime(3, 'sourit')
T_REP = wtime(6, '2e')
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

def sock(d, x, y, s, black, rot=0.0):
    """chaussette en L : tige verticale + pied vers la droite"""
    col = (24, 22, 28) if black else (245, 242, 236)
    ol = (200, 190, 200) if black else (30, 22, 28)
    pts = [(-14, -44), (14, -44), (14, 12), (30, 12), (34, 30), (26, 44), (-6, 44), (-14, 32)]
    c, sn = math.cos(rot), math.sin(rot)
    P = [(x + s * (px_ * c - py_ * sn), y + s * (px_ * sn + py_ * c)) for px_, py_ in pts]
    d.polygon(P, fill=col, outline=ol)
    d.line([P[0], P[1]], fill=(200, 60, 60) if black else (90, 150, 230), width=max(2, int(6 * s)))

def sock_home(k):
    """position de départ de la chaussette k (0-9 noires, 10-19 blanches)"""
    black = k < 10; j = k % 10
    x0 = 70 if black else 590
    return x0 + 18 + (j % 5) * 84, 560 + (j // 5) * 100, black

def crate(d, front=True):
    x0, x1 = CRX - 190, CRX + 190
    if not front:
        d.rounded_rectangle([x0 + 10, CRY - 30, x1 - 10, CRY + 20], radius=10, fill=(40, 26, 20))
        return
    d.rounded_rectangle([x0, CRY, x1, CRY + 200], radius=14, fill=(120, 76, 42), outline=(30, 18, 12), width=6)
    for k in range(1, 4):
        d.line([x0 + 6, CRY + k * 50, x1 - 6, CRY + k * 50], fill=(90, 56, 30), width=5)
    d.rectangle([x0 + 20, CRY + 4, x0 + 40, CRY + 196], fill=(96, 60, 32))
    d.rectangle([x1 - 40, CRY + 4, x1 - 20, CRY + 196], fill=(96, 60, 32))
    f = F(46); tw = d.textlength("CAISSE", font=f)
    d.rounded_rectangle([CRX - tw / 2 - 16, CRY + 70, CRX + tw / 2 + 16, CRY + 130], radius=12, fill=(250, 240, 220))
    d.text((CRX, CRY + 101), "CAISSE", font=f, fill=(30, 20, 26), anchor='mm')

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
    ('PRISONNIER', "11 !", lambda: T_FAUX - 0.05, lambda: s4 + 0.3, 330, 770, 280),
    ('GARDIEN', "Tu es sûr ?", lambda: T_SOURIT, lambda: s4 + 0.6, 780, 770, 840),
]

def cam(t):
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
    for hh, amp in [(0.0, 14), (T_MIX + 0.5, 8), (T_NOIR, 10), (T_FAUX, 8), (STAMP, 16)]:
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

def darkness(t):
    """0 = éclairé, 1 = noir"""
    if t < T_NOIR - 0.15: return 0.0
    if t < s4: return 0.62 * clamp((t - (T_NOIR - 0.15)) / 0.2)
    return 0.62 * (1 - clamp((t - s4) / 0.4)) + 0.25 * clamp((t - s4) / 0.4)

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['rdark'], G['rlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # personnages
    pm = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    mood = -1 if t < T_FAUX - 0.6 else 0
    for nm, x in [('GARDIEN', XG), ('PRISONNIER', XP)]:
        if nm == 'PRISONNIER':
            im = draw_person(nm, t, pm, (t % 3.2) < 0.12, mood, label='PRISONNIER')
        else:
            im = draw_person(nm, t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0, label='GARDIEN')
        img.alpha_composite(im, (int(x - 150), PY))
    d = ImageDraw.Draw(img)
    crate(d, front=False)
    # chaussettes : apparition (noires puis blanches), vol vers la caisse au mot « mélangées »
    for k in range(20):
        hx, hy, black = sock_home(k)
        tin = (T_N - 0.25 + (k % 10) * 0.03) if black else (T_B - 0.25 + (k % 10) * 0.03)
        if t < tin: continue
        u = ease_back((t - tin) / 0.25)
        tf = T_MIX - 0.1 + ((k * 7) % 20) * 0.025
        if t < tf:
            sock(d, hx, hy, 0.9 * clamp(u, 0, 1.2), black)
        else:
            v = clamp((t - tf) / 0.45)
            tx_ = CRX - 120 + ((k * 37) % 240); ty_ = CRY + 20
            x = hx + (tx_ - hx) * v; y = hy + (ty_ - hy) * v - 220 * math.sin(math.pi * v)
            if v < 1: sock(d, x, y, 0.9 - 0.2 * v, black, rot=v * 6 + k)
    if t >= T_MIX + 0.3:
        # tas mélangé qui dépasse de la caisse
        rr = random.Random(3)
        for k in range(9):
            sock(d, CRX - 150 + k * 37, CRY + 6 - rr.randint(0, 22), 0.75, k % 2 == 0, rot=rr.uniform(-0.9, 0.9))
    crate(d, front=True)
    # étiquettes 10 NOIRES / 10 BLANCHES
    if T_N - 0.25 <= t < T_MIX + 0.2:
        badge(d, 280, 760, "10 NOIRES", ease_back((t - (T_N - 0.25)) / 0.3), fill=(30, 26, 34), tcol=(255, 255, 255), size=52)
    if T_B - 0.25 <= t < T_MIX + 0.2:
        badge(d, 800, 760, "10 BLANCHES", ease_back((t - (T_B - 0.25)) / 0.3), fill=(245, 242, 236), size=52)
    # dès le début : définition de la paire
    if HOOK_UP <= t < T_MIX - 0.15:
        badge(d, 540, 470, "PAIRE = 2 DE MÊME COULEUR", ease_back((t - HOOK_UP) / 0.3), fill=(255, 206, 40), size=50)
    if T_MIX - 0.15 <= t < T_NOIR - 0.15:
        badge(d, 540, 470, "TOUT EST MÉLANGÉ", ease_back((t - (T_MIX - 0.15)) / 0.3), fill=(255, 206, 40), size=58)
    # obscurité
    k = darkness(t)
    if k > 0:
        dark = Image.new('RGBA', (W, H), (4, 2, 8, int(255 * k)))
        img.alpha_composite(dark)
        d = ImageDraw.Draw(img)
    if T_NOIR - 0.15 <= t < CE:
        badge(d, 540, 470, "DANS LE NOIR", ease_back((t - (T_NOIR - 0.15)) / 0.3), fill=(20, 16, 40), tcol=(255, 255, 255), size=62)
        # chaussettes « ? » qui sortent de la caisse
        if t < s4 + 0.3:
            for j in range(3):
                tj = T_NOIR + j * 0.3
                if t >= tj:
                    v = clamp((t - tj) / 0.35)
                    xx = CRX - 110 + j * 110; yy = CRY - 30 - 160 * ss(v)
                    d.ellipse([xx - 44, yy - 44, xx + 44, yy + 44], fill=(70, 66, 80), outline=(20, 12, 18), width=5)
                    d.text((xx, yy + 2), "?", font=F(62), fill=(255, 255, 255), anchor='mm')
    if s4 <= t < CE:
        badge(d, 500, 740, "COMBIEN POUR ÊTRE SÛR ?", ease_back((t - s4) / 0.3) * (1 + 0.05 * math.sin(t * 8)), fill=RED, tcol=(255, 255, 255), size=54)
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
    d.text((W / 2, y - 40), "ÉCRIS 2, 3 OU 11", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

CHN = [('2', 'CHAUSSETTES', '2'), ('3', 'CHAUSSETTES', '3'), ('11', 'CHAUSSETTES', '11')]
CHC = [(255, 150, 40), (80, 150, 230), (180, 110, 230)]
def choices(img, d, t):
    if not (wtime(4, 'premier') - 0.3 <= t < ANS): return
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

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['ddark'], G['dlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    off = (t * 520) % 140
    for k in range(10):
        x = k * 140 - off
        d.line([x, FLOOR + 22, x - 60, 1262], fill=(48, 36, 46), width=6)
    for nm, x, ph, lab in [('GARDE2', 200, 0.0, 'GARDE'), ('GARDIEN', 880, 1.3, 'GARDE'), ('PRISONNIER', 540, 2.1, 'PRISONNIER')]:
        bob = -abs(math.sin(t * 9 + ph)) * 16
        im = draw_person(nm, t + ph, 0, (t % 3.1) < 0.12, 1 if nm == 'PRISONNIER' and t >= T_REP else 0, label=lab)
        img.alpha_composite(im, (int(x - 150), int(PY + bob)))
    d = ImageDraw.Draw(img)
    u = ease_back((t - (ANS + 0.1)) / 0.3)
    place_tag(d, 880, 800, "1ER", (210, 70, 60), u)
    place_tag(d, 540, 800, "2E", GREEN, u * (1 + (0.12 * math.sin(t * 10) if t >= T_REP else 0)))
    place_tag(d, 200, 800, "3E", (80, 150, 230), u)
    if t >= T_REP:
        v = ease_back((t - T_REP) / 0.3)
        badge(d, 540, 470, "2E !", v, fill=GREEN, tcol=(255, 255, 255), size=90)
        badge(d, 540, 620, "PAS PREMIER : IL PREND SA PLACE", clamp((t - T_REP - 0.3) / 0.3), fill=(255, 206, 40), size=46)
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

