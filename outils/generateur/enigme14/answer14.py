CHN = [('24', 'JOUR'), ('46', 'JOUR'), ('47', 'JOUR')]
def choices(img, d, t):
    T0 = wtime(4, '24') - 0.2
    if not (T0 - 0.05 <= t < ANS): return
    for k, (big, small) in enumerate(CHN):
        col = CHC[k]
        ts = wtime(4, big) - 0.15
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
            d.text((x, y + 22 * s), big, font=F(84 * s), fill=(255, 255, 255), anchor='mm')
            d.text((x, y - 44 * s), small, font=F(38 * s), fill=col, anchor='mm')

def answer_frame(t):
    f = 0.5 + 0.22 * math.sin(t * 7.1) + 0.12 * math.sin(t * 13.7 + 1)
    img = Image.blend(G['adark'], G['alit'], clamp(f)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for k, (tx, ty) in enumerate(TORCH): flame(d, tx, ty + 8, t, k * 3)
    # table : batte + balle avec prix
    TX0, TX1, TY = 300, 780, 1040
    d.rectangle([TX0 + 30, TY, TX0 + 60, TY + 200], fill=(70, 44, 26)); d.rectangle([TX1 - 60, TY, TX1 - 30, TY + 200], fill=(70, 44, 26))
    d.rounded_rectangle([TX0, TY - 26, TX1, TY + 16], radius=10, fill=(128, 82, 46))
    x, y = 430, 995; k = 1.25
    pts = [(x + k * a, y + k * b) for a, b in [(-120, 14), (-118, -4), (20, -30), (120, -44), (132, -22), (122, 4), (20, 6)]]
    d.polygon(pts, fill=(196, 140, 80), outline=(60, 36, 20))
    bx, by, r = 680, 966, 46
    d.ellipse([bx - r - 4, by - r - 4, bx + r + 4, by + r + 4], fill=(40, 26, 18)); d.ellipse([bx - r, by - r, bx + r, by + r], fill=(245, 240, 230))
    d.arc([bx - r - 18, by - r, bx - 6, by + r], -60, 60, fill=(210, 40, 40), width=6); d.arc([bx + 6, by - r, bx + r + 18, by + r], 120, 240, fill=(210, 40, 40), width=6)
    got = t >= T_REP
    if got:
        u = ease_back((t - T_REP) / 0.3)
        badge(d, 540, 470, "5 CENTIMES !", u, fill=GREEN, tcol=(255, 255, 255), size=80)
        badge(d, 680, 870, "0,05 €", clamp((t - T_REP - 0.3) / 0.3), fill=(245, 240, 230), size=52)
        badge(d, 400, 870, "1,05 €", clamp((t - T_REP - 0.5) / 0.3), fill=(196, 140, 80), size=52)
        badge(d, 540, 640, "1,05 + 0,05 = 1,10 €", clamp((t - T_REP - 0.8) / 0.3), fill=(255, 206, 40), size=50)
    img.alpha_composite(G['sil'], (-70, 1250))
    return img
