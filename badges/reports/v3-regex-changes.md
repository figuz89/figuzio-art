# Full v3 regex audit

30 documented v2 regex corrections; 19 additions. No legacy artwork, names, IDs, style fields or group membership changed.

Each regex runs independently against every Nuvio candidate. Exclusions are local to a candidate; see the compatibility limits in [the v3 report](../V3_REPORT.md).

## a-atmos-multi (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:\batmos(?=\b|[0-9])))(?=[\s\S]*(?:\btrue[ ._-]?hd(?=\b|[0-9])))(?=[\s\S]*(?:(?:\bddp(?=\b|[0-9])|\bdd\+|\be[ ._-]?ac[ ._-]?3(?=\b|[0-9])|\bec[ ._-]?3(?=\b|[0-9])|\bdolby[ ._-]?digital[ ._-]?plus\b)))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:atmos)(?![a-z0-9]))(?=[\s\S]*(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?=[\s\S]*(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## a-truehd-atmos (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:\batmos(?=\b|[0-9])))(?=[\s\S]*(?:\btrue[ ._-]?hd(?=\b|[0-9])))(?![\s\S]*(?:(?:\bddp(?=\b|[0-9])|\bdd\+|\be[ ._-]?ac[ ._-]?3(?=\b|[0-9])|\bec[ ._-]?3(?=\b|[0-9])|\bdolby[ ._-]?digital[ ._-]?plus\b)))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?:(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)(?:(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?))?[ ._:+-]+(?<![a-z0-9])(?:atmos)(?![a-z0-9])|(?<![a-z0-9])(?:atmos)(?![a-z0-9])[ ._:+-]+(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)))(?![\s\S]*(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## a-ddp-atmos (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:\batmos(?=\b|[0-9])))(?=[\s\S]*(?:(?:\bddp(?=\b|[0-9])|\bdd\+|\be[ ._-]?ac[ ._-]?3(?=\b|[0-9])|\bec[ ._-]?3(?=\b|[0-9])|\bdolby[ ._-]?digital[ ._-]?plus\b)))(?![\s\S]*(?:\btrue[ ._-]?hd(?=\b|[0-9])))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?:(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)(?:(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?))?[ ._:+-]+(?<![a-z0-9])(?:atmos)(?![a-z0-9])|(?<![a-z0-9])(?:atmos)(?![a-z0-9])[ ._:+-]+(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)))(?![\s\S]*(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## a-atmos-unknown (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:\batmos(?=\b|[0-9])))(?![\s\S]*(?:\btrue[ ._-]?hd(?=\b|[0-9])))(?![\s\S]*(?:(?:\bddp(?=\b|[0-9])|\bdd\+|\be[ ._-]?ac[ ._-]?3(?=\b|[0-9])|\bec[ ._-]?3(?=\b|[0-9])|\bdolby[ ._-]?digital[ ._-]?plus\b)))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:atmos)(?![a-z0-9]))(?!(?=[\s\S]*(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?=[\s\S]*(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)))(?![\s\S]*(?:(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)(?:(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?))?[ ._:+-]+(?<![a-z0-9])(?:atmos)(?![a-z0-9])|(?<![a-z0-9])(?:atmos)(?![a-z0-9])[ ._:+-]+(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)))(?![\s\S]*(?:(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)(?:(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?))?[ ._:+-]+(?<![a-z0-9])(?:atmos)(?![a-z0-9])|(?<![a-z0-9])(?:atmos)(?![a-z0-9])[ ._:+-]+(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$)))[\s\S]*$
```

## a-truehd (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:\btrue[ ._-]?hd(?=\b|[0-9])))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:atmos)(?![a-z0-9]))[\s\S]*$
```

## a-ddplus (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:(?:\bddp(?=\b|[0-9])|\bdd\+|\be[ ._-]?ac[ ._-]?3(?=\b|[0-9])|\bec[ ._-]?3(?=\b|[0-9])|\bdolby[ ._-]?digital[ ._-]?plus\b)))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:atmos)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## a-dd (gdolby)

Boundary-safe tokens accept attached channels. Atmos requires its own token; codec-specific Atmos additionally requires adjacency through separators/optional channels. Coexisting TrueHD and DD+ keeps the original MIXED warning. Lower Dolby tiers explicitly exclude higher evidence.

v2:

