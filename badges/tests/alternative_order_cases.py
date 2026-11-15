"""Explicit order regressions from the user's screenshot and the three films."""
from itertools import permutations

ORDER_CASES=[]


def add(name,candidates,expected):
    ORDER_CASES.append({'name':name,'candidates':candidates,'expected':expected,'required':[],'absent':[]})


SCREENSHOT_ROWS=[
    ('His.Dark.Materials.S02.GERMAN.DUBBED.DL.EAC3.2160p.DV.HDR.WEB.H265-SHITASTE',
     ['r-2160','v-dolbyvision','v-hdr','a-ddplus','q-webdl','c-hevc']),
    ('His.Dark.Materials.S02E07.Aesahaettr.2160p.MAX.WEB-DL.DTS-HD.MA.5.1.DoVi.H.265-NTb',
     ['r-2160','v-dolbyvision','a-dtsma','ch-51','q-webdl','c-hevc']),
    ('His.Dark.Materials.S02E07.Aesahaettr.REPACK.2160p.MAX.WEB-DL.DTS-HD.MA.5.1.HDR.DoVi.H.265-NTb',
     ['r-2160','v-dolbyvision','v-hdr','a-dtsma','ch-51','q-webdl','e-repack','c-hevc']),
]
for index,(filename,expected) in enumerate(SCREENSHOT_ROWS,1):
    fields=[filename,'Ninja Central 2160p NNTP','WEB-DL H.265']
    for order in permutations(range(3)):
        add(f'screenshot-{index}-fields-'+''.join(map(str,order)),[fields[i] for i in order],expected)

add('order-film-A',['Animals.2026.2160p.NF.WEB-DL.DV.HDR.MULTi'],
    ['r-2160','v-dolbyvision','v-hdr','q-webdl','s-netflix'])
add('order-film-B',['Kingsman.The.Secret.Service.2014.Unrated.UHD.BluRay.2160p.DTS-HD.MA.7.1.DV.HEVC.HYBRID.REMUX-FraMeSToR'],
    ['r-2160','v-dolbyvision','a-dtsma','ch-71','q-remux','q-bluray','e-unrated','e-hybrid','c-hevc'])
add('order-film-C',['Mission.Impossible.II.2000.USA.BluRay.Remux.UHD.DoVi.HDR10.2160p.TrueHD5.1-CHD'],
    ['r-2160','v-dolbyvision','v-hdr10','a-truehd','ch-51','q-remux','q-bluray'])
add('order-no-resolution',['Film.2025.WEB-DL.DDP5.1.H264'],
    ['a-ddplus','ch-51','q-webdl','c-avc'])
add('order-1080-first',['Film.2025.WEB-DL.1080p.DDP5.1.H264'],
    ['r-1080','a-ddplus','ch-51','q-webdl','c-avc'])
