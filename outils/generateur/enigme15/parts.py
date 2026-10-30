def clamp(x, a=0, b=1): return max(a, min(b, x))
def ss(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def glow_layer(strength):
    arr = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for (tx, ty) in TORCH:
        dd = np.sqrt((xx - tx) ** 2 + ((yy - ty + 20) * 0.9) ** 2)
        g = np.exp(-(dd / 330.0) ** 2) * strength
        arr[..., 0] += g * 255; arr[..., 1] += g * 150; arr[..., 2] += g * 60
    dd = np.sqrt((xx - 540) ** 2 + (yy - 820) ** 2)
    g = np.exp(-(dd / 520.0) ** 2) * strength * 0.35
    arr[..., 0] += g * 255; arr[..., 1] += g * 170; arr[..., 2] += g * 90
    return arr

def vignette(col=(0, 0, 0), power=2.2, amt=0.85):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dd = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = np.clip(dd ** power, 0, 1) * amt
    img = np.zeros((H, W, 4), np.uint8); img[..., :3] = col; img[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')

def grad_band(y0, y1, peak, top_solid=False):
    img = np.zeros((H, W, 4), np.uint8)
    for y in range(y0, y1):
        u = (y - y0) / (y1 - y0)
        a = (1 - u) if top_solid else math.sin(math.pi * u) ** 0.7
        img[y, :, 3] = int(255 * peak * a)
    img[..., :3] = (12, 8, 14)
    return Image.fromarray(img, 'RGBA')

def stamp_img(text, col, size, w_pad=26, rot=-12):
    f = F(size)
    tmp = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    tw = tmp.textlength(text, font=f)
    w, h = int(tw + w_pad * 2), int(size * 1.45)
    im = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w * 2 - 6, h * 2 - 6], radius=18, outline=col + (255,), width=12)
    d.text((w, h), text, font=F(size * 2), fill=col + (255,), anchor='mm')
    return im.resize((w, h), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)


