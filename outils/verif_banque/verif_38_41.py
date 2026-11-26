# Vérification par énumération de la banque #38-#41 (ajoutée le 26/11/2026)
from itertools import combinations_with_replacement
from fractions import Fraction as Fr
res = {}
# #38 LES DEUX PIÈCES : 2 pièces (euros) font 30 centimes, l'une n'est pas une pièce de 10. Choix IMPOSSIBLE / 20 + 10 / 15 + 15
coins = [1, 2, 5, 10, 20, 50]
pairs = [p for p in combinations_with_replacement(coins, 2) if sum(p) == 30]
ok = [p for p in pairs if any(c != 10 for c in p)]   # « l'UNE n'est pas une 10 » (l'autre peut l'être)
assert pairs == [(10, 20)] and ok == [(10, 20)]; res[38] = '20 + 10'
# #39 L'HORLOGE DU DONJON : 6 coups en 5 s (coups instantanés, intervalles égaux). 12 coups ? Choix 10 / 11 / 12 s
iv = Fr(5, 6 - 1); res[39] = (12 - 1) * iv; assert res[39] == 11
# #40 QUI A OUVERT LA CELLULE ? Léa : « C'est Hugo. » Hugo : « Ce n'est pas moi. » Nina : « Ce n'est pas moi. » Un seul dit vrai.
sol = []
for c in ['LÉA', 'HUGO', 'NINA']:
    v = [c == 'HUGO', c != 'HUGO', c != 'NINA']
    if sum(v) == 1: sol.append(c)
assert sol == ['NINA']; res[40] = sol[0]
# #41 LE SEAU DU PUITS : plein = 10 kg, à moitié plein = 6 kg. Seau vide ? Choix 4 / 2 / 5 kg
sol = [s for s in range(0, 11) for w in range(0, 11) if s + w == 10 and Fr(s) + Fr(w, 2) == 6]
assert sol == [2]; res[41] = 2
for k, v in res.items(): print(f'#{k} ->', v)
print('ok : solution unique parmi les choix')
