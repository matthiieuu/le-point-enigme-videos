# Vérifie #11 (âge des trois filles) et #10 (aiguilles à 3 h 15)
from fractions import Fraction as Fr
from collections import Counter
from itertools import combinations_with_replacement as cwr
T = [c for c in cwr(range(1, 37), 3) if c[0] * c[1] * c[2] == 36]
S = Counter(sum(c) for c in T)
amb = [c for c in T if S[sum(c)] > 1]          # la somme ne suffit pas
print('triplets produit 36 :', T); print('ambigus :', amb)
sol = [c for c in amb if c[2] > c[1]]          # une aînée unique
assert sol == [(2, 2, 9)], sol
assert [x for x in (6, 9, 12) if x == sol[0][2]] == [9]
a = abs(Fr(30) * 3 + Fr(30) * 15 / 60 - 90)
assert a == Fr(15, 2)
print('OK : réponse #11 = 9, 2 et 2 (aînée 9 ans) ; réponse #10 = 7,5°')