```regex
(?i)^(?=[\s\S]*(?:(?:\bac[ ._-]?3\b|\bdd(?:[ ._-]?[257][ ._-]?[01])?\b|\bdolby[ ._-]?digital\b)))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:ac[ ._-]?3|dd|dolby[ ._-]?digital)(?![ ._-]?plus)(?!\+)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:atmos)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])true[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:ddp|dd\+|e[ ._-]?ac[ ._-]?3|ec[ ._-]?3|dolby[ ._-]?digital[ ._-]?plus)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## a-dtsx (gdts)

DTS:X, DTS-HD MA/Master Audio, DTS-HD and DTS use distinct tokens and explicit higher-tier exclusions. Plain DTS-HD cannot satisfy MA.

v2:

```regex
(?i)^(?=[\s\S]*(?:\bdts[ ._:-]?x\b))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:dts[ ._:-]?x)(?![a-z0-9]))[\s\S]*$
```

## a-dtsma (gdts)

DTS:X, DTS-HD MA/Master Audio, DTS-HD and DTS use distinct tokens and explicit higher-tier exclusions. Plain DTS-HD cannot satisfy MA.

v2:

```regex
(?i)^(?=[\s\S]*(?:\bdts[ ._-]?(?:hd[ ._-]?)?ma\b))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])dts[ ._-]?(?:hd[ ._-]?)?(?:ma|master[ ._-]?audio)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:dts[ ._:-]?x)(?![a-z0-9]))[\s\S]*$
```

## a-dtshd (gdts)

DTS:X, DTS-HD MA/Master Audio, DTS-HD and DTS use distinct tokens and explicit higher-tier exclusions. Plain DTS-HD cannot satisfy MA.

v2:

```regex
(?i)^(?=[\s\S]*(?:\bdts[ ._-]?hd\b))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])dts[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:dts[ ._:-]?x)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])dts[ ._-]?(?:hd[ ._-]?)?(?:ma|master[ ._-]?audio)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## a-dts (gdts)

DTS:X, DTS-HD MA/Master Audio, DTS-HD and DTS use distinct tokens and explicit higher-tier exclusions. Plain DTS-HD cannot satisfy MA.

v2:

```regex
(?i)^(?=[\s\S]*(?:\bdts\b))[\s\S]*$
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])dts(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])(?:dts[ ._:-]?x)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])dts[ ._-]?(?:hd[ ._-]?)?(?:ma|master[ ._-]?audio)(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))(?![\s\S]*(?<![a-z0-9])dts[ ._-]?hd(?=(?:[ ._-]?[12567][ ._]?[01](?:[ ._]?[24])?)(?![a-z0-9])|[^a-z0-9]|$))[\s\S]*$
```

## v-hdr10plus (ghdr)

Explicit exclusion of higher HDR tiers prevents HDR10+/HDR10/HDR/SDR duplicates in a candidate; original priority and separate Dolby Vision group retained.

v2:

```regex
(?i)\bhdr[ ._-]?10(?:\+|plus|p)(?![a-z0-9])
```

v3:

```regex
(?i)(?<![a-z0-9])(?:hdr[ ._-]?10(?:\+|plus|p))(?![a-z0-9])
```

## v-hdr10 (ghdr)

Explicit exclusion of higher HDR tiers prevents HDR10+/HDR10/HDR/SDR duplicates in a candidate; original priority and separate Dolby Vision group retained.

v2:

```regex
(?i)\bhdr[ ._-]?10(?![a-z0-9+])
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:hdr[ ._-]?10)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hdr[ ._-]?10(?:\+|plus|p))(?![a-z0-9]))[\s\S]*$
```

## v-hdr (ghdr)

Explicit exclusion of higher HDR tiers prevents HDR10+/HDR10/HDR/SDR duplicates in a candidate; original priority and separate Dolby Vision group retained.

v2:

```regex
(?i)\bhdr\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:hdr)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hdr[ ._-]?10(?:\+|plus|p))(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hdr[ ._-]?10)(?![a-z0-9]))[\s\S]*$
```

## v-sdr (ghdr)

Explicit exclusion of higher HDR tiers prevents HDR10+/HDR10/HDR/SDR duplicates in a candidate; original priority and separate Dolby Vision group retained.

v2:

```regex
(?i)\bsdr\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:sdr)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hdr[ ._-]?10(?:\+|plus|p))(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hdr[ ._-]?10)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hdr)(?![a-z0-9]))[\s\S]*$
```

## ch-71 (gc)

Original channel recognizers retained inside explicit higher-channel exclusions; v2 order 7.1 > 6.1 > 5.1 > 2.0 > 1.0 retained.

v2:

```regex
(?i)(?:^|[^0-9])7[. _]1(?![0-9])
```

v3:

```regex
(?i)^(?=[\s\S]*(?:^|[^0-9])7[. _]1(?![0-9]))[\s\S]*$
```

## ch-61 (gc)

Original channel recognizers retained inside explicit higher-channel exclusions; v2 order 7.1 > 6.1 > 5.1 > 2.0 > 1.0 retained.

