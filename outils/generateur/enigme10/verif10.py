# Vérifie #10 (angle entre les aiguilles à 3 h 15) et #09 (escargot)
from fractions import Fraction as Fr
h, m = 3, 15
minute = Fr(360) * m / 60                 # 90°
heure = Fr(30) * h + Fr(30) * m / 60      # 97,5°
a = abs(heure - minute); a = min(a, 360 - a)
print('angle à 3 h 15 =', float(a)); assert a == Fr(15, 2)
assert [c for c in [Fr(0), Fr(15, 2), Fr(15)] if c == a] == [Fr(15, 2)]  # choix unique : 7,5
def jours(H=10, up=3, down=2):
    pos, d = 0, 0
    while True:
        d += 1; pos += up
        if pos >= H: return d
        pos -= down
assert jours() == 8
print('OK : réponse #10 = 7,5° ; réponse #09 = 8 jours')