def silhouette():
    S = 2
    im = Image.new('RGBA', (460 * S, 700 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = (255, 140, 40, 255); b = (14, 10, 16, 255)
    d.ellipse([60 * S, 380 * S, 460 * S, 900 * S], fill=o)
    d.ellipse([66 * S, 386 * S, 454 * S, 894 * S], fill=b)
    d.ellipse([130 * S, 120 * S, 390 * S, 400 * S], fill=o)
    d.ellipse([136 * S, 126 * S, 384 * S, 394 * S], fill=b)
    d.rectangle([80 * S, 600 * S, 460 * S, 700 * S], fill=b)
    return im.resize((460, 700), Image.LANCZOS)

def flame(d, x, y, t, k):
    fl = 1 + 0.18 * math.sin(t * 23 + k) + 0.1 * math.sin(t * 37 + 2 * k)
    hh = 70 * fl
    d.polygon([(x - 22, y + 8), (x - 16, y - hh * 0.4), (x + math.sin(t * 15 + k) * 8, y - hh), (x + 16, y - hh * 0.45), (x + 22, y + 8)], fill=(255, 140, 40))
    d.polygon([(x - 11, y + 6), (x - 7, y - hh * 0.3), (x + math.sin(t * 17 + k) * 4, y - hh * 0.65), (x + 7, y - hh * 0.3), (x + 11, y + 6)], fill=(255, 226, 120))

def text_stroke(d, xy, txt, f, fill, stroke=(10, 6, 12), sw=6, anchor='mm'):
    d.text(xy, txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def wrap(d, text, f, maxw):
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        tst = (cur + ' ' + w_).strip()
        if d.textlength(tst, font=f) <= maxw: cur = tst
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def norm(w_):
    return w_.lower().strip(".,!?:;…'’«»").replace("qu'", '').replace("n'", '').replace("c'", '').replace("l'", '').replace("d'", '')

def word_times(i):
    words = SUBS[i].split()
    wts = [len(w_) + 3 + (6 if w_.rstrip('»')[-1] in '.,!?:…' else 0) for w_ in words]
    tot = sum(wts); acc = 0; out = []
    for w_, wt in zip(words, wts):
        out.append(STARTS[i] + D[i] * acc / tot * 0.95); acc += wt
    return words, out
WT = [word_times(i) for i in range(NL)]
def wtime(i, word, nth=0):
    ws, ts = WT[i]; c = 0
    for w_, tt in zip(ws, ts):
        if norm(w_) == word:
            if c == nth: return tt
            c += 1
    return STARTS[i]

def chunks(words, d, f, maxw):
    res = []; cur = []
    for k, w_ in enumerate(words):
        test = cur + [k]
        lines = wrap(d, ' '.join(words[j] for j in test), f, maxw)
        if len(lines) > 2 or (cur and words[cur[-1]].rstrip('»')[-1] in '.!?…' and len(cur) >= 2):
            res.append(cur); cur = [k]
        else: cur = test
    if cur: res.append(cur)
    return res

def draw_subs(img, d, t):
    f = F(64)
    for i in range(NL):
        st = STARTS[i]; en = st + D[i] + GAP
        if i == 5: en = ANS - 0.05
        if i == 4: en = CS + 0.6
        if i == 6: en = T + 1
        if not (st - 0.001 <= t < en) and not (i == 0 and t < 0.001): continue
        words, times = WT[i]
        grp = chunks(words, d, f, 900)
        cur = 0
        for gi, g in enumerate(grp):
            if t >= times[g[0]] - 0.02: cur = gi
        g = grp[cur]
        vis = [k for k in g if t >= times[k] - 0.02 or k == g[0] or (i == 0 and cur == 0)]
        lines = wrap(d, ' '.join(words[k] for k in g), f, 900)
        idx = 0; y = 1450 if len(lines) == 2 else 1480
        for li, ln in enumerate(lines):
            lw = ln.split(); total = d.textlength(ln, font=f) + 12 * (len(lw) - 1)
            x = W / 2 - total / 2
            for w_ in lw:
                k = g[idx]; idx += 1
                ww = d.textlength(w_, font=f)
                if k in vis:
                    age = t - times[k]
                    sc = 1 + 0.12 * max(0, 1 - age / 0.15) if age > 0 else 1
                    col = (255, 214, 50) if norm(w_) in KEY[i] else (255, 255, 255)
                    text_stroke(d, (x + ww / 2, y + li * 82), w_, F(int(64 * sc)), col, sw=6)
                x += ww + d.textlength(' ', font=f) + 12


def draw_person(name, t, mouth, blink, mood=0, label=None):
    """mood : 0 neutre, 1 sourire en coin (suspect), -1 inquiet"""
    c = CHAR[name]
    S = 2; w, h = 300, 560
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = c['col']; skin = c['skin']; hair = c['hair']
    br = math.sin(t * 2 * math.pi / 3.0 + c['x']) * 4
    cx = w // 2; hy = 230 + br * 0.5
    by0 = 320 + br
    if c['style'] == 'long':
        d.rounded_rectangle([(cx - 92) * S, (hy - 60) * S, (cx + 92) * S, (hy + 150) * S], radius=50 * S, fill=hair)
    d.rounded_rectangle([(cx - 110) * S, by0 * S, (cx + 110) * S, (h + 40) * S], radius=60 * S, fill=tuple(int(v * 0.75) for v in col))
    d.polygon([(cx - 46) * S, by0 * S, (cx + 46) * S, by0 * S, cx * S, (by0 + 60) * S], fill=skin)
    # plaque nominative
    plate = label if label is not None else name
    fs = 40 if len(plate) > 2 else 60
    if len(plate) > 7: fs = 32
    tw = d.textlength(plate, font=F(fs * S)) / S
    d.rounded_rectangle([(cx - tw / 2 - 18) * S, (by0 + 82) * S, (cx + tw / 2 + 18) * S, (by0 + 150) * S], radius=14 * S, fill=(250, 240, 220), outline=col, width=6 * S)
    d.text((cx * S, (by0 + 117) * S), plate, font=F(fs * S), fill=(30, 20, 26), anchor='mm')
    d.rectangle([(cx - 26) * S, (hy + 50) * S, (cx + 26) * S, (hy + 92) * S], fill=tuple(int(v * 0.88) for v in skin))
    d.ellipse([(cx - 80) * S, (hy - 80) * S, (cx + 80) * S, (hy + 80) * S], fill=skin)
    d.chord([(cx - 84) * S, (hy - 88) * S, (cx + 84) * S, (hy + 40) * S], 180, 360, fill=hair)
    for k in range(5):
        xx = cx - 70 + k * 35
        d.ellipse([(xx - 22) * S, (hy - 70) * S, (xx + 22) * S, (hy - 34) * S], fill=hair)
    if c['style'] == 'bun':
        d.ellipse([(cx - 36) * S, (hy - 130) * S, (cx + 36) * S, (hy - 62) * S], fill=hair)
    if c['style'] == 'long':
        d.chord([(cx - 84) * S, (hy - 86) * S, (cx + 20) * S, (hy - 10) * S], 180, 360, fill=hair)
    # sourcils
    for sgn in (-1, 1):
        x0 = cx + sgn * 44; x1 = cx + sgn * 14
        if mood == 1 and sgn == 1: d.line([x0 * S, (hy - 36) * S, x1 * S, (hy - 24) * S], fill=(50, 30, 24), width=9 * S)
        elif mood == 1: d.line([x0 * S, (hy - 26) * S, x1 * S, (hy - 28) * S], fill=(50, 30, 24), width=9 * S)
        elif mood == -1: d.line([x0 * S, (hy - 26) * S, x1 * S, (hy - 38) * S], fill=(50, 30, 24), width=9 * S)
        else: d.line([x0 * S, (hy - 22) * S, x1 * S, (hy - 30) * S], fill=(50, 30, 24), width=9 * S)
    for sgn in (-1, 1):
        ex = cx + sgn * 30; ey = hy - 2
        if blink:
            d.line([(ex - 10) * S, ey * S, (ex + 10) * S, ey * S], fill=(30, 20, 20), width=5 * S)
        else:
            d.ellipse([(ex - 13) * S, (ey - 13) * S, (ex + 13) * S, (ey + 13) * S], fill=(255, 255, 255))
            d.ellipse([(ex - 7) * S, (ey - 8) * S, (ex + 7) * S, (ey + 8) * S], fill=(30, 20, 20))
    d.ellipse([(cx - 10) * S, (hy + 10) * S, (cx + 12) * S, (hy + 28) * S], fill=tuple(int(v * 0.9) for v in skin))
    my = hy + 48
    if mouth >= 0.08:
        oh = 6 + mouth * 24
        d.ellipse([(cx - 20) * S, (my - oh / 2) * S, (cx + 20) * S, (my + oh / 2) * S], fill=(70, 22, 26))
    elif mood == 1:
        d.arc([(cx - 10) * S, (my - 22) * S, (cx + 34) * S, (my + 8) * S], 20, 150, fill=(70, 30, 30), width=6 * S)
    elif mood == -1:
        d.arc([(cx - 18) * S, (my - 2) * S, (cx + 18) * S, (my + 16) * S], 200, 340, fill=(70, 30, 30), width=5 * S)
    else:
        d.arc([(cx - 22) * S, (my - 10) * S, (cx + 22) * S, (my + 8) * S], 20, 160, fill=(70, 30, 30), width=5 * S)
    return im.resize((w, h), Image.LANCZOS)

def small_bubble(img, d, cx, cy, txt, col, u, n, tail_x=None, maxw=300):
    if u <= 0: return
    f = F(42)
    lines = wrap(d, txt, f, maxw)
    bw = max(d.textlength(l, font=f) for l in lines) + 50; bh = 36 + 54 * len(lines)
    sc = clamp(u, 0.01, 1.2)
    tx = cx if tail_x is None else tail_x
    def S(x, y): return (cx + (x - cx) * sc, cy + (y - cy) * sc)
    x0, y0 = cx - bw / 2, cy - bh / 2
    p0, p1 = S(x0, y0), S(x0 + bw, y0 + bh)
    d.rounded_rectangle([p0[0] - 6, p0[1] - 6, p1[0] + 6, p1[1] + 6], radius=30, fill=col)
    d.polygon([S(tx - 22, y0 + bh), S(tx + 22, y0 + bh), S(tx - 6, y0 + bh + 46)], fill=col)
    d.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]], radius=26, fill=(255, 255, 255))
    d.polygon([S(tx - 13, y0 + bh - 3), S(tx + 13, y0 + bh - 3), S(tx - 3, y0 + bh + 32)], fill=(255, 255, 255))
    if u > 0.9:
        shown = 0
        for li, ln in enumerate(lines):
            part = ln[:max(0, n - shown)]; shown += len(ln) + 1
            d.text((cx - d.textlength(ln, font=f) / 2, y0 + 18 + 27 + li * 54), part, font=f, fill=(30, 20, 26), anchor='lm')


