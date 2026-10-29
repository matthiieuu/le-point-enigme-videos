T_DBL = wtime(1, 'doublent')
T_48 = wtime(2, '48')
T_FAUX = wtime(3, '24')
T_SOURIT = wtime(3, 'sourit')
T_REP = wtime(6, '5')
HOOK_END = 1.75; HOOK_UP = 2.25

CHAR['PRISONNIER']['x'] = 190
CHAR['GARDIEN']['x'] = 890
PY = 690
FLOOR = 930
LX, LY, LRX, LRY = 540, 1085, 300, 140   # lac (ellipse)

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
    if not doors:
        # lac souterrain : margelle de pierre + eau
        d.ellipse([(LX - LRX - 26) * S, (LY - LRY - 22) * S, (LX + LRX + 26) * S, (LY + LRY + 22) * S], fill=(96, 84, 92))
        d.ellipse([(LX - LRX) * S, (LY - LRY) * S, (LX + LRX) * S, (LY + LRY) * S], fill=(28, 70, 96))
        for k in range(6):
            yy = LY - LRY + 40 + k * 40; ww = LRX * 0.7 * (1 - abs(k - 2.5) / 4)
            d.line([(LX - ww) * S, yy * S, (LX - ww + 60) * S, yy * S], fill=(60, 120, 150), width=3 * S)
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

def draw_pads(d, n, pop_from=0, tpop=1.0):
    for k, (x, y) in enumerate(PADS[:n]):
        s = 1.0 if k < pop_from else clamp(tpop)
        r = 21 * s
        if r < 2: continue
        d.ellipse([x - r, y - r * 0.62, x + r, y + r * 0.62], fill=(70, 170, 80), outline=(30, 90, 40), width=2)
        d.polygon([(x, y), (x + r, y - r * 0.25), (x + r, y + r * 0.1)], fill=(28, 70, 96))
        if k % 7 == 0 and s > 0.8:
            d.ellipse([x - 6, y - 10, x + 6, y - 2], fill=(240, 150, 200))

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
    ('PRISONNIER', "Jour 24 !", lambda: T_FAUX - 0.05, lambda: s4 + 0.2, 300, 770, 210),
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
    for hh, amp in [(0.0, 14), (T_48 + 0.3, 12), (T_FAUX, 8), (STAMP, 16)]:
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

def lake_state(t):
    """(jour affiché, nb nénuphars, nb déjà là, avancement pop)"""
    if t < T_DBL - 0.1: return ('?', 1, 0, 1.0)
    if t < s2:
        step = (s2 - (T_DBL - 0.1)) / 4.2
        k = min(4, int((t - (T_DBL - 0.1)) / step))  # jours 1..5
        n = 2 ** k; prev = 2 ** (k - 1) if k else 0
        return (str(k + 1), n, prev, (t - (T_DBL - 0.1) - k * step) / 0.2)
    if t < T_48:
        return ('…', 16, 16, 1.0)
    return ('48', len(PADS), 16, (t - T_48) / 0.35)

def scene(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1) + 0.08 * math.sin(t * 29)
    img = Image.blend(G['ddark'], G['dlit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    day, n, prev, u = lake_state(t)
    draw_pads(d, n, prev, u)
    bl = (t % 3.2) < 0.12
    mp = mouth_at(3, t) if T_FAUX - 0.6 <= t < T_SOURIT - 0.1 else 0
    pm = -1 if t < T_FAUX - 0.6 else 0
    img.alpha_composite(draw_person('PRISONNIER', t, mp, bl, pm), (CHAR['PRISONNIER']['x'] - 150, PY))
    img.alpha_composite(draw_person('GARDIEN', t + 1, 0, (t % 2.9) < 0.12, 1 if t >= T_SOURIT else 0), (CHAR['GARDIEN']['x'] - 150, PY))
    d = ImageDraw.Draw(img)
    for k in range(7):
        cx = CHAR['PRISONNIER']['x'] - 90 + k * 16; cy = PY + 470 + (k % 2) * 6
        d.ellipse([cx - 10, cy - 7, cx + 10, cy + 7], outline=(150, 150, 160), width=4)
    # compteur de jours au-dessus du lac
    pul = 1 + 0.12 * max(0, 1 - ((t - T_DBL) % 0.4) / 0.15) if T_DBL <= t < s2 else 1
    if t >= T_48: pul = 1 + 0.2 * max(0, 1 - (t - T_48) / 0.2)
    badge(d, LX, 905, f"JOUR {day}", min(1.15, ease_back((t - 0.6) / 0.3) * pul) if t >= 0.6 else 0,
          fill=(255, 206, 40) if day != '48' else GREEN, tcol=(24, 14, 20), size=54)
    if t >= T_DBL - 0.1:
        badge(d, 540, 450, "× 2 CHAQUE JOUR", ease_back((t - (T_DBL - 0.1)) / 0.3), fill=(80, 150, 230), tcol=(255, 255, 255), size=56)
    if t >= T_48:
        badge(d, 540, 570, "JOUR 48 = TOUT COUVERT", ease_back((t - T_48) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=52)
    if s4 <= t < CE:
        badge(d, 540, 690, "MOITIÉ = QUEL JOUR ?", ease_back((t - s4) / 0.3) * (1 + 0.05 * math.sin(t * 8)), fill=RED, tcol=(255, 255, 255), size=52)
    d = ImageDraw.Draw(img)
    for (who, txt, t0f, t1f, cx, cy, tx) in BUBS:
        t0, t1 = t0f(), t1f()
        if t0 <= t < t1:
            small_bubble(img, d, cx, cy, txt, CHAR[who]['col'], ease_back((t - t0) / 0.25), int((t - t0 - 0.15) * 30), tail_x=tx, maxw=380)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img
