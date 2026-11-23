# Vérification de la banque ajoutée le 23/11 (#34-#37) : une seule bonne réponse parmi les 3 choix.
from fractions import Fraction as Fr
from itertools import permutations

def unique(nom, choix, ok):
    bons = [c for c in choix if ok(c)]
    assert len(bons) == 1, (nom, bons)
    print(nom, '->', bons[0])
    return bons[0]

# #34 LES SŒURS : Paul a 4 sœurs, chaque sœur a exactement 1 frère. Combien d'enfants en tout ?
def enfants():
    for garcons in range(1, 10):
        filles = 4  # les sœurs de Paul
        if all(garcons == 1 for _ in range(filles)): return garcons + filles
assert unique('#34 sœurs', [5, 8, 9], lambda c: c == enfants()) == 5

# #35 LES BILLES : 3 rouges + 5 bleues dans le noir. Minimum pour être SÛR d'avoir 2 bleues ?
def minimum_sur(rouges=3, bleues=5, voulu=2):
    sac = ['R'] * rouges + ['B'] * bleues
    for n in range(1, len(sac) + 1):
        # pire cas : on tire d'abord toutes les rouges possibles
        if all(sorted(p)[:0] == [] and p[:n].count('B') >= voulu for p in set(permutations(sac))): return n
assert unique('#35 billes', [2, 5, 7], lambda c: c == minimum_sur()) == 5

# #36 LA VITESSE MOYENNE : aller à 30 km/h, retour (même distance) à 60 km/h. Vitesse moyenne ?
d = Fr(60)
moy = 2 * d / (d / 30 + d / 60)
assert unique('#36 vitesse', [45, 40, 50], lambda c: c == moy) == 40

# #37 LE TROU : combien de terre dans un trou de 2 m × 2 m × 2 m ? (un trou est vide)
terre = 0
assert unique('#37 trou', [8, 0, 4], lambda c: c == terre) == 0
print('ok : solution unique parmi les choix')
