# Vérifie #08 (qui a volé le diamant) : un seul dit vrai
sols = []
for v in ['Léa', 'Hugo', 'Nina']:
    dits = [v == 'Hugo', v != 'Hugo', v != 'Nina']  # Léa: c'est Hugo ; Hugo: Léa ment ; Nina: pas moi
    if sum(dits) == 1: sols.append(v)
print('voleur(s) possible(s) :', sols); assert sols == ['Nina']
from itertools import product
s7 = [(A, B) for A, B in product([True, False], repeat=2) if A == ((not A) or (not B))]
assert s7 == [(True, False)]
print('OK : réponse #08 = NINA ; réponse #07 = A dit VRAI (B ment)')
