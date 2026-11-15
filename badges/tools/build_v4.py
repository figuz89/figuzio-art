"""Figuz Smart Badges v4: readability pass on the alternative metal style.

Input: Figuz_Smart_Badges_v3_Alternative.json (read-only). Output: new v4 JSON,
assets under badges/assets/v4/ and previews under badges/previews/v4/.

Changes vs v3_alternative
- One-line labels instead of tiny two-line subtitles (Atmos variants, IMAX Enhanced).
- Wide labels are condensed horizontally (max ~25 %) instead of shrunk, because
  Nuvio caps image width at 92 dp (ratio 5.75 at 16 dp height).
- Thin streaming logos are thickened; Prime loses its small arrow; Disney+ and
  Paramount+ script logos become bold wordmarks.
- Director's Cut uses the same Arial Black face as the other labels.
- AVC, PROPER, REPACK, HYBRID and SeaDex are disabled (kept in the file).
- New: NORSK (language) and Viaplay / TV 2 / NRK streaming badges.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.v3-cache/alternative-deps'))
sys.path.insert(0, str(ROOT / 'badges/tools'))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402
import build_alternative as alt  # noqa: E402
import render_v3 as base_art  # noqa: E402

SRC = ROOT / 'badges/Figuz_Smart_Badges_v3_Alternative.json'
DEST = ROOT / 'badges/Figuz_Smart_Badges_v4.json'
ASSETS = ROOT / 'badges/assets/v4'
PREVIEWS = ROOT / 'badges/previews/v4'
CONFIG = ROOT / 'badges/tools/v4_config.json'
SS = alt.SS
H = alt.H
MAX_W = 736            # 5.75 * 128: widest PNG Nuvio shows at full 16 dp height
MAX_SQUEEZE = 0.75     # never condense letters below 75 % width

DISABLED = {'c-avc', 'e-proper', 'e-repack', 'e-hybrid', 'v-seadex'}

B = r'(?<![a-z0-9])'
A = r'(?![a-z0-9])'
RES = r'(?:(?:2160|1440|1080|720|480)p[ ._-]+)?'
NET = r'(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)'


def service_pattern(tags, network):
    return (f'(?i)(?:{B}(?:(?:{tags})[ ._-]+{RES}web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+{RES}(?:{tags})){A}'
            f'|{NET}(?:{network})(?![a-z0-9+]))')


NEW_GROUPS = [
    {'id': 'glang', 'name': 'Language', 'color': '#FFA7B5C7', 'borderColor': '#FFA7B5C7', 'isExpanded': True},
]
NEW_FILTERS = [
    {'id': 'l-norsk', 'groupId': 'glang', 'name': 'Norsk',
     'pattern': f'(?i)(?:{B}(?:norwegian|norsk|norweg[ ._-]?subs?|nor[ ._-]?subs?|nordic){A}|🇳🇴)'},
    {'id': 's-viaplay', 'groupId': 'gstreaming', 'name': 'Viaplay',
     'pattern': service_pattern('VIAP|VIAPLAY', 'Viaplay')},
    {'id': 's-tv2', 'groupId': 'gstreaming', 'name': 'TV 2',
     'pattern': service_pattern('TV2|TV2P|TV2PLAY', r'TV[ ._-]?2(?:[ ._-]?Play)?')},
    {'id': 's-nrk', 'groupId': 'gstreaming', 'name': 'NRK',
     'pattern': service_pattern('NRK|NRKTV', r'NRK(?:[ ._-]?(?:TV|1|2|3|Super))?')},
]
STYLE = {'tagColor': '#00000000', 'borderColor': '#00000000', 'textColor': '#FFFFFFFF',
         'tagStyle': 'bordered', 'type': 'filter', 'isEnabled': True}
# Language right after resolution: when a Norwegian track exists it matters
# more for the family than codec or release details.
DISPLAY_GROUP_ORDER = ['gr', 'glang', 'gvision', 'ghdr', 'gdolby', 'gdts', 'gc',
                       'gq', 'gimax', 'gseadex', 'gstreaming', 'gcodec']
WORDMARKS = {'s-disney': 'Disney+', 's-paramount': 'Paramount+', 's-viaplay': 'Viaplay',
             's-tv2': 'TV 2', 's-nrk': 'NRK', 'l-norsk': 'NORSK', 's-skyshowtime': 'SkyShowtime', 's-peacock': 'Peacock'}
THICKEN = {'s-prime': 3, 's-appletv': 2, 's-hulu': 1,
           's-netflix': 1}


def build_pack():
    pack = copy.deepcopy(json.loads(SRC.read_text(encoding='utf-8')))
    pack['groups'] += NEW_GROUPS
    for f in NEW_FILTERS:
        pack['filters'].append({**f, 'imageURL': '', **STYLE})
    for f in pack['filters']:
        if f['id'] in DISABLED:
            f['isEnabled'] = False
    assert set(DISPLAY_GROUP_ORDER) == {g['id'] for g in pack['groups']}
    rank = {g: i for i, g in enumerate(DISPLAY_GROUP_ORDER)}
    # Stable sort: priorities inside each group stay as before; new streaming
    # services land after the existing ones.
    pack['filters'].sort(key=lambda b: rank[b['groupId']])
    return pack


def strip_arrow(mask):
    """Prime Video: keep the words, drop the thin smile arrow underneath."""
    mask = mask.crop(mask.getbbox())
    rows = [sum(1 for x in range(0, mask.width, 2) if mask.getpixel((x, y)) > 128) for y in range(mask.height)]
    # The words occupy the upper part; find the first empty row after them.
    top_text = next(y for y, n in enumerate(rows) if n)
    cut = next((y for y in range(top_text + mask.height // 3, mask.height) if rows[y] == 0), mask.height)
    return mask.crop((0, 0, mask.width, cut))


def face_mask(badge):
    ident = badge['id']
    if ident in WORDMARKS:
        src = alt.label(WORDMARKS[ident])
        method = 'Arial Black wordmark (readability at 16 dp)'
        source = Path(__file__).resolve()
    elif ident.startswith('s-'):
        src = Image.open(ROOT / '.v3-cache/alternative-masks' / (ident + '.png')).convert('RGBA').getchannel('A')
        if ident == 's-prime':
            src = strip_arrow(src)
        method = 'Original vector alpha, thickened for small sizes'
        source = ROOT / 'badges/assets/v3_frameless/sources' / (ident + '.svg')
    elif ident == 'e-directors-cut':
        src = alt.label("Director's Cut"); method = 'Arial Black'; source = Path(__file__).resolve()
    elif ident == 'a-dtsma':
        # Same artwork as before, but "HD MA" at 200 instead of 140 px.
        word = alt.join(alt.symbol('dts'), alt.label('HD MA', 200), 22)
        src = alt.join(alt.symbol('dts-rings', 285), word, 30)
        method = 'Larger HD MA'; source = Path(__file__).resolve()
    elif ident == 'v-imax-enh':
        src = alt.join(alt.label('IMAX'), alt.label('ENHANCED', narrow=True), 95)
        method = 'One-line label'; source = Path(__file__).resolve()
    elif badge['groupId'] == 'gdolby' and ident in ('a-atmos-multi', 'a-truehd-atmos', 'a-ddp-atmos'):
        # TrueHD Atmos = gold "Atmos" (the only gold Atmos), DD+ Atmos = silver
        # "DD+ Atmos", mixed fields = "Atmos MIX". No tiny second line.
        if ident == 'a-truehd-atmos':
            text = alt.label('Atmos')
        else:
            first, second, narrow = {'a-ddp-atmos': ('DD+', 'Atmos', False),
                                     'a-atmos-multi': ('Atmos', 'MIX', True)}[ident]
            text = alt.join(alt.label(first), alt.label(second, narrow=narrow), 95)
        src = alt.join(alt.symbol('dolby', 300), text)
        method = 'One-line label'; source = Path(__file__).resolve()
    else:
        src = alt.native_mask(badge)
        method = 'Same as v3_alternative'; source = Path(alt.__file__).resolve()
    src = src.crop(src.getbbox())
    # Fit height first (110 px of 128), then condense width if the PNG would
    # exceed Nuvio's 92 dp cap, and only shrink when condensing is not enough.
    h = 110 * SS
    w = src.width * h / src.height
    max_w = (MAX_W - 22) * SS
    if w > max_w:
        squeeze = max(MAX_SQUEEZE, max_w / w)
        w *= squeeze
        if w > max_w:
            h *= max_w / w; w = max_w
    mask = src.resize((max(1, round(w)), max(1, round(h))), Image.Resampling.LANCZOS)
    radius = THICKEN.get(ident)
    if radius:
        # Pad first so the dilated strokes are not clipped at the edges.
        pad = radius * SS * 2
        padded = Image.new('L', (mask.width + 2 * pad, mask.height + 2 * pad)); padded.paste(mask, (pad, pad))
        mask = padded.filter(ImageFilter.MaxFilter(2 * radius * SS + 1))
        mask = mask.crop(mask.getbbox())
        if mask.height > 110 * SS:
            mask = mask.resize((round(mask.width * 110 * SS / mask.height), 110 * SS), Image.Resampling.LANCZOS)
    return mask, {'source': source.relative_to(ROOT).as_posix(),
                  'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'method': method}


def render_assets(pack, asset_ref):
    ASSETS.mkdir(parents=True, exist_ok=True)
    manifest = {'style': 'Alternative sculpted metal, v4 readability pass', 'heightPx': H,
                'renderer': 'badges/tools/build_v4.py', 'tierCounts': {}, 'badges': []}
    for badge in pack['filters']:
        ident = badge['id']; mask, source = face_mask(badge); color = alt.tier(ident)
        result = alt.metal(mask, color); path = ASSETS / (ident + '.png'); result.save(path, optimize=True)
        manifest['tierCounts'][color] = manifest['tierCounts'].get(color, 0) + 1
        manifest['badges'].append({'id': ident, 'name': badge['name'], 'tier': color, 'enabled': badge['isEnabled'],
                                   'file': path.relative_to(ROOT).as_posix(), 'width': result.width,
                                   'height': result.height, 'ratio': round(result.width / result.height, 2),
                                   'bytes': path.stat().st_size,
                                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **source})
    (ASSETS / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return manifest


def write_json(pack, asset_ref):
    out = copy.deepcopy(pack)
    for b in out['filters']:
        b['imageURL'] = f'https://raw.githubusercontent.com/figuz89/figuzio-art/{asset_ref}/badges/assets/v4/{b["id"]}.png'
    DEST.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def image_for(ident):
    return Image.open(ASSETS / (ident + '.png')).convert('RGBA')


def readability(pack):
    """Old (v3_alternative) vs new at Nuvio size, 1x and 3x, for every badge."""
    old_dir = ROOT / 'badges/assets/v3_alternative'
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    rows = pack['filters']
    im = Image.new('RGBA', (1500, len(rows) * 64 + 190), '#171c24'); d = ImageDraw.Draw(im)
    d.text((40, 30), f'v4: ALLE {len(rows)} MERKER VED NUVIO-STØRRELSE', font=base_art.font(29, True), fill='white')
    d.text((40, 80), 'Venstre: før (v3 alternativ) · Høyre: v4 · 16 dp, 1× og 3× · grå navn = slått av',
           font=base_art.font(20), fill='#a9b7cc')
    d.text((330, 130), 'før 1×', font=base_art.font(18), fill='#7f8ba0')
    d.text((560, 130), 'v4 1×', font=base_art.font(18), fill='#7f8ba0')
    d.text((800, 130), 'v4 3×', font=base_art.font(18), fill='#7f8ba0')
    for i, b in enumerate(rows):
        y = 170 + i * 64
        d.text((40, y + 9), b['name'], font=base_art.font(21), fill='#dce5f2' if b['isEnabled'] else '#69738a')
        old = old_dir / (b['id'] + '.png')
        if old.exists():
            base_art.image_for = lambda ident: Image.open(old_dir / (ident + '.png')).convert('RGBA')
            im.alpha_composite(base_art.badge_strip([b['id']], 1), (330, y + 12))
        else:
            d.text((330, y + 12), 'ny', font=base_art.font(18), fill='#7fd18b')
        base_art.image_for = image_for
        im.alpha_composite(base_art.badge_strip([b['id']], 1), (560, y + 12))
        im.alpha_composite(base_art.badge_strip([b['id']], 3), (800, y - 6))
    im.convert('RGB').save(PREVIEWS / 'v4_readability.png', optimize=True)


def streamcards(pack):
    base_art.image_for = image_for
    samples = [
        ('Animals (2026)', ['r-2160', 'v-dolbyvision', 'v-hdr', 'a-ddp-atmos', 'ch-51', 'q-webdl', 's-netflix']),
        ('Kingsman (2014)', ['r-2160', 'v-dolbyvision', 'a-dtsma', 'ch-71', 'q-remux', 'e-unrated']),
        ('Mission: Impossible II (2000)', ['r-2160', 'v-dolbyvision', 'v-hdr10', 'a-truehd-atmos', 'ch-71', 'q-remux']),
        ('Norsk serie (eksempel)', ['r-1080', 'l-norsk', 'a-ddplus', 'ch-51', 'q-webdl', 's-nrk']),
    ]
    im = Image.new('RGBA', (1500, 210 + len(samples) * 420), '#11151b'); d = ImageDraw.Draw(im)
    d.text((70, 48), 'v4 I STREAMKORT — SIMULERING', font=base_art.font(36, True), fill='#eef3fc')
    d.text((70, 110), 'Faktiske v4-filer · 16 dp høyde, maks 92 dp bredde · ingen fysisk test', font=base_art.font(23), fill='#a8b6cc')
    for i, (title, ids) in enumerate(samples):
        y = 205 + i * 420
        d.text((70, y), title, font=base_art.font(29, True), fill='#eaf0fa')
        bar = base_art.badge_strip(ids, 3)
        for n, (lbl, width) in enumerate([('iPhone / Mobile · start', 326), ('Google TV / TV · start', 416)]):
            top = y + 57 + n * 129
            d.rounded_rectangle((60, top, 1440, top + 112), radius=13, fill='#1d2531')
            d.text((80, top + 10), lbl, font=base_art.font(20), fill='#9caecb')
            im.alpha_composite(bar.crop((0, 0, min(bar.width, width * 3), bar.height)), (80, top + 42))
    im.convert('RGB').save(PREVIEWS / 'v4_streamcards.png', optimize=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--json-only', action='store_true'); args = ap.parse_args()
    cfg = json.loads(CONFIG.read_text(encoding='utf-8')) if CONFIG.exists() else {'assetCommit': 'main'}
    pack = build_pack()
    if not args.json_only:
        m = render_assets(pack, cfg['assetCommit'])
        readability(pack); streamcards(pack)
        wide = [b['id'] for b in m['badges'] if b['ratio'] > 5.75]
        print('Merker:', len(m['badges']), 'farger:', m['tierCounts'], 'for brede:', wide or 'ingen')
    write_json(pack, cfg['assetCommit'])
    print('Skrev', DEST.relative_to(ROOT))
