"""v4 checks with the same Java regex engine as Nuvio TV (BadgeRegexHarness).

1. All 391 earlier cases give the same hits as v3_alternative, minus the five
   badges that v4 switches off, in the same order.
2. New badges (Norsk, Viaplay, TV 2, NRK): positive and negative cases.
3. The 52 earlier regexes are byte-identical; image widths stay within 92 dp.
Usage: python check_v4.py <path-to-java>
"""
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
JAVA = sys.argv[1] if len(sys.argv) > 1 else 'java'
OLD = json.loads((ROOT / 'badges/Figuz_Smart_Badges_v3_Alternative.json').read_text(encoding='utf-8'))
NEW = json.loads((ROOT / 'badges/Figuz_Smart_Badges_v4.json').read_text(encoding='utf-8'))
MANIFEST = json.loads((ROOT / 'badges/assets/v4/manifest.json').read_text(encoding='utf-8'))
DISABLED = {f['id'] for f in NEW['filters'] if not f['isEnabled']}

NEW_CASES = [
    # (name, candidate text, must contain, must not contain)
    ('no-1', 'Exit.S01E01.NORWEGIAN.1080p.WEB-DL.DDP5.1.H.264-NTb', {'l-norsk'}, set()),
    ('no-2', 'Film.2020.NORDiC.1080p.BluRay.x264-RAPiDCOWS', {'l-norsk'}, set()),
    ('no-3', 'Movie 2023 1080p WEB-DL 🇳🇴 🇬🇧', {'l-norsk'}, set()),
    ('no-4', 'Movie.2023.1080p.WEB-DL.NOR.SUBS', {'l-norsk'}, set()),
    ('no-5', 'Languages: Norwegian, English', {'l-norsk'}, set()),
    ('no-6', 'Movie.2021.1080p.WEB-DL.Norsk.Tale', {'l-norsk'}, set()),
    ('no-neg-1', 'Normal.People.S01E01.1080p.WEB-DL', set(), {'l-norsk'}),
    ('no-neg-2', 'North.by.Northwest.1959.1080p.BluRay', set(), {'l-norsk'}),
    ('no-neg-3', 'Norbit.2007.1080p.BluRay.x264', set(), {'l-norsk'}),
    ('no-neg-4', 'Neither.Nor.2023.1080p.WEB-DL', set(), {'l-norsk'}),
    ('via-1', 'Series.S01E01.1080p.VIAP.WEB-DL.DDP5.1.H.264', {'s-viaplay'}, set()),
    ('via-2', 'Series.S01E01.WEB-DL.1080p.VIAPLAY', {'s-viaplay'}, set()),
    ('via-3', '📡 Viaplay', {'s-viaplay'}, set()),
    ('via-neg', 'Viaplay.Documentary.2020.1080p.BluRay', set(), {'s-viaplay'}),
    ('tv2-1', 'Exit.S01E01.1080p.TV2.WEB-DL.AAC2.0.H.264', {'s-tv2'}, set()),
    ('tv2-2', '📡 TV 2 Play', {'s-tv2'}, set()),
    ('tv2-3', '[FIGUZ_NETWORK=TV2]', {'s-tv2'}, set()),
    ('tv2-neg', 'Show.TV2.2019.720p.HDTV', set(), {'s-tv2'}),
    ('nrk-1', 'Skam.S01E01.1080p.NRK.WEB-DL.AAC2.0.H.264', {'s-nrk'}, set()),
    ('nrk-2', '📡 NRK1', {'s-nrk'}, set()),
    ('nrk-3', 'network: NRK TV', {'s-nrk'}, set()),
    ('nrk-neg', 'NRK.Dokumentar.2019.720p.HDTV', set(), {'s-nrk'}),
    ('mix-1', 'Exit.S02E01.NORWEGIAN.1080p.NRK.WEB-DL.DDP5.1.H.264',
     {'r-1080', 'l-norsk', 'q-webdl', 's-nrk', 'a-ddplus', 'ch-51'}, {'s-netflix', 's-tv2'}),
]


def b64(s):
    return base64.b64encode(s.encode('utf-8')).decode('ascii')


def run(pack, cases):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / 'filters.tsv'; c = Path(tmp) / 'cases.tsv'
        f.write_text(''.join(f"{x['id']}\t{b64(x['imageURL'])}\t{b64(x['pattern'])}\n"
                             for x in pack['filters'] if x['isEnabled']), encoding='utf-8')
        c.write_text(''.join(name + ''.join('\t' + b64(s) for s in cands) + '\n' for name, cands in cases), encoding='utf-8')
        out = subprocess.run([JAVA, '-Dstdout.encoding=UTF-8', str(ROOT / 'badges/tests/BadgeRegexHarness.java'), str(f), str(c)],
                             capture_output=True, text=True, encoding='utf-8', check=True).stdout
    return {line.split('\t')[0]: [x for x in line.split('\t')[1].split(',') if x]
            for line in out.splitlines() if line}


def main():
    errors = []
    old_by_id = {f['id']: f for f in OLD['filters']}
    for f in NEW['filters']:
        if f['id'] in old_by_id and f['pattern'] != old_by_id[f['id']]['pattern']:
            errors.append('regex endret: ' + f['id'])
    for b in MANIFEST['badges']:
        if b['ratio'] > 5.75:
            errors.append(f"for bred (blir krympet i Nuvio): {b['id']} {b['ratio']}")

    old_results = json.loads((ROOT / 'badges/reports/alternative-filename-results.json').read_text(encoding='utf-8'))['results']
    got = run(NEW, [(r['case'], r['candidates']) for r in old_results])
    changed = 0
    for r in old_results:
        expected = [i for i in r['matched'] if i not in DISABLED]
        # New badges may add hits; the old ones must remain, in the same relative order.
        old_part = [i for i in got[r['case']] if i in old_by_id]
        extra = [i for i in got[r['case']] if i not in old_by_id]
        if old_part != expected:
            errors.append(f"{r['case']}: ventet {expected}, fikk {old_part}")
        if extra:
            changed += 1
            print(f"  ny treff i gammel test {r['case']}: {extra}  <- {r['candidates'][0][:80]}")
        if got[r['case']] and got[r['case']][0] != expected[0] if expected else False:
            pass

    got_new = run(NEW, [(n, [s]) for n, s, _, _ in NEW_CASES])
    for name, text, must, must_not in NEW_CASES:
        hits = set(got_new[name])
        if not must <= hits or hits & must_not:
            errors.append(f'{name}: {text!r} -> {sorted(hits)}')
        else:
            print(f'  OK {name:9s} {", ".join(got_new[name]) or "(ingen)"}')

    print(f'\nGamle tilfeller: {len(old_results)}, nye tilfeller: {len(NEW_CASES)}, '
          f'gamle tilfeller med nye treff: {changed}, avslått: {sorted(DISABLED)}')
    if errors:
        print('\nFEIL:'); [print('  ' + e) for e in errors]; sys.exit(1)
    print('Alt bestått.')


if __name__ == '__main__':
    main()
