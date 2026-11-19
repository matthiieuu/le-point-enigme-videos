# Vérification par calcul/simulation des énigmes #30-#33 (banque ajoutée le 19/11/2026)
from fractions import Fraction as Fr

def unique(nom, choix, ok):
    bons = [c for c in choix if ok(c)]
    assert len(bons) == 1, (nom, bons)
    print(nom, '->', bons[0])
    return bons[0]

# #30 LA GRENOUILLE DU PUITS : puits de 20 m, +5 m le jour, -4 m la nuit. Jour de sortie ?
def sortie(h=20, up=5, down=4):
    pos, jour = 0, 0
    while True:
        jour += 1; pos += up
        if pos >= h: return jour
        pos -= down
assert unique('#30 grenouille', [20, 16, 15], lambda c: c == sortie()) == 16

# #31 LES BACTÉRIES : doublent chaque minute ; 1 bactérie remplit le bocal en 60 min. Avec 2 au départ ?
def minutes(depart, plein=2 ** 60):
    n, m = depart, 0
    while n < plein: n *= 2; m += 1
    return m
assert minutes(1) == 60
assert unique('#31 bactéries', [30, 59, 60], lambda c: c == minutes(2)) == 59

# #32 LE LIVRE : il coûte 10 € plus la moitié de son prix. Prix ?
assert unique('#32 livre', [15, 20, 10], lambda c: Fr(c) == 10 + Fr(c, 2)) == 20

# #33 LE CHEVAL : achète 60, vend 70, rachète 80, revend 90. Gain total ?
gain = -60 + 70 - 80 + 90
assert unique('#33 cheval', [10, 20, 0], lambda c: c == gain) == 20
print('ok : solution unique parmi les choix')
