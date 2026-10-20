from fractions import Fraction as Fr
from itertools import permutations
def ex(nums):
    if len(nums)==1: yield nums[0][0], nums[0][1], None; return
    for i in range(1,len(nums)):
        for l in ex(nums[:i]):
            for r in ex(nums[i:]):
                a,sa,_=l; b,sb,_=r
                yield a+b,f"({sa}+{sb})",'+'
                yield a-b,f"({sa}-{sb})",'-'
                yield a*b,f"({sa}*{sb})",'*'
                if b!=0: yield a/b,f"({sa}/{sb})",'/'
sols=set(); tops=set()
for p in permutations([1,3,4,6]):
    for v,s,op in ex([(Fr(x),str(x)) for x in p]):
        if v==24: sols.add(s); tops.add(op)
print(len(sols), sorted(sols)); print('opérations finales:', tops)
