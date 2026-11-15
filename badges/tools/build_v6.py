"""Figuz Smart Badges v6: v5 with HEVC turned off.

Nearly every 4K release is HEVC and all the family's devices play it, so the
badge only took space. Images are unchanged and stay pinned to the v5 artwork.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'badges/Figuz_Smart_Badges_v5.json'
DEST = ROOT / 'badges/Figuz_Smart_Badges_v6.json'
DISABLE = {'c-hevc'}

pack = json.loads(SRC.read_text(encoding='utf-8'))
for f in pack['filters']:
    if f['id'] in DISABLE:
        f['isEnabled'] = False
assert all(not f['isEnabled'] for f in pack['filters'] if f['id'] in DISABLE)
DEST.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print('Skrev', DEST.relative_to(ROOT), '- på:', sum(f['isEnabled'] for f in pack['filters']), 'av', len(pack['filters']))
