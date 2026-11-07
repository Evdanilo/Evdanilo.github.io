# As 3 Regras do Prédio — Short (9:16, 66 s)

Vídeo vertical para YouTube Shorts, TikTok ou Reels, animado com código em estilo flat e com tema de terror.

- `as-3-regras-do-predio.mp4`: vídeo final (1080x1920, 30 fps, com trilha)
- `cena.html`: todas as cenas e legendas. Se você abrir no navegador, ele toca em tempo real.
- `render.js`: renderiza quadro a quadro via Playwright e grava com o ffmpeg
- `audio.py`: trilha sintetizada (ambiente, batidas, coração e susto)

## Gerar de novo
```bash
python3 audio.py                 # -> trilha.wav
node render.js video_mudo.mp4    # -> vídeo sem som
ffmpeg -i video_mudo.mp4 -i trilha.wav -c:v libx264 -crf 23 -c:a aac -shortest as-3-regras-do-predio.mp4
```
Para mudar os textos, edite a lista `CAPS` em `cena.html`. Para mudar as regras, edite `RULES`.
