# annemiekmaissan.nl

Website van Zangstudio Annemiek Maissan. Een statische Astro-site op Netlify, met Sveltia CMS zodat
Annemiek zelf teksten, prijzen en foto's kan aanpassen. Opvolger van de Kirby 4-site
(repo `joranovski/annemiekmaissan`).

- **Node** 22.12 of nieuwer (Astro 7.3). `npm install`, dan `npm run dev` (http://localhost:4321).
- **Bouwen**: `npm run build` → `dist/`. Netlify bouwt automatisch bij elke push naar `main`.

## Waar staat wat

| Wat | Waar |
|---|---|
| Pagina's (blokken + foto's) | `src/content/pages/<slug>/index.md`, foto's in dezelfde map |
| Contactgegevens, sociale media | `src/data/site.json` |
| Keuzes en teksten van het contactformulier | `src/data/formulier.json` |
| Kleuren, letters, ruimte | `src/styles/tokens.css` (overzicht op `/designsystem`) |
| Bloktypes | `src/components/blokken/` (Hero, Punten, Tekst, Fotos, Prijzen, Formulier) |
| Kop, voet, iconen, foto's | `src/components/` |
| Paginasjabloon, SEO, JSON-LD | `src/layouts/Basis.astro` |
| Contentschema | `src/content.config.ts` |
| CMS-instellingen | `public/admin/config.yml`, beheerpagina `src/pages/admin/index.astro` |
| Redirects en headers | `netlify.toml` |
| Import uit Kirby | `scripts/kirby2astro.py` |

### Adressen

De oude adressen blijven hetzelfde: `/`, `/gezond-stemgebruik`, `/koorscholing` (zonder slash aan het eind;
daarom `trailingSlash: "never"` en `build.format: "file"`). Oude Kirby-adressen (`/home`, `/panel`,
`/media/pages/…`) sturen met een 301 door naar de juiste pagina.

### Een pagina of blok toevoegen

Via het CMS (zie hieronder) of met de hand: maak `src/content/pages/<slug>/index.md` met `title`, `order`
en een lijst `blocks`. Elk blok heeft een `type`: `hero`, `punten`, `tekst`, `fotos`, `prijzen` of
`formulier`. Kijk in `src/content.config.ts` welke velden een blok heeft. Foto's zet je in dezelfde map en
noem je bij hun bestandsnaam (`foto: annemiek.jpg`).

## Beheer (CMS)

Annemiek gaat naar **https://www.annemiekmaissan.nl/admin** en logt in met GitHub. Ze ziet:

- **Pagina's**: per pagina de titel, plaats in het menu en de blokken. Blokken kun je toevoegen,
  aanpassen, verslepen en verwijderen. Onderaan staan de titel en omschrijving voor Google.
- **Instellingen → Gegevens van de zangstudio**: naam, e-mailadres en sociale media.
- **Instellingen → Contactformulier**: de keuzes in het formulier en de tekst op de bedankpagina.

Opslaan is een commit op GitHub; Netlify zet de wijziging binnen ± 3 minuten live.

### Inrichten (eenmalig)

1. Koppel deze repo aan een Netlify-project (build: `npm run build`, publish: `dist`; staat al in `netlify.toml`).
2. GitHub → *Settings → Developer settings → OAuth Apps → New OAuth App*: homepage
   `https://www.annemiekmaissan.nl`, callback **`https://api.netlify.com/auth/done`**.
3. Netlify → *Project configuration → Access & security → OAuth → Install provider → GitHub*, met de
   Client ID en Client Secret uit stap 2.
4. Annemiek maakt een gratis GitHub-account. Geef haar in deze repo onder *Settings → Collaborators*
   schrijfrechten.
5. Annemiek gaat naar `/admin` → *Sign In with GitHub*.

Staat het Netlify-project achter wachtwoord- of SSO-beveiliging voor alle deploys, dan kan ook Annemiek niet
bij `/admin`. Zet beveiliging alleen op previews.

### Lokaal proberen

`npm run dev`, open in Chrome of Edge `http://localhost:4321/admin` → *Work with Local Repository* → kies deze
map. Wijzigingen komen direct in de bestanden; zelf committen.

## Toegankelijkheid en CSS

De site is gebouwd volgens **WCAG 2.2, niveau AA**, en gecontroleerd met axe-core (wcag2a/aa, 2.1, 2.2 en
best practices) op 1440 en 320 px: geen meldingen.

