import json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR = 44100
TL = json.load(open('timeline.json'))
T = TL['T']; N = int(T * SR) + 1
rng = np.random.default_rng(7)
t = np.arange(N) / SR

def lp(x, f): return sosfilt(butter(4, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def add(buf, sig, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    n = min(len(sig), len(buf) - i); buf[i:i + n] += sig[:n] * g
def env(n, a=0.005, dcy=0.5):
    tt = np.arange(n) / SR
    return np.minimum(1, tt / a) * np.exp(-tt / dcy)

mus = np.zeros(N)
# nappe grave (Ré mineur)
for f, g in [(36.71, 0.32), (73.42, 0.18), (110.0, 0.09), (87.31, 0.07)]:
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * t + f)
    mus += g * lfo * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t))
mus = lp(mus, 400)
# ambiance : grondement + crépitement torches + gouttes
rum = lp(rng.standard_normal(N), 120) * 0.25
crk = hp(rng.standard_normal(N) * (rng.random(N) < 0.0009) * 1.0, 2000)
crk = lp(crk, 6000) * 0.5
mus += rum + crk
for at in np.arange(0.7, T, 1.9) + rng.random(len(np.arange(0.7, T, 1.9))):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    f = 1400 + 900 * np.exp(-tt * 40)
    add(mus, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 35), at, 0.05)

def bell(f0=392.0):
    n = int(2.5 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for r, g, dc in [(1, 1, 1.4), (2.0, 0.5, 0.9), (2.76, 0.35, 0.6), (5.4, 0.2, 0.3)]:
        s += g * np.sin(2 * np.pi * f0 * r * tt) * np.exp(-tt / dc)
    return s * np.minimum(1, tt / 0.003)
def taiko():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    f = 48 + 90 * np.exp(-tt * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5)
    s += lp(rng.standard_normal(n), 900) * np.exp(-tt * 30) * 0.6
    return s
def impact():
    n = int(1.4 * SR); tt = np.arange(n) / SR
    f = 40 + 120 * np.exp(-tt * 10)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3) * 1.1
    s += lp(rng.standard_normal(n), 3000) * np.exp(-tt * 14) * 0.7
    return s
def thump():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (55 + 30 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 18)
def tick(f):
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) + hp(rng.standard_normal(n), 3000) * 0.5) * np.exp(-tt * 120)

for k, st in enumerate(TL['starts']):
    add(mus, bell([392, 440, 466, 523, 349, 392, 523][k % 7]), st, 0.16)
    add(mus, taiko(), st, 0.55)
add(mus, impact(), TL['FAUXT'], 0.5)
# HOOK : impact + whoosh dès 0,0 s
add(mus, impact(), 0.0, 1.0)
nw = int(0.45 * SR); tw = np.arange(nw) / SR
wh = hp(rng.standard_normal(nw), 900); wh = lp(wh, 5000) * np.exp(-tw * 7) * 0.9
add(mus, wh, 0.0, 1.0)
add(mus, impact(), TL['STAMP'], 0.75)
add(mus, impact(), TL['ANS'], 0.4)
# chrono : cordes tendues, tic-tac, coeur
CS, CE = TL['CS'], TL['CE']
n = int((CE - CS) * SR); tt = np.arange(n) / SR
strings = np.zeros(n)
for f in [146.83, 155.56, 220.0, 233.08, 293.66]:
    ph = 2 * np.pi * f * tt + 0.004 * f * np.sin(2 * np.pi * 5.5 * tt)
    strings += (2 * ((ph / (2 * np.pi)) % 1) - 1)
strings = lp(strings, 1800) * (0.25 + 0.75 * tt / tt[-1]) * (0.8 + 0.2 * np.sin(2 * np.pi * 9 * tt)) * 0.07
add(mus, strings, CS)
for s in range(int(TL['CHR'])): add(mus, tick(1800 if s % 2 == 0 else 1300), CS + s, 0.35)
x = 0.0
while x < CE - CS:
    rate = 1.2 + x * 0.25
    add(mus, thump(), CS + x, 0.7); add(mus, thump(), CS + x + 0.16, 0.45)
    x += 1 / rate
# réverb légère
ir_n = int(1.3 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.35); ir = lp(ir, 5000); ir /= np.abs(ir).sum() / 6
mus = mus + 0.25 * fftconvolve(mus, ir)[:N]

# voix
voice = np.zeros(N); act = np.zeros(N)
for k, st in enumerate(TL['starts']):
    v, sr = sf.read(f'v{k}.wav')
    v = v + 0.45 * lp(v, 260); v = lp(v, 8500)
    add(voice, v, st); add(act, np.ones(len(v)), st)
vrev = fftconvolve(voice, ir * 0.5)[:N]
voice = voice + 0.12 * vrev
# ducking -60 %
k = int(0.15 * SR); sm = np.convolve(act, np.ones(k) / k, 'same')
duck = 1 - 0.6 * np.clip(sm, 0, 1)
mus *= duck
mus /= np.abs(mus).max() + 1e-9
voice /= np.abs(voice).max() + 1e-9
mix = 0.5 * mus + 0.9 * voice
# fondu de bouclage
F0 = TL['FADE']; fi = t >= F0
mix[fi] *= np.clip(1 - (t[fi] - F0) / 0.4, 0, 1) * 0.7 + 0.3
mix[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= 0.89 / np.abs(mix).max()
sf.write('mix.wav', np.stack([mix, mix], 1).astype(np.float32), SR)
print('ok', len(mix) / SR)
