"""Filename regressions run through Java's regex engine (the Android TV matcher).

python -m unittest discover -s badges/tests -v
JAVA_HOME may select a JDK. Otherwise java must be on PATH.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
V2 = json.loads((ROOT / 'badges/Figuz_Smart_Badges_v2.json').read_text(encoding='utf-8'))
V3 = json.loads((ROOT / 'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
BY_ID = {b['id']: b for b in V3['filters']}
CASES = []


def case(name, text, expected=None, required=(), absent=()):
    CASES.append({'name': name, 'candidates': text if isinstance(text, list) else [text], 'expected': expected, 'required': list(required), 'absent': list(absent)})


FILMS = [
    ('A', 'Animals.2026.2160p.NF.WEB-DL.DV.HDR.MULTi', ['q-webdl', 'r-2160', 'v-dolbyvision', 'v-hdr', 's-netflix']),
    ('B', 'Kingsman.The.Secret.Service.2014.Unrated.UHD.BluRay.2160p.DTS-HD.MA.7.1.DV.HEVC.HYBRID.REMUX-FraMeSToR', ['q-remux', 'q-bluray', 'r-2160', 'v-dolbyvision', 'a-dtsma', 'ch-71', 'c-hevc', 'e-unrated', 'e-hybrid']),
    ('C', 'Mission.Impossible.II.2000.USA.BluRay.Remux.UHD.DoVi.HDR10.2160p.TrueHD5.1-CHD', ['q-remux', 'q-bluray', 'r-2160', 'v-dolbyvision', 'v-hdr10', 'a-truehd', 'ch-51']),
]
for name, filename, expected in FILMS:
    case('film-' + name, filename, expected)

for label, aliases in [('s-netflix', ['NF', 'NFLX']), ('s-appletv', ['ATVP']), ('s-prime', ['AMZN']), ('s-disney', ['DSNP']), ('s-hbomax', ['HMAX', 'HBOMAX']), ('s-skyshowtime', ['SKYSHOWTIME']), ('s-paramount', ['PMTP']), ('s-peacock', ['PCOK']), ('s-hulu', ['HULU'])]:
    for alias in aliases:
        for sep in ['.', '-', ' ', '_']:
            for source in ['WEB-DL', 'WEBRip']:
                case(f'service-{alias}-{ord(sep)}-{source}', f'Film{sep}2026{sep}1080p{sep}{alias.lower()}{sep}{source}', required=[label])
                case(f'service-reverse-{alias}-{ord(sep)}-{source}', f'Film{sep}2026{sep}{source}{sep}{alias}{sep}1080p', required=[label])

for name, full in [('s-netflix', 'Netflix'), ('s-appletv', 'Apple TV+'), ('s-prime', 'Amazon Prime Video'), ('s-disney', 'Disney+'), ('s-hbomax', 'HBO Max'), ('s-skyshowtime', 'SkyShowtime'), ('s-paramount', 'Paramount+'), ('s-peacock', 'Peacock'), ('s-hulu', 'Hulu')]:
    for prefix in ['📡 ', 'Network: ', '[FIGUZ_NETWORK=']:
        case(f'network-{name}-{prefix}', prefix + full + ']', [name])

for i, text in enumerate(['The.Apple.2026.1080p.WEB-DL', 'Mad.Max.2015.2160p.WEB-DL', 'MAX', 'ATV', 'NF', 'NFLX', 'Netflix.and.Chill.2026.WEB-DL', 'Hulu.2026.1080p.WEB-DL', 'Peacock.2010.1080p.WEB-DL', 'Sky.2026.WEB-DL', 'HBO.2026.WEB-DL', 'NFish.WEB-DL', 'WEB-DL.ATVPLUS', 'Film.2026.1080p.WEB-DL', 'An.Apple.TV.Story.2026.WEB-DL']):
    case(f'no-service-{i}', text, absent=[b['id'] for b in V3['filters'] if b['groupId'] == 'gstreaming'])

for ident, aliases in [('c-hevc', ['H265', 'H.265', 'H-265', 'H_265', 'x265', 'HEVC']), ('c-avc', ['H264', 'H.264', 'x264', 'AVC']), ('c-av1', ['AV1'])]:
    for alias in aliases:
        case('codec-' + alias, alias.lower(), [ident])
case('codec-dedupe', 'HEVC.H.265.x265.HEVC', ['c-hevc'])
case('codec-priority-av1', 'AV1.HEVC.AVC', ['c-av1'])
case('codec-priority-hevc', 'HEVC.AVC.H.264', ['c-hevc'])
case('codec-no-partials', 'AV10.X2650.H2640.HEVCish', [])

for ident, aliases in [
    ('a-truehd', ['TrueHD5.1', 'TrueHD.5.1', 'TrueHD7.1', 'TrueHD.7.1', 'TRUE-HD', 'true_hd']),
    ('a-truehd-atmos', ['TrueHD.Atmos', 'TrueHD5.1.Atmos', 'TrueHD.7.1.Atmos', 'Atmos.TrueHD']),
    ('a-ddplus', ['DDP5.1', 'DDP.5.1', 'DD+', 'EAC3', 'E-AC-3', 'EC3', 'Dolby Digital Plus']),
    ('a-ddp-atmos', ['DDP5.1.Atmos', 'EAC3.Atmos', 'DD+.5.1.Atmos', 'Atmos.EAC3', 'Dolby Digital Plus Atmos']),
    ('a-atmos-unknown', ['Atmos', 'TrueHD.AAC.Atmos']),
    ('a-atmos-multi', ['TrueHD7.1.DDP5.1.Atmos', 'TrueHD.Atmos.DDP5.1']),
    ('a-dd', ['DD5.1', 'DD.5.1', 'AC3', 'AC-3.5.1', 'Dolby Digital']),
    ('a-dtsx', ['DTS:X', 'DTS.X', 'DTS-X', 'DTSX', 'DTS:X.DTS-HD.MA.7.1']),
    ('a-dtsma', ['DTS-HD.MA.7.1', 'DTS-HD.MA.5.1', 'DTS-HD MA', 'DTSHDMA5.1', 'DTS Master Audio']),
    ('a-dtshd', ['DTS-HD', 'DTS.HD.5.1']),
    ('a-dts', ['DTS', 'DTS5.1']),
]:
    for alias in aliases:
        competing = [b['id'] for b in V3['filters'] if b['groupId'] == BY_ID[ident]['groupId'] and b['id'] != ident]
        case('audio-' + alias, alias, required=[ident], absent=competing)

for i, text in enumerate(['TrueHD5.1', 'TrueHD', 'MULTI.TrueHD7.1', 'TRUEHD.5.1.DTS-HD.MA.7.1', 'Atmosphere.2026.1080p', 'NotTrueHD.Atmosphere', 'DDPI5.1', 'EAC30', 'TRUEHD500']):
    case('audio-negative-' + str(i), text, absent=['a-atmos-multi', 'a-truehd-atmos', 'a-ddp-atmos', 'a-atmos-unknown'])
case('no-ma-in-dtshd', 'DTS-HD.7.1', absent=['a-dtsma', 'a-dtsx'])
case('no-ma-in-matrix', 'DTS-HD.MATRIX.7.1', absent=['a-dtsma'])
case('audio-dedupe', 'DDP5.1.EAC3.DD+.Dolby.Digital.Plus.Atmos', required=['a-ddp-atmos'], absent=['a-ddplus', 'a-dd'])
case('no-language-multi', 'Film.2026.MULTI.WEB-DL', ['q-webdl'])
case('no-language-dl', 'Film.2026.GERMAN.DL.1080p', ['r-1080'])
case('subtitles-only', 'Film.2026.SUBS.NORWEGIAN.1080p', ['r-1080'])

for ident, text in [('e-unrated','Unrated'), ('e-extended','Extended'), ('e-directors-cut', "Director's.Cut"), ('e-directors-cut', 'Directors-Cut'), ('e-directors-cut', 'Director’s Cut'), ('e-theatrical','Theatrical'), ('e-proper','PROPER'), ('e-repack','REPACK2'), ('e-hybrid','HYBRID')]:
    case('edition-' + text, 'Film.2026.' + text + '.1080p.BluRay', required=[ident])
case('multiple-editions', 'Film.2026.Unrated.Extended.Directors.Cut.Theatrical.PROPER.REPACK.HYBRID.1080p', required=[b['id'] for b in V3['filters'] if b['id'].startswith('e-')])
case('edition-title-negative', 'Hybrid.2019.1080p.WEB-DL', absent=['e-hybrid'])
case('extended-title-negative', 'Extended.Family.2026.1080p.WEB-DL', absent=['e-extended'])
case('priority-resolution', '2160p.1080p.720p.480p', ['r-2160'])
case('priority-hdr', 'HDR10+.HDR10.HDR.SDR', ['v-hdr10plus'])
case('priority-imax', 'IMAX.Enhanced', ['v-imax-enh'])
case('priority-channels', '7.1.6.1.5.1.2.0.1.0', ['ch-71'])
case('priority-source', 'REMUX.BluRay.WEB-DL.WEBRip', ['q-remux', 'q-bluray'])
case('seadex-preserved', 'ʙᴇsᴛ ʀᴇʟᴇᴀsᴇ', ['v-seadex'])
for ident, text in [('r-1440','1440p'), ('r-720','720p'), ('r-480','480p'), ('v-sdr','SDR'), ('v-imax','IMAX'), ('ch-61','6.1'), ('ch-20','2.0'), ('ch-10','1.0')]:
    case('legacy-smoke-' + ident, text, [ident])
case('repeated-fields', [FILMS[1][1], FILMS[1][1]], FILMS[1][2])
case('split-fields-atmos-pair', ['TrueHD5.1', 'Atmos'], required=['a-truehd-atmos'])

# These are intentional characterization tests, not claimed pack guarantees.
# The Nuvio matcher runs each field separately before joining fields. JSON cannot
# exclude a hit in another field. Keep this limitation visible and reproducible.
case('client-limit-conflicting-codecs', ['AV1', 'HEVC'], ['c-av1', 'c-hevc'])
case('client-limit-split-audio', ['TrueHD5.1', 'Atmos'], required=['a-truehd', 'a-atmos-unknown', 'a-truehd-atmos'])


def run_java():
    java_home = os.environ.get('JAVA_HOME')
    java = str(Path(java_home) / 'bin/java') if java_home else shutil.which('java')
    if not java:
        raise RuntimeError('A JDK 17+ is required; set JAVA_HOME or add java to PATH')
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    with tempfile.TemporaryDirectory(prefix='figuz-badges-') as directory:
        tmp = Path(directory)
        (tmp / 'filters.tsv').write_text('\n'.join('\t'.join([b['id'], b64(b['imageURL']), b64(b['pattern'])]) for b in V3['filters']), encoding='utf-8')
        (tmp / 'cases.tsv').write_text('\n'.join('\t'.join([str(i)] + [b64(s) for s in c['candidates']]) for i,c in enumerate(CASES)), encoding='utf-8')
        proc = subprocess.run([java, str(ROOT / 'badges/tests/BadgeRegexHarness.java'), str(tmp/'filters.tsv'), str(tmp/'cases.tsv')], check=True, text=True, encoding='utf-8', capture_output=True)
    return {int(line.split('\t')[0]): line.split('\t')[1].split(',') if line.split('\t')[1] else [] for line in proc.stdout.splitlines()}


class FilenameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = run_java()

    def test_filename_cases_with_java_pattern(self):
        for i, c in enumerate(CASES):
            with self.subTest(case=c['name']):
                actual = self.results[i]
                self.assertEqual(len(actual), len(set(actual)))
                if c['expected'] is not None:
                    self.assertEqual(set(actual), set(c['expected']))
                self.assertTrue(set(c['required']) <= set(actual), (c['name'], actual))
                self.assertFalse(set(c['absent']) & set(actual), (c['name'], actual))
                if len(c['candidates']) == 1:
                    for group in ['gdolby','gdts','gc','gr','ghdr','gimax','gcodec']:
                        self.assertLessEqual(sum(BY_ID[k]['groupId'] == group for k in actual),1,(c['name'],group,actual))
        self.assertEqual({k for hits in self.results.values() for k in hits},set(BY_ID),'Every badge must have positive matching coverage')
        results = [{'case': c['name'], 'candidates': c['candidates'], 'matched': self.results[i]} for i,c in enumerate(CASES)]
        if os.environ.get('FIGUZ_WRITE_REPORT'):
            (ROOT / 'badges/reports/v3-filename-results.json').write_text(json.dumps({'engine': 'java.util.regex.Pattern.find; ordered imageURL dedupe; individual and joined candidates', 'caseCount': len(CASES), 'results': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class PackTests(unittest.TestCase):
    def test_additive_schema_and_groups(self):
        self.assertEqual(len(V3['filters']), 52)
        self.assertEqual(len(V3['groups']), 11)
        self.assertEqual(len(BY_ID), 52)
        groups = {g['id'] for g in V3['groups']}
        self.assertEqual(V3['groups'][:9], V2['groups'])
        for b in V3['filters']:
            self.assertIn(b['groupId'], groups)
            self.assertEqual(set(b), set(V2['filters'][0]))
            self.assertEqual(b['tagColor'], '#00000000')
            self.assertEqual(b['borderColor'], '#00000000')
            self.assertTrue(b['imageURL'].startswith('https://'))
            self.assertNotIn('base64', b['imageURL'])

    def test_all_original_badges_and_artwork_are_preserved(self):
        for old in V2['filters']:
            new = BY_ID[old['id']]
            for key in old:
                if key != 'pattern':
                    self.assertEqual(new[key], old[key], (old['id'], key))
        self.assertEqual(BY_ID['v-seadex'], next(b for b in V2['filters'] if b['id'] == 'v-seadex'))

    def test_order_and_membership(self):
        for group in ['gdolby','gdts','gc','gq','gr','ghdr','gimax']:
            self.assertEqual([b['id'] for b in V3['filters'] if b['groupId'] == group], [b['id'] for b in V2['filters'] if b['groupId'] == group])
        first_info = min(i for i,b in enumerate(V3['filters']) if b['groupId'] in ['gstreaming','gcodec'] or b['id'].startswith('e-'))
        self.assertTrue(all(i < first_info for i,b in enumerate(V3['filters']) if b['groupId'] in ['gdolby','gdts','gc']))
        self.assertEqual({b['groupId'] for b in V3['filters'] if b['id'].startswith('e-')}, {'gseadex'})
        self.assertFalse(any('lang' in b['id'] for b in V3['filters']))

    def test_new_png_transparency_size_and_sources(self):
        from PIL import Image
        for b in V3['filters']:
            if '/v3_frameless/' not in b['imageURL']:
                continue
            path = ROOT / 'badges/assets/v3_frameless' / (b['id'] + '.png')
            self.assertLess(path.stat().st_size, 80_000)
            with Image.open(path) as im:
                self.assertEqual(im.mode, 'RGBA')
                self.assertEqual(im.height, 64)
                self.assertLessEqual(im.width, 420)
                alpha = im.getchannel('A')
                self.assertEqual(alpha.getpixel((0,0)), 0)
                self.assertGreater(alpha.getextrema()[1], 240)
                self.assertLess(alpha.getbbox()[3] - alpha.getbbox()[1], 64)
                self.assertEqual(alpha.crop((0,0,im.width,1)).getextrema()[1],0)
                self.assertEqual(alpha.crop((0,63,im.width,64)).getextrema()[1],0)
                # All new marks are neutral/cool silver, never a gold tier signal.
                self.assertTrue(all(b >= r for r,g,b,a in im.get_flattened_data() if a > 240))
        manifest = json.loads((ROOT / 'badges/assets/v3_frameless/sources/manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest), 9)
        for entry in manifest.values():
            path = ROOT / entry['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])


if __name__ == '__main__':
    unittest.main()
