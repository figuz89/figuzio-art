# Figuz Smart Badges v3 — utvikling og test

**Status: forslag i arbeidsgren, klart for gjennomgang. Ikke aktivert.**

Sluttkontrollrunden er dokumentert i [FINAL_QA.md](FINAL_QA.md), inkludert kjøring av de faktiske matcherfunksjonene fra Mobile og TV.

v3 inneholder **52 badges i 11 kategorier**: alle 33 fra v2 og 19 nye. Alle eksisterende ID-er, navn, gruppetilhørigheter, bilde-URL-er og stilfelter er bevart. De ni opprinnelige gruppene er identiske. v2-filen og eksisterende grafikk er ikke endret.

- [v3-JSON](Figuz_Smart_Badges_v3.json)
- [Komplett PNG-katalog](previews/v3/Figuz_Smart_Badges_v3.png)
- [TV-simulering av A/B/C](previews/v3/Nuvio_streamlist_TV_simulation.png)
- [Mobil-simulering av A/B/C](previews/v3/Nuvio_streamlist_mobile_simulation.png)
- [Lesbarhetsark ved 16 dp](previews/v3/Nuvio_badge_readability.png)
- [Logoer før/etter](previews/v3/Streaming_logo_before_after.png)
- [Simulering med 12 samtidige merker](previews/v3/Nuvio_priority_stress_simulation.png)
- [Kjørte upstream-matcherimplementasjoner](reports/v3-upstream-matcher-results.json)
- [Kontroll av den avgrensede sluttdiffen](reports/v3-final-audit.json)
- [Alle regex-endringer, før/etter og nye regler](reports/v3-regex-changes.md)
- [Maskinlesbar endringslogg](reports/v3-regex-changes.json)
- [Alle testtilfeller og faktiske treff](reports/v3-filename-results.json)
- [Full bilde-URL-kontroll](reports/v3-url-check.json)

## Nye merker

| Kategori | Merker | Sikre identifikatorer |
| --- | --- | --- |
| Streaming Services | Netflix | NF, NFLX |
| Streaming Services | Apple TV+ | ATVP |
| Streaming Services | Amazon Prime Video | AMZN |
| Streaming Services | Disney+ | DSNP |
| Streaming Services | HBO Max | HMAX, HBOMAX |
| Streaming Services | SkyShowtime | SKYSHOWTIME, SKST, SKYSHO |
| Streaming Services | Paramount+ | PMTP |
| Streaming Services | Peacock | PCOK |
| Streaming Services | Hulu | HULU |
| Video Codec | HEVC / H.265 | HEVC, H265, H.265, H-265, H_265, x265 |
| Video Codec | AVC / H.264 | AVC, H264, H.264, x264, tilsvarende separatorer |
| Video Codec | AV1 | AV1 som avgrenset token |
| Release | Unrated, Extended, Director’s Cut, Theatrical, PROPER, REPACK, HYBRID | Eksplisitte utgavetagger etter årstall, episode- eller teknisk metadataanker |

Korte tjenestetagger må stå ved en WEB-DL/WEBRip-tag, eventuelt med oppløsning mellom dem. Begge rekkefølger støttes, med punktum, mellomrom, bindestrek og understrek. Eksempler: `NF.WEB-DL`, `WEB-DL.NFLX`, `ATVP-1080p-WEBRip`. En enslig `NF`, `ATV`, `MAX`, `HBO` eller et tjenestenavn i en filmtittel gir ikke tjenestemerke. SKST og SKYSHO ble lagt til i sluttkontrollen etter verifikasjon i AIOStreams sin faktiske release-parser; se kilde i FINAL_QA.md.

Fullstendige navn støttes i tydelig merkede nettverksfelt som `📡 Netflix`, `Network: Apple TV+` eller `[FIGUZ_NETWORK=Disney+]`. Dette fungerer hvis slik tekst allerede inngår i Nuvios matchgrunnlag. Ingen tjeneste utledes fra filmens innhold eller hvem som produserte filmen.

Utgavetagger er beskrivende informasjon, uten ny kvalitetsrangering. Flere kan vises samtidig med SeaDex. Tittelen `Hybrid.2019.1080p` gir ikke HYBRID; `Film.2026.HYBRID.1080p` gjør det. `DC` alene brukes ikke som Director’s Cut.

## Bevaring av v2 og grafikk

Utgangspunktet er commit `9e3334897ad2df04630220b619072212a3dac35a`. De originale gull-, sølv/blå- og kobberbildene brukes gjennom nøyaktig de samme URL-ene som i v2, inkludert de åtte eksterne k45sle-bildene. SeaDex er bevart som komplett, uendret regel.