def mouth_env(i):
    v, sr = sf.read(f'v{i}.wav')
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(v[k:k + hop] ** 2)) for k in range(0, len(v), hop)])
    return e / (e.max() + 1e-9)


def badge(d, x, y, txt, u, fill=(255, 206, 40), tcol=(24, 14, 20), size=44):
    if u <= 0: return
    f = F(size * clamp(u, 0.05, 1.2)); tw = d.textlength(txt, font=f)
    h = size * 0.75 * clamp(u, 0.05, 1.2)
    if h < 8: return
    d.rounded_rectangle([x - tw / 2 - 20, y - h, x + tw / 2 + 20, y + h], radius=int(h), fill=(16, 10, 16))
    d.rounded_rectangle([x - tw / 2 - 16, y - h + 4, x + tw / 2 + 16, y + h - 4], radius=int(h) - 4, fill=fill)
    d.text((x, y + 2), txt, font=f, fill=tcol, anchor='mm')


def camera(img, t):
    z, cx, cy = cam(t)
    sx, sy = shake(t)
    if CS <= t < CE:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
        z *= 1 + 0.012 * math.exp(-ph * 9)
    cx = clamp(cx + sx, W / 2 / z, W - W / 2 / z); cy = cy + sy
    a = 1 / z; c = cx - (W / 2) / z; e = 1 / z; fy = cy - cy / z
    return img.transform((W, H), Image.AFFINE, (a, 0, c, 0, e, fy), resample=Image.BILINEAR)


