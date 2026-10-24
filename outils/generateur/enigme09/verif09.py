# Vérifie #09 (escargot dans le puits 10 m, +3 le jour, -2 la nuit) et #08 (diamant)
def jours(h=10, up=3, down=2):
    pos, d = 0, 0
    while True:
        d += 1; pos += up
        if pos >= h: return d
        pos -= down
r = jours(); print('escargot : sort le jour', r); assert r == 8
assert [h for h in [7, 8, 10] if h == r] == [8]  # choix unique
sols = [v for v in ['Léa', 'Hugo', 'Nina'] if sum([v == 'Hugo', v != 'Hugo', v != 'Nina']) == 1]
assert sols == ['Nina']
print('OK : réponse #09 = 8 jours (B) ; réponse #08 = NINA')
