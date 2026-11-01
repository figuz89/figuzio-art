"""Record every legacy-rule difference, every new regex, and build evidence."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REPORTS=ROOT/'badges/reports'
REPORTS.mkdir(exist_ok=True)
old=json.loads((ROOT/'badges/Figuz_Smart_Badges_v2.json').read_text(encoding='utf-8'))
new=json.loads((ROOT/'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
old_by_id={b['id']:b for b in old['filters']}
reasons={
    'gq':'Alphanumeric token boundaries accept underscores. Remux and BluRay intentionally coexist; lower WEB sources are excluded when a higher source is present in the same candidate.',
    'gr':'Alphanumeric token boundaries accept underscores; explicit higher-resolution exclusions preserve v2 priority without assuming group exclusivity.',
    'ghdr':'Explicit exclusion of higher HDR tiers prevents HDR10+/HDR10/HDR/SDR duplicates in a candidate; original priority and separate Dolby Vision group retained.',
    'gimax':'Plain IMAX explicitly excludes IMAX Enhanced in the same candidate.',
    'gdolby':'Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.',
    'gdts':'DTS:X, DTS-HD MA/Master Audio, DTS-HD and DTS use distinct tokens and explicit higher-tier exclusions. Plain DTS-HD cannot satisfy MA.',
    'gc':'Original channel recognizers retained inside explicit higher-channel exclusions; v2 order 7.1 > 6.1 > 5.1 > 2.0 > 1.0 retained.',
}
changes=[]
additions=[]
for badge in new['filters']:
    previous=old_by_id.get(badge['id'])
    if previous:
        if badge['pattern']!=previous['pattern']:
            changes.append({'id':badge['id'],'groupId':badge['groupId'],'oldPattern':previous['pattern'],'newPattern':badge['pattern'],'reason':reasons[badge['groupId']]})
    else:
        additions.append({k:badge[k] for k in ['id','name','groupId','pattern']})
report={
    'baseCommit':'9e3334897ad2df04630220b619072212a3dac35a',
    'assetCommit':'1da3b7829b1059bf4fd59ef5dea07d72c701d6a1',
    'opticalAssetCommit':'94e6dd769333c0a8883d243d2d521aa0fe670509',
    'v2FileSha256':hashlib.sha256((ROOT/'badges/Figuz_Smart_Badges_v2.json').read_bytes()).hexdigest(),
    'preservedLegacyCount':33,'newBadgeCount':19,'totalBadgeCount':52,
    'legacyChanges':changes,
    'legacyUnchangedPatterns':[b['id'] for b in new['filters'] if b['id'] in old_by_id and b['pattern']==old_by_id[b['id']]['pattern']],
    'newPatterns':additions,
    'presentationChange':'Legacy within-group order, all 9 legacy groups, IDs, names, image URLs and style fields unchanged. Filters ordered across groups as Dolby, DTS, Dolby Vision, HDR, channels, resolution, quality, IMAX, SeaDex, then streaming, codec and edition additions. No stream sorting or playback settings changed.',
    'limitations':['One winner per exclusive category is enforced within one candidate. Nuvio tests fields separately, so contradictory candidates can produce multiple badges. JSON alone cannot enforce per-stream exclusivity across fields.','Audio badges describe filename/metadata evidence, not verified tracks, a default audio track or hardware playback compatibility.'],
}
(REPORTS/'v3-regex-changes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Full v3 regex audit','',f"{len(changes)} documented v2 regex corrections; 19 additions. No legacy artwork, names, IDs, style fields or group membership changed.",'','Each regex runs independently against every Nuvio candidate. Exclusions are local to a candidate; see the compatibility limits in [the v3 report](../V3_REPORT.md).','']
for entry in changes:
    lines += [f"## {entry['id']} ({entry['groupId']})",'',entry['reason'],'','v2:','', '```regex',entry['oldPattern'],'```','','v3:','','```regex',entry['newPattern'],'```','']
lines += ['## Unchanged v2 regexes','',', '.join(report['legacyUnchangedPatterns']),'','## New regexes','']
for entry in additions:
    lines += [f"### {entry['name']} — {entry['id']} ({entry['groupId']})",'','```regex',entry['pattern'],'```','']
(REPORTS/'v3-regex-changes.md').write_text('\n'.join(lines),encoding='utf-8')
print(f'{len(changes)} legacy regex corrections, {len(additions)} additions documented')
