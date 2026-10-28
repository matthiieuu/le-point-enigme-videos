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