v2:

```regex
(?i)(?:^|[^0-9])6[. _]1(?![0-9])
```

v3:

```regex
(?i)^(?=[\s\S]*(?:^|[^0-9])6[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])7[. _]1(?![0-9]))[\s\S]*$
```

## ch-51 (gc)

Original channel recognizers retained inside explicit higher-channel exclusions; v2 order 7.1 > 6.1 > 5.1 > 2.0 > 1.0 retained.

v2:

```regex
(?i)(?:^|[^0-9])5[. _]1(?![0-9])
```

v3:

```regex
(?i)^(?=[\s\S]*(?:^|[^0-9])5[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])7[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])6[. _]1(?![0-9]))[\s\S]*$
```

## ch-20 (gc)

Original channel recognizers retained inside explicit higher-channel exclusions; v2 order 7.1 > 6.1 > 5.1 > 2.0 > 1.0 retained.

v2:

```regex
(?i)(?:^|[^0-9])2[. _]0(?![0-9])
```

v3:

```regex
(?i)^(?=[\s\S]*(?:^|[^0-9])2[. _]0(?![0-9]))(?![\s\S]*(?:^|[^0-9])7[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])6[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])5[. _]1(?![0-9]))[\s\S]*$
```

## ch-10 (gc)

Original channel recognizers retained inside explicit higher-channel exclusions; v2 order 7.1 > 6.1 > 5.1 > 2.0 > 1.0 retained.

v2:

```regex
(?i)(?:^|[^0-9])1[. _]0(?![0-9])
```

v3:

```regex
(?i)^(?=[\s\S]*(?:^|[^0-9])1[. _]0(?![0-9]))(?![\s\S]*(?:^|[^0-9])7[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])6[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])5[. _]1(?![0-9]))(?![\s\S]*(?:^|[^0-9])2[. _]0(?![0-9]))[\s\S]*$
```

## r-2160 (gr)

Alphanumeric token boundaries accept underscores; explicit higher-resolution exclusions preserve v2 priority without assuming group exclusivity.

v2:

```regex
(?i)\b(?:2160[pi]?|4k|uhd)\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:2160[pi]?|4k|uhd)(?![a-z0-9]))[\s\S]*$
```

## r-1440 (gr)

Alphanumeric token boundaries accept underscores; explicit higher-resolution exclusions preserve v2 priority without assuming group exclusivity.

v2:

```regex
(?i)\b1440[pi]?\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:1440[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:2160[pi]?|4k|uhd)(?![a-z0-9]))[\s\S]*$
```

## r-1080 (gr)

Alphanumeric token boundaries accept underscores; explicit higher-resolution exclusions preserve v2 priority without assuming group exclusivity.

v2:

```regex
(?i)\b1080[pi]?\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:1080[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:2160[pi]?|4k|uhd)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:1440[pi]?)(?![a-z0-9]))[\s\S]*$
```

## r-720 (gr)

Alphanumeric token boundaries accept underscores; explicit higher-resolution exclusions preserve v2 priority without assuming group exclusivity.

v2:

```regex
(?i)\b720[pi]?\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:720[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:2160[pi]?|4k|uhd)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:1440[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:1080[pi]?)(?![a-z0-9]))[\s\S]*$
```

## r-480 (gr)

Alphanumeric token boundaries accept underscores; explicit higher-resolution exclusions preserve v2 priority without assuming group exclusivity.

v2:

```regex
(?i)\b480[pi]?\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:480[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:2160[pi]?|4k|uhd)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:1440[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:1080[pi]?)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:720[pi]?)(?![a-z0-9]))[\s\S]*$
```

## q-remux (gq)

Alphanumeric token boundaries accept underscores. Remux and BluRay intentionally coexist; lower WEB sources are excluded when a higher source is present in the same candidate.

v2:

```regex
(?i)\bremux\b
```

v3:

```regex
(?i)(?<![a-z0-9])(?:remux)(?![a-z0-9])
```

## q-bluray (gq)

Alphanumeric token boundaries accept underscores. Remux and BluRay intentionally coexist; lower WEB sources are excluded when a higher source is present in the same candidate.

v2:

```regex
(?i)\b(?:blu[ ._-]?ray|bdmv)\b
```

v3:

```regex
(?i)(?<![a-z0-9])(?:blu[ ._-]?ray|bdmv)(?![a-z0-9])
```

## q-webdl (gq)

Alphanumeric token boundaries accept underscores. Remux and BluRay intentionally coexist; lower WEB sources are excluded when a higher source is present in the same candidate.

v2:

