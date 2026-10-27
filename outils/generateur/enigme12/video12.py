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

NUM = "12"; TITRE = "LES 3 PORTES DU GARDIEN"; CONTRAINTE = "UNE SEULE PORTE = LA LIBERTÉ"
TITRE_HIER = "L'ÂGE DES TROIS FILLES"
HOOK = ["UNE SEULE", "PORTE", "LE LIBÈRE"]
CHR = 6.0
D = json.load(open('durees.json'))
SUBS = ["Une seule de ces 3 portes le libère !",
        "Derrière les 2 autres : un mur.",
        "Il choisit la porte 1. Le gardien, qui sait tout, ouvre la porte 3 : un mur !",
        "Puis il demande : tu gardes la porte 1, ou tu changes pour la 2 ?",
        "Alors : garder, changer, ou c'est pareil ?",
        "Écris un seul mot. Réponse demain !",
        "Réponse d'hier : 9 ans ! 2, 2 et 9."]
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
KEY = [["seule", "3", "portes", "libère"], ["2", "mur"], ["1", "gardien", "3", "mur"],
       ["gardes", "1", "changes", "2"], ["garder", "changer", "pareil"], ["mot", "demain"], ["9", "ans", "2"]]
TORCH = [(395, 500), (685, 500)]

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts.py')).read())

T_UN = wtime(2, '1')
T_OUVRE = wtime(2, 'ouvre')
T_MUR = wtime(2, 'mur')
T_GARDE = wtime(3, 'gardes')
T_REP = wtime(6, '9')
HOOK_END = 1.75; HOOK_UP = 2.25

CHAR['PRISONNIER']['x'] = 320
CHAR['GARDIEN']['x'] = 790
CHAR['F1']['x'] = 420; CHAR['F2']['x'] = 640; CHAR['F3']['x'] = 860
PY = 710
DOORS = [250, 540, 830]; DW = 210; DT = 440; DB = 850
FLOOR = 862

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
        for k, cx in enumerate(DOORS):
            x0, x1 = cx - DW / 2, cx + DW / 2
            # encadrement de pierre (arc)
            d.rounded_rectangle([(x0 - 26) * S, (DT - 30) * S, (x1 + 26) * S, (DB + 10) * S], radius=int(DW / 2 + 26) * S, fill=(96, 84, 92))
            d.rounded_rectangle([(x0 - 14) * S, (DT - 18) * S, (x1 + 14) * S, (DB + 10) * S], radius=int(DW / 2 + 14) * S, fill=(72, 62, 70))
            d.rounded_rectangle([x0 * S, (DT - 4) * S, x1 * S, DB * S], radius=int(DW / 2) * S, fill=(10, 6, 10))
            if k == 2:  # derrière la porte 3 : un mur de briques
                yy = DT + 30; r = 0
                while yy + 24 < DB:
                    off = 0 if r % 2 == 0 else 26
                    xx = x0 + 6 - off
                    while xx < x1 - 6:
                        a, b = max(xx, x0 + 8), min(xx + 50, x1 - 8)
                        if b - a > 8: d.rectangle([a * S, yy * S, (b - 4) * S, (yy + 22) * S], fill=(150, 64, 44))
                        xx += 52
                    yy += 26; r += 1
                d.rounded_rectangle([x0 * S, (DT - 4) * S, x1 * S, (DT + 60) * S], radius=int(DW / 2) * S, fill=(10, 6, 10))
    return im

def door_leaf(d, k, open_u, hi):
    cx = DOORS[k]; x0, x1 = cx - DW / 2 + 6, cx + DW / 2 - 6
    w = (x1 - x0) * (1 - 0.85 * open_u)
    xe = x0 + w
    shade = 1 - 0.45 * open_u
    wood = tuple(int(v * shade) for v in (128, 82, 46))
    dark = tuple(int(v * shade) for v in (92, 56, 30))
    r = int(min(w, DW) / 2)
    d.rounded_rectangle([x0, DT + 2, xe, DB - 2], radius=max(4, r), fill=wood, outline=(255, 150, 40) if hi else (40, 26, 18), width=8 if hi else 4)
    np_ = 4
    for j in range(1, np_):
        xx = x0 + w * j / np_
        d.line([xx, DT + 40, xx, DB - 6], fill=dark, width=4)
    for yy in (DT + 150, DB - 110):
        d.rectangle([x0 + 4, yy, xe - 4, yy + 18], fill=(50, 44, 48))
    if open_u < 0.3:
        d.ellipse([xe - 40, (DT + DB) / 2 + 20, xe - 22, (DT + DB) / 2 + 38], fill=(220, 180, 70))
        # numéro
        d.ellipse([cx - 44, DT + 56, cx + 44, DT + 144], fill=(250, 240, 220), outline=(40, 26, 18), width=5)
        d.text((cx, DT + 102), str(k + 1), font=F(66), fill=(30, 20, 26), anchor='mm')

def init():
    random.seed(1)
    for nm, im in [('d', wall(2, True)), ('a', wall(2, False))]:
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
    for i in (2, 3): G[f'env{i}'] = mouth_env(i)

BUBS = [  # (perso, texte, t0, t1, cx, cy, tail_x)
    ('PRISONNIER', "Je prends la 1 !", lambda: T_UN - 0.1, lambda: T_OUVRE - 0.1, 440, 790, 330),
    ('GARDIEN', "Tu gardes la 1… ou tu prends la 2 ?", lambda: s3 + 0.1, lambda: s4 + 0.4, 600, 770, 790),
]

