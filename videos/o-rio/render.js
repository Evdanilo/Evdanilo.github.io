// Renderiza cena.html quadro a quadro e gera o MP4.
// Uso: node render.js [saida.mp4]          -> vídeo completo
//      node render.js --frames 5,14,28     -> só PNGs de teste em ./preview
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const FPS = 30;
(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'cena.html'));
  await page.evaluate(() => window.ready);
  const grab = async t => {
    const b64 = await page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', .93).split(',')[1]; }, t);
    return Buffer.from(b64, 'base64');
  };
  if (args[0] === '--frames') {
    fs.mkdirSync(path.join(__dirname, 'preview'), { recursive: true });
    for (const t of args[1].split(',').map(Number)) fs.writeFileSync(path.join(__dirname, 'preview', `t${t}.jpg`), await grab(t));
  } else {
    const out = args[0] || 'video_mudo.mp4';
    const dur = await page.evaluate(() => window.DUR);
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'ignore', 'inherit'] });
    const n = Math.round(dur * FPS);
    for (let i = 0; i < n; i++) {
      const buf = await grab(i / FPS);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`quadro ${i}/${n}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
