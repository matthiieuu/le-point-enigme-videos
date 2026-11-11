# Vérifie l'énigme #21 (chats) : 3 chats -> 3 souris en 3 min, donc 1 chat = 1 souris / 3 min.
# Combien de chats pour 100 souris en 100 min ? On cherche le minimum n parmi les choix.
from fractions import Fraction as Fr
rate_per_cat = Fr(3, 3 * 3)            # souris par minute et par chat
ok = [n for n in (100, 33, 3) if n * rate_per_cat * 100 >= 100]
print('choix suffisants', ok, '-> minimum', min(ok))
assert min(ok) == 3
# #20 : nombre de mois avec au moins 28 jours
import calendar
print('#20', sum(1 for m in range(1, 13) if calendar.monthrange(2026, m)[1] >= 28))
