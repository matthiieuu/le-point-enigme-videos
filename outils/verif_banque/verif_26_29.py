# Vérification des énigmes piège #26-#29 (banque ajoutée le 15/11/2026)
# #26 LES BOUGIES : 10 bougies allumées, le vent en éteint 3 (elles restent entières),
# les 7 autres brûlent jusqu'au bout. Combien de bougies restent à la fin ?
allumees = 10; eteintes = 3
restent = eteintes  # les bougies allumées fondent entièrement
print('#26 bougies', restent, '(piège 7)'); assert restent == 3
# #27 LES ŒUFS : 1 œuf cuit en 5 min. 3 œufs dans la même casserole, en même temps ?
t_un = 5; t_trois = max([t_un] * 3)  # cuisson simultanée
print('#27 œufs', t_trois, 'min (piège 15)'); assert t_trois == 5
# #28 LES POMMES : il y a 3 pommes, tu en prends 2. Combien en as-tu ?
panier = 3; prises = 2; tu_as = prises
print('#28 pommes', tu_as, '(piège 1)'); assert tu_as == 2
# #29 LES 9 : en écrivant les nombres de 1 à 100, combien de fois écris-tu le chiffre 9 ?
n9 = sum(str(k).count('9') for k in range(1, 101))
print('#29 chiffre 9', n9, '(piège 10)'); assert n9 == 20
for n, choix, rep in [(26, (7, 3, 10), 3), (27, (15, 5, 3), 5), (28, (1, 2, 3), 2), (29, (10, 11, 20), 20)]:
    assert choix.count(rep) == 1
print('ok : solution unique parmi les choix')
