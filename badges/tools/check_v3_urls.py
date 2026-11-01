"""GET and decode every configured badge URL; verify local/new artwork hashes.

Network check only. Does not import badges into Nuvio or touch any configuration.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import urllib.request
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def check(badge):
    url=badge['imageURL']
    result={'id':badge['id'],'url':url}
    try:
        if not url.startswith('https://'):
            raise ValueError('Expected an HTTPS image URL')
        req=urllib.request.Request(url,headers={'User-Agent':'FiguzSmartBadges/3.0 (development validation)'})
        with urllib.request.urlopen(req,timeout=45) as res:
            data=res.read(10_000_001)
            result.update(status=res.status,contentType=res.headers.get('Content-Type'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        if len(data)>10_000_000:
            raise ValueError('Image exceeds 10 MB validation limit')
        with Image.open(BytesIO(data)) as im:
            im.verify()
        with Image.open(BytesIO(data)) as im:
            rgba=im.convert('RGBA')
            result.update(format=im.format,width=im.width,height=im.height,alphaRange=list(rgba.getchannel('A').getextrema()))
        if result['format']!='PNG' or result['alphaRange'] != [0,255]:
            raise ValueError('Expected a nonempty transparent PNG')
        if '/v3_frameless/' in url:
            local=ROOT/'badges/assets/v3_frameless'/(badge['id']+'.png')
        elif '/figuz89/figuzio-art/main/' in url:
            local=ROOT/url.split('/main/')[1]
        else:
            local=None
        if local:
            result['matchesLocal']=hashlib.sha256(local.read_bytes()).hexdigest()==result['sha256']
            if not result['matchesLocal']:
                raise ValueError('Remote image differs from the checked-in asset')
        cache=ROOT/'.v3-cache/images'/(badge['id']+'.png')
        cache.parent.mkdir(parents=True,exist_ok=True)
        cache.write_bytes(data)
        result['ok']=True
    except Exception as error:
        result.update(ok=False,error=str(error))
    return result


if __name__=='__main__':
    pack=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(check,pack['filters']))
    report={'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'method':'Unauthenticated HTTPS GET, full PNG decode, alpha validation, local hash comparison where available','count':len(results),'passed':sum(r['ok'] for r in results),'results':results}
    destination=ROOT/'badges/reports/v3-url-check.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Image URLs: {report['passed']}/{report['count']} passed")
    for result in results:
        if not result['ok']:
            print(result['id'],result['error'])
    raise SystemExit(0 if report['passed']==report['count'] else 1)