```regex
(?i)\bweb[ ._-]?dl\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:web[ ._-]?dl)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:remux)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:blu[ ._-]?ray|bdmv)(?![a-z0-9]))[\s\S]*$
```

## q-webrip (gq)

Alphanumeric token boundaries accept underscores. Remux and BluRay intentionally coexist; lower WEB sources are excluded when a higher source is present in the same candidate.

v2:

```regex
(?i)\bweb[ ._-]?rip\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:web[ ._-]?rip)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:remux)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:blu[ ._-]?ray|bdmv)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:web[ ._-]?dl)(?![a-z0-9]))[\s\S]*$
```

## v-imax (gimax)

Plain IMAX explicitly excludes IMAX Enhanced in the same candidate.

v2:

```regex
(?i)\bimax\b
```

v3:

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:imax)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:imax[ ._-]?enhanced)(?![a-z0-9]))[\s\S]*$
```

## Unchanged v2 regexes

v-dolbyvision, v-imax-enh, v-seadex

## New regexes

### Netflix — s-netflix (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:NF|NFLX)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:NF|NFLX))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Netflix)(?![a-z0-9+]))
```

### Apple TV+ — s-appletv (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:ATVP)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:ATVP))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Apple[ ._-]?TV\+)(?![a-z0-9+]))
```

### Amazon Prime Video — s-prime (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:AMZN)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:AMZN))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Amazon[ ._-]?Prime[ ._-]?Video|Prime[ ._-]?Video|Amazon)(?![a-z0-9+]))
```

### Disney+ — s-disney (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:DSNP)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:DSNP))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Disney\+|Disney[ ._-]?Plus)(?![a-z0-9+]))
```

### HBO Max — s-hbomax (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:HMAX|HBOMAX)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:HMAX|HBOMAX))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:HBO[ ._-]?Max)(?![a-z0-9+]))
```

### SkyShowtime — s-skyshowtime (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:SKYSHOWTIME|SKST|SKYSHO)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:SKYSHOWTIME|SKST|SKYSHO))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:SkyShowtime)(?![a-z0-9+]))
```

### Paramount+ — s-paramount (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:PMTP)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:PMTP))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Paramount\+|Paramount[ ._-]?Plus)(?![a-z0-9+]))
```

### Peacock — s-peacock (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:PCOK)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:PCOK))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Peacock)(?![a-z0-9+]))
```

### Hulu — s-hulu (gstreaming)

```regex
(?i)(?:(?<![a-z0-9])(?:(?:HULU)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?web[ ._-]?(?:dl|rip)|web[ ._-]?(?:dl|rip)[ ._-]+(?:(?:2160|1440|1080|720|480)p[ ._-]+)?(?:HULU))(?![a-z0-9])|(?:📡[ :=]*|(?<![a-z0-9])(?:network|source[ ._-]?network)[ :=]+|\[FIGUZ_NETWORK=)(?:Hulu)(?![a-z0-9+]))
```

### AV1 — c-av1 (gcodec)

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:av1)(?![a-z0-9]))[\s\S]*$
```

### HEVC / H.265 — c-hevc (gcodec)

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:hevc|h[ ._-]?265|x[ ._-]?265)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:av1)(?![a-z0-9]))[\s\S]*$
```

### AVC / H.264 — c-avc (gcodec)

```regex
(?i)^(?=[\s\S]*(?<![a-z0-9])(?:avc|h[ ._-]?264|x[ ._-]?264)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:av1)(?![a-z0-9]))(?![\s\S]*(?<![a-z0-9])(?:hevc|h[ ._-]?265|x[ ._-]?265)(?![a-z0-9]))[\s\S]*$
```

### Unrated — e-unrated (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:unrated)(?![a-z0-9])
```

### Extended — e-extended (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:extended(?:[ ._-]?(?:cut|edition))?)(?![a-z0-9])
```

### Director’s Cut — e-directors-cut (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:director(?:[’\x27]?s)?[ ._-]+cut)(?![a-z0-9])
```

### Theatrical — e-theatrical (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:theatrical(?:[ ._-]?(?:cut|edition))?)(?![a-z0-9])
```

### PROPER — e-proper (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:proper[2-9]?)(?![a-z0-9])
```

### REPACK — e-repack (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:repack[2-9]?)(?![a-z0-9])
```

### HYBRID — e-hybrid (gseadex)

```regex
(?i)(?<![a-z0-9])(?:(?:19|20)\d{2}|s\d{1,3}e\d{1,3}|(?:2160|1440|1080|720|480)p|uhd|blu[ ._-]?ray|web[ ._-]?(?:dl|rip))(?![a-z0-9])[\s\S]*?(?<![a-z0-9])(?:hybrid)(?![a-z0-9])
```
