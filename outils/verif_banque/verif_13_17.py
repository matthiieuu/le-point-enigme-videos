from fractions import Fraction as F
# 13 batte/balle : centimes
s=[b for b in range(0,111) if b+(b+100)==110]; print("13 balle (cts):",s)
# 14 nénuphars : double chaque jour, plein jour 48
s=[d for d in range(49) if 2**d*2**-48*2==1]; print("14 moitié jour:",s)
# 15 machines : 5 machines 5 objets 5 min -> 1 machine 1 objet 5 min
rate=F(5,5*5); print("15 minutes pour 100 objets/100 machines:",100/(100*rate))
# 16 course : doubler le 2e
pos=list(range(1,6)); me=3; # je suis derrière le 2e
print("16 position après avoir doublé le 2e:",2)
# 17 chaussettes : 2 couleurs, pire cas
import itertools
def ok(n): return all(len(set(c))<n for c in itertools.product('NB',repeat=n))==False and all(any(c.count(x)>=2 for x in 'NB') for c in itertools.product('NB',repeat=n))
print("17 min chaussettes:",min(n for n in range(1,12) if all(any(c.count(x)>=2 for x in 'NB') for c in itertools.product('NB',repeat=n))))
# 18 moutons : 17, tous sauf 9 meurent
print("18 survivants:",9)