De ni nye tjenestemerkene bruker originale SVG-logoformer, uten tegning på nytt eller bildegenerering. Originalkilder, kreditering og SHA-256 ligger i [kildemanifestet](assets/v3_frameless/sources/manifest.json). SVGL-lisensen følger kildene. Sølv/blå-paletten er målt fra v2-bildet `r-1080.png`. Samme palett og forsiktig relieff brukes på kodeker og utgaver. Ingen nye bilder bruker gull, merkevarefarger, rammer eller bakgrunnsbokser.

Alle 19 nye PNG-er har transparent RGBA-bakgrunn og 64 px bildehøyde. De er omtrent 5–25 kB hver. De nye bilde-URL-ene er festet til uforanderlige artwork-commiter: `1da3b7829b1059bf4fd59ef5dea07d72c701d6a1` for 15 bilder og `94e6dd769333c0a8883d243d2d521aa0fe670509` for de fire finjusterte logoene. Disse fire bruker 60 px logoform i stedet for 56 px, med bevart proporsjon, gradient og relieff. Alle ni SVG-originaler er uendret. De eksisterende eksterne v2-bildene er langt større, men er beholdt uendret som bestilt.

30 eksisterende regexer har dokumenterte rettelser fra første v3-runde. Ingen v2-regex ble endret ytterligere i sluttkontrollen. Alle andre felter i de 33 reglene er uendret. De tre uendrede regexene er Dolby Vision, IMAX Enhanced og SeaDex. Endringene gjelder separatorgrenser, presis lydidentifikasjon og eksplisitt undertrykking av lavere treff i samme kandidat. Hver gammel og ny regex finnes i [den komplette gjennomgangen](reports/v3-regex-changes.md).

## Faktisk Nuvio-kompatibilitet og prioritet

Undersøkt kildekode:

