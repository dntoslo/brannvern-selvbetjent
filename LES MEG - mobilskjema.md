# Sikkerhetskontroll på mobil, prototype

Offline utfyllingsskjema for den årlige sikkerhetskontrollen på de selvbetjente hyttene.
Tilsynet fyller ut på hytta uten dekning, og sender en JSON-fil til bygningsansvarlig
når det er dekning igjen. Fila er laget for å kunne importeres rett inn i
Brannvern og vedlikehold.

Appversjon 2026-09-18-3, skjemaformat versjon 1.

---

## 1. Filene

| Fil | Rolle |
|---|---|
| `index.html` | Hele skjemaet, all logikk og alt grensesnitt. |
| `grunndata.js` | Hytter, bygg og utstyr med årstall, hentet fra `data.js`. |
| `sw.js` | Service worker. Gjør at appen virker uten dekning. |
| `manifest.webmanifest` | Navn og ikon når appen legges på hjemskjermen. |
| `ikon-192.png`, `ikon-512.png` | Ikoner. Bytt gjerne til DNT-ikon. |
| `lag-grunndata.py` | Lager `grunndata.js` fra `data.js` og bumper cacheversjonen i `sw.js`. |
| `eksempel-eksport.json` | Ferdig utfylt eksempel på fila tilsynet sender. |

## 2. Publisering

Legg alle filene i samme mappe på nettsidene, for eksempel
`https://…/sikkerhetskontroll/`. Tre krav:

- **HTTPS.** Service worker og dermed offline virker ikke på http.
- **Samme mappe.** Alle stiene er relative, så mappenavnet kan være hva som helst.
- **`.webmanifest` må serveres som `application/manifest+json`.** De fleste
  webservere gjør dette selv, men det er verdt å nevne til den som legger det ut.

Ingen bygging, ingen installasjon, ingen backend. Oppdatering er å bytte ut filene.

**Mottakeradresse.** Står som `MOTTAKER` øverst i `index.html`, nå satt til
jon-leo.svendsen@dnt.no. Før skjemaet deles med tilsynene bør den byttes til en egen
funksjonsadresse, så er du ikke flaskehals i ferier, og adressen kan videresendes til
den som vikarierer.

**GitHub Pages.** Legg filene i rota av repoet, eller i en mappe du peker Pages til.
Settings, Pages, Source: Deploy from a branch, branch `main`, mappe `/ (root)`.
Adressen blir `https://brukernavn.github.io/repo/`. Pages gir https, som er det
service workeren trenger. Merk at Pages krever at repoet er offentlig, med mindre
organisasjonen har betalt plan. `grunndata.js` inneholder hyttenavn, byggnavn og
årstall på brannutstyr, ingen personopplysninger, men det blir lesbart for alle.
Vil du unngå det, er Azure Static Web Apps eller foreningens egen webserver
alternativer med samme oppsett.

## 3. Oppdatere hyttedataene

Kjør før sesongen, og ellers når bygg eller utstyr endres:

```
python lag-grunndata.py "C:\…\Brannvern og vedlikehold\data.js" "C:\…\sikkerhetskontroll"
```

Skriptet skriver `grunndata.js` og teller opp cachenavnet i `sw.js`. Last opp begge.
Telefonene henter ny utgave første gang de åpner appen med dekning.

## 4. Slik virker det for tilsynet

1. Åpner lenka hjemme, mens det er nett, og legger den til på hjemskjermen.
   Dette er det eneste som **må** gjøres på forhånd. Uten det kan iPhone rydde bort
   lagringen, og appen åpner seg ikke uten dekning.
2. Velger hytte og hvilke bygg kontrollen gjelder.
3. Velger type brannvarsling øverst i røykvarslerbolken. Valget er forhåndsutfylt
   fra registreringen, og styrer hvilke punkter som vises. Batterispørsmålene kommer
   bare ved løse 9-voltsbatterier, og sentralpunktet bare ved alarmanlegg.
