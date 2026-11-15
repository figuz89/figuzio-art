// Rasterize original vector geometry only. The metallic treatment is applied by
// render_v3.py; no legacy artwork is regenerated or overwritten.
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '../..');
const out = path.resolve(process.argv[2] || path.join(root, '.v3-cache/masks'));
fs.mkdirSync(out, {recursive: true});
(async () => {
  const src = path.join(root, 'badges/assets/v3_frameless/sources');
  for (const name of fs.readdirSync(src).filter(x => x.endsWith('.svg'))) {
    // Render at 4× final content height, then crop transparent margins in Pillow.
    const svg = fs.readFileSync(path.join(src, name), 'utf8')
      .replace(/(\b(?:width|height)="[\d.]+)pt"/g, '$1"');
    await sharp(Buffer.from(svg), {density: 72})
      .resize({height: 256, withoutEnlargement: false})
      .png().toFile(path.join(out, name.replace('.svg', '.png')));
    process.stdout.write(`${name}\n`);
  }
})().catch(e => { process.stderr.write(String(e)); process.exitCode = 1; });
