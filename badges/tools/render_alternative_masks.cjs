// Render the existing, unmodified source vectors at enough resolution for
// the alternative metal shader. Source files and v3 assets are read-only inputs.
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '../..');
const src = path.join(root, 'badges/assets/v3_frameless/sources');
const out = path.join(root, '.v3-cache/alternative-masks');
fs.mkdirSync(out, {recursive:true});
(async () => {
  for (const file of fs.readdirSync(src).filter(x=>x.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(src,file),'utf8').replace(/(\b(?:width|height)="[\d.]+)pt"/g,'$1"');
    await sharp(Buffer.from(svg),{density:72}).resize({height:768}).png().toFile(path.join(out,file.replace('.svg','.png')));
  }
  const symbols=path.join(root,'badges/assets/v3_alternative/sources');
  for (const file of fs.readdirSync(symbols).filter(x=>x.endsWith('.svg'))) {
    await sharp(path.join(symbols,file),{density:72}).resize({height:768}).png().toFile(path.join(out,'symbol-'+file.replace('.svg','.png')));
  }
  process.stdout.write('Rendered streaming logos and clean vector symbols for the alternative style\n');
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
