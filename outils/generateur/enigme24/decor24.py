def wall(S):
    """cour du cachot : mur de pierre brun-violet, sol de terre, torches (retour au donjon, T19 abandonné)"""
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
    # bande de terre où planter la clôture
    d.rectangle([0, FGND * S, W * S, (FGND + 26) * S], fill=(74, 52, 38))
    d.rectangle([0, (FGND + 26) * S, W * S, FLOOR * S], fill=(52, 38, 40))
    d.rectangle([0, FLOOR * S, W * S, H * S], fill=(26, 18, 25))
    for i in range(22):
        yy = (FLOOR + 20 + i * 48) * S
        d.line([0, yy, W * S, yy], fill=(36, 26, 34), width=3 * S)
    d.rectangle([0, 0, W * S, 330 * S], fill=(22, 15, 22))
    for (tx, ty) in TORCH:
        d.polygon([(tx - 18) * S, (ty + 20) * S, (tx + 18) * S, (ty + 20) * S, (tx + 8) * S, (ty + 110) * S, (tx - 8) * S, (ty + 110) * S], fill=(70, 46, 30))
        d.rounded_rectangle([(tx - 26) * S, (ty + 8) * S, (tx + 26) * S, (ty + 30) * S], radius=6 * S, fill=(96, 66, 40))
    return im

def bracket(d, x0, x1, y, txt, u, col, size=46):
    if u <= 0: return
    m = (x0 + x1) / 2; h = (x1 - x0) / 2 * clamp(u, 0, 1)
    d.line([(m - h, y), (m + h, y)], fill=(16, 10, 16), width=12)
    d.line([(m - h, y), (m + h, y)], fill=col, width=6)
    for xx in (m - h, m + h):
        d.line([(xx, y - 18), (xx, y + 18)], fill=(16, 10, 16), width=12)
        d.line([(xx, y - 16), (xx, y + 16)], fill=col, width=6)
    badge(d, m, y - 46, txt, ease_back(u), fill=col, size=size)

def post(d, x, u, hi=False):
    if u <= 0: return
    h = (FGND + 10 - FTOP) * clamp(u, 0, 1.15)
    top = FGND + 10 - h
    col = (255, 206, 40) if hi else (168, 116, 66)
    d.polygon([(x - 13, top + 16), (x, top), (x + 13, top + 16), (x + 13, FGND + 10), (x - 13, FGND + 10)], fill=col, outline=(20, 12, 12))
    d.line([(x - 5, top + 24), (x - 5, FGND + 4)], fill=tuple(int(c * 0.8) for c in col), width=3)

def rails(d, u):
    if u <= 0: return
    xe = FX0 + (FX1 - FX0) * clamp(u)
    for y in (FTOP + 30, FTOP + 78):
        d.rectangle([FX0, y, xe, y + 14], fill=(130, 90, 54), outline=(20, 12, 12))

def fence_scene(d, t):
    if t < T_CLOT - 0.15: return
    rails(d, (t - (T_CLOT - 0.15)) / 0.5)
    if t < CE:
        bracket(d, FX0, FX1, 500, "10 MÈTRES", (t - (T_10M - 0.15)) / 0.35, (120, 200, 255), size=48)
    if t >= T_POTEAU - 0.15:
        u = ease_back((t - (T_POTEAU - 0.15)) / 0.3)
        hi = t >= T_BOUTS - 0.15
        post(d, FX0, u, hi); post(d, FX0 + MPX, ease_back((t - (T_POTEAU + 0.05)) / 0.3))
        if u > 0.5:
            text_stroke(d, (FX0 + MPX / 2, FTOP + 120), "1 M", F(36), (255, 255, 255), sw=5)
        if t < CE:
            badge(d, 540, 400, "1 POTEAU À CHAQUE MÈTRE", u, fill=(255, 140, 60), size=48)
    if t >= T_BOUTS - 0.15:
        u = ease_back((t - (T_BOUTS - 0.15)) / 0.3)
        post(d, FX1, u, True)
        if t < CE:
            badge(d, FX0 + 10, 548, "BOUT", u, fill=(255, 206, 40), size=34)
            badge(d, FX1 - 10, 548, "BOUT", u, fill=(255, 206, 40), size=34)
        for k, x in enumerate((370, 590, 810)):
            text_stroke(d, (x, FTOP + 62 + 6 * math.sin(t * 5 + k)), "?", F(int(80 * clamp(u, 0, 1.1)) + 1), (255, 214, 50), sw=7)

def answer_scene(d, t):
    """réponse #23 : le rail en 10 morceaux, 9 traits de coupe qui apparaissent un par un ; « 10 » barré en rouge (T22)"""
    rail_bar(d, t, show_pieces=True)
    pw = (BX1 - BX0) / 10
    for k in range(1, 10):
        tk = ANS + 0.15 + (k - 1) * 0.12
        if t >= tk:
            x = BX0 + k * pw
            d.line([(x, BY - 40), (x, BY + 40)], fill=(16, 10, 16), width=12)
            d.line([(x, BY - 38), (x, BY + 38)], fill=(255, 60, 50), width=6)
            if t - tk < 0.15:
                for a in range(6):
                    ang = -0.5 - a * 0.4
                    d.line([(x, BY - 30), (x + 40 * math.cos(ang), BY - 30 + 40 * math.sin(ang))], fill=(255, 200, 80), width=4)
    ncut = sum(1 for k in range(1, 10) if t >= ANS + 0.15 + (k - 1) * 0.12)
    if ncut > 0:
        badge(d, 540, 470, f"{ncut} COUPE" + ("S" if ncut > 1 else ""), 1, fill=(255, 140, 60), size=52)
    if t >= T_REP - 0.3:
        badge(d, 540, 800, "9 MINUTES !", ease_back((t - T_REP + 0.3) / 0.3), fill=GREEN, tcol=(255, 255, 255), size=96)
    tp = wtime(6, 'pas') - 0.15
    if t >= tp:
        u = ease_back((t - tp) / 0.3)
        badge(d, 540, 960, "10 MINUTES", u, fill=(150, 140, 150), tcol=(60, 50, 60), size=60)
        if t >= tp + 0.2:
            v = clamp((t - tp - 0.2) / 0.2)
            for (a, b) in [((330, 925), (750, 995)), ((330, 995), (750, 925))]:
                xe = (a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v)
                d.line([a, xe], fill=(16, 10, 16), width=22)
                d.line([a, xe], fill=RED, width=12)
            badge(d, 540, 1070, "10 MORCEAUX = 9 COUPES", v, fill=(255, 206, 40), size=46)
