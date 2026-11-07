"""Mixa narração + trilha + efeitos -> mix.wav (níveis pensados para alto-falante de celular)."""
import json, wave, numpy as np
SR = 44100
TL = json.loads(open('timeline.js').read().split('=', 1)[1].rstrip().rstrip(';'))
DUR = TL['dur']; N = int(SR * DUR); F = TL['falas']; T0 = lambda i: F[i]['t0']
rng = np.random.default_rng(3); t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
def lp(x, k):
    y = np.empty_like(x); a = 0.0
    for i in range(len(x)): a += k * (x[i] - a); y[i] = a
    return y
def env(n, a, d): x = np.arange(n) / SR; return np.minimum(x / max(a, 1e-4), 1) * np.exp(-x / d)
def add(s, at, gain=1., pan=0.):
    i = int(at * SR); j = min(N, i + len(s)); s = s[:j - i] * gain
    L[i:j] += s * (1 - max(pan, 0)); R[i:j] += s * (1 + min(pan, 0))

# ---- narração (reamostrada para 44.1k) ----
with wave.open('narracao.wav') as w: sr0 = w.getframerate(); v = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
v = np.interp(np.arange(int(len(v) * SR / sr0)) / SR, np.arange(len(v)) / sr0, v)
v = v / np.abs(v).max() * .9
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]

# ---- trilha: acordes de pad (frequências médias, audíveis no celular) ----
def pad(freqs, d):
    n = int(SR * d); x = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for det in (-.6, .6): s += np.sin(2 * np.pi * (f + det) * x + np.sin(2 * np.pi * 5 * x) * .3)
        s += .3 * np.sin(2 * np.pi * f * 2 * x)
    a = np.minimum(x / 1.2, 1) * np.minimum((d - x) / 1.2, 1)
    return s / len(freqs) * a
Am, F_, C_, G_, Dm, E_ = [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7], [146.8, 174.6, 220], [164.8, 207.7, 246.9]
prog_ = [Am, F_, C_, G_, Am, F_, Dm, E_]
k, ci = 0.0, 0
while k < DUR:
    cs = prog_[ci % len(prog_)]
    if k > T0(10): cs = [f * .5 for f in [Am, Dm, E_][ci % 3][::1]] + [311.1]  # escurece no fim
    add(pad(cs, 4.6), k, .10); k += 4; ci += 1
# dedilhado (viola) nas cenas da manhã
notes = [440, 523.3, 659.3, 523.3, 587.3, 523.3, 493.9, 392]
for i, k in enumerate(np.arange(T0(2) - .2, T0(6), .5)):
    n = int(SR * .9); x = np.arange(n) / SR; f = notes[i % len(notes)]
    s = (np.sin(2 * np.pi * f * x) + .4 * np.sin(4 * np.pi * f * x) + .2 * np.sin(6 * np.pi * f * x)) * env(n, .003, .25)
    add(s, k, .07, .3 if i % 2 else -.3)
# água correndo (ruído filtrado em banda média)
wn = rng.standard_normal(N); wn = lp(wn, .25) - lp(wn, .02)
L += wn * .07 * (.7 + .3 * np.sin(2 * np.pi * .21 * t)); R += wn * .07 * (.7 + .3 * np.cos(2 * np.pi * .17 * t))

# ---- efeitos ----
def splash():
    n = int(SR * .5); s = rng.standard_normal(n); s = (lp(s, .5) - lp(s, .05)) * env(n, .02, .12); return s
for k in np.arange(T0(2) - .3, T0(5), 1.3): add(splash(), k, .35, -.3)
def hit(f=60, d=1.6):
    n = int(SR * d); x = np.arange(n) / SR
    return np.sin(2 * np.pi * (f + 60 * np.exp(-x * 9)) * x) * env(n, .004, d / 3) + lp(rng.standard_normal(n), .2) * env(n, .001, .08)
add(hit(), 0.05, .6); add(hit(55, 2), T0(1) + 2.0, .6)               # título / olhos abrem
def drip(): n = int(SR * .25); x = np.arange(n) / SR; return np.sin(2 * np.pi * (900 + 1400 * x * 4) * x) * env(n, .001, .03)
for k in np.arange(T0(4) + .3, T0(5) - .2, .83): add(drip(), k, .25)
add(hit(70, 1.2), T0(5) - .1, .45)                                   # placa da regra
L0 = T0(9) + 1.6
for kk in range(3):                                                  # lanterna
    n = int(SR * .12); add(np.sin(2 * np.pi * 1760 * np.arange(n) / SR) * env(n, .001, .03), L0 + kk * .55, .3, .4)
for i in range(30):                                                  # bolhas
    n = int(SR * .12); x = np.arange(n) / SR; f = rng.uniform(300, 700)
    add(np.sin(2 * np.pi * (f + 2500 * x) * x) * env(n, .002, .03), T0(11) + .8 + i * .22 + rng.random() * .1, .22, rng.uniform(-.4, .4))
add(hit(45, 2.8), T0(12) + 2.4, .9)                                   # susto
# tensão crescendo na reta final
ten = np.clip((t - T0(11)) / 8, 0, 1) * (t < T0(13))
L += np.sin(2 * np.pi * 466 * t) * .03 * ten; R += np.sin(2 * np.pi * 494 * t) * .03 * ten

# ---- mix: abaixa a trilha quando tem voz (ducking) ----
envv = lp(np.abs(voice), .0008); duck = 1 - .45 * np.clip(envv / (envv.max() * .25), 0, 1)
L = L * duck + voice; R = R * duck + voice
fade = np.clip((DUR - t) / 1.0, 0, 1); L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L / pk * .95, R / pk * .95
with wave.open('mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([L, R], 1) * 32767).astype('<i2').tobytes())
print('ok', DUR)
