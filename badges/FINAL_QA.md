# Figuz Smart Badges v3 — sluttkontroll

**Leveranse for siste vurdering i eksisterende Draft PR #4. Ingen aktivering eller merge.**

[Import-JSON](https://raw.githubusercontent.com/figuz89/figuzio-art/codex/figuz-smart-badges-v3/badges/Figuz_Smart_Badges_v3.json) · [Samlet katalog](previews/v3/Figuz_Smart_Badges_v3.png) · [TV](previews/v3/Nuvio_streamlist_TV_simulation.png) · [iPhone](previews/v3/Nuvio_streamlist_mobile_simulation.png) · [12-merkers stresstest](previews/v3/Nuvio_priority_stress_simulation.png) · [Logoer før/etter](previews/v3/Streaming_logo_before_after.png)

## Hva som er endret i denne runden

- Prime Video, Disney+, SkyShowtime og Paramount+: logoformen er skalert jevnt fra 56 til 60 px høyde på samme 64 px transparente lerret. Det gir omtrent 7 % større synlig logo ved Nuvios faste bildehøyde. Originale SVG-former, proporsjoner, gradient og relieff er bevart. De øvrige 15 nye PNG-ene er bit-identiske med forrige PR-versjon, og alle ni SVG-originalene er uendret.
- Visningsrekkefølgen er nå lyd, Dolby Vision, HDR, kanaler, oppløsning og deretter kilde-/utgaveinformasjon. Prioriteten innad i hver etablert kategori er bevart. Dette påvirker bare badges, ikke sorteringen av strømmer.
- Den eksisterende SkyShowtime-regelen støtter nå også **SKST** og **SKYSHO**, verifisert i [AIOStreams sin release-parser](https://github.com/AIOStreams/release-parser/blob/d5a0b99bc77b7a0ba45786023e186e290a0430af/src/handlers.ts#L3277). WEB-DL/WEBRip-kontekst kreves fortsatt. Dette er eneste regex-endring siden forrige PR-versjon. Ingen flere tjenester er lagt til.
- TV-simuleringen er korrigert fra en for bred merkerad på 850 dp til et modellert utsnitt på 416 dp, beregnet fra [Nuvios 40/60-skjermfordeling og padding](https://github.com/NuvioMedia/NuvioTV/blob/fa194b008e331780d2391491879e4a0a343641ef/app/src/main/java/com/nuvio/tv/ui/screens/stream/StreamScreen.kt#L454) og plass til addon-logo. Det finnes også separate [TV-bilder for A](previews/v3/Nuvio_TV_A.png), [B](previews/v3/Nuvio_TV_B.png) og [C](previews/v3/Nuvio_TV_C.png), med start og senere posisjon på samme rad.

[Sluttdiff-auditen](reports/v3-final-audit.json) kontrollerer omfanget mot commit `41a1870f67a6cda74b098789760ced582d0e5639`: 52 badges, samme 11 grupper, nøyaktig fire oppdaterte PNG-er og fire bilde-URL-er, én dokumentert tjenestealias-endring, ingen øvrige regelfeltendringer. v2-JSON og eksisterende v2-bilder er uendret i Git. Windows-checkoutens linjeskift endrer ikke dette repository-innholdet.

## Test av gruppekonflikten mot implementasjonene

Matcherobjektet, compiled-filter-klassen og dedupe-funksjonen er hentet fra commit-festet kilde, kontrollert mot original Git-blobhash og **kompilert uendret**. Små domenemodeller erstatter Android-/serialiseringsavhengigheter i testen. Faktisk `compile()`, innsamling av kandidatfelter og matching kjøres. Testen bruker én allerede normalisert, aktiv import.

- [TV-kilde, commit fa194b0](https://github.com/NuvioMedia/NuvioTV/blob/fa194b008e331780d2391491879e4a0a343641ef/app/src/main/java/com/nuvio/tv/core/streams/StreamBadgeRules.kt): både `matchedBadges(stream, filters)` og `matchedBadgesPooled(...)` kjøres.
- [Mobile-kilde, commit 3829500](https://github.com/NuvioMedia/NuvioMobile/blob/38295004e4d4002f5520fe4120230253b64af63d/composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamBadgeRules.kt): den felles Kotlin-implementasjonen av `matchedBadges(stream, filters)` kjøres på JVM.

| Tilfelle | TV vanlig | TV pooled | Mobile felleskode |
| --- | --- | --- | --- |
| Kingsman: Unrated + HYBRID | Begge | Begge | Begge |
| SeaDex + Extended | Begge | Begge | Begge |
| SeaDex + Extended + HYBRID | Alle tre | Alle tre | Alle tre |
| Remux + BluRay | Begge | Begge | Begge |

**Konklusjon:** Ingen Release-gruppekonflikt er funnet i disse implementasjonene. De samler alle treff og dedupliserer etter bilde-URL; gruppen begrenser ikke streamlisten til ett treff. De opprinnelige gruppene, inkludert `gseadex` og `gq`, er derfor beholdt. Visningsløkkene i [TV](https://github.com/NuvioMedia/NuvioTV/blob/fa194b008e331780d2391491879e4a0a343641ef/app/src/main/java/com/nuvio/tv/ui/components/StreamBadgeChips.kt) og [Mobile](https://github.com/NuvioMedia/NuvioMobile/blob/38295004e4d4002f5520fe4120230253b64af63d/composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamCard.kt) itererer over alle bildebadges. Et merke kan ligge utenfor utsnittet, men er ikke borte på grunn av samme groupId.

## Automatiske tester, simuleringer og fysisk kontroll

| Kontroll | Resultat | Hva dette beviser |
| --- | --- | --- |
| Java-regex og pakkekontroller | 368 tilfeller; fem unittest-metoder passerer | Forventede positive/negative treff, alle 52 merker dekket, JSON, grupper, prioritet, duplikater, bevaring av 33 gamle merker og PNG-egenskaper |
| Faktisk TV-matcher | 736 kjøringer passerer | Alle 368 tilfeller gir samme forventede treff og rekkefølge i begge TV-kall |
| Faktisk Mobile-matcher på JVM | 368 kjøringer passerer | Alle tilfellene gir samme forventede treff og rekkefølge i den felles Kotlin-koden |
| Bilde-URL-er | 52/52 består | Uautentisert HTTPS GET, full PNG-dekoding, transparens og samsvar med lokal bildehash der tilgjengelig |
| Visuell simulering | Samlet katalog, iPhone, TV og tett 12-merkers rad gjennomgått | Modellert lesbarhet, skala, rulling og prioritering ved oppgitte størrelser |
| Fysisk iPhone / Google TV Streamer | **Ikke utført** | Ingen påstand om fysisk skjermtest |
| Native iOS-binær / komplett Nuvio-app | **Ikke kjørt** | JVM-testen er ikke en native iOS-test eller en full UI-integrasjonstest |

De to kjente klientbegrensningene inngår som karakteriseringstester. At disse passerer betyr at begrensningen er dokumentert og reprodusert, ikke at den er fjernet.

[Alle filnavn og treff](reports/v3-filename-results.json) · [Upstream-kjøringer og kildehasher](reports/v3-upstream-matcher-results.json) · [Testlogg](reports/v3-test-run.txt) · [URL-kontroll](reports/v3-url-check.json) · [Logo-målinger](reports/v3-logo-sizing.json) · [Layout-målinger](reports/v3-layout-measurements.json)

De tre oppgitte filnavnene gir nøyaktig de forventede treffene. Ingen av dem får Atmos. Ekstra syntetiske, realistiske Usenet-navn dekker blant annet AMZN/DD+ Atmos, ATVP/DV/HDR10+, Director’s Cut/TrueHD, DSNP/AV1, REPACK/DTS-HD MA og ukjent tjeneste. Ingen faktisk fil er lastet ned eller probet i denne kontrollen.

## Lesbarhet og prioritering

Nuvios undersøkte kort bruker 16 dp bildehøyde i en 20 dp beholder og 34–92 dp bildebredde. De fire finjusterte logoene utnytter mer av samme bildehøyde. Scriptlogoer kan fortsatt ikke få like tykk skrift som Netflix uten å endre logoformen; denne grensen er beholdt.

Mobilmodellen bruker et 326 dp badge-utsnitt, tilsvarende en modellert 390 dp iPhone-layout med marger. TV-modellen bruker 960 × 540 logiske dp og 416 dp til merkeraden. Dette er dokumenterte modellvalg, ikke avleste verdier fra dine fysiske enheter.

For A/B/C er alle treff innen lyd, Dolby Vision og HDR helt synlige ved starten av begge modellerte rader. Flere kilde- og utgavemerker ligger senere i raden. Mobile har horisontal sveiping; TV klipper raden uten fokus og bruker marquee med fokus. Ingen hard badge-antallsgrense finnes i de undersøkte løkkene. Simuleringene viser også den senere delen av raden, der utgavemerkene ligger. Ingen badges er fjernet, og Nuvios kildekode er ikke endret.

## Norsk lyd og tekst — kort anbefaling, ingen implementasjon

**Gjennomførbart og nyttig når faktisk sporinformasjon finnes.** AIOStreams har separate `stream.audioTracks` og `stream.subtitleTracks`, samt `stream.mediaInfoQuality`. [Usenet-motoren kan køe filprober](https://github.com/Viren070/AIOStreams/blob/c358754b0ae4758d034badf8618de6fdb7fa9333/packages/core/src/media-info/play.ts#L89), og [bibliotekprober kan undersøke hver fil](https://github.com/Viren070/AIOStreams/blob/c358754b0ae4758d034badf8618de6fdb7fa9333/packages/core/src/usenet/integration/library-probes.ts). ffprobe-data holdes atskilt som lyd- og tekstspor i [media-info-oversettelsen](https://github.com/Viren070/AIOStreams/blob/c358754b0ae4758d034badf8618de6fdb7fa9333/packages/core/src/media-info/wire.ts).

Et senere språkmerke bør kreve riktig sportype, eksplisitt normalisert norsk språkmetadata og helst `mediaInfoQuality=probe`. Lyd og tekst må få hver sin markør. MULTI, DL, landkode, generelle språkønsker eller manglende spor er ikke bevis. Et språkfelt dokumenterer metadata; selve talen/teksten er ikke språkanalysert. [AIOStreams-dokumentasjonen](https://docs.aiostreams.viren070.me/reference/custom-formatter/) beskriver også at sporlistene mangler for strømmer som aldri er probet. Generelle Usenet-søketreff kan derfor ikke forventes å ha dette før probing eller annen pålitelig medieinformasjon er tilgjengelig. Din aktive instans og formatter er ikke undersøkt eller endret.

Ingen språkmerker eller formatterendringer er implementert. Forslaget bør vurderes separat med et anonymisert eksempel på faktiske spor-/proveniensdata.

**NRK TV, TV 2 Play og Viaplay:** ingen nettverkshandler eller dokumentert alias for disse ble funnet i den undersøkte [AIOStreams release-parseren](https://github.com/AIOStreams/release-parser/blob/d5a0b99bc77b7a0ba45786023e186e290a0430af/src/handlers.ts). Det beviser ikke at ingen addon kan levere slike kilder, men gir ikke grunnlag for sikre generelle Usenet-regler. Anbefalingen er å vente på eksplisitt kildefelt eller dokumenterte reelle filnavneksempler. Ingen nye tjenester er implementert.

## Gjenstående begrensninger

1. Nuvio matcher kandidatfeltene hver for seg før/ved sammenslåing. Motstridende felt kan fortsatt gi flere kodekmerker eller både basis- og Atmos-merke. Dette er reprodusert med den faktiske koden og kan ikke garanteres løst med vanlig badge-JSON alene.
2. Lang merkerad krever sveip eller fokus-rulling. Ved flere separate lydformater kan også en prioritert rad bli bredere enn et smalt mobilutsnitt. Ingen globale UI-/rendererendringer er gjort.
3. Fin skrift og 16 dp visningshøyde setter grenser, særlig for Disney+ og Paramount+. Fysisk lesbarhet og native iOS-regex er ikke verifisert i denne runden.
4. Regex beskriver metadata, ikke verifisert standardlydspor eller maskinvarens passthrough. Filer som etterligner tekniske tagger i titler kan fortsatt gi falske treff. Eksisterende eksterne v2-URL-er avhenger av sine opprinnelige verter.

v2, main, aktiv Nuvio-konfigurasjon, AIOStreams, Oracle VPS og driftsinnstillinger er ikke endret. Ingen omstart, merge eller aktivering er utført. Stoppunktet er oppdatert Draft PR og dokumenterte kontroller.
