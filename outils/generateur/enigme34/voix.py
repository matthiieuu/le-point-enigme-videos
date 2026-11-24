import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from scipy.signal import resample_poly
from fractions import Fraction
import os
M=os.environ.get('KOKORO_DIR','/home/claude/kokoro/')
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
L=json.load(open('lignes.json'))
# #34 (24/11) : une seule voix (narratrice), hook en speed 1.0
# T26 (18/11) : les personnages parlent avec leur propre voix.
# Kokoro n'a qu'une voix française (ff_siwis) -> voix grave obtenue en générant plus vite
# puis en ralentissant d'un facteur r (hauteur ET formants baissent de 12*log2(r) demi-tons, débit inchangé).
# T26 abandonné (22/11) : une seule voix (narratrice) pour tout
PITCH={'narr':1.0,'prisonnier':1.0,'gardien':1.0}
def say(voice,t,speed):
    r=PITCH[voice]
    s,sr=k.create(t,voice='ff_siwis',speed=min(1.6,speed*r),lang='fr-fr')
    fr=Fraction(147*r/80).limit_denominator(2000)
    s=resample_poly(s,fr.numerator,fr.denominator).astype(np.float32)
    a=np.abs(s); idx=np.where(a>0.01)[0]; return s[max(0,idx[0]-300):idx[-1]+1500]
out=[]; split={}
for i,e in enumerate(L):
    sp=1.0 if i==0 else 0.92
    if isinstance(e[0],list):
        a=say(e[0][0],e[0][1],sp); b=say(e[1][0],e[1][1],sp)
        gap=np.zeros(int((0.15 if i==0 else 0.3)*44100),np.float32)
        s=np.concatenate([a,gap,b]); split[f"split{i}"]=(len(a)+len(gap))/44100
    else: s=say(e[0],e[1],sp)
    sf.write(f'v{i}.wav',s,44100); out.append(len(s)/44100)
    print(i,round(len(s)/44100,2),e)
json.dump(out,open('durees.json','w')); json.dump(split,open('split.json','w'))
