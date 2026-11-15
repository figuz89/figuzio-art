"""Run the existing pinned Nuvio source tests against the alternative URLs."""
import json
from pathlib import Path
import test_v3 as base
import check_upstream_matchers as upstream
from alternative_order_cases import ORDER_CASES

ROOT=Path(__file__).resolve().parents[2]

if __name__=='__main__':
    alt=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3_Alternative.json').read_text(encoding='utf-8'))
    original=base.run_java()
    base.V3=alt
    base.CASES=base.CASES+ORDER_CASES
    result=base.run_java()
    for i,hits in original.items():
        assert set(result[i])==set(hits)
    for i,case in enumerate(ORDER_CASES,len(original)):
        assert result[i]==case['expected'],(case['name'],result[i],case['expected'])
    upstream.V3=alt
    upstream.CASES=base.CASES
    report={'pack':'Figuz_Smart_Badges_v3_Alternative.json','physicalDeviceTests':False,'iosBinaryTests':False,'method':'Pinned and hash-verified upstream matcher source extracted and compiled unchanged with test-only domain models, as documented in FINAL_QA.md. Alternative URLs and resolution-first filters array supplied. Original recognition unchanged; explicit screenshot, field permutation and film order regressions included.','platforms':{}}
    for platform,info in upstream.SOURCES.items():
        report['platforms'][platform]=upstream.execute(platform,info,result)
        print(platform,report['platforms'][platform]['executions'],'executions passed')
    (ROOT/'badges/reports/alternative-upstream-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