- Contrast: witte tekst op de achtergrond 4,95:1, zachte tekst 4,6:1, tekst op de kaarten ≥ 5,5:1,
  randen van invoervelden 5,5:1. Het patroon maakt de achtergrond alleen donkerder.
- Toetsenbord: skiplink, een focusring in twee kleuren (geel met donkere rand) die op wit en op petrol
  zichtbaar is, en `scroll-padding` zodat de focus nooit onder de vaste kop valt (2.4.11).
- Tikdoelen minimaal 44 × 44 px (2.5.8 vraagt 24). Geen horizontaal scrollen op 320 px (1.4.10).
- Formulier: zichtbare labels, `autocomplete`, uitleg over verplichte velden vóór het formulier (3.3.2),
  rode rand pas na een verzendpoging (`:user-invalid`).
- Houdt rekening met `prefers-reduced-motion`, `prefers-contrast: more` en `forced-colors`.

Moderne CSS: cascade layers (`reset`, `tokens`, `basis`, `hulp`; componentstijlen staan erbuiten en winnen),
native nesting, container queries (elke `.sectie` is een container), logische eigenschappen
(`inline-size`, `margin-block`), `text-wrap: balance/pretty`, `field-sizing`, `:user-invalid`,
`translate` en view transitions tussen pagina's. Doelgroep: browsers van de laatste twee jaar
(Chrome/Edge 120+, Safari 17.2+, Firefox 117+); oudere browsers tonen de site zonder de extra's.

## Formulier

Het contactformulier gebruikt **Netlify Forms** (naam `contact`, met een verborgen veld `pagina` en een
honeypot). Na verzenden komt de bezoeker op `/bedankt`.

- Zet in Netlify *Forms* de formulierdetectie aan.
- Stel onder *Forms → Form notifications* een e-mailmelding in naar **info@annemiekmaissan.nl**.

Het SMTP-wachtwoord van de oude site is hier niet meer nodig.

## Import uit Kirby

`python3 scripts/kirby2astro.py <pad-naar-kirby-site>` leest `content/` en schrijft de pagina's en
`src/data/site.json` opnieuw (bestaande paginamappen worden eerst leeggemaakt). Foto's worden verkleind tot
maximaal 2400 px. Vereist Python 3 met PyYAML en Pillow.

## Open punten

- [ ] **Backup van de live site importeren.** De eerste import kwam uit de repo, en die was ouder dan live.
      Een paar teksten zijn met de hand gelijkgetrokken met live (15-11-2026): het welkomstwoord op home, de
      afzegregel, "Kleurgebruik" weg bij Gezond stemgebruik, de kop "Koorscholing en stemvorming" en de
      menuvolgorde. Draai het importscript op de backup; daarna is dit niet meer nodig.
- [ ] **Gezond stemgebruik**: op live staan twee foto's die niet in de repo zitten
      (`whatsapp-image-2025-04-16-at-10.31.34-1.jpeg`, `workshop-33.jpg`) met de tekst "Workshop - Spreken met
      goed stemgebruik bij vergaderingen en presentaties". Komen mee met de backup.
- [ ] **Home**: de tekst "Het doel is om in een korte periode gericht te werken…" stond in Kirby, maar werd door
      een fout in het oude sjabloon nooit getoond. Nu staat hij er wel: nog bevestigen met Annemiek.
- [ ] **Nog bevestigen**: de tekst op de bedankpagina ("Annemiek neemt zo snel mogelijk contact met je op.")
      is nieuw geschreven.
- [ ] **Zoekmachines**: de live Kirby-site staat volledig op `noindex`. Deze site is wél vindbaar. Bevestigen
      dat dat de bedoeling is. Alle pagina's gebruiken nog de omschrijving "Zangstudio Annemiek Maissan";
      per pagina een eigen omschrijving schrijven.
- [ ] **Alt-teksten**: de drie grote foto's hebben een korte omschrijving gekregen; laten nakijken door Annemiek.
- [ ] **DNS-overstap**: de e-mail van info@annemiekmaissan.nl loopt via TransIP. Laat bij het omzetten de
      MX-, SPF- en DKIM-records staan en verander alleen de records voor de website.
- [ ] Niet overgenomen: de licht/donker-schakelaar, de opvultekst in de footer, en de ongebruikte blokken voor
      testimonials en video's. De letter Calendas Plus komt van de oude site; licentie voor webgebruik
      nakijken.
