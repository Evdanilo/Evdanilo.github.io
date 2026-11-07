"""Gera a narração com Piper (voz pt_BR) e o arquivo timeline.js usado pelas cenas."""
import sys, wave, json, numpy as np
from piper import PiperVoice, SynthesisConfig
from roteiro import FALAS
MODEL = sys.argv[1]
voice = PiperVoice.load(MODEL)
cfg = SynthesisConfig(length_scale=1.08, noise_scale=0.6, noise_w_scale=0.7)
SR = voice.config.sample_rate
INTRO, GAP, OUTRO = 0.6, 0.38, 2.2
pcm, t, tl = [np.zeros(int(SR*INTRO), np.int16)], INTRO, []
for cena, texto, cores in FALAS:
    chunks = [np.frombuffer(c.audio_int16_bytes, np.int16) for c in voice.synthesize(texto, syn_config=cfg)]
    a = np.concatenate(chunks)
    # remove silêncio nas pontas
    nz = np.where(np.abs(a) > 300)[0]; a = a[max(0, nz[0]-200): nz[-1]+800]
    d = len(a) / SR
    tl.append({"cena": cena, "t0": round(t, 3), "t1": round(t + d, 3), "texto": texto, "cores": cores})
    pcm += [a, np.zeros(int(SR*GAP), np.int16)]; t += d + GAP
pcm.append(np.zeros(int(SR*OUTRO), np.int16)); t += OUTRO
with wave.open("narracao.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.concatenate(pcm).tobytes())
open("timeline.js", "w").write("window.TL = " + json.dumps({"dur": round(t, 2), "falas": tl}, ensure_ascii=False) + ";\n")
print("duração total", round(t, 1), "s")
