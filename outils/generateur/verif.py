from itertools import permutations
labels=['Pommes','Oranges','Mélange']
contents=['P','O','M']
lab2c={'Pommes':'P','Oranges':'O','Mélange':'M'}
assign=[dict(zip(labels,p)) for p in permutations(contents) if all(lab2c[l]!=c for l,c in zip(labels,p))]
print(len(assign),'configurations possibles')
for box in labels:
    ok=True
    for a in assign:
        draws={'P':['P'],'O':['O'],'M':['P','O']}[a[box]]
        for d in draws:
            compat=[b for b in assign if d in {'P':['P'],'O':['O'],'M':['P','O']}[b[box]]]
            if len(compat)!=1: ok=False
    print(box,'->','SUFFIT' if ok else 'insuffisant')
