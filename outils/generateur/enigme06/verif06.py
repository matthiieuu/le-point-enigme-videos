# Vérifie #06 (deux cordes, 45 min) : quels nombres de bouts allumés au départ permettent de mesurer 45 min ?
# Modèle : une corde a un "contenu" de 60 min ; 1 bout allumé -> brûle au rythme 1, 2 bouts -> rythme 2
# (vrai quelle que soit l'irrégularité). On ne peut agir qu'à t=0 ou quand une corde finit de brûler.
from fractions import Fraction as Fr
from itertools import product
res = {}
def explore(t, ropes, start_ends, times):
    # ropes: list of (remaining, ends_lit)
    burning = [(r / e, i) for i, (r, e) in enumerate(ropes) if e > 0 and r > 0]
    if not burning: return
    dt, _ = min(burning)
    t2 = t + dt
    new = []
    for r, e in ropes:
        if e > 0 and r > 0: r = r - dt * e
        new.append((r, e))
    times.add((start_ends, t2))
    # à cet instant, on peut allumer des bouts supplémentaires sur les cordes non finies
    for choice in product(*[[e] if r <= 0 else ([e, 2] if e == 1 else ([0, 1, 2] if e == 0 else [2])) for r, e in new]):
        explore(t2, [(r, c) for (r, _), c in zip(new, choice)], start_ends, times)
times = set()
for a, b in product([0, 1, 2], repeat=2):
    if a + b == 0: continue
    explore(Fr(0), [(Fr(60), a), (Fr(60), b)], a + b, times)
ok = sorted({s for s, t in times if t == 45})
print('instants mesurables :', sorted({float(t) for s, t in times}))
print('bouts allumés au départ permettant 45 min :', ok)
assert ok == [3]
# énigme #05 (réponse d'hier) : dernier signe de 6/(1-3/4)
assert Fr(6) / (1 - Fr(3, 4)) == 24
print('OK : réponse #06 = B (3 bouts) ; réponse #05 = A (÷)')
