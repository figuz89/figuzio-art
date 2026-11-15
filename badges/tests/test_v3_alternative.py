"""Functional checks for the independently importable alternative style."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

import numpy as np
from PIL import Image
import test_v3 as base
from alternative_order_cases import ORDER_CASES

ROOT=Path(__file__).resolve().parents[2]
ALT=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3_Alternative.json').read_text(encoding='utf-8'))
SOURCE=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
MANIFEST=json.loads((ROOT/'badges/assets/v3_alternative/manifest.json').read_text(encoding='utf-8'))


class AlternativeTests(unittest.TestCase):
    def test_only_image_urls_and_display_order_change(self):
        self.assertEqual(ALT['groups'],SOURCE['groups'])
        self.assertEqual(len(ALT['filters']),52)
        self.assertEqual(len({x['imageURL'] for x in ALT['filters']}),52)
        originals={b['id']:b for b in SOURCE['filters']}
        self.assertEqual(set(originals),{b['id'] for b in ALT['filters']})
        for new in ALT['filters']:
            original=originals[new['id']]
            normalized=copy.deepcopy(new)
            normalized['imageURL']=original['imageURL']
            self.assertEqual(normalized,original)
            self.assertIn('/badges/assets/v3_alternative/',new['imageURL'])
            self.assertTrue(new['imageURL'].startswith('https://raw.githubusercontent.com/'))
            self.assertNotIn('base64',new['imageURL'])
        # The approved base JSON, assets and prior reports are immutable inputs.
        proc=subprocess.run(['git','diff','--exit-code','b9666fa48b774a49b21b9ca6553c093b67e98224','--','badges/Figuz_Smart_Badges_v2.json','badges/Figuz_Smart_Badges_v3.json','badges/assets/v2_frameless','badges/assets/v3_frameless','badges/reports/v3-filename-results.json'],cwd=ROOT,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr.decode(errors='replace'))

    def test_matching_and_fixed_order_regressions(self):
        expected=base.run_java()
        saved=base.V3; saved_cases=base.CASES
        try:
            base.V3=ALT
            base.CASES=saved_cases+ORDER_CASES
            actual=base.run_java()
        finally:
            base.V3=saved
            base.CASES=saved_cases
        for i,hits in expected.items():
            self.assertEqual(set(actual[i]),set(hits),saved_cases[i]['name'])
        all_cases=saved_cases+ORDER_CASES
        ranks={b['id']:i for i,b in enumerate(ALT['filters'])}
        for i,case in enumerate(all_cases):
            with self.subTest(case=case['name']):
                hits=actual[i]
                self.assertEqual(len(hits),len(set(hits)))
                self.assertEqual(hits,sorted(hits,key=ranks.__getitem__))
                resolutions=[k for k in hits if k.startswith('r-')]
                self.assertEqual(hits[:len(resolutions)],resolutions)
                if case['expected'] is not None:
                    self.assertEqual(set(hits),set(case['expected']))
                    if case in ORDER_CASES:
                        self.assertEqual(hits,case['expected'])
                self.assertTrue(set(case['required'])<=set(hits))
                self.assertFalse(set(case['absent'])&set(hits))
        report={'caseCount':len(all_cases),'baseCaseCount':len(saved_cases),'orderRegressionCases':len(ORDER_CASES),'sameMatchesAsBaseV3':True,'resolutionFirst':True,'engine':'java.util.regex.Pattern.find; separate and joined candidates; ordered URL dedupe','results':[{'case':c['name'],'candidates':c['candidates'],'matched':actual[i]} for i,c in enumerate(all_cases)]}
        (ROOT/'badges/reports/alternative-filename-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

    def test_display_category_order_and_unchanged_priorities(self):
        expected_groups=['gr','gvision','ghdr','gdolby','gdts','gc','gq','gimax','gseadex','gstreaming','gcodec']
        encountered=list(dict.fromkeys(b['groupId'] for b in ALT['filters']))
        self.assertEqual(encountered,expected_groups)
        for group in expected_groups:
            self.assertEqual([b['id'] for b in ALT['filters'] if b['groupId']==group],
                             [b['id'] for b in SOURCE['filters'] if b['groupId']==group])

    def test_all_images_and_quality_tiers(self):
        self.assertEqual(MANIFEST['tierCounts'],{'silver':35,'gold':9,'bronze':8})
        self.assertEqual(len(MANIFEST['badges']),52)
        self.assertEqual({x['id'] for x in MANIFEST['badges']},{b['id'] for b in ALT['filters']})
        digests=set()
        for item in MANIFEST['badges']:
            with self.subTest(badge=item['id']):
                path=ROOT/item['file']; data=path.read_bytes()
                digest=hashlib.sha256(data).hexdigest()
                self.assertEqual(digest,item['sha256'])
                self.assertNotIn(digest,digests)
                digests.add(digest)
                self.assertLess(len(data),150_000)
                source=ROOT/item['source']
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),item['sourceSha256'])
                with Image.open(path) as im:
                    self.assertEqual(im.mode,'RGBA')
                    self.assertEqual(im.height,128)
                    self.assertLessEqual(im.width,882)
                    a=np.asarray(im)
                    self.assertEqual(a[:,:,3].min(),0)
                    self.assertEqual(a[:,:,3].max(),255)
                    self.assertEqual(a[0,:,3].max(),0)
                    self.assertEqual(a[-1,:,3].max(),0)
                    self.assertEqual(a[:,0,3].max(),0)
                    self.assertEqual(a[:,-1,3].max(),0)
                    visible=a[a[:,:,3]>245,:3].astype(int)
                    self.assertGreater(len(visible),30)
                    if item['tier']=='silver':
                        self.assertGreater(np.mean(visible[:,2]>=visible[:,0]),.98)
                    else:
                        self.assertGreater(np.mean((visible[:,0]>=visible[:,1])&(visible[:,1]>=visible[:,2])),.98)
                if item['id'].startswith(('s-','e-','c-')) or item['id']=='v-seadex':
                    self.assertEqual(item['tier'],'silver')


if __name__=='__main__':
    unittest.main()
