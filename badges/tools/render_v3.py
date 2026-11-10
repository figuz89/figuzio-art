"""Deterministic v3-only metal treatment and honest, source-sized simulations.

Requires Pillow; run render_svg_masks.cjs first. No v2 file is written.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import subprocess
from io import BytesIO
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'badges/assets/v3_frameless'
PREVIEWS = ROOT / 'badges/previews/v3'
CACHE = ROOT / '.v3-cache'
PACK = json.loads((ROOT / 'badges/Figuz_Smart_Badges_v3.json').read_text(encoding='utf-8'))
BY_ID = {b['id']: b for b in PACK['filters']}
FONT_DIR = Path(os.environ.get('FIGUZ_FONT_DIR', 'C:/Windows/Fonts'))
OPTICAL_LOGOS = {'s-prime','s-disney','s-skyshowtime','s-paramount'}


def font(size, bold=False, narrow=False):
    filename = 'ARIALNB.TTF' if narrow else 'arialbd.ttf' if bold else 'arial.ttf'
    return ImageFont.truetype(str(FONT_DIR / filename), size)


def fit(im, max_w, max_h):
    scale = min(max_w / im.width, max_h / im.height)
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.LANCZOS)


def text_mask(text, narrow=False):
    f = font(224, bold=True, narrow=narrow)
    box = f.getbbox(text)
    im = Image.new('L', (box[2]-box[0]+16, box[3]-box[1]+16))
    ImageDraw.Draw(im).text((8-box[0],8-box[1]), text, font=f, fill=255, stroke_width=1)
    return im.crop(im.getbbox())


def metal(mask, content_height=56):
    # Palette sampled directly from high-alpha rows of v2 r-1080.png. The only
    # transformation on original logo sources is alpha geometry -> neutral metal.
    palette = [(255,255,255),(244,250,255),(218,228,240),(185,201,221),(203,216,230),(245,250,253),(211,220,231),(168,183,203),(141,160,186),(168,186,209),(198,214,234)]
    mask = mask.crop(mask.getbbox())
    mask = fit(mask, 408, content_height)
    # Preserve source proportions, leave 4 px at each side, and keep a common
    # 64 px canvas like the v2 audio assets. 2 px relief stays inside this canvas.
    canvas = Image.new('L', (mask.width+8, 64))
    y = (64-mask.height)//2-1
    canvas.paste(mask, (4,y))
    shadow_mask = ImageChops.offset(canvas, 0, 2)
    out = Image.new('RGBA', canvas.size)
    out.alpha_composite(Image.new('RGBA', canvas.size, (72,90,115,255)))
    out.putalpha(shadow_mask)
    gradient = Image.new('RGBA', canvas.size)
    draw = ImageDraw.Draw(gradient)
    for row in range(canvas.height):
        pos = max(0,min(10,(row-y)/max(1,mask.height-1)*10))
        lo, hi = math.floor(pos), min(10,math.ceil(pos))
        color = tuple(round(palette[lo][c]*(1-(pos-lo)) + palette[hi][c]*(pos-lo)) for c in range(3))
        draw.line((0,row,canvas.width,row), fill=(*color,255))
    gradient.putalpha(canvas)
    out.alpha_composite(gradient)
    # A restrained upper bevel, no rectangular border, glow box or background.
    upper_edge = ImageChops.subtract(canvas, ImageChops.offset(canvas, 0, 1)).point(lambda p: round(p*.36))
    light = Image.new('RGBA', out.size, (255,255,255,255))
    light.putalpha(upper_edge)
    out.alpha_composite(light)
    return out


def render_assets():
    for path in sorted((CACHE/'masks').glob('s-*.png')):
        with Image.open(path) as src:
            content_height = 60 if path.stem in OPTICAL_LOGOS else 56
            metal(src.convert('RGBA').getchannel('A'), content_height).save(ASSETS / path.name, optimize=True)
    labels = {'c-hevc':'HEVC','c-avc':'AVC','c-av1':'AV1','e-unrated':'Unrated','e-extended':'Extended','e-directors-cut':"Director’s Cut",'e-theatrical':'Theatrical','e-proper':'PROPER','e-repack':'REPACK','e-hybrid':'HYBRID'}
    for ident, label in labels.items():
        metal(text_mask(label, narrow=ident == 'e-directors-cut')).save(ASSETS / (ident+'.png'), optimize=True)


def source_manifest():
    svgl = 'https://raw.githubusercontent.com/pheralb/svgl/c0ec7ab121354ac1096b17b3aebbb293c8ce5600/static/library/'
    sources = {
        's-netflix': (svgl+'netflix-wordmark.svg','Netflix / SVGL; MIT collection, brand rights retained'),
        's-appletv': ('https://upload.wikimedia.org/wikipedia/commons/2/28/Apple_TV_Plus_Logo.svg','Apple Inc.; Wikimedia Commons PD-textlogo'),
        's-prime': (svgl+'prime-video.svg','Amazon / SVGL; MIT collection, brand rights retained'),
        's-disney': (svgl+'disneyplus.svg','Disney / SVGL; MIT collection, brand rights retained'),
        's-hbomax': ('https://upload.wikimedia.org/wikipedia/commons/7/7e/HBO_Max_May_2025_%28Horizontal%29.svg','Warner Bros. Discovery; Wikimedia Commons PD-textlogo'),
        's-skyshowtime': ('https://upload.wikimedia.org/wikipedia/commons/8/80/SkyShowtime_Logo.svg','Comcast / Paramount / SkyShowtime; Wikimedia Commons PD-textlogo'),
        's-paramount': ('https://upload.wikimedia.org/wikipedia/commons/4/4e/Paramount%2B_logo.svg','Paramount; Wikimedia Commons PD-textlogo'),
        's-peacock': ('https://upload.wikimedia.org/wikipedia/commons/2/20/NBCUniversal_Peacock_Logo_%282026%29.svg','NBCUniversal; Wikimedia Commons logo source'),
        's-hulu': (svgl+'hulu.svg','Hulu / SVGL; MIT collection, brand rights retained'),
    }
    entries={}
    for ident,(url,credit) in sources.items():
        path=ASSETS/'sources'/(ident+'.svg')
        entries[ident]={'path':path.relative_to(ROOT).as_posix(),'sourceURL':url,'credit':credit,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'transformation':'Original alpha geometry, aspect ratio preserved; v2-derived silver/blue palette and restrained relief; transparent PNG','faceHeightPx':60 if ident in OPTICAL_LOGOS else 56}
    (ASSETS/'sources/manifest.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def image_for(ident):
    badge = BY_ID[ident]
    if '/v3_frameless/' in badge['imageURL']:
        path = ASSETS / (ident+'.png')
    elif '/figuz89/figuzio-art/' in badge['imageURL']:
        path = ROOT / badge['imageURL'].split('/main/')[1]
    else:
        path = CACHE / 'images' / (ident+'.png')
    return Image.open(path).convert('RGBA')


def catalog():
    W = 1440
    im = Image.new('RGBA', (W,3800),(29,26,20,255))
    d = ImageDraw.Draw(im)
    d.text((72,46),'Figuz Smart Badges v3',font=font(40,True),fill='#ffffff')
    d.text((72,102),'Draft · 33 eksisterende + 19 nye · uendret v2-grafikk',font=font(22),fill='#b8bcc3')
    y = 174
    for group in PACK['groups']:
        d.text((72,y),group['name'],font=font(34,True),fill='#ffffff')
        y += 66
        x = 82
        h = 58
        for badge in [b for b in PACK['filters'] if b['groupId'] == group['id']]:
            pic = fit(image_for(badge['id']), 330,h)
            item_w = pic.width + 58
            if x+pic.width > W-72:
                x=82
                y+=96
            im.alpha_composite(pic,(x,y+(h-pic.height)//2))
            x+=item_w
        y += h+72
    d.text((72,y),'Metalliske logoer på transparent bakgrunn · Ingen fysisk enhetstest',font=font(19),fill='#a5a9b2')
    im.crop((0,0,W,y+74)).convert('RGB').save(PREVIEWS/'Figuz_Smart_Badges_v3.png', optimize=True)


def badge_strip(ids, scale=3, overrides=None):
    # Mirror 20 dp container, 16 dp image, 34–92 dp image width, 3 dp padding,
    # 4 dp gap. Use the full source bitmap, exactly as ContentScale.Fit does.
    tiles=[]
    for ident in ids:
        raw = overrides[ident] if overrides and ident in overrides else image_for(ident)
        image_w = max(34*scale,min(92*scale,round(raw.width/raw.height*16*scale)))
        pic=fit(raw,image_w,16*scale)
        tile=Image.new('RGBA',(image_w+6*scale,20*scale))
        tile.alpha_composite(pic,((tile.width-pic.width)//2,(tile.height-pic.height)//2))
        tiles.append(tile)
    out=Image.new('RGBA',(sum(t.width for t in tiles)+max(0,len(tiles)-1)*4*scale,20*scale))
    x=0
    for t in tiles:
        out.alpha_composite(t,(x,0)); x+=t.width+4*scale
    return out


def strip_geometry(ids, scale):
    x=0; items=[]
    for ident in ids:
        raw=image_for(ident)
        w=max(34*scale,min(92*scale,round(raw.width/raw.height*16*scale)))+6*scale
        items.append({'id':ident,'startDp':x/scale,'endDp':(x+w)/scale})
        x+=w+4*scale
    return items


def clipped_text(draw, text, xy, f, max_width, color):
    while draw.textlength(text,font=f)>max_width and len(text)>1:
        text=text[:-2]+'…'
    draw.text(xy,text,font=f,fill=color)


def simulations():
    sys.path.insert(0,str(ROOT/'badges/tests'))
    from test_v3 import FILMS
    results=json.loads((ROOT/'badges/reports/v3-filename-results.json').read_text(encoding='utf-8'))['results']
    film_hits={r['case']:r['matched'] for r in results if r['case'] in ['film-A','film-B','film-C']}
    titles=['Animals (2026)','Kingsman: The Secret Service (2014)','Mission: Impossible II (2000)']
    # TV source: 40% title pane + 60% stream pane. At 960 logical dp,
    # 576 - 48 outer - 32 panel - 32 card - 48 addon slot = 416 badge dp.
    # Each full frame is a model, not a screenshot of the application.
    widths={}; tv_frames=[]
    for i,(letter,filename,_) in enumerate(FILMS):
        ids=film_hits['film-'+letter]
        tv=Image.new('RGBA',(1920,1080),'#101217'); d=ImageDraw.Draw(tv)
        d.text((72,46),'Nuvio TV · Google TV Streamer — simulering',font=font(28,True),fill='#e9edf5')
        d.text((72,92),'Ingen fysisk enhetstest · modell ved 960 × 540 dp / 2× raster',font=font(21),fill='#aab2c1')
        # Left title pane, 40% of total screen width.
        words=titles[i].split(); lines=[]; line=''
        for word in words:
            if d.textlength((line+' '+word).strip(),font=font(45,True))>600:
                lines.append(line); line=word
            else: line=(line+' '+word).strip()
        lines.append(line)
        for n,line in enumerate(lines): d.text((96,410+n*64),line,font=font(45,True),fill='#f0f3f8')
        d.text((96,620),'Film '+letter+' · oppgitt filnavn',font=font(24),fill='#9ca9bc')
        # RightStreamSection: 60%, 48 dp right margin, 16 dp panel/card padding.
        d.rounded_rectangle((768,174,1824,962),radius=28,fill='#171c24')
        d.text((800,212),'Strømmer',font=font(32,True),fill='#e7ecf5')
        d.text((800,268),'AIOStreams',font=font(25),fill='#a6bad5')
        for row,offset in [(0,0),(1,max(0,badge_strip(ids,2).width-832))]:
            y=334+row*252
            d.text((800,y-30),'Start av raden' if row==0 else 'Samme rad etter rulling med fokus',font=font(20),fill='#9faec3')
            d.rounded_rectangle((800,y,1792,y+190),radius=14,fill='#202732',outline='#759bcf' if row==0 else '#354052',width=2)
            d.text((832,y+20),'Eksempel fra AIOStreams',font=font(25,True),fill='#f2f5fa')
            clipped_text(d,filename,(832,y+64),font(19),832,'#aab3c2')
            strip=badge_strip(ids,2)
            tv.alpha_composite(strip.crop((offset,0,min(strip.width,offset+832),strip.height)),(832,y+120))
            d.text((1702,y+120),'AIO',font=font(20),fill='#8b9bb0')
        d.text((800,916),'416 dp merkerad · fokus gir marquee; ellers klippes raden',font=font(19),fill='#aab2c1')
        tv.convert('RGB').save(PREVIEWS/f'Nuvio_TV_{letter}.png',optimize=True)
        tv_frames.append(tv.resize((1280,720),Image.Resampling.LANCZOS))
        tv_items=strip_geometry(ids,2); mobile_items=strip_geometry(ids,3)
        widths[letter]={'badgeRowDp':badge_strip(ids,2).width/2,'tvAvailableDp':416,'mobileAvailableDp':326,'tvInitialFullyVisible':[x['id'] for x in tv_items if x['endDp']<=416],'mobileInitialFullyVisible':[x['id'] for x in mobile_items if x['endDp']<=326],'tvGeometry':tv_items,'mobileGeometry':mobile_items}
    composite=Image.new('RGBA',(1280,2160),'#101217')
    for i,frame in enumerate(tv_frames): composite.alpha_composite(frame,(0,i*720))
    composite.convert('RGB').save(PREVIEWS/'Nuvio_streamlist_TV_simulation.png',optimize=True)

    mobile=Image.new('RGBA',(1170,2260),'#101217'); d=ImageDraw.Draw(mobile)
    d.text((72,58),'Nuvio',font=font(48,True),fill='#f3f5fa')
    d.text((72,132),'iPhone · Nuvio Mobile · SIMULERING',font=font(28,True),fill='#a8bbd8')
    d.text((72,182),'Tre separate filmeksempler',font=font(28),fill='#adb5c4')
    d.text((72,224),'Ingen fysisk enhetstest',font=font(26),fill='#adb5c4')
    for i,(letter,filename,_) in enumerate(FILMS):
        y=330+i*568
        clipped_text(d,f'{letter}  {titles[i]}',(72,y),font(37,True),1026,'#edf1f7')
        d.rounded_rectangle((60,y+82,1110,y+470),radius=28,fill='#1b2029',outline='#354052',width=3)
        d.text((96,y+116),'AIOStreams',font=font(35,True),fill='#ffffff')
        # Filename text is representational; badge dimensions below follow source.
        clipped_text(d,filename,(96,y+185),font(25),978,'#a9b2c2')
        ids=film_hits['film-'+letter]
        strip=badge_strip(ids,scale=3)
        visible=strip.crop((0,0,min(strip.width,978),strip.height))
        mobile.alpha_composite(visible,(90,y+257))
        if strip.width>978:
            d.text((96,y+346),'Sveip merkeraden →',font=font(27),fill='#a8bbd8')
            d.text((96,y+390),'Visningen her er ved starten av raden.',font=font(23),fill='#9aa5b7')
        else:
            d.text((96,y+353),'Alle treff vises i denne bredden.',font=font(25),fill='#9aa5b7')
    d.text((72,2100),'16 dp bildehøyde · 34–92 dp bildebredde',font=font(25),fill='#9aa5b7')
    d.text((72,2146),'Lyd, Dolby Vision og HDR prioriteres først.',font=font(25),fill='#9aa5b7')
    mobile.convert('RGB').save(PREVIEWS/'Nuvio_streamlist_mobile_simulation.png',optimize=True)
    (ROOT/'badges/reports/v3-layout-measurements.json').write_text(json.dumps(widths,indent=2)+'\n',encoding='utf-8')
    # Critical information in all three real filenames fits both initial viewports.
    for letter,ids in film_hits.items():
        key=letter.removeprefix('film-')
        critical=[ident for ident in ids if BY_ID[ident]['groupId'] in ['gdolby','gdts','gvision','ghdr']]
        for field in ['tvInitialFullyVisible','mobileInitialFullyVisible']:
            assert set(critical)<=set(widths[key][field]),(key,field,critical)
    stress=next(r for r in results if r['case']=='layout-stress')
    stress_preview(stress['matched'])


def stress_preview(ids):
    im=Image.new('RGBA',(1440,1160),'#13171f'); d=ImageDraw.Draw(im)
    d.text((60,42),'Mange samtidige merker — simulert utsnitt',font=font(34,True),fill='white')
    d.text((60,100),'Syntetisk 12-badge-filnavn · 16 dp bildehøyde · ingen fysisk enhetstest',font=font(21),fill='#abb7ca')
    y=186
    for label,available in [('iPhone / Nuvio Mobile',326),('Google TV Streamer / Nuvio TV',416)]:
        d.text((60,y),label,font=font(27,True),fill='#e3eaf6'); y+=60
        bar=badge_strip(ids,3)
        for position,offset in [('Start',0),('Etter sveip / fokus-rulling',max(0,bar.width-available*3))]:
            d.text((60,y),position,font=font(21),fill='#a9bbd7')
            im.alpha_composite(bar.crop((offset,0,min(bar.width,offset+available*3),bar.height)),(60,y+40))
            y+=126
        d.text((60,y),'Lyd + Dolby Vision + HDR før oppløsning, kilde og utgaver.',font=font(20),fill='#abb7ca')
        y+=90
    im.crop((0,0,1440,y+40)).convert('RGB').save(PREVIEWS/'Nuvio_priority_stress_simulation.png',optimize=True)


def logo_comparison():
    baseline='41a1870f67a6cda74b098789760ced582d0e5639'
    im=Image.new('RGBA',(1440,950),'#1d1a14'); d=ImageDraw.Draw(im)
    d.text((60,40),'Målrettet logofinjustering',font=font(34,True),fill='white')
    d.text((60,96),'Samme originale former, proporsjoner og gradient · 16 dp ved 4× raster',font=font(20),fill='#b6bfcc')
    d.text((470,158),'Før',font=font(26,True),fill='white'); d.text((930,158),'Etter',font=font(26,True),fill='white')
    audit=[]
    for i,ident in enumerate(['s-netflix','s-prime','s-disney','s-skyshowtime','s-paramount']):
        data=subprocess.check_output(['git','show',f'{baseline}:badges/assets/v3_frameless/{ident}.png'],cwd=ROOT)
        before=Image.open(BytesIO(data)).convert('RGBA'); after=image_for(ident)
        y=230+i*128
        d.text((60,y+12),BY_ID[ident]['name'],font=font(23),fill='#e2e5eb')
        im.alpha_composite(badge_strip([ident],4,{ident:before}),(460,y))
        im.alpha_composite(badge_strip([ident],4),(920,y))
        a=before.getchannel('A').getbbox(); b=after.getchannel('A').getbbox()
        audit.append({'id':ident,'beforeSize':list(before.size),'afterSize':list(after.size),'beforeInkHeightPx':a[3]-a[1],'afterInkHeightPx':b[3]-b[1],'scaleOfFace':60/56 if ident in OPTICAL_LOGOS else 1,'originalVectorUnchanged':True})
    d.text((60,900),'Fire logoer: 56 → 60 px logoform på samme 64 px lerret. Netflix-referansen er uendret.',font=font(21),fill='#b6bfcc')
    im.convert('RGB').save(PREVIEWS/'Streaming_logo_before_after.png',optimize=True)
    (ROOT/'badges/reports/v3-logo-sizing.json').write_text(json.dumps({'baselineCommit':baseline,'method':'Uniform scaling of original SVG alpha; 4 px face-height increase, unchanged gradient and 2 px relief; no SVG path edits','logos':audit},indent=2)+'\n',encoding='utf-8')


def readability():
    im=Image.new('RGBA',(1440,2180),'#1b1e24'); d=ImageDraw.Draw(im)
    d.text((64,42),'Lesbarhet ved Nuvios bildestørrelse',font=font(34,True),fill='white')
    d.text((64,100),'Venstre: 16 dp / 1× raster · Høyre: 3× raster for mobil · ikke en fysisk skjermtest',font=font(20),fill='#b9c1ce')
    y=180
    ids=[b['id'] for b in PACK['filters'] if '/v3_frameless/' in b['imageURL']]
    for ident in ids:
        d.text((64,y),BY_ID[ident]['name'],font=font(22),fill='#d8dce6')
        # Keep the 1× swatch native-sized so the preview does not hide tiny glyphs.
        im.alpha_composite(badge_strip([ident],1),(490,y+5))
        im.alpha_composite(badge_strip([ident],3),(760,y-8))
        y+=90
    im.crop((0,0,1440,y+36)).convert('RGB').save(PREVIEWS/'Nuvio_badge_readability.png',optimize=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--assets-only',action='store_true'); args=parser.parse_args()
    PREVIEWS.mkdir(parents=True,exist_ok=True)
    source_manifest(); render_assets()
    if not args.assets_only:
        catalog(); simulations(); readability(); logo_comparison()
    print('Rendered v3 assets' + ('' if args.assets_only else ' and updated PNG previews'))
