# Vérifie #07 (île des menteurs) : A dit « Au moins l'un de nous deux est un menteur. »
from itertools import product
sols = []
for A, B in product([True, False], repeat=2):  # True = dit toujours vrai
    S = (not A) or (not B)
    if A == S: sols.append((A, B))
print('solutions (A_vrai, B_vrai) :', sols)
assert sols == [(True, False)]
# #06 (réponse d'hier) : 3 bouts (A par 2 bouts + B par 1) -> 30 + 15 = 45
assert 60/2 + (60-30)/2 == 45
print('OK : réponse #07 = A dit VRAI (B ment) ; réponse #06 = B (3 bouts)')
