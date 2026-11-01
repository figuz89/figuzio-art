"""Build the separate, importable sculpted-metal variant from verified v3.

Source identity, regexes, groups, names, priorities and style fields are retained.
Only imageURL is changed in the alternative JSON. v2/v3 are never written.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
local_deps=ROOT/'.v3-cache/alternative-deps'
if local_deps.exists():
    sys.path.insert(0,str(local_deps))

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter

sys.path.insert(0,str(ROOT/'badges/tools'))
import render_v3 as base_art

ASSETS=ROOT/'badges/assets/v3_alternative'
PREVIEWS=ROOT/'badges/previews/v3_alternative'
BASE_PATH=ROOT/'badges/Figuz_Smart_Badges_v3.json'
DESTINATION=ROOT/'badges/Figuz_Smart_Badges_v3_Alternative.json'
PACK=json.loads(BASE_PATH.read_text(encoding='utf-8'))
BY_ID={b['id']:b for b in PACK['filters']}
GOLD={'q-remux','r-2160','v-dolbyvision','v-hdr10plus','a-truehd-atmos','a-truehd','a-dtsx','a-dtsma','ch-71'}
BRONZE={'q-webrip','r-720','r-480','v-sdr','a-dd','a-dts','ch-20','ch-10'}
# Pin URLs independently of the renderer source, avoiding a self-referential
# renderer/manifest hash when the immutable artwork commit becomes available.
CONFIG=ROOT/'badges/tools/alternative_config.json'
ASSET_REF=json.loads(CONFIG.read_text(encoding='utf-8'))['assetCommit'] if CONFIG.exists() else 'codex/figuz-smart-badges-v3'
H=128
SS=3

PALETTES={
    'gold':[(0,(255,247,201)),(.12,(255,228,126)),(.35,(234,180,48)),(.47,(183,120,17)),(.53,(255,224,107)),(.77,(231,182,51)),(1,(156,100,13))],
    'silver':[(0,(252,254,255)),(.15,(231,240,255)),(.37,(180,200,229)),(.48,(126,148,182)),(.54,(243,250,255)),(.76,(206,224,248)),(1,(137,157,190))],
    'bronze':[(0,(255,226,192)),(.15,(255,195,148)),(.38,(214,137,85)),(.48,(157,82,40)),(.54,(250,189,141)),(.78,(207,131,80)),(1,(134,69,34))],
}
SIDE={'gold':(109,66,8),'silver':(60,77,103),'bronze':(95,45,20)}


def tier(ident):
    return 'gold' if ident in GOLD else 'bronze' if ident in BRONZE else 'silver'


def original_image(badge):
    if '/v3_frameless/' in badge['imageURL']:
        path=ROOT/'badges/assets/v3_frameless'/(badge['id']+'.png')
    elif '/figuz89/figuzio-art/main/' in badge['imageURL']:
        path=ROOT/badge['imageURL'].split('/main/')[1]
    else:
        path=ROOT/'.v3-cache/images'/(badge['id']+'.png')
    return Image.open(path).convert('RGBA'),path


def sized(mask,height):
    mask=mask.crop(mask.getbbox())
    return mask.resize((round(mask.width*height/mask.height),height),Image.Resampling.LANCZOS)


def label(text,height=300,narrow=False):
    font_name='ARIALNB.TTF' if narrow else 'ariblk.ttf'
    face=ImageFont.truetype(str(base_art.FONT_DIR/font_name),400)
    box=face.getbbox(text)
    mask=Image.new('L',(box[2]-box[0]+12,box[3]-box[1]+12))
    ImageDraw.Draw(mask).text((6-box[0],6-box[1]),text,font=face,fill=255)
    return sized(mask,height)


def symbol(name,height=300):
    path=ROOT/'.v3-cache/alternative-masks'/('symbol-'+name+'.png')
    return sized(Image.open(path).convert('RGBA').getchannel('A'),height)


def join(left,right,gap=40):
    out=Image.new('L',(left.width+gap+right.width,max(left.height,right.height)))
    out.paste(left,(0,(out.height-left.height)//2)); out.paste(right,(left.width+gap,(out.height-right.height)//2))
    return out


def stack(top,bottom,gap=16):
    out=Image.new('L',(max(top.width,bottom.width),top.height+gap+bottom.height))
    out.paste(top,((out.width-top.width)//2,0)); out.paste(bottom,((out.width-bottom.width)//2,top.height+gap))
    return out


def globe():
    out=Image.new('L',(320,320)); d=ImageDraw.Draw(out)
    d.ellipse((12,12,308,308),outline=255,width=13)
    d.ellipse((98,12,222,308),outline=255,width=11)
    d.line((14,160,306,160),fill=255,width=11)
    d.arc((12,75,308,245),0,180,fill=255,width=9)
    d.arc((12,75,308,245),180,360,fill=255,width=9)
    return out


def disc():
    out=Image.new('L',(310,310)); d=ImageDraw.Draw(out)
    d.ellipse((12,12,298,298),outline=255,width=15)
    d.ellipse((116,116,194,194),outline=255,width=12)
    d.arc((35,35,275,275),205,290,fill=255,width=7)
    return out


def native_mask(badge):
    ident=badge['id']
    if ident.startswith(('e-','c-')):
        text={'c-hevc':'HEVC','c-avc':'AVC','c-av1':'AV1'}.get(ident,badge['name'])
        return label(text,narrow=ident=='e-directors-cut')
    if ident.startswith('r-'):
        text=badge['name']; mask=label(text)
        if ident=='r-2160':
            skew=.18; pad=round(skew*mask.height)
            mask=mask.transform((mask.width+pad,mask.height),Image.Transform.AFFINE,(1,skew,-pad,0,1,0),Image.Resampling.BICUBIC)
        return mask
    if ident.startswith('ch-'):
        return label(badge['name'])
    if ident=='q-remux': return label('Remux')
    if ident=='q-bluray': return join(disc(),label('BluRay'))
    if ident in ['q-webdl','q-webrip']: return join(globe(),label('WebDL' if ident=='q-webdl' else 'WebRip'))
    if ident=='v-dolbyvision': return join(symbol('dolby'),label('Vision'))
    if ident in ['v-hdr10plus','v-hdr10','v-hdr','v-sdr']:
        return label({'v-hdr10plus':'HDR10+','v-hdr10':'HDR10','v-hdr':'HDR','v-sdr':'SDR'}[ident])
    if ident=='v-imax': return label('IMAX')
    if ident=='v-imax-enh':
        top=label('IMAX',190); bottom=label('ENHANCED',82)
        return stack(top,bottom,20)
    if ident=='v-seadex': return join(symbol('seadex-mark'),label('SeaDex'))
    if badge['groupId']=='gdolby':
        audio={'a-atmos-multi':('Atmos','MIXED'),'a-truehd-atmos':('TrueHD','ATMOS'),'a-ddp-atmos':('DD+','ATMOS'),'a-atmos-unknown':('Atmos ?',None),'a-truehd':('TrueHD',None),'a-ddplus':('Digital+',None),'a-dd':('Digital',None)}
        top,bottom=audio[ident]
        text=stack(label(top,190),label(bottom,85),16) if bottom else label(top)
        return join(symbol('dolby',240 if bottom else 300),text)
    if badge['groupId']=='gdts':
        word=symbol('dts')
        if ident=='a-dtsx': word=join(word,label('X'),12)
        if ident=='a-dtsma': word=join(word,label('HD MA',140),22)
        if ident=='a-dtshd': word=join(word,label('HD',285),22)
        return join(symbol('dts-rings',285),word,30)
    raise ValueError('No native mask for '+ident)


def face_mask(badge):
    ident=badge['id']
    if ident.startswith('s-'):
        mask_path=ROOT/'.v3-cache/alternative-masks'/(ident+'.png')
        path=ROOT/'badges/assets/v3_frameless/sources'/(ident+'.svg')
        src=Image.open(mask_path).convert('RGBA').getchannel('A')
        credit='Original vector alpha; same SVG used by v3'
    else:
        src=native_mask(badge)
        path=Path(__file__).resolve()
        credit='Clean native text/vector rendering; original v2/v3 images remain unchanged'
    src=src.crop(src.getbbox())
    scale=min(860*SS/src.width,110*SS/src.height)
    target=(max(1,round(src.width*scale)),max(1,round(src.height*scale)))
    return src.resize(target,Image.Resampling.LANCZOS),{'source':path.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':credit}


def shifted(mask,dx,dy):
    out=Image.new('L',mask.size)
    out.paste(mask,(dx,dy))
    return out


def metal(mask,metal_tier):
    W=math.ceil(mask.width/SS)+22
    face=Image.new('L',(W*SS,H*SS))
    left=7*SS; top=max(5*SS,(H*SS-mask.height-7*SS)//2)
    face.paste(mask,(left,top))
    alpha=np.asarray(face,dtype=np.float32)/255
    opaque=alpha>.5
    distance=distance_transform_edt(opaque).astype(np.float32)/SS
    # Rounded chamfers across the first 1.7 px inside the silhouette. Smoothing
    # the height field gives continuous normals without a polygonal outline.
    u=np.clip(distance/3.0,0,1)
    height=(u*(2-u))*2.2
    height=gaussian_filter(height,.32*SS)
    dy,dx=np.gradient(height,1/SS,1/SS)
    normal=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1)
    normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-6)
    light=np.array([-.43,-.63,.65],dtype=np.float32)
    light/=np.linalg.norm(light)
    diffuse=np.clip(np.sum(normal*light,axis=-1),0,1)
    half=light+np.array([0,0,1],dtype=np.float32); half/=np.linalg.norm(half)
    spec=np.clip(np.sum(normal*half,axis=-1),0,1)**28
    yy,xx=np.indices(alpha.shape,dtype=np.float32)
    v=np.clip((yy-top)/max(mask.height-1,1),0,1)
    palette=PALETTES[metal_tier]
    stops=np.array([p[0] for p in palette]); colors=np.array([p[1] for p in palette])
    rgb=np.stack([np.interp(v,stops,colors[:,c]) for c in range(3)],axis=-1).astype(np.float32)
    rgb*=np.expand_dims(.60+.63*diffuse,-1)
    # Controlled reflection and restrained brushed-satin lines, rather than a
    # flat brightness boost or an enclosing backplate.
    reflection=np.exp(-((v-(.19+.045*xx/max(alpha.shape[1],1)))/.034)**2)*.13
    brushed=(np.sin(yy*1.37)+np.sin(yy*.47+xx*.008))*.003
    sheen=np.clip(reflection+.20*spec+brushed,0,.45)[...,None]
    rgb=rgb*(1-sheen)+np.array([255,255,255],dtype=np.float32)*sheen
    rgba=np.concatenate((np.clip(rgb,0,255),alpha[...,None]*255),axis=-1).astype(np.uint8)
    front=Image.fromarray(rgba)
    out=Image.new('RGBA',face.size)
    shadow=shifted(face,round(2.6*SS),round(6.4*SS)).filter(ImageFilter.GaussianBlur(1.15*SS)).point(lambda a:round(a*.50))
    shadow_layer=Image.new('RGBA',face.size,(0,0,0,255)); shadow_layer.putalpha(shadow); out.alpha_composite(shadow_layer)
    side=SIDE[metal_tier]
    # Layered, colored sidewalls create actual relief that remains attached to
    # the glyphs. Every region outside the mark stays transparent.
    for step in range(18,0,-1):
        depth=step/3
        side_mask=shifted(face,round(depth*.38*SS),round(depth*SS))
        factor=.65+.35*(1-step/18)
        color=tuple(round(c*factor) for c in side)
        layer=Image.new('RGBA',face.size,(*color,255)); layer.putalpha(side_mask); out.alpha_composite(layer)
    out.alpha_composite(front)
    out=out.resize((W,H),Image.Resampling.LANCZOS)
    # Remove sub-visible resampling residue at the canvas edge.
    a=out.getchannel('A').point(lambda x:0 if x<3 else x)
    out.putalpha(a)
    return out


def render_assets():
    ASSETS.mkdir(parents=True,exist_ok=True)
    manifest={'style':'Alternative sculpted metal','referenceConcept':'badges/previews/concepts/Figuz_Smart_Badges_Alternative_Style.png','heightPx':H,'renderer':'badges/tools/build_alternative.py','symbolSources':{'dolby':'https://github.com/simple-icons/simple-icons/blob/13.21.0/icons/dolby.svg','dts':'https://github.com/simple-icons/simple-icons/blob/13.21.0/icons/dts.svg','seadex-mark':'Curve paths derived from badges/assets/v1_2/v-seadex.svg','dts-rings':'Native geometric ring ornament'},'fontNames':['Arial Black','Arial Narrow Bold'],'tierCounts':{},'badges':[]}
    for badge in PACK['filters']:
        ident=badge['id']; mask,source=face_mask(badge); color=tier(ident)
        result=metal(mask,color); path=ASSETS/(ident+'.png'); result.save(path,optimize=True)
        manifest['tierCounts'][color]=manifest['tierCounts'].get(color,0)+1
        manifest['badges'].append({'id':ident,'name':badge['name'],'tier':color,'file':path.relative_to(ROOT).as_posix(),'width':result.width,'height':result.height,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'originalImageURL':badge['imageURL'],**source})
    (ASSETS/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return manifest


def build_json():
    alternative=copy.deepcopy(PACK)
    for badge in alternative['filters']:
        badge['imageURL']=f"https://raw.githubusercontent.com/figuz89/figuzio-art/{ASSET_REF}/badges/assets/v3_alternative/{badge['id']}.png"
    DESTINATION.write_text(json.dumps(alternative,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return alternative


def image_for(ident):
    return Image.open(ASSETS/(ident+'.png')).convert('RGBA')


def catalog():
    PREVIEWS.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGBA',(1800,5200),'#101112'); d=ImageDraw.Draw(im)
    d.text((80,50),'FIGUZ SMART BADGES',font=base_art.font(56,True),fill='#eef3fc')
    d.text((82,126),'ALTERNATIV STIL',font=base_art.font(24),fill='#a6b2c5')
    for x,label,color in [(1180,'GULL','#f4ce69'),(1360,'SØLV','#d1e0f5'),(1540,'BRONSE','#da976a')]:
        d.ellipse((x,76,x+25,101),fill=color); d.text((x+40,77),label,font=base_art.font(21),fill='#adb8c9')
    d.line((900,230,900,5000),fill='#30333a',width=1)
    columns=[['gq','gr','gvision','ghdr','gimax','gcodec'],['gseadex','gdolby','gdts','gc','gstreaming']]
    for column,groups in enumerate(columns):
        x0=80+column*870; y=230
        for group_id in groups:
            group=next(g for g in PACK['groups'] if g['id']==group_id)
            label=group['name'].upper(); d.text((x0,y),label,font=base_art.font(26,True),fill='#aeb9ca')
            title_width=d.textlength(label,font=base_art.font(26,True))
            d.line((x0+title_width+24,y+19,x0+755,y+19),fill='#3b3c3e',width=1)
            y+=66; x=x0; row_height=108
            badges=[b for b in PACK['filters'] if b['groupId']==group_id]
            if group_id in ['gseadex','gstreaming']:
                cols=2 if group_id=='gseadex' else 3
                cell_w=770/cols
                for n,badge in enumerate(badges):
                    pic=base_art.fit(image_for(badge['id']),cell_w-24,104)
                    im.alpha_composite(pic,(round(x0+(n%cols)*cell_w),round(y+(n//cols)*132+(row_height-pic.height)/2)))
                y+=math.ceil(len(badges)/cols)*132+63
                continue
            for badge in badges:
                pic=base_art.fit(image_for(badge['id']),390,104)
                if x+pic.width>x0+770:
                    x=x0; y+=132
                im.alpha_composite(pic,(x,y+(row_height-pic.height)//2)); x+=pic.width+38
            y+=row_height+85
        if column==0: bottom_left=y
        else: bottom_right=y
    bottom=max(bottom_left,bottom_right)+12
    d.text((80,bottom),'Faktiske transparente PNG-merker · 52 merker · samme gjenkjenning som testet v3',font=base_art.font(23),fill='#a3adbd')
    d.text((80,bottom+40),'Gull: høyeste etablerte nivå · Sølv: middels / informasjon · Bronse: lavere nivå',font=base_art.font(22),fill='#a3adbd')
    im.crop((0,0,1800,bottom+105)).convert('RGB').save(PREVIEWS/'Figuz_Smart_Badges_v3_Alternative.png',optimize=True)


def examples():
    # Reuse only the measured chip drawing primitive, never v3's file writers.
    base_art.image_for=image_for
    results=json.loads((ROOT/'badges/reports/v3-filename-results.json').read_text(encoding='utf-8'))['results']
    names={'film-A':'Animals (2026)','film-B':'Kingsman (2014)','film-C':'Mission: Impossible II (2000)'}
    im=Image.new('RGBA',(1500,1600),'#11151b'); d=ImageDraw.Draw(im)
    d.text((70,48),'NY STIL I STREAMKORT — SIMULERING',font=base_art.font(36,True),fill='#eef3fc')
    d.text((70,110),'Faktiske badgefiler · modellert 16 dp bildehøyde · ingen fysisk enhetstest',font=base_art.font(23),fill='#a8b6cc')
    geometry={}
    for i,name in enumerate(names):
        r=next(r for r in results if r['case']==name); ids=r['matched']; y=205+i*420
        d.text((70,y),names[name],font=base_art.font(29,True),fill='#eaf0fa')
        bar=base_art.badge_strip(ids,3)
        for n,(label,width) in enumerate([('iPhone / Mobile · start',326),('Google TV / TV · start',416)]):
            top=y+57+n*129
            d.rounded_rectangle((60,top,1440,top+112),radius=13,fill='#1d2531')
            d.text((80,top+10),label,font=base_art.font(20),fill='#9caecb')
            im.alpha_composite(bar.crop((0,0,min(bar.width,width*3),bar.height)),(80,top+42))
        geometry[name]={'mobileViewportDp':326,'tvViewportDp':416,'items':base_art.strip_geometry(ids,3)}
    d.text((70,1515),'Lyd, Dolby Vision og HDR står først. Resten av merkeraden nås med sveip / fokus-rulling.',font=base_art.font(22),fill='#a8b6cc')
    im.convert('RGB').save(PREVIEWS/'Nuvio_Alternative_streamcards.png',optimize=True)
    (ROOT/'badges/reports/alternative-layout.json').write_text(json.dumps(geometry,indent=2)+'\n',encoding='utf-8',newline='\n')


def small_sizes():
    base_art.image_for=image_for
    im=Image.new('RGBA',(1440,52*64+200),'#171c24'); d=ImageDraw.Draw(im)
    d.text((50,35),'ALLE 52 MERKER VED NUVIO-STØRRELSE',font=base_art.font(29,True),fill='white')
    d.text((50,88),'16 dp ved 1× og 3× raster · ikke en fysisk skjermtest',font=base_art.font(21),fill='#a9b7cc')
    for i,badge in enumerate(PACK['filters']):
        y=160+i*64
        d.text((50,y+9),badge['name'],font=base_art.font(21),fill='#dce5f2')
        im.alpha_composite(base_art.badge_strip([badge['id']],1),(480,y+12))
        im.alpha_composite(base_art.badge_strip([badge['id']],3),(780,y-6))
    im.convert('RGB').save(PREVIEWS/'Nuvio_Alternative_readability.png',optimize=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--json-only',action='store_true'); parser.add_argument('--assets-only',action='store_true'); args=parser.parse_args()
    if not args.json_only:
        render_assets()
    build_json()
    if not args.json_only and not args.assets_only:
        catalog(); examples(); small_sizes()
    print('Alternative style: 52 independent PNGs; same v3 rules and groups')
