import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from scipy.signal import resample_poly
M='/tmp/claude-0/-home-claude-le-point-enigme-videos/bbc3ec43-4551-5a58-8bcd-b625487d9689/scratchpad/models/'
k=Kokoro(M+'kokoro-v1.0.onnx',M+'voices-v1.0.bin')
L=json.load(open('lignes.json'))
out=[]
for i,t in enumerate(L):
    s,sr=k.create(t,voice='ff_siwis',speed=0.92,lang='fr-fr')
    s=resample_poly(s,147,80).astype(np.float32)
    # trim silence
    a=np.abs(s); idx=np.where(a>0.01)[0]; s=s[max(0,idx[0]-400):idx[-1]+2000]
    sf.write(f'v{i}.wav',s,44100); out.append(len(s)/44100)
    print(i,round(len(s)/44100,2),t)
json.dump(out,open('durees.json','w'))