- [Nuvio TV 1.0.0: matcher og JSON-parser](https://github.com/NuvioMedia/NuvioTV/blob/9f17e8bf4abc799dc8c832d2894a8b3b166e4353/app/src/main/java/com/nuvio/tv/core/streams/StreamBadgeRules.kt)
- [Nuvio TV: nyere matcher](https://github.com/NuvioMedia/NuvioTV/blob/fa194b008e331780d2391491879e4a0a343641ef/app/src/main/java/com/nuvio/tv/core/streams/StreamBadgeRules.kt)
- [Nuvio TV: streamradens størrelse, klipping og marquee](https://github.com/NuvioMedia/NuvioTV/blob/fa194b008e331780d2391491879e4a0a343641ef/app/src/main/java/com/nuvio/tv/ui/components/StreamBadgeChips.kt)
- [Nuvio Mobile: matcher](https://github.com/NuvioMedia/NuvioMobile/blob/38295004e4d4002f5520fe4120230253b64af63d/composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamBadgeRules.kt)
- [Nuvio Mobile: horisontal rulling](https://github.com/NuvioMedia/NuvioMobile/blob/38295004e4d4002f5520fe4120230253b64af63d/composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamCard.kt)
- [Nuvio Mobile: badge-dimensjoner](https://github.com/NuvioMedia/NuvioMobile/blob/38295004e4d4002f5520fe4120230253b64af63d/composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamBadgeChip.kt)

Disse versjonene samler **alle regex-treff** i filterrekkefølge og dedupliserer etter bilde-URL. `groupId` gir **ikke** «første treff vinner» i streamlisten. v3 avhenger derfor ikke av den antakelsen. JSON bruker de samme støttede feltene som v2, og mønstrene bruker Java-kompatibel syntaks. Regexene er kjørt med `java.util.regex.Pattern` og `find()`. Mobile-syntaksen er vurdert mot den felles kildekoden; iOS-motoren er ikke kjørt eller fysisk testet.

Innen ett filnavn håndhever regexene de opprinnelige prioritetene for oppløsning, HDR, IMAX, Dolby, DTS og kanaler. Remux og BluRay vises sammen med hensikt i B/C. WEB-kilder undertrykkes i samme kandidat når Remux/BluRay finnes. Dolby Vision og HDR er fortsatt separate grupper.

Lyd, Dolby Vision og HDR ligger først i filterlisten, deretter kanaler, oppløsning, kilde, IMAX og Release. Alle nye informasjonsmerker ligger etter dette. Prioriteten innad i hver opprinnelige kategori er bevart. Atmos MIXED står fortsatt først som et **varsel om uklart lydgrunnlag**. Kodekreglene velger AV1 før HEVC før AVC dersom ett filnavn inneholder motstridende kodekord; dette er en deterministisk tie-break, ingen kvalitetsvurdering av streamen.

**Klientbegrensning:** Nuvio tester hvert felt separat, og dessuten en sammenslått kandidat. En negativ lookahead i filnavnet kan ikke trekke tilbake treff fra et annet felt. Derfor kan ingen vanlig badge-JSON garantere nøyaktig én kodek per stream dersom for eksempel ett felt sier AV1 og et annet sier HEVC. Lyd kan tilsvarende få både en basisbadge og en Atmos-badge ved oppdelte/inkonsistente felt. To eksplisitte karakteriseringstester dokumenterer dette; de er ikke bevis for at problemet er løst. Én kodek og én badge per eksklusiv kategori er testet for alle enkeltkandidater. En garanti på tvers av felter krever en separat klientendring.

Ingen hard antallsgrense ble funnet i de undersøkte visningsløkkene. TV bruker en klippet rad og marquee når raden har fokus; Mobile lar raden rulles horisontalt. Bildene får 16 dp høyde innen en 20 dp beholder, med 34–92 dp bildebredde. Radene A/B/C er omtrent 327/632/471 dp. Simuleringene bruker 326 dp mobilutsnitt og et mer konservativt 416 dp TV-utsnitt, beregnet fra TV-skjermens 40/60-fordeling og padding ved 960 dp logisk bredde. Den tidligere TV-modellen på 850 dp er erstattet. Lyd, Dolby Vision og HDR fra A/B/C er helt synlige i starten av begge modellerte utsnitt. Utgaver kan ligge utenfor utsnittet. Ingen badges er fjernet for å spare plass.

## Lydgjenkjenning

| Grunnlag | Badge |
| --- | --- |
| `TrueHD5.1`, `TrueHD.5.1`, `TrueHD7.1` | TrueHD + riktig kanalmerke; ingen Atmos |
| `TrueHD.Atmos`, `TrueHD.7.1.Atmos` | TrueHD Atmos |
| `DDP5.1.Atmos`, `EAC3.Atmos`, `DD+.5.1.Atmos` | DD+ Atmos |
| `Atmos` uten sikker kodektilknytning | Atmos ? |
| `TrueHD.AAC.Atmos` | Atmos ?; kodeken til Atmos gjettes ikke |
| TrueHD, DD+ og Atmos i samme kandidat | Opprinnelig Atmos MIXED / sjekk lyd |
| `DTS-HD.MA.7.1`, `DTS-HD.MA.5.1`, `DTS-HD MA` | DTS-HD MA + eventuelle kanaler |
| `DTS-HD.7.1` | DTS-HD; aldri automatisk MA |
| `DTS:X` | DTS:X; ikke vanlig DTS-HD MA |

Kodekspesifikk Atmos krever et eget Atmos-token og nærhet til kodeken gjennom separatorer og eventuelle kanaler. TrueHD alene er aldri Atmos-grunnlag. DD+/EAC3, Dolby Digital/AC3 og DTS-variantene har avgrensede regler som hindrer lavere doble treff i samme kandidat.

Merket beskriver tilgjengelig metadata. Det verifiserer ikke filens faktiske spor, standardspor eller passthrough. Skillet DD+ Atmos/TrueHD Atmos er synlig for oppsettet Google TV Streamer, LG C2 og HW-Q995B, uten endring av sortering eller lydinnstillinger.

## Resultat for de faktiske filmene

| Test | Faktiske treff | Uønskede antakelser |
| --- | --- | --- |
| A — Animals | WebDL, 4K, Dolby Vision, HDR, Netflix | Ingen Atmos eller norsk |
| B — Kingsman | DTS-HD MA, 7.1, Remux, BluRay, 4K, Dolby Vision, HEVC, Unrated, HYBRID | Ingen Atmos |
| C — Mission: Impossible II | TrueHD, 5.1, Remux, BluRay, 4K, Dolby Vision, HDR10 | Ingen Atmos |

**368 tilfeller passerer**, inkludert to tester som fastholder klientbegrensningene. Alle 52 merker har minst ett positivt testtilfelle. Fem testmetoder kontrollerer dessuten struktur, de 33 bevarte reglene, grupper, prioritet, transparens, nøytral farge, filstørrelse og kildehasher. Negative tester dekker blant annet MAX, usikre tjenestenavn, MULTI, GERMAN.DL, undertekstspråk, vanlig DTS-HD, vanlig TrueHD og duplikater av samme format. I tillegg kjøres alle tilfellene gjennom uendret matcher-kilde fra TV (vanlig og pooled-kall) og Mobile (felles Kotlin-kode på JVM): 1104 kjøringer. Kildehasher og resultatene finnes i upstream-rapporten. Dette er ikke en kjøring av iOS-binæren eller hele Nuvio-appen.

**52/52 bilde-URL-er returnerte gyldige transparente PNG-er** ved uautentisert HTTPS GET. Bilder i dette repoet er også kontrollert mot lokale SHA-256-hasher. Tidspunkt og detaljresultater finnes i URL-rapporten. Fremtidig tilgjengelighet for v2s eksterne URL-er kan ikke garanteres.

## AIOStreams og språk — separate forslag

[AIOStreams dokumenterer `stream.network`, lydspor og språkfelter](https://docs.aiostreams.viren070.me/reference/custom-formatter/). Nuvios undersøkte kandidatliste leser ikke et eget `stream.network`-objekt. Informasjonen kan brukes uten konfigurasjonsendring dersom nettverksnavnet **allerede** skrives til et matchbart tekstfelt med en av de eksplisitte etikettene ovenfor. Det er ikke kontrollert at din aktive formatter gjør dette.

Ingen språkbadge inngår i v3. `stream.languages` kan bygge på filnavn eller sporinformasjon; feltet alene dokumenterer ikke et bestemt lydspor. MULTI, GERMAN.DL, landkoder og norsk undertekst gir ingen norsk lydbadge.

Følgende er dokumenterte forslag som krever et eget, godkjent oppdrag:

1. La en formatter skrive en entydig nettverksmarkør fra `stream.network` dersom dagens tekst skjuler nettverket. v3 støtter allerede `[FIGUZ_NETWORK=...]`; ingen formatter er endret her.
2. Vurder senere separate merker for norsk lyd fra **audioTracks** og norsk tekst fra **subtitleTracks**, helst med `mediaInfoQuality=probe` og eksplisitt språkmetadata. AIOStreams har slike separate data også for probede Usenet-filer, men ikke nødvendigvis for hvert søkeresultat. Dette krever separat formatterarbeid og tester. Ingen språkmerker er implementert i denne runden.
3. Rett Nuvios matcher dersom én kodek per stream skal garanteres også ved motstridende felt. Dette krever kandidatbevisst prioritering i klienten, uten å gjøre alle Release-merker eksklusive.

Andre kjente grenser: et filnavn som bevisst etterligner tekniske tagger kan fortsatt gi et falskt treff. Tjenestetagger uten WEB-kontekst eller tydelig nettverksetikett utelates med vilje. Utgavemerker uten metadataanker utelates også. Logoer med fin skrift, særlig Disney+, Prime Video og Paramount+, må vurderes på fysisk skjerm før eventuell aktivering. Lesbarhetsarket viser dem i modellert størrelse, og er ingen godkjenning på fysisk mobil/TV.

## Reproduksjon

Testene trenger Python 3.12+, Pillow og en JDK 17+ på PATH eller via JAVA_HOME:

```text
python -m pip install -r badges/tools/requirements-v3.txt
python badges/tools/build_v3.py
python -m unittest discover -s badges/tests -v
python badges/tests/check_upstream_matchers.py
python badges/tools/check_v3_urls.py
python badges/tools/audit_v3_final.py
```

Sett `FIGUZ_WRITE_REPORT=1` ved behov for å regenerere treffrapporten. Grafikken kan regenereres fra de medfølgende SVG-ene:

```text
npm --prefix badges/tools install
node badges/tools/render_svg_masks.cjs
python badges/tools/render_v3.py
python badges/tools/write_v3_report.py
```

Renderer bruker installerte Arial/Arial Bold/Arial Narrow Bold fra Windows, eller tilsvarende fontfiler i `FIGUZ_FONT_DIR`. Fontfiler distribueres ikke. `check_v3_urls.py` fyller den ignorerte bildecachen for uendret ekstern v2-grafikk før forhåndsvisningene regenereres. Java-harnessen modellerer matcherens regex-/kandidat-/URL-dedupe-adferd. Upstream-kontrollen trenger Kotlin/JVM via `KOTLINC` eller PATH og henter offentlig, commit-festet kilde til den ignorerte cachen; matcherobjektet, compiled-filter-klassen og dedupe-funksjonen kompileres uendret med små domenemodeller for testen. Ingen av testene kjører hele Nuvio-appen.

Ingen aktiv Nuvio-konfigurasjon, AIOStreams-innstilling, stream-sortering, lydinnstilling eller Oracle VPS er endret. Ingen omstart, merge eller aktivering inngår i dette arbeidet. Draft PR-en er stoppunktet for godkjenning.
