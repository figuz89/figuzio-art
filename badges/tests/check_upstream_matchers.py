"""Execute pinned Nuvio TV/Mobile matching code, not a reimplementation.

Requires Kotlin/JVM (KOTLINC executable) and JDK (JAVA_HOME or PATH).
Downloads only public source into .v3-cache. No Nuvio installation is changed.
Mobile common code runs on JVM; this is not an iOS binary or a device test.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'badges/tests'))
from test_v3 import CASES, V3, run_java

SOURCES={
    'tv':{'repo':'NuvioMedia/NuvioTV','ref':'fa194b008e331780d2391491879e4a0a343641ef','path':'app/src/main/java/com/nuvio/tv/core/streams/StreamBadgeRules.kt','blob':'68f76d00286014924089a7d90eac3cf9d83e6988','marker':'internal object StreamBadgeMatcher'},
    'mobile':{'repo':'NuvioMedia/NuvioMobile','ref':'38295004e4d4002f5520fe4120230253b64af63d','path':'composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamBadgeRules.kt','blob':'b74eb8e6260fd19bb77f22e0fb542d539ff1b53c','marker':'object StreamBadgeMatcher'},
}


def verified_source(platform, info):
    path=ROOT/'.v3-cache/upstream'/(platform+'.kt')
    if not path.exists():
        url=f"https://raw.githubusercontent.com/{info['repo']}/{info['ref']}/{info['path']}"
        with urllib.request.urlopen(url,timeout=30) as res:
            data=res.read()
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    data=path.read_bytes()
    # Connector cache writes may include a final extra newline; normalize only
    # that transport artifact, then require the exact upstream Git blob hash.
    for candidate in [data,data.rstrip(b'\n')+b'\n']:
        digest=hashlib.sha1(b'blob '+str(len(candidate)).encode()+b'\0'+candidate).hexdigest()
        if digest==info['blob']:
            return candidate.decode('utf-8')
    raise AssertionError(f'Upstream source hash mismatch for {platform}')


def execute(platform, info, baseline):
    source=verified_source(platform,info)
    # This contiguous span contains the ENTIRE original matcher object, original
    # CompiledStreamBadgeFilter, and original dedupeKey extension. No replacements.
    span=source[source.index(info['marker']):]
    span=span[:span.index('\n@Serializable')]
    directory=ROOT/'.v3-cache/upstream-build'/platform
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'Matcher.kt').write_text('import java.util.regex.Pattern\nimport java.util.regex.Matcher\n\n'+span,encoding='utf-8')
    shutil.copyfile(ROOT/'badges/tests/upstream_models.kt',directory/'Models.kt')
    b64=lambda s:base64.b64encode(s.encode()).decode()
    (directory/'filters.tsv').write_text('\n'.join('\t'.join([b['id']]+[b64(b[k]) for k in ['imageURL','pattern','name','groupId']]) for b in V3['filters']),encoding='utf-8')
    (directory/'cases.tsv').write_text('\n'.join('\t'.join([str(i)]+[b64(x) for x in c['candidates']]) for i,c in enumerate(CASES)),encoding='utf-8')
    pooled='''
        val pooled=StreamBadgeMatcher.matchedBadgesPooled(stream,filters,hashMapOf())
        println("$id\\tpooled\\t"+pooled.joinToString(","){ids.getValue(it.imageURL)})
''' if platform=='tv' else ''
    main='''import java.io.File
import java.util.Base64
fun decode(s:String)=String(Base64.getDecoder().decode(s),Charsets.UTF_8)
fun main(args:Array<String>){
    val fs=File(args[0]).readLines().map{line->
        val p=line.split("\\t")
        StreamBadgeFilter(id=p[0],imageURL=decode(p[1]),pattern=decode(p[2]),name=decode(p[3]),groupId=decode(p[4]))
    }
    val ids=fs.associate{it.imageURL to it.id}
    val filters=StreamBadgeMatcher.compile(StreamBadgeRules(listOf(StreamBadgeImport(fs))))
    check(filters.size==fs.size){"Some upstream regexes did not compile"}
    File(args[1]).forEachLine{line->
        val p=line.split("\\t"); val id=p[0]; val cs=p.drop(1).map(::decode)
        check(cs.size<=3)
        val stream=Stream(behaviorHints=Hints(cs.getOrNull(0)),title=cs.getOrNull(1),description=cs.getOrNull(2))
        val hits=StreamBadgeMatcher.matchedBadges(stream,filters)
        println("$id\\tstream\\t"+hits.joinToString(","){ids.getValue(it.imageURL)})
        POOLED
    }
}
'''.replace('POOLED',pooled)
    (directory/'Main.kt').write_text(main,encoding='utf-8')
    compiler=os.environ.get('KOTLINC') or shutil.which('kotlinc')
    if not compiler:
        raise RuntimeError('Set KOTLINC to a Kotlin/JVM compiler executable')
    jar=directory/'matcher-tests.jar'
    args=[compiler,str(directory/'Models.kt'),str(directory/'Matcher.kt'),str(directory/'Main.kt'),'-include-runtime','-d',str(jar)]
    subprocess.run(args,check=True,capture_output=True,text=True,encoding='utf-8')
    java=str(Path(os.environ['JAVA_HOME'])/'bin/java') if os.environ.get('JAVA_HOME') else shutil.which('java')
    run=subprocess.run([java,'-jar',str(jar),str(directory/'filters.tsv'),str(directory/'cases.tsv')],check=True,capture_output=True,text=True,encoding='utf-8')
    results=[]
    for line in run.stdout.splitlines():
        ident,mode,hits=line.split('\t')
        i=int(ident); actual=hits.split(',') if hits else []
        assert actual==baseline[i],(platform,mode,CASES[i]['name'],actual,baseline[i])
        results.append({'case':CASES[i]['name'],'mode':mode,'matched':actual})
    return {'sourceURL':f"https://github.com/{info['repo']}/blob/{info['ref']}/{info['path']}",'sourceGitBlob':info['blob'],'extractedSpanSha256':hashlib.sha256(span.encode()).hexdigest(),'caseCount':len(CASES),'executions':len(results),'results':results}


if __name__=='__main__':
    baseline=run_java()
    report={'method':'Pinned upstream matcher object + compiled-filter class + dedupe extension extracted verbatim, compiled with test-only domain-model adapters; actual compile(), candidate collection and matching functions executed. One normalized active import.','physicalDeviceTests':False,'iosBinaryTests':False,'platforms':{}}
    for platform,info in SOURCES.items():
        report['platforms'][platform]=execute(platform,info,baseline)
        print(platform,report['platforms'][platform]['executions'],'executions passed')
    (ROOT/'badges/reports/v3-upstream-matcher-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
