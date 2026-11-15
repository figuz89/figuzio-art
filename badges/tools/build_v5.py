"""Figuz Smart Badges v5: same badges and rules as v4, smoother metal.

v4's palettes jump from dark to bright at ~50 % height, which reads as a
horizontal line through every word at 16 dp. v5 uses a continuous top-light /
bottom-dark gradient, a broad soft reflection instead of a thin streak and no
brushed lines. Chamfer, sidewall depth and drop shadow are unchanged.
"""
import json
import math
from pathlib import Path
import sys

import build_v4 as v4
alt = v4.alt
np = alt.np
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
from scipy.ndimage import distance_transform_edt, gaussian_filter  # noqa: E402

ROOT = v4.ROOT
v4.DEST = ROOT / 'badges/Figuz_Smart_Badges_v5.json'
v4.ASSETS = ROOT / 'badges/assets/v5'
v4.PREVIEWS = ROOT / 'badges/previews/v5'
v4.CONFIG = ROOT / 'badges/tools/v5_config.json'
H, SS = alt.H, alt.SS

PALETTES = {
    'gold':   [(0, (255, 242, 186)), (.30, (248, 210, 98)), (.65, (226, 168, 44)), (1, (176, 114, 20))],
    'silver': [(0, (250, 253, 255)), (.30, (224, 235, 251)), (.65, (184, 202, 229)), (1, (142, 162, 194))],
    'bronze': [(0, (255, 222, 188)), (.30, (242, 184, 134)), (.65, (208, 134, 84)), (1, (152, 82, 42))],
}


def metal(mask, metal_tier):
    W = math.ceil(mask.width / SS) + 22
    face = Image.new('L', (W * SS, H * SS))
    left = 7 * SS; top = max(5 * SS, (H * SS - mask.height - 7 * SS) // 2)
    face.paste(mask, (left, top))
    alpha = np.asarray(face, dtype=np.float32) / 255
    distance = distance_transform_edt(alpha > .5).astype(np.float32) / SS
    u = np.clip(distance / 3.0, 0, 1)
    height = gaussian_filter((u * (2 - u)) * 2.2, .32 * SS)
    dy, dx = np.gradient(height, 1 / SS, 1 / SS)
    normal = np.stack((-dx, -dy, np.ones_like(dx)), axis=-1)
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-6)
    light = np.array([-.43, -.63, .65], dtype=np.float32); light /= np.linalg.norm(light)
    diffuse = np.clip(np.sum(normal * light, axis=-1), 0, 1)
    half = light + np.array([0, 0, 1], dtype=np.float32); half /= np.linalg.norm(half)
    spec = np.clip(np.sum(normal * half, axis=-1), 0, 1) ** 28
    yy, _ = np.indices(alpha.shape, dtype=np.float32)
    v = np.clip((yy - top) / max(mask.height - 1, 1), 0, 1)
    pal = PALETTES[metal_tier]
    stops = np.array([p[0] for p in pal]); colors = np.array([p[1] for p in pal])
    rgb = np.stack([np.interp(v, stops, colors[:, c]) for c in range(3)], axis=-1).astype(np.float32)
    rgb *= np.expand_dims(.66 + .52 * diffuse, -1)
    # Broad, soft top glow: no visible edge anywhere inside the letters.
    glow = np.exp(-((v - .15) / .28) ** 2) * .10
    sheen = np.clip(glow + .20 * spec, 0, .40)[..., None]
    rgb = rgb * (1 - sheen) + 255 * sheen
    front = Image.fromarray(np.concatenate((np.clip(rgb, 0, 255), alpha[..., None] * 255), axis=-1).astype(np.uint8))
    out = Image.new('RGBA', face.size)
    shadow = alt.shifted(face, round(2.6 * SS), round(6.4 * SS)).filter(ImageFilter.GaussianBlur(1.15 * SS)).point(lambda a: round(a * .50))
    layer = Image.new('RGBA', face.size, (0, 0, 0, 255)); layer.putalpha(shadow); out.alpha_composite(layer)
    side = alt.SIDE[metal_tier]
    for step in range(18, 0, -1):
        depth = step / 3
        f = .65 + .35 * (1 - step / 18)
        layer = Image.new('RGBA', face.size, (*(round(c * f) for c in side), 255))
        layer.putalpha(alt.shifted(face, round(depth * .38 * SS), round(depth * SS)))
        out.alpha_composite(layer)
    out.alpha_composite(front)
    out = out.resize((W, H), Image.Resampling.LANCZOS)
    out.putalpha(out.getchannel('A').point(lambda x: 0 if x < 3 else x))
    return out


alt.metal = metal


def write_json(pack, asset_ref):
    import copy
    out = copy.deepcopy(pack)
    for b in out['filters']:
        b['imageURL'] = f'https://raw.githubusercontent.com/figuz89/figuzio-art/{asset_ref}/badges/assets/v5/{b["id"]}.png'
    v4.DEST.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def compare(pack):
    """v4 vs v5 at 3x Nuvio size for the badges from the screenshot."""
    ids = ['r-2160', 'v-dolbyvision', 'v-hdr10plus', 'q-webdl', 'a-ddp-atmos', 'ch-51', 'l-norsk', 's-nrk', 's-tv2', 'q-remux', 'q-webrip']
    im = Image.new('RGBA', (1500, 120 + len(ids) * 70), '#2a2e33'); d = ImageDraw.Draw(im)
    d.text((40, 30), 'v4 (venstre) vs v5 (høyre) · 3× Nuvio-størrelse', font=v4.base_art.font(26, True), fill='white')
    for i, ident in enumerate(ids):
        y = 100 + i * 70
        for x, folder in [(40, 'v4'), (760, 'v5')]:
            pic = Image.open(ROOT / 'badges/assets' / folder / (ident + '.png')).convert('RGBA')
            pic = pic.resize((round(pic.width * 48 / pic.height), 48), Image.Resampling.LANCZOS)
            im.alpha_composite(pic, (x, y))
    v4.PREVIEWS.mkdir(parents=True, exist_ok=True)
    im.convert('RGB').save(v4.PREVIEWS / 'v4_vs_v5.png', optimize=True)


if __name__ == '__main__':
    cfg = json.loads(v4.CONFIG.read_text(encoding='utf-8')) if v4.CONFIG.exists() else {'assetCommit': 'main'}
    pack = v4.build_pack()
    if '--json-only' not in sys.argv:
        m = v4.render_assets(pack, cfg['assetCommit'])
        compare(pack)
        print('Merker:', len(m['badges']), 'for brede:', [b['id'] for b in m['badges'] if b['ratio'] > 5.75] or 'ingen')
    write_json(pack, cfg['assetCommit'])
    print('Skrev', v4.DEST.relative_to(ROOT))
