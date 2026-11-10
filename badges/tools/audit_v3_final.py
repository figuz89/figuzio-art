"""Verify the narrow final-review delta against the previous Draft PR commit."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE='41a1870f67a6cda74b098789760ced582d0e5639'
TARGETS={'s-prime','s-disney','s-skyshowtime','s-paramount'}


def old_file(path):
    return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)


def git_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


if __name__=='__main__':
    before=json.loads(old_file('badges/Figuz_Smart_Badges_v3.json'))
    after=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
    b={x['id']:x for x in before['filters']}; a={x['id']:x for x in after['filters']}
    assert set(a)==set(b) and len(a)==52
    assert before['groups']==after['groups']
    image_changes=[]; regex_changes=[]
    for ident in a:
        for key in a[ident]:
            if a[ident][key]!=b[ident][key]:
                if key=='imageURL':
                    assert ident in TARGETS,(ident,key)
                    image_changes.append(ident)
                else:
                    assert key=='pattern' and ident=='s-skyshowtime',(ident,key)
                    regex_changes.append(ident)
    assert set(image_changes)==TARGETS
    assert regex_changes==['s-skyshowtime']
    tree=subprocess.check_output(['git','ls-tree','-r',BASE,'badges/assets/v3_frameless'],cwd=ROOT,text=True)
    changed_png=[]; unchanged_png=[]; svg_count=0
    for line in tree.splitlines():
        meta,path=line.split('\t'); expected=meta.split()[2]
        if path.endswith('.png'):
            ident=Path(path).stem
            changed=git_hash((ROOT/path).read_bytes())!=expected
            (changed_png if changed else unchanged_png).append(ident)
        elif path.endswith('.svg'):
            assert git_hash((ROOT/path).read_bytes())==expected,path
            svg_count+=1
    assert set(changed_png)==TARGETS and len(unchanged_png)==15 and svg_count==9
    # Git compares repository content while honoring Windows checkout line ends.
    subprocess.run(['git','diff','--exit-code',BASE,'--','badges/Figuz_Smart_Badges_v2.json','badges/assets/v2_frameless'],cwd=ROOT,check=True,capture_output=True)
    measurements=json.loads((ROOT/'badges/reports/v3-layout-measurements.json').read_text(encoding='utf-8'))
    results=json.loads((ROOT/'badges/reports/v3-filename-results.json').read_text(encoding='utf-8'))
    for r in results['results']:
        if r['case'] not in ['film-A','film-B','film-C']: continue
        key=r['case'][-1]
        critical=[i for i in r['matched'] if a[i]['groupId'] in ['gdolby','gdts','gvision','ghdr']]
        for field in ['mobileInitialFullyVisible','tvInitialFullyVisible']:
            assert set(critical)<=set(measurements[key][field])
    report={'baselineCommit':BASE,'badgeCount':52,'legacyBadgeCount':33,'newBadgeCount':19,'groupChanges':0,'regexChangesSincePreviousPR':regex_changes,'regexChangeReason':'Verified SKST and SKYSHO aliases for existing SkyShowtime badge; still requires WEB context. No v2 regex changed in this review round.','changedBadgeImageURLs':sorted(image_changes),'changedPNGs':sorted(changed_png),'unchangedNewPNGs':len(unchanged_png),'unchangedOriginalSVGs':svg_count,'v2FileAndArtworkUnchanged':True,'displayOrderChanged':True,'criticalBadgesFitInitialModelledViewportsForABC':True,'physicalDeviceTests':False,'iosBinaryTests':False}
    (ROOT/'badges/reports/v3-final-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Final delta audit passed: 1 documented service-alias change, 0 group changes; exactly 4 updated logos; v2 unchanged')
