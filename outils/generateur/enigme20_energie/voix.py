import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from scipy.signal import resample_poly
M='/tmp/claude-0/-home-claude/d56930f9-e62d-5f9f-9be3-9e4b2704cef3/scratchpad/voices/'
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
L=json.load(open('lignes.json'))
out=[]
for i,t in enumerate(L):
    # style « énergie YouTube » : débit rapide sur toute la vidéo
    s,sr=k.create(t,voice='ff_siwis',speed=1.15,lang='fr-fr')
    s=resample_poly(s,147,80).astype(np.float32)
    a=np.abs(s); idx=np.where(a>0.01)[0]; s=s[max(0,idx[0]-300):idx[-1]+1200]
    # compression simple : plus de présence, plus « punchy »
    s=np.tanh(s*2.2)/np.tanh(2.2)
    sf.write(f'v{i}.wav',s,44100); out.append(len(s)/44100)
    print(i,round(len(s)/44100,2),t)
json.dump(out,open('durees.json','w'))
