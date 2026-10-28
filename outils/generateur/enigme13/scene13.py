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
