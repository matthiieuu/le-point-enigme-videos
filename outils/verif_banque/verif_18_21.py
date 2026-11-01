# Vérification des énigmes piège ajoutées le 01/11/2026
import calendar, itertools
from fractions import Fraction as F
# 18 moutons : 17 moutons, tous sauf 9 meurent -> survivants
moutons = 17; survivants = 9; print("18 survivants:", survivants, "(piège 8 = 17-9)")
# 19 pilules : 3 pilules, une toutes les 30 min, la 1re tout de suite
prises = [k * 30 for k in range(3)]; print("19 minutes pour tout prendre:", prises[-1] - prises[0], "(piège 90)")
# 20 mois avec 28 jours (au moins 28 jours)
print("20 mois ayant 28 jours:", sum(1 for m in range(1, 13) if calendar.monthrange(2026, m)[1] >= 28), "(piège 1)")
# 21 chats : 3 chats attrapent 3 souris en 3 min -> 1 chat = 1 souris / 3 min ; chats pour 100 souris en 100 min
taux = F(3, 3 * 3)  # souris par chat par minute
sol = [c for c in range(1, 200) if c * taux * 100 >= 100 and (c - 1) * taux * 100 < 100]
print("21 chats:", sol, "(piège 100)")
