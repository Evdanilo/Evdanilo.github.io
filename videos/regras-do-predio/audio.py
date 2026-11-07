"""Gera a trilha sonora sintetizada (sem samples externos) -> trilha.wav"""
import numpy as np, wave
SR = 44100; DUR = 66.5; N = int(SR * DUR)
rng = np.random.default_rng(7)
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

def env(n, a, d):  # ataque/decay exponencial
    x = np.arange(n) / SR
    return np.minimum(x / max(a, 1e-4), 1) * np.exp(-x / d)
def lp(x, k):      # passa-baixa simples (média exponencial)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig)); s = sig[: j - i] * gain
    L[i:j] += s * (1 - max(pan, 0)); R[i:j] += s * (1 + min(pan, 0))
def seg(a, b): return (t >= a) & (t < b)

# ---------- drone de fundo ----------
lvl = np.interp(t, [0, 4, 12, 25, 31, 44, 56, 58.3, 61, 66.5], [.35, .45, .5, .55, .7, .85, 1, 1.2, .6, 0])
lfo = .6 + .4 * np.sin(2 * np.pi * .13 * t)
drone = (np.sin(2*np.pi*55*t) + .6*np.sin(2*np.pi*55.4*t) + .35*np.sin(2*np.pi*82.5*t) + .2*np.sin(2*np.pi*110.7*t))
hiss = lp(rng.standard_normal(N), .02) * 1.5
L += (drone * .10 + hiss * .05) * lvl * lfo
R += (drone * .10 + hiss * .05) * lvl * (1.2 - lfo * .4)
# nota aguda dissonante crescendo (tensão) 44-58
ten = seg(44, 58.4) * np.clip((t - 44) / 14, 0, 1) ** 2
L += np.sin(2*np.pi*740*t) * .025 * ten; R += np.sin(2*np.pi*784*t) * .025 * ten

# ---------- impacto de título / cortes ----------
def boom(d=1.8, f=48):
    n = int(SR * d); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(f + 40*np.exp(-x*8))*x) * env(n, .005, d/3)
    s += lp(rng.standard_normal(n), .05) * env(n, .002, .25) * .8
    return s
add(boom(), .2, .55); add(boom(), 61.0, .45)
for at in [4.0, 25.0, 31.0, 38.0, 44.0, 50.0, 56.0]:
    n = int(SR*.6); w = lp(rng.standard_normal(n), .08) * np.hanning(n); add(w, at - .3, .25)

# ---------- "3 REGRAS" ----------
add(boom(1.2, 70), 7.4, .4)

# ---------- caneta escrevendo ----------
for a, b in [(12.4, 14.6), (16.6, 19.6), (21.3, 23.0)]:
    n = int(SR*(b-a)); x = np.arange(n)/SR
    scr = np.diff(lp(rng.standard_normal(n+1), .5)) * (0.5 + 0.5*np.abs(np.sin(2*np.pi*3.3*x + rng.random()*6)))
    add(scr * np.minimum(1, (b-a-x)*8), a, .5, .2)

# ---------- relógio (quarto) ----------
for k in np.arange(25.2, 28.0, .5):
    n = int(SR*.03); add(rng.standard_normal(n) * env(n, .0005, .004), k, .3, -.4 if int(k*2)%2 else .4)

# ---------- batidas na porta ----------
def knock():
    n = int(SR*.35); x = np.arange(n)/SR
    s = np.sin(2*np.pi*(95 + 60*np.exp(-x*40))*x) * env(n, .001, .07)
    s += lp(rng.standard_normal(n), .3) * env(n, .0005, .012) * 1.2
    return s
for k in [28.0, 28.55, 29.1]: add(knock(), k, 1.0, .25)
for k in [29.7, 30.15, 30.6]: add(knock(), k, .35, .25)  # eco na contagem

# ---------- voz abafada "Lia..." (formante sintético) ----------
n = int(SR*1.1); x = np.arange(n)/SR
f0 = 190 - 30*x
ph = 2*np.pi*np.cumsum(f0)/SR
voice = sum(np.sin(ph*h) * np.exp(-((h*f0 - 650)/300)**2) for h in range(1, 12))
voice = lp(voice, .15) * np.sin(np.pi*np.clip(x/1.1, 0, 1)) ** 1.5
add(voice, 34.0, .35, .3)

# ---------- coração ----------
beat_t, k, per = [], 38.2, .95
while k < 58.2:
    beat_t.append(k); k += per; per = max(.42, per * .965)
def lub(g):
    n = int(SR*.18); x = np.arange(n)/SR
    return np.sin(2*np.pi*(52 + 30*np.exp(-x*30))*x) * env(n, .004, .05) * g
for b in beat_t:
    gg = .55 + .4 * (b - 38) / 20
    add(lub(1), b, gg); add(lub(.7), b + .16, gg)

# ---------- chaves tilintando ----------
for i in range(9):
    n = int(SR*.5); x = np.arange(n)/SR; f = rng.uniform(2500, 5200)
    add(np.sin(2*np.pi*f*x) * env(n, .001, .08), 50.3 + i*.045 + rng.random()*.03, .08, rng.uniform(-.5, .5))
add(boom(1.4, 60), 52.4, .5)

# ---------- susto: quatro pés ----------
st = boom(3.0, 38); add(st, 58.3, 1.0)
n = int(SR*2.2); x = np.arange(n)/SR
scr = (np.sin(2*np.pi*(1200 + 300*np.sin(2*np.pi*7*x))*x) + np.sin(2*np.pi*1270*x) + .6*np.sin(2*np.pi*1840*x)) * env(n, .01, .7)
add(scr, 58.3, .12)
# silêncio total logo antes do susto
duck = np.ones(N); duck[seg(57.6, 58.28)] = np.linspace(1, .15, seg(57.6, 58.28).sum())
L *= duck; R *= duck

# ---------- final ----------
for k in np.arange(62.0, 66.0, 1.0):
    add(lub(1), k, .35); add(lub(.7), k + .16, .35)

# master
fade = np.clip((DUR - t) / 1.2, 0, 1) * np.clip(t / .15, 0, 1)
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max()); L, R = L/peak*.89, R/peak*.89
st = np.stack([L, R], 1)
with wave.open('trilha.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
