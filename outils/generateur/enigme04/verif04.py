from itertools import product
# 3 blancs, 2 noirs ; C voit B et A ; B voit A
cfg=[c for c in product('BN',repeat=3) if c.count('N')<=2]  # (A,B,C)
def c_sait(a,b): return a=='N' and b=='N'   # C voit 2 noirs -> blanc
s1=[c for c in cfg if not c_sait(c[0],c[1])]
def b_sait(a, monde):
    poss={x[1] for x in monde if x[0]==a}
    return len(poss)==1
s2=[c for c in s1 if not b_sait(c[0],s1)]
print('configs restantes',s2); print('A =',{c[0] for c in s2})