def cam(t):
    keys = [(0, 1.10, 330, 1020), (0.4, 1.0, 540, 960), (s1, 1.0, 540, 960), (s1 + 0.5, 1.05, 540, 680), (s2 - 0.1, 1.05, 540, 680),
            (s2 + 0.3, 1.09, 330, 820), (T_OUVRE - 0.2, 1.09, 330, 820), (T_OUVRE + 0.25, 1.10, 760, 700), (s3 - 0.1, 1.10, 760, 700),
            (s3 + 0.3, 1.05, 620, 860), (s4 - 0.1, 1.05, 620, 860), (s4 + 0.4, 1.0, 540, 900),
            (CE, 1.06, 540, 860), (CE + 0.6, 1.03, 540, 900), (ANS, 1.03, 540, 900)]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ss((t - a[0]) / max(1e-6, b[0] - a[0]))
            if a[0] == 0: u = 1 - (1 - clamp((t - a[0]) / (b[0] - a[0]))) ** 3
            return tuple(a[k] + (b[k] - a[k]) * u for k in (1, 2, 3))
    return keys[-1][1:]

def shake(t):
    sx = sy = 0
    for hh, amp in [(0.0, 14), (T_MUR, 16), (STAMP, 16)]:
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
    op3 = ss((t - T_OUVRE) / 0.6) if T_OUVRE <= t < ANS else 0
    for k in range(3):
        hi = (k == 0 and T_UN <= t < ANS)
        door_leaf(d, k, op3 if k == 2 else 0, hi)
    if t >= T_MUR and t < ANS:
        u = ease_back((t - T_MUR) / 0.3)
        badge(d, DOORS[2], 600, "MUR", u, fill=RED, tcol=(255, 255, 255), size=46)
    if T_UN <= t < s3:
        u = ease_back((t - T_UN) / 0.3)
        badge(d, DOORS[0], 400, "SON CHOIX", u, fill=(255, 150, 40), size=46)
    if t >= T_GARDE - 0.1 and t < ANS:
        u0 = ease_back((t - (T_GARDE - 0.1)) / 0.3)
        badge(d, DOORS[0], 400, "GARDER ?", u0, fill=(255, 150, 40), size=46)
        u1 = ease_back((t - (T_GARDE + 0.5)) / 0.3)
        badge(d, DOORS[1], 400, "CHANGER ?", u1, fill=(80, 150, 230), tcol=(255, 255, 255), size=46)
    # personnages
    bl = (t % 3.2) < 0.12
    mp = mouth_at(2, t) if T_UN - 0.3 <= t < T_OUVRE - 0.3 else 0
    mg = mouth_at(3, t)
    img.alpha_composite(draw_person('PRISONNIER', t, mp, bl, -1), (CHAR['PRISONNIER']['x'] - 150, PY))
    img.alpha_composite(draw_person('GARDIEN', t + 1, mg, (t % 2.9) < 0.12, 1 if t >= T_OUVRE else 0), (CHAR['GARDIEN']['x'] - 150, PY))
    d = ImageDraw.Draw(img)
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
    d.text((W / 2, y - 40), "ÉCRIS UN SEUL MOT", font=f, fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, y + 44), "EN COMMENTAIRE", font=f, fill=(255, 214, 50), anchor='mm')
    if t >= STAMP:
        sc = 1 + 1.6 * max(0, 1 - (t - STAMP) / 0.13)
        st = G['rd']; s = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        img.alpha_composite(s, (int(W / 2 - s.width / 2), int(800 - s.height / 2)))

AGES = ['9', '2', '2']
def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['adark'], G['alit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    got = t >= T_REP
    img.alpha_composite(draw_person('MÈRE', t, 0, (t % 3.2) < 0.12, 1), (170 - 150, 760))
    for k, nm in enumerate(['F1', 'F2', 'F3']):
        sc = 0.78 if k == 0 else 0.6
        p = draw_person(nm, t + k, 0, ((t + k) % 3.4) < 0.12, 0, label=(AGES[k] if got else '?'))
        p = p.resize((int(p.width * sc), int(p.height * sc)), Image.LANCZOS)
        img.alpha_composite(p, (int(CHAR[nm]['x'] - p.width / 2), int(1320 - p.height)))
    d = ImageDraw.Draw(img)
    if got:
        u = ease_back((t - T_REP) / 0.3)
        badge(d, 620, 520, "9 ANS !", u, fill=GREEN, tcol=(255, 255, 255), size=72)
        badge(d, 620, 650, "2 × 2 × 9 = 36", clamp((t - T_REP - 0.4) / 0.3), fill=(240, 230, 210), size=40)
        badge(d, 620, 750, "2 + 2 + 9 = 13 = 1 + 6 + 6", clamp((t - T_REP - 0.8) / 0.3), fill=(240, 230, 210), size=32)
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
        print('T', T, 'CS', CS, 'ANS', ANS, 'starts', [round(x, 2) for x in STARTS], 'ouvre', T_OUVRE, 'mur', T_MUR)
    else:
        json.dump({'T': T, 'starts': STARTS, 'CS': CS, 'CE': CE, 'CHR': CHR, 'STAMP': STAMP, 'ANS': ANS, 'FADE': FADE, 'FAUXT': T_MUR, 'NF': NF}, open('timeline.json', 'w'))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'video_seule.mp4'], stdin=subprocess.PIPE)
        with mp.Pool(mp.cpu_count(), initializer=init) as pool:
            for k, b in enumerate(pool.imap(work, range(NF), chunksize=4)):
                p.stdin.write(b)
                if k % 150 == 0: print(k, NF, flush=True)
        p.stdin.close(); p.wait()
        print('ok')
