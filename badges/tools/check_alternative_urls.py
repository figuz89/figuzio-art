"""Validate every alternative PNG without replacing the original v3 cache."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import urllib.request
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]


def check(badge):
    result={'id':badge['id'],'url':badge['imageURL']}
    try:
        req=urllib.request.Request(badge['imageURL'],headers={'User-Agent':'FiguzBadges-Alternative/1.0'})
        with urllib.request.urlopen(req,timeout=40) as res:
            data=res.read(1_000_001)
            result.update(status=res.status,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        expected=ROOT/'badges/assets/v3_alternative'/(badge['id']+'.png')
        assert result['sha256']==hashlib.sha256(expected.read_bytes()).hexdigest(),'Remote/local hash mismatch'
        with Image.open(BytesIO(data)) as im:
            im.verify()
        with Image.open(BytesIO(data)) as im:
            assert im.format=='PNG' and im.mode=='RGBA' and im.height==128
            assert im.getchannel('A').getextrema()==(0,255)
            result.update(width=im.width,height=im.height,transparent=True)
        result['ok']=True
    except Exception as e:
        result.update(ok=False,error=str(e))
    return result


if __name__=='__main__':
    path=ROOT/'badges/Figuz_Smart_Badges_v3_Alternative.json'
    pack=json.loads(path.read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(check,pack['filters']))
    report={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'packSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'count':len(results),'passed':sum(x['ok'] for x in results),'method':'Unauthenticated HTTPS GET, full PNG decode, RGBA transparency and exact local/remote SHA-256 comparison','results':results}
    (ROOT/'badges/reports/alternative-url-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"Alternative images: {report['passed']}/{report['count']} passed")
    for r in results:
        if not r['ok']: print(r['id'],r['error'])
    raise SystemExit(0 if report['passed']==report['count'] else 1)
