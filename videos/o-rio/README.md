# O Rio — Episódio 1 (Short 9:16, 61 s)

Série original de sobrevivência em que o público decide o próximo episódio.

- `o-rio-ep1.mp4`: vídeo final, com narração, trilha e legendas
- `roteiro.py`: o texto narrado, a cena de cada fala e as palavras destacadas
- `narracao.py`: gera a narração com a voz pt_BR do Piper e o `timeline.js`
- `cena.html`: as cenas animadas em canvas (abra no navegador para ver uma prévia)
- `audio.py`: mixa a narração com a trilha e os efeitos
- `render.js`: renderiza os quadros com Playwright e envia ao ffmpeg

## Gerar de novo
```bash
pip install piper-tts   # voz: pt_BR-faber-medium.onnx (rhasspy/piper-voices no Hugging Face)
python3 narracao.py caminho/pt_BR-faber-medium.onnx
python3 audio.py
node render.js video_mudo.mp4
ffmpeg -i video_mudo.mp4 -i mix.wav -c:v libx264 -crf 23 -af loudnorm=I=-14 -c:a aac -shortest o-rio-ep1.mp4
```
Para um episódio novo, basta reescrever as falas em `roteiro.py` e ajustar as cenas em `cena.html`.
