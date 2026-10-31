# 16 La course : simulation. Doubler = prendre la place du coureur juste devant soi.
def double(ordre, moi, cible):
    i, j = ordre.index(moi), ordre.index(cible)
    assert j == i - 1, "on ne double que le coureur juste devant"
    ordre[i], ordre[j] = ordre[j], ordre[i]
    return ordre
res = set()
for n in range(3, 10):              # nombre de coureurs
    ordre = [f"c{k}" for k in range(1, n + 1)]
    ordre = double(ordre, "c3", ordre[1])   # je suis 3e, je double le 2e
    res.add(ordre.index("c3") + 1)
print("16 place après avoir doublé le 2e :", res)
assert res == {2}
