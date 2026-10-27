# Vérifie #12 (Monty Hall) par énumération exacte, et rappelle #11
from fractions import Fraction as Fr
from itertools import product
gain = {'GARDER': Fr(0), 'CHANGER': Fr(0)}
for tresor, choix in product(range(3), range(3)):
    p = Fr(1, 9)
    ouvrables = [d for d in range(3) if d != choix and d != tresor]
    for o in ouvrables:              # le gardien choisit au hasard s'il a deux portes possibles
        q = p / len(ouvrables)
        autre = [d for d in range(3) if d not in (choix, o)][0]
        gain['GARDER'] += q * (choix == tresor)
        gain['CHANGER'] += q * (autre == tresor)
print(gain)
assert gain['GARDER'] == Fr(1, 3) and gain['CHANGER'] == Fr(2, 3)
assert 2 * 2 * 9 == 36 and 2 + 2 + 9 == 13 and 1 + 6 + 6 == 13
print('OK : réponse #12 = CHANGER (2/3 contre 1/3) ; réponse #11 = 9 ans (2, 2, 9)')
