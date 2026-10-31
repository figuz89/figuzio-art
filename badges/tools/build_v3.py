"""Build the additive v3 pack; v2 and every legacy image URL are immutable inputs."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_REF = '1da3b7829b1059bf4fd59ef5dea07d72c701d6a1'
ASSET_BASE = f'https://raw.githubusercontent.com/figuz89/figuzio-art/{ASSET_REF}/badges/assets/v3_frameless'


def token(body):
    return rf'(?<![a-z0-9])(?:{body})(?![a-z0-9])'


def rule(required, excluded=()):
    return '(?i)^' + ''.join(rf'(?=[\s\S]*{x})' for x in required) + ''.join(rf'(?![\s\S]*{x})' for x in excluded) + r'[\s\S]*$'


def build():
    original = json.loads((ROOT / 'badges/Figuz_Smart_Badges_v2.json').read_text(encoding='utf-8'))
    pack = copy.deepcopy(original)
    by_id = {b['id']: b for b in pack['filters']}

    # The clients inspect all regex hits: groupId is not an exclusivity mechanism.
    # Keep Remux + BluRay together, but suppress lower source tiers on one candidate.
    remux = token('remux')
    bluray = token(r'blu[ ._-]?ray|bdmv')
    webdl = token(r'web[ ._-]?dl')
    webrip = token(r'web[ ._-]?rip')
    for ident, pat in [('q-remux', remux), ('q-bluray', bluray)]:
        by_id[ident]['pattern'] = '(?i)' + pat
    by_id['q-webdl']['pattern'] = rule([webdl], [remux, bluray])
    by_id['q-webrip']['pattern'] = rule([webrip], [remux, bluray, webdl])

    higher = []
    for ident, body in [('r-2160', r'2160[pi]?|4k|uhd'), ('r-1440', r'1440[pi]?'), ('r-1080', r'1080[pi]?'), ('r-720', r'720[pi]?'), ('r-480', r'480[pi]?')]:
        part = token(body)
        by_id[ident]['pattern'] = rule([part], higher)
        higher.append(part)

    hdrp = token(r'hdr[ ._-]?10(?:\+|plus|p)')
    hdr10 = token(r'hdr[ ._-]?10')
    hdr = token('hdr')
    by_id['v-hdr10plus']['pattern'] = '(?i)' + hdrp
    by_id['v-hdr10']['pattern'] = rule([hdr10], [hdrp])
    by_id['v-hdr']['pattern'] = rule([hdr], [hdrp, hdr10])
    by_id['v-sdr']['pattern'] = rule([token('sdr')], [hdrp, hdr10, hdr])
    by_id['v-imax']['pattern'] = rule([token('imax')], [token(r'imax[ ._-]?enhanced')])

    # Audio tokens allow attached channels, but never arbitrary numeric suffixes.
    channel = r'(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)'
    tail = rf'(?={channel}(?![a-z0-9])|[^a-z0-9]|$)'
    thd = r'(?<![a-z0-9])true[ ._-]?hd' + tail
    ddp = r'(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)' + tail
    atmos = token('atmos')
    # Proximity associates Atmos with a codec only across separators/channels.
    # Coexisting TrueHD and DD+ remains the original MIXED warning, not a guess.
    def pair(codec):
        return rf'(?:{codec}(?:{channel})?[ ._:+-]+{atmos}|{atmos}[ ._:+-]+{codec})'
    mixed = [atmos, thd, ddp]
    by_id['a-atmos-multi']['pattern'] = rule(mixed)
    by_id['a-truehd-atmos']['pattern'] = rule([pair(thd)], [ddp])
    by_id['a-ddp-atmos']['pattern'] = rule([pair(ddp)], [thd])
    # Explicitly exclude the mixed case while preserving the unknown-codec state.
    by_id['a-atmos-unknown']['pattern'] = '(?i)^' + rf'(?=[\s\S]*{atmos})(?!' + rf'(?=[\s\S]*{thd})(?=[\s\S]*{ddp})' + ')' + rf'(?![\s\S]*{pair(thd)})(?![\s\S]*{pair(ddp)})[\s\S]*$'
    by_id['a-truehd']['pattern'] = rule([thd], [atmos])
    by_id['a-ddplus']['pattern'] = rule([ddp], [atmos, thd])
    dd = r'(?<![a-z0-9])(?:ac[ ._-]?3|dd|dolby[ ._-]?digital)(?![ ._-]?plus)(?!\+)' + tail
    by_id['a-dd']['pattern'] = rule([dd], [atmos, thd, ddp])

    dtsx = token(r'dts[ ._:-]?x')
    dtsma = r'(?<![a-z0-9])dts[ ._-]?(?:hd[ ._-]?)?(?:ma|master[ ._-]?audio)' + tail
    dtshd = r'(?<![a-z0-9])dts[ ._-]?hd' + tail
    dts = r'(?<![a-z0-9])dts' + tail
    for ident, part, higher in [('a-dtsx', dtsx, []), ('a-dtsma', dtsma, [dtsx]), ('a-dtshd', dtshd, [dtsx, dtsma]), ('a-dts', dts, [dtsx, dtsma, dtshd])]:
        by_id[ident]['pattern'] = rule([part], higher)

    # Channel formats and within-category order are v2's; suppress lower hits.
    higher = []
    for ident in ['ch-71', 'ch-61', 'ch-51', 'ch-20', 'ch-10']:
        part = by_id[ident]['pattern'].removeprefix('(?i)')
        by_id[ident]['pattern'] = rule([part], higher)
        higher.append(part)

    def add(ident, name, group, pattern):
        badge = copy.deepcopy(original['filters'][0])
        badge.update(id=ident, name=name, groupId=group, pattern=pattern, imageURL=f'{ASSET_BASE}/{ident}.png')
        by_id[ident] = badge
        return badge

    services = [
        ('s-netflix', 'Netflix', 'NF|NFLX', 'Netflix'),
        ('s-appletv', 'Apple TV+', 'ATVP', r'Apple[ ._-]?TV\+'),
        ('s-prime', 'Amazon Prime Video', 'AMZN', r'Amazon[ ._-]?Prime[ ._-]?Video|Prime[ ._-]?Video|Amazon'),
        ('s-disney', 'Disney+', 'DSNP', r'Disney\+|Disney[ ._-]?Plus'),
        ('s-hbomax', 'HBO Max', 'HMAX|HBOMAX', r'HBO[ ._-]?Max'),
        ('s-skyshowtime', 'SkyShowtime', 'SKYSHOWTIME', r'SkyShowtime'),
        ('s-paramount', 'Paramount+', 'PMTP', r'Paramount\+|Paramount[ ._-]?Plus'),
        ('s-peacock', 'Peacock', 'PCOK', r'Peacock'),
        ('s-hulu', 'Hulu', 'HULU', r'Hulu'),
    ]
    web = r'web[ ._-]?(?:dl|rip)'
    sep = r'[ ._-]+'
    resolution = r'(?:2160|1440|1080|720|480)p'
    for ident, name, aliases, full in services:
        # Short tags are deliberately tied to WEB source metadata. Plain MAX,
        # ATV, NF in prose, titles named Hulu, etc. are not identifiers.
        source_tag = token(rf'(?:{aliases}){sep}(?:{resolution}{sep})?{web}|{web}{sep}(?:{resolution}{sep})?(?:{aliases})')
        labelled = rf'(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:{full})(?![a-z0-9+])'
        add(ident, name, 'gstreaming', '(?i)(?:' + source_tag + '|' + labelled + ')')

    codec_specs = [('c-av1', 'AV1', 'av1'), ('c-hevc', 'HEVC / H.265', r'hevc|h[ ._-]?265|x[ ._-]?265'), ('c-avc', 'AVC / H.264', r'avc|h[ ._-]?264|x[ ._-]?264')]
    higher = []
    for ident, name, body in codec_specs:
        part = token(body)
        add(ident, name, 'gcodec', rule([part], higher))
        higher.append(part)

    metadata_anchor = token(r'(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip)')
    for ident, name, body in [
        ('e-unrated', 'Unrated', 'unrated'),
        ('e-extended', 'Extended', r'extended(?:[ ._-]?(?:cut|edition))?'),
        ('e-directors-cut', "Director’s Cut", r'director(?:[’\x27]?s)?[ ._-]+cut'),
        ('e-theatrical', 'Theatrical', r'theatrical(?:[ ._-]?(?:cut|edition))?'),
        ('e-proper', 'PROPER', r'proper[2-9]?'),
        ('e-repack', 'REPACK', r'repack[2-9]?'),
        ('e-hybrid', 'HYBRID', 'hybrid'),
    ]:
        add(ident, name, 'gseadex', '(?i)' + metadata_anchor + r'[\s\S]*?' + token(body))

    # Audio and channels stay ahead of descriptive additions in clipped TV rows.
    # Original within-category priority is unchanged, including MIXED as a warning.
    order = [b['id'] for b in original['filters'] if b['groupId'] in ('gdolby', 'gdts', 'gc')]
    order += [b['id'] for b in original['filters'] if b['groupId'] not in ('gdolby', 'gdts', 'gc')]
    order += [x[0] for x in services] + [x[0] for x in codec_specs]
    order += ['e-unrated', 'e-extended', 'e-directors-cut', 'e-theatrical', 'e-proper', 'e-repack', 'e-hybrid']
    pack['filters'] = [by_id[k] for k in order]
    for ident, name in [('gstreaming', 'Streaming Services'), ('gcodec', 'Video Codec')]:
        group = copy.deepcopy(original['groups'][-1])
        group.update(id=ident, name=name)
        pack['groups'].append(group)
    destination = ROOT / 'badges/Figuz_Smart_Badges_v3.json'
    destination.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return pack


if __name__ == '__main__':
    result = build()
    print(f"Built {len(result['filters'])} badges in {len(result['groups'])} groups")
