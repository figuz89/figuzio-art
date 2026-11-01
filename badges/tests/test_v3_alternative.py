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

ROOT=Path(__file__).resolve().parents[2]
ALT=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3_Alternative.json').read_text(encoding='utf-8'))
SOURCE=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
MANIFEST=json.loads((ROOT/'badges/assets/v3_alternative/manifest.json').read_text(encoding='utf-8'))


class AlternativeTests(unittest.TestCase):
    def test_only_image_urls_change(self):
        self.assertEqual(ALT['groups'],SOURCE['groups'])
        self.assertEqual(len(ALT['filters']),52)
        self.assertEqual(len({x['imageURL'] for x in ALT['filters']}),52)
        for new,original in zip(ALT['filters'],SOURCE['filters']):
            normalized=copy.deepcopy(new)
            normalized['imageURL']=original['imageURL']
            self.assertEqual(normalized,original)
            self.assertIn('/badges/assets/v3_alternative/',new['imageURL'])
            self.assertTrue(new['imageURL'].startswith('https://raw.githubusercontent.com/'))
            self.assertNotIn('base64',new['imageURL'])
        # The approved base JSON, assets and prior reports are immutable inputs.
        proc=subprocess.run(['git','diff','--exit-code','b9666fa48b774a49b21b9ca6553c093b67e98224','--','badges/Figuz_Smart_Badges_v2.json','badges/Figuz_Smart_Badges_v3.json','badges/assets/v2_frameless','badges/assets/v3_frameless','badges/reports/v3-filename-results.json'],cwd=ROOT,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr.decode(errors='replace'))

    def test_all_368_cases_and_no_new_duplicates(self):
        expected=base.run_java()
        saved=base.V3
        try:
            base.V3=ALT
            actual=base.run_java()
        finally:
            base.V3=saved
        self.assertEqual(actual,expected)
        for i,case in enumerate(base.CASES):
            with self.subTest(case=case['name']):
                hits=actual[i]
                self.assertEqual(len(hits),len(set(hits)))
                if case['expected'] is not None:
                    self.assertEqual(set(hits),set(case['expected']))
                self.assertTrue(set(case['required'])<=set(hits))
                self.assertFalse(set(case['absent'])&set(hits))
        report={'caseCount':len(base.CASES),'sameResultsAsBaseV3':True,'engine':'java.util.regex.Pattern.find; separate and joined candidates; URL dedupe','results':[{'case':c['name'],'matched':actual[i]} for i,c in enumerate(base.CASES)]}
        (ROOT/'badges/reports/alternative-filename-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

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
