# Figuz Smart Badges v3 — alternativ metallstil

En egen importerbar variant av stilskissen brukeren valgte. Alle 52 merker er separate, transparente PNG-filer med tydeligere relieff, fasetter, metallreflekser og mørkere sideflater. Gull, sølv/blått og bronse følger samme etablerte fargehierarki. Dette er ferdige badgefiler, ikke utsnitt av konseptbildet.

**Import-JSON:** [Figuz_Smart_Badges_v3_Alternative.json](Figuz_Smart_Badges_v3_Alternative.json)

- [Faktisk samlet forhåndsvisning](previews/v3_alternative/Figuz_Smart_Badges_v3_Alternative.png)
- [Streamkort for de tre filmene](previews/v3_alternative/Nuvio_Alternative_streamcards.png)
- [Alle 52 merker ved modellert Nuvio-størrelse](previews/v3_alternative/Nuvio_Alternative_readability.png)
- [Konseptbildet som stilreferanse](previews/concepts/Figuz_Smart_Badges_Alternative_Style.png)

## Innhold og farger

| Metall | Antall | Betydning |
| --- | ---: | --- |
| Gull | 9 | Høyeste etablerte nivå: Remux, 4K, Dolby Vision, HDR10+, TrueHD Atmos, TrueHD, DTS:X, DTS-HD MA og 7.1 |
| Sølv/blått | 35 | Middels nivå og nøytral informasjon |
| Bronse | 8 | WebRip, 720p, 480p, SDR, Dolby Digital, DTS, 2.0 og 1.0 |

Alle strømmetjenester, videokodeker og utgavemerker er sølv/blå. HYBRID, PROPER og REPACK får ingen ny kvalitetsrangering. Fargene endrer ikke sortering eller avspilling.

Alternativet kopierer den testede v3-JSON-en og endrer **bare imageURL**. Alle 52 ID-er, navn, regexer, grupper, prioriteringer, aktiveringsflagg og transparente stilfelter er identiske med v3. Den opprinnelige v2 og den tidligere kontrollerte v3 er beholdt uendret, inkludert deres bilder og importfiler.

## Grafikk og hosting

- 52 unike PNG-filer under `badges/assets/v3_alternative/`, alle med RGBA-transparens.
- Felles bildehøyde 128 px, maksimalt 882 px bredde. Dette gir nok oppløsning til små bilder på mobil og TV.
- Filene er omtrent 12–80 kB; samlet omtrent 2,2 MB.
- Alle bildeadresser er offentlig HTTPS, festet til artwork-commit `9b5433262445441f706bd4e5ce2e73987f12db5a`. Ingen base64-bilder i JSON.
- Strømmetjenestene bruker de eksisterende originale SVG-ordmerkene. Dolby- og DTS-symbolene bruker rene vektorkilder; øvrige tekstmerker og geometriske symboler er tegnet i høy oppløsning og får samme metallbehandling.
- Fontnavn, kilder, filstørrelser og bildehasher finnes i [manifestet](assets/v3_alternative/manifest.json). Kreditering står i [kildeoversikten](assets/v3_alternative/sources/README.md).

## Verifikasjon

| Kontroll | Resultat |
| --- | --- |
| Original v3 + alternativets enhetstester | Åtte testmetoder passerer |
| Alternative filnavn og metadata | Alle 368 tilfeller gir samme treff som testet v3 |
| Faktisk TV-matcher, vanlig og pooled-kall | 736 kjøringer passerer med alternative bilde-URL-er |
| Faktisk Mobile-felleskode på JVM | 368 kjøringer passerer med alternative bilde-URL-er |
| Offentlige bildeadresser | 52/52 hentet, PNG-dekodet og kontrollert mot lokal SHA-256 |
| Farge og bildeegenskaper | Riktig fargeklasse, full transparens ved alle lerretskanter, gyldige RGBA-PNG-er og unike bildehasher |
| Bevaring | Bare nye filer; v2 og den eksisterende v3 er uendret |

[Testlogg](reports/alternative-test-run.txt) · [Alle filnavntreff](reports/alternative-filename-results.json) · [Upstream-kode og kjøringer](reports/alternative-upstream-results.json) · [URL-kontroll](reports/alternative-url-check.json) · [Layoutmål](reports/alternative-layout.json)

Animals gir fortsatt Netflix, WEB-DL, 4K, Dolby Vision og HDR. Kingsman gir blant annet DTS-HD MA, 7.1, Unrated og HYBRID. Mission: Impossible II gir TrueHD og 5.1, uten Atmos. Negative tester for TrueHD/Atmos, DTS-HD/MA, ukjente tjenester, MAX, MULTI og dupliserte formatnavn består.

Upstream-testene kjører de samme commit-festede, hash-verifiserte matcherfunksjonene som er beskrevet i [sluttkontrollen](FINAL_QA.md), med små domenemodeller og én normalisert aktiv import. Mobile-koden kjøres på JVM. Dette er ikke en kjøring av native iOS-binæren eller hele Nuvio-appen.

## Visningsgrenser

Forhåndsvisningene er laget av de faktiske PNG-filene. Streamkortene modellerer 16 dp bildehøyde, 326 dp mobilutsnitt og 416 dp TV-utsnitt. Lyd, Dolby Vision og HDR vises først; senere merker nås med horisontal sveiping eller fokus-rulling. Bredere og kraftigere bokstaver kan gi en lengre rad enn i standardstilen.

Ingen fysisk iPhone- eller Google TV Streamer-test er utført. Tynn skrift i enkelte tjenestelogoer og de små Atmos-undertekstene bør vurderes på brukerens skjerm.

Nuvios eksisterende begrensning ved motstridende metadatafelter er uendret: flere kodekmerker eller både basis- og Atmos-merke kan forekomme på tvers av kandidatfelter. De to karakteriseringstestene dokumenterer dette; de er ikke en påstand om at klientbegrensningen er fjernet. Ingen språkmerker eller nye tjenester er lagt til.

## Reproduksjon

```text
python -m pip install -r badges/tools/requirements-alternative.txt
npm --prefix badges/tools install
node badges/tools/render_alternative_masks.cjs
python badges/tools/build_alternative.py
python -m unittest discover -s badges/tests -v
python badges/tests/check_alternative_upstream.py
python badges/tools/check_alternative_urls.py
```

Sett JAVA_HOME og KOTLINC eller ha JDK 17+ og Kotlin/JVM på PATH. Renderer bruker installerte Arial Black og Arial Narrow Bold fra Windows, eventuelt via FIGUZ_FONT_DIR. Fontfiler distribueres ikke. Den lokale SciPy-installasjonen kan ligge i den ignorerte `.v3-cache/alternative-deps/`-mappen.

Ingen aktiv Nuvio-konfigurasjon, AIOStreams-innstilling, VPS, driftsinnstilling eller eksisterende importfil er endret. Ingen merge eller aktivering er utført. Varianten legges til i eksisterende Draft PR #4.
