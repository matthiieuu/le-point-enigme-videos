import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from scipy.signal import resample_poly
import os
M=os.environ.get('KOKORO_DIR','/home/claude/kokoro/')
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
L=json.load(open('lignes.json'))
out=[]
for i,t in enumerate(L):
    # T18 (style énergie, speed 1.1) abandonné le 14/11 -> retour à 0.92 (hook à 1.0)
    s,sr=k.create(t,voice='ff_siwis',speed=(1.0 if i==0 else 0.92),lang='fr-fr')
    s=resample_poly(s,147,80).astype(np.float32)
    a=np.abs(s); idx=np.where(a>0.01)[0]; s=s[max(0,idx[0]-300):idx[-1]+1500]
    sf.write(f'v{i}.wav',s,44100); out.append(len(s)/44100)
    print(i,round(len(s)/44100,2),t)
json.dump(out,open('durees.json','w'))