def chrono(img, d, t):
    if not (CS <= t < CE + 0.3): return
    rem = max(0, CE - t); frac = rem / CHR
    ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
    beat = 1 + 0.08 * math.exp(-ph * 8)
    cx, cy, r = 905, 600, int(82 * beat)
    d.ellipse([cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16], fill=(16, 10, 16, 235))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(70, 50, 60), width=18)
    col = (255, 206, 40) if rem > 2.5 else (255, 60, 50)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=col, width=18)
    d.text((cx, cy + 4), str(int(math.ceil(rem))) if rem > 0 else "0", font=F(int(90 * beat)), fill=(255, 255, 255), anchor='mm')

def red_vig(img, t):
    if CS <= t < CE + 0.5:
        ph = ((t - CS) * (1.2 + (t - CS) * 0.25)) % 1
        a = (0.25 + 0.55 * (t - CS) / CHR) * (0.6 + 0.4 * math.exp(-ph * 6))
        if t > CE: a *= max(0, 1 - (t - CE) / 0.5)
        r = G['red'].copy(); r.putalpha(r.getchannel('A').point(lambda v: int(v * clamp(a))))
        img.alpha_composite(r)


CHAR = {
    'LÉA': dict(x=200, col=(230, 110, 160), hair=(50, 30, 26), style='long', skin=(226, 170, 124)),
    'HUGO': dict(x=540, col=(80, 150, 230), hair=(130, 80, 40), style='short', skin=(206, 150, 106)),
    'NINA': dict(x=880, col=(90, 200, 120), hair=(190, 80, 40), style='bun', skin=(236, 186, 140)),
    'GARDIEN': dict(x=190, col=(210, 70, 60), hair=(40, 30, 30), style='short', skin=(206, 150, 106)),
    'PRISONNIER': dict(x=440, col=(200, 130, 70), hair=(70, 44, 30), style='short', skin=(220, 166, 120)),
    'MÈRE': dict(x=180, col=(230, 110, 160), hair=(70, 40, 30), style='long', skin=(230, 176, 130)),
    'DÉTECTIVE': dict(x=900, col=(80, 150, 230), hair=(40, 30, 30), style='short', skin=(206, 150, 106)),
    'F1': dict(x=400, col=(250, 170, 60), hair=(150, 80, 40), style='bun', skin=(236, 186, 140)),
    'F2': dict(x=540, col=(180, 110, 230), hair=(60, 36, 28), style='long', skin=(226, 170, 124)),
    'F3': dict(x=680, col=(90, 200, 120), hair=(190, 80, 40), style='short', skin=(220, 166, 120)),
    'A': dict(x=330, col=(180, 110, 230), hair=(60, 36, 28), style='short', skin=(226, 170, 124)),
    'B': dict(x=750, col=(90, 190, 120), hair=(150, 70, 40), style='short', skin=(226, 170, 124)),
}

G = {}