4. Går gjennom åtte bolker med Ja, Nei og Ikke aktuelt. Svarer de Nei, kommer det
   opp et felt der de beskriver avviket med en gang. Hver bolk har i tillegg et
   felt for andre avvik. Brannslukkerne har ikke Ikke aktuelt, og solcellebolken
   åpner seg først når de bekrefter at hytta har anlegg.
5. Fyller inn årstall på slukkere, regulatorsett og varslere, forhåndsutfylt med
   det som står i systemet i dag, med fargemerke for hva som er forfalt.
6. Krysser av for feiing med dato, og melder eventuelle vedlikeholdsbehov.
7. Trykker Del skjemaet når det er dekning, velger e-post, og sender.

Alt lagres fortløpende på telefonen. De kan lukke appen, sove en natt og fortsette.
Flere hytter samtidig går fint, skjemaene ligger som hver sin kladd.

## 5. Formatet på fila

Filnavn: `Internkontroll_Hyttenavn_ÅÅÅÅ-MM-DD.json`. Se `eksempel-eksport.json`.

| Felt | Innhold |
|---|---|
| `skjemaType`, `skjemaVersjon` | Alltid `dnt-internkontroll` og et versjonstall, så importen kan avvise ukjente filer. |
| `grunndataVersjon` | Versjonen av `data.js` skjemaet ble laget fra. Avvik fra dagens versjon betyr at bygg kan ha endret seg. |
| `hytteId`, `bygg[]` | Samme id-er som i `data.js`, så koblingen er entydig. |
| `omfang` | `anlegg` eller `bygg`, som i kontrolltabellen. |
| `dato`, `utfortAv` | Går rett inn i kontrollen. |
| `varslertype` | `9v`, `10ar` eller `sentral`. Sier hvilke punkter som var synlige, og kan brukes til å rette opp registreringen på bygget. |
| `svar` | Ett felt per kontrollpunkt med `ja`, `nei` eller `ia`. Punkter som ikke var synlige, mangler. |
| `avvik[]` | Ett objekt per avvik, med bolk, hvilket punkt det gjelder og fri tekst. |
| `notater[]` | Opplysninger som ikke er avvik, i dag hva som er skiftet på gassblussapparatet. |
| `utstyr[]` | `utstyrId`, `tidligereAar`, `montertAar` og `endret`. Bare de med `endret: true` trenger oppdatering. |
| `feiing` | `utfort` og `dato`. |
| `vedlikehold[]` | Overskrift og notat, ment å bli oppgaver. |
| `kommentar` | Fritekst fra tilsynet. |

## 6. Det som gjenstår

**Import i Brannvern og vedlikehold.** Neste steg. Forslag:
`lagre.py` får et endepunkt som lister JSON-filer i en `Innboks`-mappe ved siden av
`data.js`. Appen viser «3 nye kontrollskjemaer», du får en forhåndsvisning av hva som
blir opprettet, altså kontroll, avvik, årstall, feiedato og oppgaver, og godkjenner.
Da flyttes fila til `Innboks/behandlet`.

**PDF til arkivet.** Kan lages ved import, av samme data, og skrives rett i årsmappa
under Kontrollskjema med filnavnet appen allerede bruker.
Tilsynet kan i mellomtiden bruke Skriv ut på sammendragssiden.

**Bilder.** Bevisst utelatt i denne omgangen.

## 7. Kjente begrensninger

- iPhone kan rydde bort lagringen for nettsider som ikke er lagt på hjemskjermen,
  og som ikke har vært brukt på en uke. Instruksjonen i punkt 4.1 er derfor viktig.
- Deling av filvedlegg krever iOS 15 eller nyere, eller Android med Chrome.
  Faller det ut, lastes fila ned i stedet, og tilsynet legger den ved selv.
- Sletter tilsynet appen fra hjemskjermen, forsvinner kladdene.
- Ett skjema er én kontrolldato. Går tilsynet over flere dager, blir det enten
  ett skjema med én dato, eller flere skjemaer.
