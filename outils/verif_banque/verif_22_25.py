# Vérification des énigmes piège #22-#25 (banque ajoutée le 11/11/2026)
from fractions import Fraction as Fr
# #22 LE TRAIN ET LE TUNNEL : train de 1 km, tunnel de 1 km, 1 km/min.
# Temps entre l'entrée de l'avant et la sortie de l'arrière ?
L_train, L_tunnel, v = 1, 1, 1
t22 = Fr(L_train + L_tunnel, v); print('#22 train', t22, 'min (piège 1)'); assert t22 == 2
# #23 LA BARRE DE FER : couper en 10 morceaux, 1 coupe = 1 minute (pas d'empilement).
coupes = 10 - 1; print('#23 barre', coupes, 'min (piège 10)'); assert coupes == 9
# #24 LES POTEAUX : clôture droite de 10 m, un poteau tous les 1 m, aux deux bouts compris.
poteaux = len([x for x in range(0, 11)]); print('#24 poteaux', poteaux, '(piège 10)'); assert poteaux == 11
# #25 L'ESCALIER : du 1er au 3e étage = 30 marches. Du 1er au 6e ?
par_etage = Fr(30, 3 - 1); m = par_etage * (6 - 1); print('#25 escalier', m, 'marches (piège 90)'); assert m == 75
for n, choix, rep in [(22, (1, 2, 3), 2), (23, (10, 9, 5), 9), (24, (10, 11, 9), 11), (25, (60, 75, 90), 75)]:
    assert choix.count(rep) == 1
print('ok : solution unique parmi les choix')
